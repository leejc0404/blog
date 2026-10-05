#!/usr/bin/env python3
"""자동완성 조회 (가이드 1-T 존재·각도 관문).
  python3 tools/ac.py g "헤드" ...   # 구글 (EUC-KR 응답 디코드)
  python3 tools/ac.py n "헤드" ...   # 네이버 (ac.search.naver.com)
"""
import sys, json, subprocess, urllib.parse

def google(q):
    b = subprocess.run(["curl", "-s", "--max-time", "15",
        "https://suggestqueries.google.com/complete/search?client=firefox&hl=ko&q=" + urllib.parse.quote(q)],
        capture_output=True).stdout
    for enc in ("euc-kr", "cp949", "utf-8"):
        try:
            return json.loads(b.decode(enc))[1]
        except Exception:
            pass
    return None

def naver(q):
    b = subprocess.run(["curl", "-s", "--max-time", "12", "-G", "https://ac.search.naver.com/nx/ac",
        "--data-urlencode", "q=" + q, "-d", "st=100", "-d", "frm=nv", "-d", "r_format=json"],
        capture_output=True).stdout
    try:
        return [x[0] for x in json.loads(b)["items"][0]]
    except Exception:
        return None

if __name__ == "__main__":
    fn = google if sys.argv[1] == "g" else naver
    for q in sys.argv[2:]:
        r = fn(q)
        print(f"[{sys.argv[1]}] {q} → " + ("조회 실패" if r is None else (" · ".join(r) or "(없음)")))
