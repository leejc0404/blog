#!/usr/bin/env python3
"""GSC 수집기 (지침서 0-9 SSOT).
  python3 tools/gsc_pull.py --site https://koreaplug.com/ --days 90 --out out/gsc

키: 환경변수 GSC_SA_JSON(JSON 원문 한 줄 또는 base64) 또는 GSC_SA_JSON_PATH(파일 경로).
    키 파일은 세션 임시 폴더에만 두고 저장소에 커밋하지 않는다(.gitignore 처리).
의존성: requests + PyJWT[crypto] (google 클라이언트 라이브러리 불필요)

산출물: out/gsc/{도메인}/{오늘}/
  daily.csv · pages_28d.csv · queries_28d.csv · query_page_28d.csv
  country_28d.csv · device_28d.csv · query_page_90d.csv
  engine_g_candidates.csv (노출 ≥ 50 · 순위 5~30 · 비정의형) · summary.md
기준일 = 오늘 − 3일 (GSC 확정 데이터 지연, dataState=final)
"""
import argparse, base64, csv, datetime as dt, json, os, re, sys, time, urllib.parse

import jwt
import requests

SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
DEFINITION_Q = re.compile(r"\b(meaning|means|definition|what is|what does|explained|why do koreans)\b", re.I)
DEFINITION_URL = re.compile(r"-meaning|why-do-koreans-|-explained")


def load_key():
    raw = os.environ.get("GSC_SA_JSON", "").strip().strip("'")
    if raw:
        try:
            return json.loads(raw)
        except ValueError:
            # 환경변수 칸에 base64로 넣은 경우
            return json.loads(base64.b64decode(raw))
    path = os.environ.get("GSC_SA_JSON_PATH")
    if path and os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    sys.exit("키 없음: GSC_SA_JSON 또는 GSC_SA_JSON_PATH를 지정하세요")


def token(key):
    now = int(time.time())
    assertion = jwt.encode({"iss": key["client_email"], "scope": SCOPE, "aud": key["token_uri"],
                            "iat": now, "exp": now + 3600}, key["private_key"], algorithm="RS256")
    r = requests.post(key["token_uri"], data={
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": assertion}, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]


class GSC:
    def __init__(self, site, tok, end):
        self.url = ("https://www.googleapis.com/webmasters/v3/sites/"
                    + urllib.parse.quote(site, safe="") + "/searchAnalytics/query")
        self.h = {"Authorization": "Bearer " + tok}
        self.end = end

    def query(self, days, dims, end=None):
        end = end or self.end
        rows, start_row = [], 0
        while True:
            r = requests.post(self.url, headers=self.h, timeout=60, json={
                "startDate": str(end - dt.timedelta(days=days - 1)), "endDate": str(end),
                "dimensions": dims, "rowLimit": 25000, "startRow": start_row, "dataState": "final"})
            if r.status_code != 200:
                sys.exit(f"GSC API {r.status_code}: {r.text[:300]}")
            batch = r.json().get("rows", [])
            rows += batch
            if len(batch) < 25000:
                return rows
            start_row += 25000


def write(path, dims, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(dims + ["clicks", "impressions", "ctr", "position"])
        for r in sorted(rows, key=lambda r: (-r["clicks"], -r["impressions"])):
            w.writerow(r["keys"] + [r["clicks"], r["impressions"], round(r["ctr"], 4), round(r["position"], 1)])


def by_page(rows):
    return {r["keys"][0]: r["clicks"] for r in rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="https://koreaplug.com/")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--out", default="out/gsc")
    a = ap.parse_args()

    end = dt.date.today() - dt.timedelta(days=3)
    g = GSC(a.site, token(load_key()), end)
    host = urllib.parse.urlparse(a.site).netloc
    out = os.path.join(a.out, host, str(dt.date.today()))
    os.makedirs(out, exist_ok=True)

    daily = g.query(a.days, ["date"])
    write(f"{out}/daily.csv", ["date"], daily)
    for name, dims in [("pages", ["page"]), ("queries", ["query"]), ("query_page", ["query", "page"]),
                       ("country", ["country"]), ("device", ["device"])]:
        write(f"{out}/{name}_28d.csv", dims, g.query(28, dims))
    qp = g.query(a.days, ["query", "page"])
    write(f"{out}/query_page_{a.days}d.csv", ["query", "page"], qp)

    cand = [r for r in qp if r["impressions"] >= 50 and 5 <= r["position"] <= 30
            and not DEFINITION_Q.search(r["keys"][0]) and not DEFINITION_URL.search(r["keys"][1])]
    write(f"{out}/engine_g_candidates.csv", ["query", "page"], cand)

    # summary.md — 7일·28일 클릭 변화, 페이지 클릭 상승·하락 상위
    clicks = [r["clicks"] for r in sorted(daily, key=lambda r: r["keys"][0])]
    s7, p7, s28, p28 = sum(clicks[-7:]), sum(clicks[-14:-7]), sum(clicks[-28:]), sum(clicks[-56:-28])
    cur = by_page(g.query(28, ["page"]))
    prev = by_page(g.query(28, ["page"], end=end - dt.timedelta(days=28)))
    delta = sorted(((cur.get(p, 0) - prev.get(p, 0), p) for p in set(cur) | set(prev)))
    pct = lambda a, b: f"{(a - b) / b * 100:+.0f}%" if b else "n/a"
    lines = [f"# GSC 요약 — {host} (기준일 {end})", "",
             f"- 7일 클릭 {s7} (직전 7일 {p7}, {pct(s7, p7)})",
             f"- 28일 클릭 {s28} (직전 28일 {p28}, {pct(s28, p28)})",
             f"- 엔진 G 후보 {len(cand)}건 (노출 100+ {sum(r['impressions'] >= 100 for r in cand)}건)", "",
             "## 28일 클릭 상승 상위"]
    lines += [f"- {d:+d} {p}" for d, p in reversed(delta[-5:]) if d > 0]
    lines += ["", "## 28일 클릭 하락 상위"]
    lines += [f"- {d:+d} {p}" for d, p in delta[:5] if d < 0]
    with open(f"{out}/summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:5]))
    print(f"→ {out}")


if __name__ == "__main__":
    main()
