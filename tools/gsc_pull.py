#!/usr/bin/env python3
"""
GSC 전수 수집기 — Search Console API (무료, 서비스 계정 인증).

사용:
  GSC_SA_JSON='{...서비스계정 JSON...}' python3 tools/gsc_pull.py
  GSC_SA_JSON_PATH=/path/key.json  python3 tools/gsc_pull.py --site https://koreaplug.com/ --days 90

산출물 (out/gsc/{site}/{YYYY-MM-DD}/):
  daily.csv            일별 클릭·노출·CTR·순위 (days일)
  pages_28d.csv        페이지별 최근 28일 + 직전 28일 델타
  queries_28d.csv      쿼리별 최근 28일 + 직전 28일 델타
  query_page_28d.csv   쿼리×페이지 (상위)
  query_page_{days}d.csv  90일 쿼리×페이지 (엔진 G 입력)
  engine_g_candidates.csv 노출≥50 · 순위 5~30 · 비정의형 쿼리 (엔진 G 1차 후보)
  device_28d.csv / country_28d.csv / appearance_28d.csv
  sitemaps.json
  summary.md           핵심 인사이트 자동 요약

인증 준비 (1회, 사용자 몫):
  1. console.cloud.google.com → 프로젝트 생성 → "Google Search Console API" 사용 설정
  2. IAM → 서비스 계정 생성 → 키(JSON) 다운로드
  3. search.google.com/search-console → 설정 → 사용자 및 권한 → 서비스 계정 이메일 추가 (권한: 전체)
  4. Claude Code 환경변수에 GSC_SA_JSON = JSON 파일 내용 통째로
"""
import argparse, csv, json, os, sys, datetime as dt
from collections import defaultdict

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    sys.exit("pip install google-auth google-api-python-client")

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def creds():
    raw = os.environ.get("GSC_SA_JSON")
    path = os.environ.get("GSC_SA_JSON_PATH")
    if raw:
        info = json.loads(raw)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    if path and os.path.exists(path):
        return service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
    sys.exit("GSC_SA_JSON 또는 GSC_SA_JSON_PATH 환경변수가 없습니다. 파일 상단 '인증 준비' 참조.")


def query(svc, site, start, end, dims, limit=25000, filters=None):
    rows, start_row = [], 0
    while True:
        body = {
            "startDate": start.isoformat(), "endDate": end.isoformat(),
            "dimensions": dims, "rowLimit": min(limit, 25000), "startRow": start_row,
            "dataState": "final",
        }
        if filters:
            body["dimensionFilterGroups"] = [{"filters": filters}]
        resp = svc.searchanalytics().query(siteUrl=site, body=body).execute()
        got = resp.get("rows", [])
        rows.extend(got)
        if len(got) < 25000 or len(rows) >= limit:
            break
        start_row += len(got)
    return rows


def flat(rows, dims):
    out = []
    for r in rows:
        d = dict(zip(dims, r["keys"]))
        d.update(clicks=r["clicks"], impressions=r["impressions"],
                 ctr=round(r["ctr"] * 100, 2), position=round(r["position"], 1))
        out.append(d)
    return out


def write_csv(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def with_delta(cur, prev, key):
    p = {r[key]: r for r in prev}
    for r in cur:
        q = p.get(r[key], {})
        r["clicks_prev"] = q.get("clicks", 0)
        r["impr_prev"] = q.get("impressions", 0)
        r["pos_prev"] = q.get("position", "")
        r["clicks_delta"] = r["clicks"] - r["clicks_prev"]
    cur.sort(key=lambda r: (-r["clicks"], -r["impressions"]))
    return cur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="https://koreaplug.com/")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--out", default="out/gsc")
    a = ap.parse_args()

    svc = build("searchconsole", "v1", credentials=creds(), cache_discovery=False)
    sites = [s["siteUrl"] for s in svc.sites().list().execute().get("siteEntry", [])]
    if a.site not in sites:
        sys.exit(f"서비스 계정이 접근 가능한 속성: {sites}\n→ GSC 사용자 및 권한에 서비스 계정 이메일을 추가했는지 확인.")

    end = dt.date.today() - dt.timedelta(days=3)          # GSC 확정 데이터 지연
    start_all = end - dt.timedelta(days=a.days - 1)
    c28_s, c28_e = end - dt.timedelta(days=27), end
    p28_s, p28_e = c28_s - dt.timedelta(days=28), c28_s - dt.timedelta(days=1)
    c7_s, p7_s = end - dt.timedelta(days=6), end - dt.timedelta(days=13)

    slug = a.site.replace("https://", "").strip("/").replace("/", "_")
    od = os.path.join(a.out, slug, dt.date.today().isoformat()); os.makedirs(od, exist_ok=True)

    # 1. 일별
    daily = flat(query(svc, a.site, start_all, end, ["date"]), ["date"])
    daily.sort(key=lambda r: r["date"])
    write_csv(f"{od}/daily.csv", daily, ["date", "clicks", "impressions", "ctr", "position"])

    # 2. 페이지 / 3. 쿼리 (28일 + 직전 28일)
    pages = with_delta(flat(query(svc, a.site, c28_s, c28_e, ["page"]), ["page"]),
                       flat(query(svc, a.site, p28_s, p28_e, ["page"]), ["page"]), "page")
    queries = with_delta(flat(query(svc, a.site, c28_s, c28_e, ["query"]), ["query"]),
                         flat(query(svc, a.site, p28_s, p28_e, ["query"]), ["query"]), "query")
    cols = ["clicks", "impressions", "ctr", "position", "clicks_prev", "impr_prev", "pos_prev", "clicks_delta"]
    write_csv(f"{od}/pages_28d.csv", pages, ["page"] + cols)
    write_csv(f"{od}/queries_28d.csv", queries, ["query"] + cols)

    # 4. 쿼리×페이지
    qp = flat(query(svc, a.site, c28_s, c28_e, ["query", "page"], limit=25000), ["query", "page"])
    qp.sort(key=lambda r: (-r["clicks"], -r["impressions"]))
    write_csv(f"{od}/query_page_28d.csv", qp, ["query", "page", "clicks", "impressions", "ctr", "position"])

    # 4-b. 엔진 G 입력 — 90일 쿼리×페이지 (지침서 0-1 G)
    qp90 = flat(query(svc, a.site, start_all, end, ["query", "page"], limit=25000), ["query", "page"])
    qp90.sort(key=lambda r: (-r["impressions"], -r["clicks"]))
    write_csv(f"{od}/query_page_{a.days}d.csv", qp90, ["query", "page", "clicks", "impressions", "ctr", "position"])
    DEF_Q = (" meaning", "what is ", "what does ", "why do ", "why are ", "why is ", " in korean", " in english")
    DEF_PAGE = ("-meaning", "why-do-koreans", "-explained", "-culture/")   # 정의형 제로클릭 페이지 — 지침서 1-6 B-Z
    gap = [r for r in qp90 if r["impressions"] >= 50 and 5 <= r["position"] <= 30
           and not any(k in r["query"] for k in DEF_Q)
           and not any(k in r["page"] for k in DEF_PAGE)
           and len(r["query"].split()) >= 2]                              # 용어 단독 쿼리 제외
    write_csv(f"{od}/engine_g_candidates.csv", gap, ["query", "page", "clicks", "impressions", "ctr", "position"])

    # 5. 기기 / 국가 / 검색 형태
    for dim in ("device", "country", "searchAppearance"):
        rows = flat(query(svc, a.site, c28_s, c28_e, [dim]), [dim])
        rows.sort(key=lambda r: -r["clicks"])
        write_csv(f"{od}/{dim.lower().replace('searchappearance','appearance')}_28d.csv", rows,
                  [dim, "clicks", "impressions", "ctr", "position"])

    # 6. 사이트맵
    try:
        sm = svc.sitemaps().list(siteUrl=a.site).execute()
        json.dump(sm, open(f"{od}/sitemaps.json", "w"), indent=1, ensure_ascii=False)
    except Exception as e:
        sm = {"error": str(e)}

    # 7. 요약
    def tot(rows, s, e):
        sub = [r for r in rows if s.isoformat() <= r["date"] <= e.isoformat()]
        c = sum(r["clicks"] for r in sub); i = sum(r["impressions"] for r in sub)
        return c, i, (c / i * 100 if i else 0), (sum(r["position"] * r["impressions"] for r in sub) / i if i else 0)

    c7, p7 = tot(daily, c7_s, end), tot(daily, p7_s, c7_s - dt.timedelta(days=1))
    c28, p28 = tot(daily, c28_s, c28_e), tot(daily, p28_s, p28_e)
    npages, nq = len(pages), len(queries)
    pages_1plus = sum(1 for r in pages if r["clicks"] >= 1)
    top10 = sum(r["clicks"] for r in pages[:10]); allc = sum(r["clicks"] for r in pages) or 1
    zero_click_big = [r for r in pages if r["impressions"] >= 300 and r["clicks"] <= 1]
    striking = [r for r in pages if 4 <= r["position"] <= 15 and r["impressions"] >= 200]
    losers = sorted(pages, key=lambda r: r["clicks_delta"])[:10]
    gainers = sorted(pages, key=lambda r: -r["clicks_delta"])[:10]

    def row(r, k):
        return f"| {r[k].replace(a.site,'/')} | {r['clicks']} | {r['impressions']} | {r['ctr']}% | {r['position']} | {r['clicks_delta']:+d} |"

    L = [f"# GSC 요약 — {a.site} (기준일 {end}, 수집 {dt.date.today()})", "",
         "## 사이트 전체", "| 구간 | 클릭 | 노출 | CTR | 순위 |", "|---|---|---|---|---|",
         f"| 최근 7일 | {c7[0]} | {c7[1]} | {c7[2]:.2f}% | {c7[3]:.1f} |",
         f"| 직전 7일 | {p7[0]} | {p7[1]} | {p7[2]:.2f}% | {p7[3]:.1f} |",
         f"| 최근 28일 | {c28[0]} | {c28[1]} | {c28[2]:.2f}% | {c28[3]:.1f} |",
         f"| 직전 28일 | {p28[0]} | {p28[1]} | {p28[2]:.2f}% | {p28[3]:.1f} |", "",
         f"- 7일 클릭 변화 **{c7[0]-p7[0]:+d}** ({(c7[0]/p7[0]-1)*100 if p7[0] else 0:+.0f}%) · 28일 **{c28[0]-p28[0]:+d}**",
         f"- 노출 페이지 {npages} · 클릭≥1 페이지 {pages_1plus} ({pages_1plus/npages*100 if npages else 0:.0f}%) · 상위 10편 클릭 집중도 {top10/allc*100:.0f}%",
         f"- 노출 쿼리 {nq}", "",
         "## 일별 (최근 21일)", "| 날짜 | 클릭 | 노출 | CTR | 순위 |", "|---|---|---|---|---|"]
    L += [f"| {r['date']} | {r['clicks']} | {r['impressions']} | {r['ctr']}% | {r['position']} |" for r in daily[-21:]]
    H = "| 페이지 | 클릭 | 노출 | CTR | 순위 | Δ클릭 |\n|---|---|---|---|---|---|"
    L += ["", "## 클릭 하락 상위 10 (28일 vs 직전 28일)", H] + [row(r, "page") for r in losers]
    L += ["", "## 클릭 상승 상위 10", H] + [row(r, "page") for r in gainers]
    L += ["", f"## 노출≥300인데 클릭≤1 (제로클릭 — {len(zero_click_big)}편)", H] + [row(r, "page") for r in zero_click_big[:25]]
    L += ["", f"## 4~15위 · 노출≥200 (업그레이드 후보 — {len(striking)}편)", H] + [row(r, "page") for r in sorted(striking, key=lambda r: -r['impressions'])[:25]]
    L += ["", "## 상위 쿼리 30", "| 쿼리 | 클릭 | 노출 | CTR | 순위 | Δ클릭 |", "|---|---|---|---|---|---|"]
    L += [f"| {r['query']} | {r['clicks']} | {r['impressions']} | {r['ctr']}% | {r['position']} | {r['clicks_delta']:+d} |" for r in queries[:30]]
    open(f"{od}/summary.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"완료 → {od}\n"); print("\n".join(L[:14]))


if __name__ == "__main__":
    main()
