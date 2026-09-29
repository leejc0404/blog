"""월간 달력 이미지 생성기 (0and1life · Routine_0and1Life-Writer STEP C · 가이드 0-8·2-9).

사용: python3 tools/month_calendar.py config.json out.png
- 화면 흐림 방지: 최종 크기(기본 2160px 폭)로 한 번에 그리고 무손실 PNG로 저장한다.
  (2026-09-29: 크게 그린 뒤 축소 + 손실 webp → 빨강·파랑 글자 번짐 → PNG로 해결)
- 필요 패키지: Pillow, korean-lunar-calendar, Noto Sans CJK(KR) 폰트

config 예:
{
 "year": 2026, "month": 11,
 "title": "2026년 11월 달력",
 "subtitle": "…",                                 # 빨간 글씨 한 줄 요약
 "holidays": {"3": "개천절"},                     # 공휴일·대체공휴일 (관공서 공휴일 규정·공식 공지로 확인한 것만)
 "notes_day": {"1": "국군의 날(평일)"},           # 날짜 칸 회색 메모
 "solar_terms": {"7": "입동", "22": "소설"},      # 24절기 (한국천문연구원 등 공식 확인분만)
 "son_eopneun": true,                             # 손없는 날 자동 표시(음력 9·10·19·20·29·30일)
 "leave": [6, 7, 8], "leave_label": "연차 추천",  # 노란 칸
 "span": [3, 11], "span_label": "9일 연휴",       # 연휴 띠 (없으면 생략)
 "footnotes": ["…"],
 "credit": "0and1life.com · 2026-10-25 기준"
}
"""
import calendar
import json
import sys

from korean_lunar_calendar import KoreanLunarCalendar
from PIL import Image, ImageDraw, ImageFont

import glob
import os

KR = 1  # NotoSansCJK .ttc 안의 KR 인덱스


def _font_file(weight):
    """Noto Sans CJK(KR) 경로 탐색. MC_FONT_DIR 환경변수 > 일반 설치 경로."""
    dirs = [os.environ.get("MC_FONT_DIR", ""), "/usr/share/fonts/opentype/noto/",
            "/usr/share/fonts/noto-cjk/", "/usr/share/fonts/truetype/noto/", "/usr/share/fonts/"]
    for d in filter(None, dirs):
        hit = glob.glob(os.path.join(d, "**", f"NotoSansCJK-{weight}.ttc"), recursive=True)
        if hit:
            return hit[0]
    raise SystemExit(f"한글 폰트 없음(NotoSansCJK-{weight}.ttc) — 가이드 2-9: HTML 달력 표로 대체")

C = {
    "bg": "#ffffff", "ink": "#1f2937", "sub": "#6b7280", "line": "#e5e7eb",
    "red": "#e11d48", "blue": "#2563eb", "leave": "#fef3c7", "leave_ink": "#b45309",
    "span": "#fee2e2", "span_ink": "#be123c", "head": "#f9fafb", "brand": "#111827",
    "term": "#047857",
}


def lunar(y, m, d):
    k = KoreanLunarCalendar()
    k.setSolarDate(y, m, d)
    _, lm, ld = map(int, k.LunarIsoFormat().split(" ")[0].split("-")[:3])
    return lm, ld


def draw(cfg, out, k=1.8):
    S = lambda v: round(v * k)
    fonts = {}

    def font(weight, size):
        key = (weight, size)
        if key not in fonts:
            fonts[key] = ImageFont.truetype(_font_file(weight), S(size), index=KR)
        return fonts[key]

    y, m = cfg["year"], cfg["month"]
    hol = {int(a): b for a, b in cfg.get("holidays", {}).items()}
    notes = {int(a): b for a, b in cfg.get("notes_day", {}).items()}
    terms = {int(a): b for a, b in cfg.get("solar_terms", {}).items()}
    son = cfg.get("son_eopneun", False)
    leave = set(cfg.get("leave", []))
    span = cfg.get("span")
    foot = cfg.get("footnotes", [])

    W, pad, top, ch, head_h = 1200, 56, 220, 170, 56
    weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(y, m)  # 일요일 시작
    cw = (W - pad * 2) / 7
    H = top + head_h + ch * len(weeks) + 60 + 40 * len(foot) + 70

    im = Image.new("RGB", (S(W), S(H)), C["bg"])
    d = ImageDraw.Draw(im)
    T = lambda x, yy, t, f, c: d.text((S(x), S(yy)), t, font=f, fill=c)
    tw = lambda t, f: d.textlength(t, font=f) / k

    T(pad, 50, cfg["title"], font("Bold", 64), C["brand"])
    T(pad, 138, cfg.get("subtitle", ""), font("Medium", 32), C["red"])

    d.rectangle([S(pad), S(top), S(W - pad), S(top + head_h)], fill=C["head"])
    for i, n in enumerate(["일", "월", "화", "수", "목", "금", "토"]):
        f = font("Bold", 28)
        col = C["red"] if i == 0 else C["blue"] if i == 6 else C["ink"]
        T(pad + i * cw + (cw - tw(n, f)) / 2, top + 10, n, f, col)

    gy = top + head_h
    for r, wk in enumerate(weeks):
        for i, day in enumerate(wk):
            x0, y0 = pad + i * cw, gy + r * ch
            x1, y1 = x0 + cw, y0 + ch
            if day and day in leave:
                d.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=C["leave"])
            d.rectangle([S(x0), S(y0), S(x1), S(y1)], outline=C["line"], width=S(2))
            if not day:
                continue
            col = C["red"] if (i == 0 or day in hol) else C["blue"] if i == 6 else C["ink"]
            T(x0 + 16, y0 + 8, str(day), font("Bold", 46), col)
            lm, ld = lunar(y, m, day)
            lt, fl = f"{lm}.{ld}", font("Regular", 20)
            T(x1 - 14 - tw(lt, fl), y0 + 16, lt, fl, C["sub"])
            ty = y0 + 70
            if day in hol:
                T(x0 + 16, ty, hol[day], font("Bold", 24), C["red"]); ty += 32
            if day in terms:
                T(x0 + 16, ty, terms[day], font("Medium", 21), C["term"]); ty += 28
            if day in notes:
                T(x0 + 16, ty, notes[day], font("Medium", 21), C["sub"]); ty += 28
            if son and ld in (9, 10, 19, 20, 29, 30) and ty < y0 + 130:
                T(x0 + 16, ty, "손없는 날", font("Regular", 19), C["sub"]); ty += 26
            if day in leave:
                T(x0 + 16, ty, cfg.get("leave_label", "연차"), font("Bold", 24), C["leave_ink"])
            if span and span[0] <= day <= span[1]:
                by = y1 - 30
                d.rectangle([S(x0 + 2), S(by), S(x1 - 2), S(y1 - 4)], fill=C["span"])
                if day == span[0] or i == 0:
                    lab = cfg.get("span_label", "") if day == span[0] else "▶"
                    T(x0 + 10, by - 1, lab, font("Bold", 20), C["span_ink"])

    fy = gy + ch * len(weeks) + 30
    for t in foot:
        T(pad, fy, "· " + t, font("Regular", 25), C["ink"]); fy += 40
    T(pad, H - 50, cfg.get("credit", ""), font("Regular", 22), C["sub"])
    note, fn = "음력은 오른쪽 위 작은 숫자", font("Regular", 20)
    T(W - pad - tw(note, fn), H - 48, note, fn, C["sub"])
    im.save(out, optimize=True)  # PNG 무손실


if __name__ == "__main__":
    draw(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2])
