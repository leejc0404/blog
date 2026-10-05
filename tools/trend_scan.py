#!/usr/bin/env python3
"""포착면 12소스 스캔 (가이드 0-2). ★ = 새 것 신호. 출력 끝에 TOTAL/NEW.
  python3 tools/trend_scan.py
헤드 추출(고유명사 1~3어절)은 이 출력을 보고 루틴이 한다."""
import subprocess,re,json,html
def get(u):
    r=subprocess.run(['curl','-s','--max-time','15','-A','Mozilla/5.0','-w','\n%{http_code}',u],capture_output=True)
    b=r.stdout; code=b[-3:].decode(); b=b[:-4]
    for e in ['utf-8','cp949','euc-kr']:
        try: return code,b.decode(e)
        except: pass
    return code,b.decode('utf-8','ignore')
out={}
c,t=get("https://trends.google.co.kr/trending/rss?geo=KR")
items=[]
for it in re.findall(r'<item>(.*?)</item>',t,re.S):
    ti=re.search(r'<title>(.*?)</title>',it).group(1)
    tr=re.search(r'<ht:approx_traffic>(.*?)</ht:approx_traffic>',it); tr=tr.group(1) if tr else ''
    ns=re.findall(r'<ht:news_item_title>(.*?)</ht:news_item_title>',it)[:2]
    items.append(f"{ti}|{tr}|{' / '.join(html.unescape(n) for n in ns)}")
out['1 trends']=(c,items)
c,t=get("https://news.naver.com/main/ranking/popularDay.naver")
out['2 rank']=(c,list(dict.fromkeys(re.findall(r'list_title[^>]*>([^<]{8,90})<',t)))[:50])
for k,u in [('3 IT','section/105'),('4 econ','section/101'),('5 life','section/103'),('7 731','breakingnews/section/105/731'),('8 226','breakingnews/section/105/226'),('9 263','breakingnews/section/101/263'),('10 376','breakingnews/section/103/376')]:
    c,t=get("https://news.naver.com/"+u)
    out[k]=(c,list(dict.fromkeys(html.unescape(x) for x in re.findall(r'class="sa_text_strong">([^<]{8,90})<',t)))[:16])
c,t=get("https://www.producthunt.com/feed"); out['6 PH']=(c,re.findall(r'<title>(.*?)</title>',t)[1:12])
c,t=get("https://rss.marketingtools.apple.com/api/v2/kr/apps/top-free/25/apps.json")
try: out['11 app']=(c,[f"{x['name']}({x['artistName']})" for x in json.loads(t)['feed']['results']])
except Exception as e: out['11 app']=(c,[str(e)])
c,t=get("https://api.signal.bz/news/realtime")
try: out['12 signal']=(c,[x['keyword'] for x in json.loads(t)['top10']])
except Exception as e: out['12 signal']=(c,[str(e)])
pat=re.compile('시행|출시|도입|개편|인상|인하|신설|확대|폐지|의무|단속|오픈|첫|바뀐|달라')
tot=0;new=0
for k,(c,l) in out.items():
    tot+=len(l)
    print(f"### {k} HTTP {c} n={len(l)}")
    for x in l:
        m=bool(pat.search(x)); new+=m
        print(('★ ' if m else '  ')+x[:160])
print('TOTAL',tot,'NEW',new)
