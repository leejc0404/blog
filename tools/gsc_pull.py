#!/usr/bin/env python3
"""Search Console 데이터 수집기 — KoreaPlug-Writer 지침 `0-9` 규격.

서비스 계정 키로 Search Console API를 직접 호출해 CSV/요약을 떨어뜨린다.
google-auth 없이 `cryptography`만으로 JWT를 서명하므로 추가 설치가 필요 없다.

사용:
    python3 tools/gsc_pull.py --site https://koreaplug.com/ --days 90 --out out/gsc

키는 `GSC_SA_JSON`(JSON 원문) 또는 `GSC_SA_JSON_PATH`(파일 경로)에서 읽는다.
"""

import argparse
import base64
import csv
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import time

import requests

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    _HAVE_CRYPTO = True
except Exception:  # 바인딩이 깨진 컨테이너에서 ImportError가 아닌 패닉이 나기도 한다
    _HAVE_CRYPTO = False

TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
API = "https://searchconsole.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query"


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def load_key():
    raw = os.environ.get("GSC_SA_JSON")
    if not raw:
        path = os.environ.get("GSC_SA_JSON_PATH")
        if not path:
            sys.exit("GSC_SA_JSON / GSC_SA_JSON_PATH 둘 다 없음")
        raw = open(path).read()
    return json.loads(raw)


def _sign(pem: str, data: bytes) -> bytes:
    """RS256 서명. cryptography가 없거나 바인딩이 깨져 있으면 openssl CLI로 떨어진다."""
    if _HAVE_CRYPTO:
        key = serialization.load_pem_private_key(pem.encode(), password=None)
        return key.sign(data, padding.PKCS1v15(), hashes.SHA256())
    with tempfile.TemporaryDirectory() as d:
        kp = os.path.join(d, "k.pem")
        with open(kp, "w") as f:
            f.write(pem)
        os.chmod(kp, 0o600)
        r = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", kp],
            input=data,
            capture_output=True,
            check=True,
        )
        return r.stdout


def access_token(sa):
    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT", "kid": sa["private_key_id"]}
    claims = {
        "iss": sa["client_email"],
        "scope": SCOPE,
        "aud": TOKEN_URI,
        "iat": now,
        "exp": now + 3600,
    }
    signing_input = f"{_b64(json.dumps(header).encode())}.{_b64(json.dumps(claims).encode())}"
    sig = _sign(sa["private_key"], signing_input.encode())
    assertion = f"{signing_input}.{_b64(sig)}"
    r = requests.post(
        TOKEN_URI,
        data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": assertion},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def query(token, site, start, end, dims, row_limit=25000, data_state="final"):
    """차원 조합으로 전체 행을 페이징해 가져온다."""
    url = API.format(site=requests.utils.quote(site, safe=""))
    rows, start_row = [], 0
    while True:
        body = {
            "startDate": start,
            "endDate": end,
            "dimensions": dims,
            "rowLimit": row_limit,
            "startRow": start_row,
            "dataState": data_state,
        }
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=body,
            timeout=120,
        )
        if r.status_code != 200:
            sys.stderr.write(f"[warn] {dims} {r.status_code}: {r.text[:300]}\n")
            return rows
        batch = r.json().get("rows", [])
        rows.extend(batch)
        if len(batch) < row_limit:
            return rows
        start_row += row_limit


def write_csv(path, dims, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(list(dims) + ["clicks", "impressions", "ctr", "position"])
        for row in rows:
            w.writerow(
                list(row.get("keys", []))
                + [
                    row.get("clicks", 0),
                    row.get("impressions", 0),
                    round(row.get("ctr", 0), 5),
                    round(row.get("position", 0), 2),
                ]
            )
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--out", default="out/gsc")
    args = ap.parse_args()

    sa = load_key()
    token = access_token(sa)

    # 기준일 = 오늘 − 3일 (GSC 확정 데이터 지연, 지침 `0-9`)
    today = dt.date.today()
    end = today - dt.timedelta(days=3)
    start_long = end - dt.timedelta(days=args.days - 1)
    start_28 = end - dt.timedelta(days=27)

    host = args.site.replace("https://", "").replace("http://", "").strip("/")
    outdir = os.path.join(args.out, host, today.isoformat())
    os.makedirs(outdir, exist_ok=True)

    def pull(name, dims, start, end_, **kw):
        rows = query(token, args.site, start, end_, dims, **kw)
        n = write_csv(os.path.join(outdir, name), dims, rows)
        print(f"{name}: {n} rows")
        return rows

    daily = pull("daily.csv", ["date"], start_long.isoformat(), end.isoformat())
    pull("pages_28d.csv", ["page"], start_28.isoformat(), end.isoformat())
    pull("queries_28d.csv", ["query"], start_28.isoformat(), end.isoformat())
    qp28 = pull("query_page_28d.csv", ["query", "page"], start_28.isoformat(), end.isoformat())
    pull("country_28d.csv", ["country"], start_28.isoformat(), end.isoformat())
    pull("device_28d.csv", ["device"], start_28.isoformat(), end.isoformat())
    # 엔진 G 입력 — 90일 query_page
    qp_long = pull(
        f"query_page_{args.days}d.csv", ["query", "page"], start_long.isoformat(), end.isoformat()
    )

    # 엔진 G 1차 필터: 노출 >= 50 · 순위 5~30 · 비정의형
    defn = ("meaning", "what is", "what's", "why do", "why does", "why are", "explained", "definition")
    cands = [
        r
        for r in qp_long
        if r.get("impressions", 0) >= 50
        and 5 <= r.get("position", 0) <= 30
        and not any(t in r["keys"][0].lower() for t in defn)
    ]
    cands.sort(key=lambda r: -r["impressions"])
    write_csv(os.path.join(outdir, "engine_g_candidates.csv"), ["query", "page"], cands)
    print(f"engine_g_candidates.csv: {len(cands)} rows")

    # summary.md
    def window(rows, days):
        cutoff = end - dt.timedelta(days=days - 1)
        sel = [r for r in rows if r["keys"][0] >= cutoff.isoformat()]
        return sum(r.get("clicks", 0) for r in sel), sum(r.get("impressions", 0) for r in sel)

    c7, i7 = window(daily, 7)
    c7p, i7p = 0, 0
    cut_a, cut_b = end - dt.timedelta(days=13), end - dt.timedelta(days=7)
    for r in daily:
        if cut_a.isoformat() <= r["keys"][0] <= cut_b.isoformat():
            c7p += r.get("clicks", 0)
            i7p += r.get("impressions", 0)
    c28, i28 = window(daily, 28)
    c28p = sum(
        r.get("clicks", 0)
        for r in daily
        if (end - dt.timedelta(days=55)).isoformat() <= r["keys"][0] <= (end - dt.timedelta(days=28)).isoformat()
    )

    # 페이지별 클릭 상승·하락 (직전 28일 대비)
    def page_clicks(start, end_):
        rows = query(token, args.site, start, end_, ["page"])
        return {r["keys"][0]: r.get("clicks", 0) for r in rows}

    cur = page_clicks(start_28.isoformat(), end.isoformat())
    prev = page_clicks(
        (end - dt.timedelta(days=55)).isoformat(), (end - dt.timedelta(days=28)).isoformat()
    )
    delta = {p: cur.get(p, 0) - prev.get(p, 0) for p in set(cur) | set(prev)}
    up = sorted(delta.items(), key=lambda kv: -kv[1])[:5]
    down = sorted(delta.items(), key=lambda kv: kv[1])[:5]

    with open(os.path.join(outdir, "summary.md"), "w", encoding="utf-8") as f:
        f.write(f"# GSC summary — {host} (기준일 {end.isoformat()}, dataState=final)\n\n")
        f.write(f"- 7일 클릭 {c7} (직전 7일 {c7p}, {c7 - c7p:+d}) · 노출 {i7}\n")
        f.write(f"- 28일 클릭 {c28} (직전 28일 {c28p}, {c28 - c28p:+d}) · 노출 {i28}\n")
        f.write(f"- 28일 query_page 행 {len(qp28)} · {args.days}일 query_page 행 {len(qp_long)}\n")
        f.write(f"- 엔진 G 1차 후보 {len(cands)}건 (노출≥50 · 순위 5~30 · 비정의형)\n\n")
        f.write("## 클릭 상승 상위\n")
        for p, d in up:
            f.write(f"- {d:+d} {p} (28일 {cur.get(p, 0)})\n")
        f.write("\n## 클릭 하락 상위\n")
        for p, d in down:
            f.write(f"- {d:+d} {p} (28일 {cur.get(p, 0)})\n")
    print(f"out: {outdir}")


if __name__ == "__main__":
    main()
