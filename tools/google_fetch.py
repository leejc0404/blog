#!/usr/bin/env python3
"""GSC · GA4 읽기 전용 조회 (서비스계정 JWT → 액세스 토큰 → REST).

자격증명은 환경변수로만 받는다. 저장소·Notion·프롬프트에 두지 않는다.
  GOOGLE_SA_JSON   서비스계정 키 JSON 본문 그대로, 또는 그 파일 경로
  GSC_SITE_URL     예: https://0and1life.com/   (또는 sc-domain:0and1life.com)
  GA4_PROPERTY_ID  예: 540835629

사용:
  python3 tools/google_fetch.py gsc-sites
  python3 tools/google_fetch.py gsc-query  --days 28 --dim page  --limit 50
  python3 tools/google_fetch.py gsc-query  --days 28 --dim query --limit 100
  python3 tools/google_fetch.py ga4-pages  --days 28 --limit 50          # 페이지별 세션 (네이버/전체)
  python3 tools/google_fetch.py ga4-sources --days 28
출력은 TSV(stdout). 토큰·키는 절대 출력하지 않는다.
"""
import base64, json, os, sys, time, urllib.parse, urllib.request
from datetime import date, timedelta

SCOPES = ("https://www.googleapis.com/auth/webmasters.readonly "
          "https://www.googleapis.com/auth/analytics.readonly")


def _die(msg, code=2):
    print("ERR " + msg, file=sys.stderr); sys.exit(code)


def load_sa():
    raw = os.environ.get("GOOGLE_SA_JSON")
    if not raw:
        _die("GOOGLE_SA_JSON 미설정")
    if raw.strip().startswith("{"):
        return json.loads(raw)
    with open(raw, encoding="utf-8") as f:
        return json.load(f)


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def access_token(sa: dict) -> str:
    import subprocess, tempfile
    now = int(time.time())
    header = _b64(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claim = _b64(json.dumps({
        "iss": sa["client_email"], "scope": SCOPES,
        "aud": sa["token_uri"], "iat": now, "exp": now + 3600,
    }).encode())
    # openssl CLI로 RS256 서명 (python cryptography 의존 제거). 키 파일은 즉시 삭제.
    with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False) as kf:
        kf.write(sa["private_key"]); kpath = kf.name
    try:
        sig = subprocess.run(["openssl", "dgst", "-sha256", "-sign", kpath],
                             input=f"{header}.{claim}".encode(), capture_output=True, check=True).stdout
    finally:
        os.unlink(kpath)
    jwt = f"{header}.{claim}.{_b64(sig)}"
    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": jwt}).encode()
    req = urllib.request.Request(sa["token_uri"], data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["access_token"]
    except urllib.error.HTTPError as e:
        _die(f"토큰 교환 실패 HTTP {e.code}: {e.read()[:300].decode(errors='replace')}")


def call(tok: str, url: str, body=None):
    req = urllib.request.Request(url, method="POST" if body is not None else "GET",
                                 headers={"Authorization": f"Bearer {tok}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, data=json.dumps(body).encode() if body is not None else None,
                                    timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        _die(f"API 실패 HTTP {e.code} {url}: {e.read()[:400].decode(errors='replace')}")


def _range(days: int):
    end = date.today() - timedelta(days=2)          # GSC·GA4 모두 최근 2일은 미확정
    return (end - timedelta(days=days - 1)).isoformat(), end.isoformat()


def gsc_sites(tok, a):
    d = call(tok, "https://searchconsole.googleapis.com/webmasters/v3/sites")
    print("siteUrl\tpermissionLevel")
    for s in d.get("siteEntry", []):
        print(f"{s['siteUrl']}\t{s['permissionLevel']}")


def gsc_query(tok, a):
    site = os.environ.get("GSC_SITE_URL") or _die("GSC_SITE_URL 미설정")
    s, e = _range(a.days)
    body = {"startDate": s, "endDate": e, "dimensions": [a.dim],
            "rowLimit": a.limit, "dataState": "final"}
    if a.contains:
        body["dimensionFilterGroups"] = [{"filters": [
            {"dimension": a.dim, "operator": "contains", "expression": a.contains}]}]
    d = call(tok, "https://searchconsole.googleapis.com/webmasters/v3/sites/"
                  f"{urllib.parse.quote(site, safe='')}/searchAnalytics/query", body)
    print(f"# {site} {s}~{e} dim={a.dim}")
    print(f"{a.dim}\tclicks\timpressions\tctr\tposition")
    for r in d.get("rows", []):
        print(f"{r['keys'][0]}\t{r['clicks']}\t{r['impressions']}\t{r['ctr']:.4f}\t{r['position']:.1f}")


def _ga4(tok, prop, body):
    return call(tok, f"https://analyticsdata.googleapis.com/v1beta/properties/{prop}:runReport", body)


def ga4_pages(tok, a):
    prop = os.environ.get("GA4_PROPERTY_ID") or _die("GA4_PROPERTY_ID 미설정")
    s, e = _range(a.days)
    body = {"dateRanges": [{"startDate": s, "endDate": e}],
            "dimensions": [{"name": "pagePath"}, {"name": "sessionSource"}],
            "metrics": [{"name": "sessions"}, {"name": "engagementRate"}],
            "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
            "limit": a.limit * 4}
    d = _ga4(tok, prop, body)
    agg = {}
    for r in d.get("rows", []):
        path, src = r["dimensionValues"][0]["value"], r["dimensionValues"][1]["value"].lower()
        n = int(r["metricValues"][0]["value"])
        t = agg.setdefault(path, [0, 0])
        t[0] += n
        if "naver" in src:
            t[1] += n
    print(f"# property {prop} {s}~{e}")
    print("pagePath\tsessions_total\tsessions_naver")
    for path, (tot, nav) in sorted(agg.items(), key=lambda x: -x[1][0])[: a.limit]:
        print(f"{path}\t{tot}\t{nav}")


def ga4_sources(tok, a):
    prop = os.environ.get("GA4_PROPERTY_ID") or _die("GA4_PROPERTY_ID 미설정")
    s, e = _range(a.days)
    d = _ga4(tok, prop, {"dateRanges": [{"startDate": s, "endDate": e}],
                         "dimensions": [{"name": "sessionSourceMedium"}],
                         "metrics": [{"name": "sessions"}, {"name": "engagementRate"}],
                         "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
                         "limit": 25})
    print(f"# property {prop} {s}~{e}")
    print("sourceMedium\tsessions\tengagementRate")
    for r in d.get("rows", []):
        v = r["metricValues"]
        print(f"{r['dimensionValues'][0]['value']}\t{v[0]['value']}\t{float(v[1]['value']):.3f}")


def main():
    import argparse
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("gsc-sites")
    q = sub.add_parser("gsc-query"); q.add_argument("--days", type=int, default=28)
    q.add_argument("--dim", choices=["page", "query", "date"], default="page")
    q.add_argument("--limit", type=int, default=50); q.add_argument("--contains", default=None)
    g = sub.add_parser("ga4-pages"); g.add_argument("--days", type=int, default=28)
    g.add_argument("--limit", type=int, default=50)
    s = sub.add_parser("ga4-sources"); s.add_argument("--days", type=int, default=28)
    a = p.parse_args()
    tok = access_token(load_sa())
    {"gsc-sites": gsc_sites, "gsc-query": gsc_query,
     "ga4-pages": ga4_pages, "ga4-sources": ga4_sources}[a.cmd](tok, a)


if __name__ == "__main__":
    main()
