#!/usr/bin/env python3
"""수요 계기판 (가이드 0-3) — 네이버 데이터랩 릴레이로 헤드별 D·F 측정.

  python3 tools/naver_gauge.py "GV80 하이브리드" "리센느 빵" ...      # 최근 37일
  python3 tools/naver_gauge.py --year-ago "도시가스 요금" ...          # 작년 같은 구간(시즌 선행)
  python3 tools/naver_gauge.py --news "헤드"                           # 신선 경로(1-T3): 뉴스 total
  --json 이면 JSON 출력.

D = 후보 최근3일 평균 / 앵커 최근3일 평균,  F = 후보 최근3일 평균 / 이전 34일 평균
(오늘 값은 미완성이라 제외. 앵커 = '실업급여 조건'. 판정 임계값은 가이드 0-3이 SSOT — 여기 두지 않는다.)
환경변수: WP_USER, WP_APP_PASS, NAVER_APIGW_KEY_ID, NAVER_APIGW_KEY (출력 금지)
"""
import sys, os, json, subprocess, datetime as dt, time

ANCHOR = "실업급여 조건"
BASE = "https://0and1life.com/wp-json/o1/v1/"

def _curl(path, params):
    cmd = ["curl", "-s", "--max-time", "25",
           "-u", f"{os.environ['WP_USER']}:{os.environ['WP_APP_PASS']}",
           "-H", f"X-O1-NKID: {os.environ['NAVER_APIGW_KEY_ID']}",
           "-H", f"X-O1-NKEY: {os.environ['NAVER_APIGW_KEY']}",
           "-G", BASE + path]
    for k, v in params.items():
        cmd += ["--data-urlencode", f"{k}={v}"]
    for attempt in range(2):
        r = subprocess.run(cmd, capture_output=True, text=True)
        try:
            return json.loads(r.stdout)
        except Exception:
            time.sleep(1)
    return {"error": r.stdout[:200]}

def measure(heads, year_ago=False):
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).date()
    end = today - dt.timedelta(days=365) if year_ago else today
    start = end - dt.timedelta(days=37)
    out = []
    for i in range(0, len(heads), 4):
        batch = heads[i:i + 4]
        body = {"startDate": start.isoformat(), "endDate": end.isoformat(), "timeUnit": "date",
                "keywordGroups": [{"groupName": k, "keywords": [k]} for k in [ANCHOR] + batch]}
        j = _curl("naver-trend", {"body": json.dumps(body, ensure_ascii=False)})
        if "results" not in j:
            out += [{"head": h, "D": None, "F": None, "err": str(j)[:120]} for h in batch]
            continue
        days = [(start + dt.timedelta(days=n)).isoformat() for n in range((end - start).days + 1)]
        if not year_ago:
            days = days[:-1]  # 오늘 제외
        series = {}
        for g in j["results"]:
            m = {d["period"]: d["ratio"] for d in g["data"]}
            series[g["title"]] = [m.get(d, 0.0) for d in days]
        a = series.get(ANCHOR, [])
        # 데이터랩 반영 지연: 앵커가 0인 꼬리 날짜(아직 집계 전)는 잘라낸다
        while a and a[-1] == 0:
            a = a[:-1]
            for k in series: series[k] = series[k][:-1]
        a3 = sum(a[-3:]) / 3 if a else 0
        for h in batch:
            v = series.get(h, [])
            if not v:
                out.append({"head": h, "D": None, "F": None, "err": "no series"}); continue
            r3 = sum(v[-3:]) / 3
            prior = sum(v[:-3]) / max(1, len(v) - 3)
            if year_ago:  # 작년: 구간 피크 / 같은 요청 앵커 평균
                D = max(v) / (sum(a) / len(a)) if a and sum(a) else 0
                F = None
            else:
                D = r3 / a3 if a3 else 0
                F = (r3 / prior) if prior > 0 else (99.0 if r3 > 0 else 0.0)
            out.append({"head": h, "D": round(D, 2), "F": None if F is None else round(F, 1),
                        "yesterday": v[-1], "max": max(v)})
        time.sleep(0.5)
    return out

def news_total(head):
    j = _curl("naver-check", {"q": head, "type": "news", "display": "10", "sort": "date"})
    return j.get("total"), [it.get("pubDate", "") for it in j.get("items", [])][:3]

if __name__ == "__main__":
    args = sys.argv[1:]
    as_json = "--json" in args
    year = "--year-ago" in args
    news = "--news" in args
    heads = [a for a in args if not a.startswith("--")]
    if news:
        res = [{"head": h, "news_total": news_total(h)[0], "latest": news_total(h)[1]} for h in heads]
    else:
        res = measure(heads, year)
        res.sort(key=lambda r: -((r["D"] or 0) * min(r["F"] or 1, 10)))
    if as_json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        for r in res:
            print(" | ".join(f"{k}={v}" for k, v in r.items()))
