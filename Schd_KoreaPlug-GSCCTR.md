# Schd_KoreaPlug-GSCCTR — 구글 "노출 많고 CTR 낮은 글" 개선 루틴 (Cowork 예약 작업용)

*매일 07:00 KST 실행. 예약 시각이 되면 같은 날 이미 실행됐더라도 다시 진행한다(판정·잠금은 `state.json` 이 막아 주므로 같은 글을 두 번 고치지 않는다).

날짜: 실행 시점의 실제 KST 날짜를 쓴다. 이 프롬프트에 적힌 고정 날짜는 무시한다.

이 루틴이 하는 일 (0and1life 네이버 루틴 `Schd_0and1Life-NaverCTR.md` 와 같은 구조, 데이터 원천만 다르다):
1. **서치콘솔 실적 화면을 Claude in Chrome 으로 읽는다** — CSV·API 키·네트워크 설정 없이 로그인된 크롬으로 본다. 날짜 범위를 지정할 수 있어 "고친 다음날 이후"만 잘라 정확히 잰다
2. **우리 사이트 자체 데이터로 "순위별 정상 CTR"을 매일 계산**하고, 같은 순위 구간의 평균보다 낮은 글을 "비정상"으로 잡는다 (고정 목표값이 아니라 우리 데이터가 기준)
3. **이미 고친 글의 효과를 매일 판정**한다 → 개선이면 유지, 개선이 없으면 재수정, 나빠졌으면 되돌림
4. 새 대상 1편을 고른다 → **우선순위 규칙(아래)** 대로. 시기성 글(긴급)은 그날 바로 수정, 상시 글도 NORMAL_MODE=AUTO 면 그날 반영
5. 그 글의 **검색어 표를 점수화해 진짜 타깃 검색어**를 고르고, **국가별 노출**로 "누가 보고 있는지"를 확인한다
6. 고치기 전에 **그 검색어로 실제 클릭을 가져가는 글(상위 노출 글)을 벤치마킹**한다 — 제목·설명·첫 문단이 어떻게 생겼는지 데이터로 확인하고, 수정안은 거기서 나온 근거로만 쓴다
7. 수정은 버전(v1·v2·v3)으로 기록해 다음 날 같은 글을 다시 고치지 않는다
8. 결과는 **누적 성적표가 붙은 쉬운 한글 보고(STEP 10)** 로 끝낸다

### 우선순위 규칙 (대상 선정의 논리 — 반드시 이 순서)
- **1차 — 데이터**: 최근 28일에 **노출은 많은데 같은 순위 구간의 우리 평균보다 CTR 이 낮은 글**부터. 기준값은 `놓친 클릭 = 노출 × (순위 구간 기준 CTR − 현재 CTR)` 이며 큰 순서로 줄을 세운다(STEP 5-0 에서 계산). 노출 300 미만은 후보에서 뺀다.
- **2차 — 시기성**: 줄 세운 후보 중 **이벤트가 3~14일 남은 글(track=urgent)** 이 있으면 그 글을 맨 앞으로 올린다. 시기를 타는 숏테일 글은 시기가 지나면 고쳐도 의미가 없기 때문이다. 이벤트가 이미 지난 글(E3)은 올해는 건드리지 않는다.
- **3차 — 제외**: AI Overview 가 그 검색어의 답을 이미 보여 주는 글(E4)은 제목·메타로 회수되지 않으므로 뺀다.
- 같은 순위면 순위(pos)가 4~10위인 글(제목만 고쳐도 효과가 나는 자리)을 먼저 고른다. 11위 밖 글은 "제목만으로 한계"를 전제로 고른다.
- 모든 선정 이유는 숫자(노출·클릭·CTR·기준 CTR·순위·놓친 클릭·남은 일수)로 `log.md` 와 STEP 10 에 적는다. 감으로 고르지 않는다.

작업 폴더: `C:\Users\win\Documents\Claude\gsc-ctr\` (blog 저장소 밖)
- `gsc_engine.py` — 계산 엔진(잠금·효과 판정·기록·기본 대기열). 판단이 필요 없는 계산은 전부 이 스크립트가 한다
- `state.json` — 이벤트 날짜, AI Overview 확인 결과, 글별 버전 이력(잠금의 유일한 근거)
- `snapshots/{데이터 종료일}.json` — 28일 페이지 표 · `after/` — 반영 후 구간 조회값 · `backups/` — 수정 전 원본 · `bench/` — 기준 CTR·검색어 점수·국가 분포·벤치마킹 기록 · `log.md` — 사람이 읽는 기록

⚠️ [무인 실행 원칙 — 최우선] 사람이 없는 시간에 실행된다. 승인이 필요한 도구 호출은 "그것 없이는 진행할 수 없음을 실측으로 확인한 뒤"에만 한다. 승인 창이 응답 없이 닫히면 재시도하지 않고 오류로 기록한 뒤 STEP 10으로 간다.
⚠️ [시간 제한] **07:25까지 끝낸다.** 06:30 0and1life 루틴·06:51 이미지 루틴이 같은 크롬을 쓰므로 07:00 전에는 시작하지 않는다. 07:22가 지났는데 STEP 8에 들어가지 못했으면 반영하지 않고 수정안만 `log.md` 에 남긴다(엔진 기록 안 함 → 다음 날 다시 뽑힌다). 07:18이 지났으면 벤치마킹(STEP 7-2)은 검색 결과 화면의 제목·설명만으로 줄인다(상대 페이지 열지 않음).
⚠️ 삭제 금지: 글·리비전·파일·Notion 행을 삭제하지 않는다.
⚠️ 변경 금지 항목: status·**슬러그(URL)**·Focus Keyword(`rank_math_focus_keyword`)·카테고리·발행일·H1·H2·도입 첫 문단 외 본문.
⚠️ git commit·push 하지 않는다 — 사용자가 직접 한다. pw.txt 값은 절대 출력하지 않는다.
⛔ 구글 API(`*.googleapis.com`)는 이 환경에서 네트워크 정책으로 막혀 있다(2026-09-24 실측 403). **API 호출을 시도하지 않는다.** 데이터는 크롬 화면으로만 읽는다.

---

## STEP 0 — 설정값 (사용자만 수정)

```
URGENT_MODE    = AUTO      # 시기성 긴급 글(이벤트 3~14일 남음): 그날 바로 반영
NORMAL_MODE    = AUTO      # 상시 글: SAMPLE = 수정안만 기록 / AUTO = 바로 반영 (2026-09-24 AUTO 로 변경)
REEDIT_MODE    = AUTO      # 효과 판정이 "개선 없음"이면 재수정
NEW_PER_DAY    = 1
REEDIT_PER_DAY = 1
BENCH_PAGES    = 3         # 벤치마킹으로 직접 여는 상위 페이지 수(최대 3)
MIN_IMPR       = 300       # 후보 최소 노출
FLOOR_CTR      = 2.5       # 순위 구간 기준 CTR 의 하한(%). 우리 평균이 이보다 낮아도 최소 이 값을 목표로 본다
FOREIGN_RATIO  = 0.7       # 한국 밖 노출 비율이 이 이상이면 "지역 의도" 판정
```
판정 기준값(긴급 창 14일, 효과 판정 노출·클릭 기준, 데이터 지연 2일, 재수정 한도 3차)은 `gsc_engine.py` 상단 `CFG` 에 있다.

---

## STEP 1 — 날짜와 폴더

1) TODAY(KST) 기록. 서치콘솔은 최근 2일치가 비어 있으므로 **LATEST = TODAY − 2일**, **START28 = LATEST − 27일** 을 계산한다(YYYYMMDD 형식도 함께).
2) device_bash 로 마운트를 찾는다.
```bash
CLAUDE_DIR=$HOME/mnt/Claude
W=$CLAUDE_DIR/gsc-ctr
echo "claude=$CLAUDE_DIR"; ls $W/gsc_engine.py; mkdir -p $W/bench $W/after $W/backups
```
- "No folders are connected" 오류가 나면 `device_request_folder_access { paths: ["C:\Users\win\Documents\Claude"] }` **1회** → 승인되면 위 명령 재실행 → 실패면 STEP 10. (2026-09-24 실측: 예약 실행 시 폴더가 미연결로 시작되는 경우가 있고 요청 1회로 통과됨)
- ⚠️ bash 는 매 호출이 새 셸이다. 위 두 줄을 이후 bash 호출마다 맨 앞에 다시 넣는다.

---

## STEP 2 — 자격증명 확인 (값은 절대 출력하지 않는다)

```bash
cd $CLAUDE_DIR
get(){ grep "^$1=" pw.txt | head -1 | cut -d'=' -f2- | tr -d '\r\n' | sed 's/^\xEF\xBB\xBF//; s/^ *//; s/ *$//'; }
U=$(get KOREAPLUG_WP_USER); P=$(get KOREAPLUG_WP_APP_PASSWORD)
for k in U P; do [ -n "${!k}" ] && echo "$k=있음" || echo "$k=없음"; done
curl -s -o /dev/null -w "WP %{http_code}\n" -u "$U:$P" "https://koreaplug.com/wp-json/wp/v2/users/me?context=edit"
```
- "없음" 또는 200 아님 → 반영 단계(STEP 8)만 건너뛰고 판정·수정안은 진행. STEP 10에 기록.
- 이후 REST 호출마다 `get` 함수와 변수 줄을 같은 명령 안에 다시 넣는다.

---

## STEP 3 — 서치콘솔 28일 페이지 표 읽기 (Claude in Chrome)

[3-1] `tabs_context_mcp { createIfEmpty: true }` → navigate:
`https://search.google.com/search-console/performance/search-analytics?resource_id=https%3A%2F%2Fkoreaplug.com%2F&breakdown=page&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION&start_date={START28}&end_date={LATEST}`
(날짜는 `20260826` 형식)

[3-2] 7초 대기 후 `javascript_tool` 로 표를 읽어 페이지 변수에 담는다(한 번에 반환하면 잘리므로 900자씩 나눠 읽는다):
```javascript
await new Promise(r=>setTimeout(r,7000));
if (!/총 클릭수/.test(document.body.innerText)) throw new Error('GSC 화면이 아님 — 로그인 확인');
const n=s=>parseFloat(String(s).replace(/[,%]/g,''))||0;
window.__rows=[...document.querySelectorAll('table tbody tr')].map(r=>[...r.querySelectorAll('td')].map(td=>td.innerText.trim()))
  .filter(r=>r.length>=5&&/koreaplug\.com\//.test(r[0]))
  .map(r=>{const m=r[0].match(/koreaplug\.com\/([^\s?#]*)/);return {slug:(m?m[1]:'').replace(/\/$/,''),clicks:n(r[1].split('\n')[0]),impr:n(r[2].split('\n')[0]),pos:n(r[4].split('\n')[0])}});
window.__f=window.__rows.filter(r=>r.impr>=100).map(r=>[r.slug,r.clicks,r.impr,r.pos].join('|')).join('\n');
const t=document.body.innerText; const tot=t.match(/총 클릭수\s*\n?\s*([\d,.만]+)[\s\S]{0,60}?총 노출수\s*\n?\s*([\d,.만]+)[\s\S]{0,60}?평균 CTR\s*\n?\s*([\d.]+%)/);
({rows:window.__rows.length, kept:window.__rows.filter(r=>r.impr>=100).length, len:window.__f.length, site:tot&&[tot[1],tot[2],tot[3]]})
```
이어서 `window.__f.slice(0,900)`, `slice(900,1800)`, … 을 `len` 까지 차례로 호출해 이어 붙인다. 행 형식 `slug|clicks|impr|pos`. 같은 slug 가 여러 행이면(URL 변형) 엔진이 합친다. 900자 경계에서 잘린 행은 앞뒤를 이어 붙여 복원한다. `site`(사이트 전체 클릭·노출·CTR, "만" 단위는 ×10,000)는 STEP 10 에 쓴다.

[3-3] 로그인 화면이거나 `rows` 가 0이면 STEP 10에 `GSC 읽기 실패 — 크롬 구글 로그인 확인` 을 적고 종료한다. 로그인 버튼을 대신 누르지 않는다.

[3-4] 저장:
```bash
cd $W && cat > /tmp/gsc.txt <<'E'
{이어 붙인 행들}
E
python3 -c "
import json;rows=[l.split('|') for l in open('/tmp/gsc.txt') if l.strip()]
json.dump([{'slug':r[0],'clicks':int(float(r[1])),'impr':int(float(r[2])),'pos':float(r[3])} for r in rows],open('/tmp/pages.json','w'))"
python3 gsc_engine.py snapshot --file /tmp/pages.json --end {LATEST}
```
탭은 이후 STEP 4·5·7 에서 계속 쓴다.

---

## STEP 4 — 반영한 글의 "반영 후" 구간 읽기

```bash
cd $W && python3 gsc_engine.py need-after --today {TODAY}
```
`need[]` 의 각 글에 대해 크롬으로 **페이지 필터 + 날짜 범위** 화면을 열어 총 클릭수·총 노출수를 읽는다:
`…/search-analytics?resource_id=https%3A%2F%2Fkoreaplug.com%2F&breakdown=query&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION&page=*https%3A%2F%2Fkoreaplug.com%2F{slug}%2F&start_date={start}&end_date={end}`
```javascript
await new Promise(r=>setTimeout(r,6000));
const t=document.body.innerText; const m=t.match(/총 클릭수\s*\n?\s*([\d,.만]+)[\s\S]{0,60}?총 노출수\s*\n?\s*([\d,.만]+)/);
const top=[...document.querySelectorAll('table tbody tr')].slice(0,5).map(r=>[...r.querySelectorAll('td')].map(td=>td.innerText.trim().split('\n')[0]).join('|'));
({clicks:m&&m[1], impr:m&&m[2], top})
```
`1.12만` 처럼 "만" 단위로 나오면 ×10,000 으로 환산한다. `after/{TODAY}.json` 에 `{"slug": {"start","end","impr","clicks"}}` 로 모아 저장한다. 조회 실패한 글은 넣지 않는다(엔진이 WAIT 처리). `need[]` 가 비어 있으면 `{}` 로 저장한다.

---

## STEP 5 — 기준 CTR 계산과 오늘 계획

[5-0] **순위 구간별 기준 CTR** — 우리 사이트 데이터로 "이 순위면 보통 이 정도는 클릭된다"를 만든다. 매일 새로 계산한다.
```bash
cd $W && python3 - <<'PY'
import json,glob,os
snap=sorted(glob.glob('snapshots/*.json'))[-1]; rows=json.load(open(snap))
rows=rows if isinstance(rows,list) else rows.get('pages',rows)
agg={}
for r in rows:
    a=agg.setdefault(r['slug'],{'clicks':0,'impr':0,'pw':0.0})
    a['clicks']+=r['clicks']; a['impr']+=r['impr']; a['pw']+=r['pos']*r['impr']
pages=[{'slug':s,'clicks':a['clicks'],'impr':a['impr'],'pos':a['pw']/a['impr'],'ctr':100*a['clicks']/a['impr']} for s,a in agg.items() if a['impr']>0]
def bucket(p): return '1-3' if p<=3.5 else '4-6' if p<=6.5 else '7-10' if p<=10.5 else '11+'
base={}
for b in ['1-3','4-6','7-10','11+']:
    g=[p for p in pages if bucket(p['pos'])==b and p['impr']>=100]
    c=sum(p['clicks'] for p in g); i=sum(p['impr'] for p in g)
    base[b]={'n':len(g),'clicks':c,'impr':i,'ctr':round(100*c/i,2) if i else None}
FLOOR=2.5; MIN_IMPR=300
for p in pages:
    b=bucket(p['pos']); ref=base[b]['ctr'] or FLOOR; ref=max(ref,FLOOR) if b!='11+' else max(ref,1.0)
    p['bucket']=b; p['ref_ctr']=round(ref,2); p['lost']=round(p['impr']*max(0,ref-p['ctr'])/100,1)
cand=sorted([p for p in pages if p['impr']>=MIN_IMPR and p['lost']>0],key=lambda p:-p['lost'])
json.dump({'snapshot':snap,'baseline':base,'candidates':cand},open('bench/baseline-{TODAY}.json','w'),ensure_ascii=False,indent=1)
print('기준 CTR:',{b:v['ctr'] for b,v in base.items()})
for p in cand[:12]: print(f"{p['slug']}|노출 {p['impr']}|클릭 {p['clicks']}|CTR {p['ctr']:.2f}%|순위 {p['pos']:.1f}({p['bucket']})|기준 {p['ref_ctr']}%|놓친 {p['lost']}")
PY
```
(`{TODAY}` 는 실제 날짜로 바꿔 넣는다.) 출력의 후보 순서가 **오늘의 1차 우선순위**다. 구간 표본(n)이 3편 미만이면 그 구간 기준은 FLOOR_CTR 로 본다.

[5-1] 엔진 계획
```bash
cd $W && python3 gsc_engine.py plan --today {TODAY} --after after/{TODAY}.json
```
| 키 | 뜻 |
|---|---|
| `stale` | true 면 최신 스냅샷이 LATEST 보다 오래됐다(STEP 3 실패) → 판정·수정 건너뛰고 STEP 10 |
| `evaluations[]` | KEEP / HOLD / WAIT / REEDIT / ROLLBACK / LIMIT. 각 행에 `ctr_before`·`ctr_after`·`impr_after`·`clicks_after`·`window` |
| `queue[]` | 엔진 기본 대기열(잠금·제외 반영됨). **순서는 5-0 의 `lost` 순으로 다시 세운다** — 5-0 후보 중 `queue[]` 에 있는 글만 대상(잠금·제외된 글은 자동으로 빠진다) |
| `excluded[]` | E3 내년용 / E4 AI Overview 선점 |
| `need_event_date[]` | 이벤트 날짜를 모르는 글 |
| `need_aio_check[]` | 대기열 상위 중 AI Overview 를 아직 확인하지 않은 글(최대 5) |

[5-2] `need_event_date` — **시기성 판별(우선순위 2차의 근거)**. 재정렬된 대기열 상위 5편은 반드시, 나머지는 시간이 남는 만큼. 글 본문(REST `content.rendered`)에서 독자 행동을 막는 날짜(명절 당일·예매 오픈·마감·시행일·행사 종료)를 찾는다. 여러 개면 아직 지나지 않은 가장 이른 것. 없거나 상시 정보면 none. **추정 금지 — 본문에 날짜가 없으면 none.** 슬러그에 chuseok·strike·festival·ticket 같은 시기성 단어가 있으면 먼저 확인한다.
```bash
python3 gsc_engine.py set-event {slug} 2026-10-03   # 또는 none
```

[5-3] **검색어 점수화 → 타깃 검색어 결정** (대기열 1순위 글, 필요하면 2순위까지)
크롬으로 페이지 필터 화면(START28~LATEST)을 열어 검색어 표 **상위 10개**를 읽는다:
`…/search-analytics?resource_id=https%3A%2F%2Fkoreaplug.com%2F&breakdown=query&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION&page=*https%3A%2F%2Fkoreaplug.com%2F{slug}%2F&start_date={START28}&end_date={LATEST}`
```javascript
await new Promise(r=>setTimeout(r,6000));
const n=s=>parseFloat(String(s).replace(/[,%]/g,''))||0;
const q=[...document.querySelectorAll('table tbody tr')].slice(0,10).map(r=>[...r.querySelectorAll('td')].map(td=>td.innerText.trim().split('\n')[0])).filter(r=>r.length>=5).map(r=>({q:r[0],clicks:n(r[1]),impr:n(r[2]),ctr:n(r[3]),pos:n(r[4])}));
q.map(x=>[x.q,x.clicks,x.impr,x.ctr,x.pos].join('|')).join('\n')
```
점수 규칙 (bash python 으로 계산해 `bench/{slug}-{TODAY}.md` 에 표로 저장):
- `score = 노출 × (1 − 현재CTR/기준CTR) × 순위가중` — 순위가중: 1~10위 = 1.0 / 11~20위 = 0.4 / 21위 밖 = 0.1 (제목을 고쳐도 2페이지 밖은 클릭이 거의 안 늘기 때문)
- 기준CTR = 그 검색어 순위의 구간 기준(5-0). 현재CTR 이 기준 이상이면 score 0.
- **TARGET_QUERY = score 최대 검색어**. 제목·메타·첫 문단은 이 검색어에 맞춘다.
- **MAIN_QUERY = 노출 최대 검색어** (AIO 확인·벤치마킹 검색에 쓴다). 둘이 다르면 STEP 10 에 "노출은 A 가 많지만 잡을 수 있는 건 B" 로 설명한다.
- 예(2026-09-24 카페 글): `best cafes with wifi near me` 7,301 노출·8.8위 vs `best cafes for studying` 2,451 노출·10.8위 → 둘 다 score 계산 후 큰 쪽이 타깃.

[5-4] **국가별 노출 — "누가 보고 있나"** (대기열 1순위 글)
`…/search-analytics?resource_id=https%3A%2F%2Fkoreaplug.com%2F&breakdown=country&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION&page=*https%3A%2F%2Fkoreaplug.com%2F{slug}%2F&start_date={START28}&end_date={LATEST}`
```javascript
await new Promise(r=>setTimeout(r,6000));
const n=s=>parseFloat(String(s).replace(/[,%]/g,''))||0;
const c=[...document.querySelectorAll('table tbody tr')].slice(0,8).map(r=>[...r.querySelectorAll('td')].map(td=>td.innerText.trim().split('\n')[0])).filter(r=>r.length>=3).map(r=>({country:r[0],clicks:n(r[1]),impr:n(r[2])}));
const tot=c.reduce((s,x)=>s+x.impr,0); const kr=c.find(x=>/대한민국|Korea/.test(x.country))||{impr:0,clicks:0};
({total:tot, korea_ratio:tot?+(kr.impr/tot).toFixed(2):null, top:c.slice(0,5)})
```
- `1 − korea_ratio ≥ FOREIGN_RATIO`(한국 밖 노출 70% 이상) 이고 TARGET_QUERY 에 지역 의도(`near me`, 도시명 없음, `where to`)가 있으면 **원인 B-지역** 확정 → 제목 맨 앞에 `in Korea`/`in Seoul` 을 두고 첫 문장에서 "한국에서는" 으로 시작한다.
- 한국 내 노출이 대부분이면 지역 표기는 필수가 아니다(이미 한국에 있는 사람이 보는 글).
- 결과를 `bench/{slug}-{TODAY}.md` 에 적는다.

[5-5] `need_aio_check`: MAIN_QUERY 로 크롬에서 `https://www.google.com/search?q={MAIN_QUERY 인코딩}&hl=en&gl=us` 를 열고:
```javascript
await new Promise(r=>setTimeout(r,3000));
const t=document.body.innerText; const aio=/AI Overview|AI 개요/.test(t);
const items=[...document.querySelectorAll('a h3')].map(h=>{const a=h.closest('a');const box=a&&a.closest('div[data-hveid],div.g,div[jscontroller]');return {url:(a||{}).href||'',title:h.innerText.trim(),snippet:box?box.innerText.replace(h.innerText,'').replace(/\n+/g,' ').trim().slice(0,220):''}}).filter(x=>x.url.startsWith('http')&&!x.url.includes('google.com'));
window.__serp=items;
({aio, aioText: aio? t.slice(t.search(/AI Overview|AI 개요/),t.search(/AI Overview|AI 개요/)+250).replace(/\n+/g,' '):'', ours: items.findIndex(x=>x.url.includes('koreaplug.com'))+1, top: items.slice(0,8), captcha:/unusual traffic|로봇이 아닙니다/.test(t)})
```
- `aio` 가 true 이고 **aioText 가 그 검색어의 핵심 답(정의·가부·날짜)을 이미 말하고 있으면** `set-aio {slug} yes` (제목·메타로 회수되지 않으므로 개선 대상 아님). 아니면 `set-aio {slug} no`.
- TARGET_QUERY 가 MAIN_QUERY 와 다르면 TARGET_QUERY 로도 1회 더 검색해 상위 8 을 읽는다(벤치마킹은 이 결과를 우선).
- `captcha` 가 true 면 더 검색하지 않고 그 글은 `미확인` 으로 둔 채 진행한다(STEP 10 기록).
- 검색은 회차당 **최대 5회**. `top`(상위 8 의 URL·**검색결과에 표시된 제목·설명**)과 `ours`(우리 순위)는 STEP 7 벤치마킹의 1차 자료다. `bench/{slug}-{TODAY}.md` 에 그대로 적는다.
[5-6] 5-2·5-5 에서 하나라도 설정했으면 `plan` 을 다시 실행한다.

---

## STEP 6 — 오늘 할 일 정하기 (이 순서, 이 한도)

1. **되돌림** `rollback[]` — 백업의 직전 버전 값으로 REST 되돌리고 `status: "rollback"` 기록.
2. **재수정** `reedit[]` — REEDIT_MODE=AUTO 면 1편. 긴급 우선.
3. **LIMIT** — `python3 gsc_engine.py close {slug} "3차까지 개선 없음 — 제목·메타로 한계"`, STEP 10에 "본문 보강·각도 재타겟 후보"로 올린다.
4. **새 대상** — 우선순위 규칙 적용: 5-0 순서로 재정렬한 대기열 상위 10편 안에 `track=urgent`(이벤트 3~14일 남음) 가 있으면 그 중 `lost` 가 가장 큰 글, 없으면 맨 위. NEW_PER_DAY 편. `aio` 가 `미확인` 인 글은 5-5 를 거친 뒤에만 고른다.
   - urgent → 바로 반영 / normal → NORMAL_MODE(AUTO 면 바로 반영, SAMPLE 이면 `status: "proposed"` 로 기록만, 14일 잠금)
   - 고른 이유를 한 줄로 적는다. 예: `노출 11,160 · CTR 0.06% · 순위 9.1(7-10 구간 기준 1.9%) · 놓친 클릭 205 → 1위, 시기성 없음, 한국 밖 노출 84%`
5. 할 일이 없으면 STEP 10.

---

## STEP 7 — 벤치마킹 → 원인 분류 → 수정안 (모두 데이터 근거)

[7-1] 우리 글 현재 값 (REST)
```bash
curl -s -u "$U:$P" "https://koreaplug.com/wp-json/wp/v2/posts?slug={slug}&context=edit&_fields=id,date,meta,content"
```
- `meta.rank_math_title` · `meta.rank_math_description` · `meta.rank_math_focus_keyword`(변경 금지)
- **도입 첫 문단 = `<p><!-- INTRO --></p>` 바로 다음 `<p>…</p>`**. 마커가 없으면 히어로 블록(`</div>` 로 닫히는 상단 영역) 다음에 오는 **텍스트 80자 이상인 첫 `<p>`** (style 속성이 있어도 됨 — 2026-09-24 실측: 첫 문단이 `<p style="font-size:16.5px…">` 였음). 히어로 블록 안의 `<h1>`·부제·"Last updated" 줄은 건드리지 않는다.
- 5-3 의 검색어 점수표(TARGET_QUERY·MAIN_QUERY) · 5-4 의 국가 분포.

[7-2] **벤치마킹 — 그 검색어의 클릭을 실제로 가져가는 글 보기**
목적: "왜 저 글은 클릭되고 우리 글은 안 되는가"를 화면에 보이는 것으로 확인한다. 추측하지 않는다.
1. 5-5 의 `top` 상위 8(TARGET_QUERY 결과 우선) 중 **글 형태의 페이지**(Reddit·Instagram·YouTube·Yelp·지도·쇼핑 제외) 위에서부터 `BENCH_PAGES` 편을 크롬으로 연다(같은 탭, 각 4초 대기). 캡차·차단·로그인 페이지는 건너뛰고 다음 후보로.
```javascript
await new Promise(r=>setTimeout(r,4000));
const t=document.body.innerText; const g=s=>(document.querySelector(s)||{}).content||'';
const h1=(document.querySelector('h1')||{}).innerText||'';
const ps=[...document.querySelectorAll('article p, main p, .entry-content p, p')].map(p=>p.innerText.trim()).filter(x=>x.length>=80);
const h2=[...document.querySelectorAll('h2')].map(h=>h.innerText.trim()).slice(0,8);
({title:document.title, desc:g('meta[name="description"]')||g('meta[property="og:description"]'), h1, first_p:(ps[0]||'').slice(0,400), h2, words:t.split(/\s+/).length, hasNumbersInTitle:/\d/.test(document.title), isQuestionTitle:/\?/.test(document.title), hasYear:/20\d\d/.test(document.title), hasPlace:/Seoul|Korea|Busan/i.test(document.title)})
```
2. 표로 정리해 `bench/{slug}-{TODAY}.md` 에 저장한다:
```
| 순위 | 도메인 | 검색결과 제목 | 숫자 | 질문형 | 연도 | 지역명 | 첫 문장이 답인가 | 우리와 다른 점 |
```
3. **패턴 결론 3줄** (이것이 수정안의 근거다) — 표의 열을 세어 "8편 중 n편" 으로 적는다:
   - 상위 글 제목의 공통 형태(예: "8편 중 6편이 'N Best …' + 도시명", "5편이 질문형 + 답")
   - 상위 글이 첫 문단에서 답을 먼저 주는지 / 우리 글은 어디서 답을 주는지
   - 상위 글이 다루는데 우리 제목·메타에 없는 요소(가격·지역·연도·개수) — 단, **우리 본문에 이미 있는 것만** 수정안에 쓸 수 있다. 본문에 없으면 "본문 보강 필요"로 STEP 10 에 올린다.
4. 벤치마킹 페이지는 읽기만 한다. 문장을 베끼지 않는다(형태·구조만 참고).

[7-3] 원인 분류 (7-2 결과와 수치로 결정)
| 분류 | 판단 근거 | 처방 |
|---|---|---|
| A 제목·메타 약함 | 순위 4~10위, 같은 구간 기준 CTR 보다 낮고, 상위 글과 검색의도는 같다 | 제목·메타·첫 문단을 벤치마킹 패턴으로 |
| B 검색의도 불일치 | TARGET_QUERY 가 묻는 것(가부·방법·비용·목록)과 제목 앞부분이 다르다. 상위 글은 그 질문에 바로 답한다 | 제목 앞부분을 질문에 대한 답 형태로, 첫 문단에서 답을 먼저 |
| B-지역 | 5-4 에서 한국 밖 노출 ≥ 70% 이고 검색어에 지역 의도 | 제목 맨 앞에 `in Korea/Seoul`, 첫 문장 "In Korea, …" 로 한국 글임을 즉시 표시 |
| C 순위·영역 문제 | 평균 순위 11위 밖, 또는 상위 8이 Reddit·정부·대형 매체·지역 서비스(Yelp 등)로 채워짐 | 제목·메타는 고치되 "제목만으로 한계" 기록 |
| E4 AIO 선점 | 5-5 에서 yes | 고치지 않는다(제외) |
분류 근거는 반드시 숫자와 벤치마킹 표를 인용해 적는다. 예: `B-지역 — TARGET 'best cafes for studying' 2,451노출/0클릭/10.8위(구간 기준 1.9%), 한국 밖 노출 84%, 상위8 중 5개가 도시명 목록, 우리 제목엔 답 없음`

[7-4] 작성 규칙 (영문 — 기준은 `KoreaPlug-Draft.md` 5-3·5-6)
- **rank_math_title**: TARGET_QUERY 원문(또는 Focus Keyword)을 맨 앞에. **60자 이하**(python `len()` 으로 확인). 질문형 검색어면 제목이 답의 방향을 보여 준다(예: `Can You Vape in Korea? Yes — But You Can't Buy Liquid`). 본문에 있는 구체값(금액·연도·장소) 1개. 벤치마킹 패턴 중 **"8편 중 과반"** 인 요소는 따르고, **상위 8 제목과 겹치지 않는 우리 글만의 각도** 1개를 넣는다. 낚시·과장 금지.
- **rank_math_description**: **150자 이하**(python `len()` 으로 확인), Focus Keyword 포함, 첫 문장에 답.
- **도입 첫 문단**: 첫 문장에 Focus Keyword 와 답. 길이 기존 ±30%, 문체 유지. `&#8217;` 같은 엔티티는 기존 표기 그대로.
- ⛔ 금지: 본문에 없는 사실 / 키워드 반복 / 슬러그·H1·H2·Focus Keyword 변경 / 첫 문단 외 본문 수정 / 벤치마킹 문장 복사.
- 재수정(v2·v3)은 `state.json` 의 이전 버전과 **다른 각도**로 쓰고(v1 이 "답 먼저"였으면 v2 는 "숫자·연도", v3 는 "질문형"), 판정 수치를 `note` 에 남긴다.

---

## STEP 8 — 반영 (반영 모드일 때만. 크롬 불필요 — REST 로 끝난다)

[8-1] 백업 — `backups/{slug}-{TODAY}-v{n-1}.json` 에 REST `context=edit` 응답(meta·content·modified)을 저장. 실패면 반영하지 않는다.

[8-2] 첫 문단 교체 — python 으로 `content.raw` 의 INTRO 문단 하나만 바꿔 `POST /wp-json/wp/v2/posts/{id}` `{"content": ...}`. 기대 문구 assert 후 교체. 8초 후 재조회: `status=publish` · `<p` 개수 동일 · 새 문장 포함. 어긋나면 백업 raw 로 원복하고 기록, 8-3 건너뜀.
- ⚠️ 크롬에 `koreaplug.com/wp-admin/post.php` 탭이 열려 있으면 먼저 `https://koreaplug.com/` 으로 옮긴다(에디터 자동저장이 REST 결과를 덮어쓴다).

[8-3] 제목·메타 — REST `meta` (Schd_KoreaPlug-Draft.md [6c] 와 같다. JS dispatch 는 저장되지 않으므로 쓰지 않는다)
```bash
curl -s -u "$U:$P" "https://koreaplug.com/wp-json/wp/v2/posts/{id}?context=edit&_fields=meta" | grep -c rank_math_focus_keyword   # 0 이면 스니펫 4183 미작동 → 반영 중단·기록
curl -s -u "$U:$P" -X POST -H "Content-Type: application/json" "https://koreaplug.com/wp-json/wp/v2/posts/{id}" \
  --data-binary '{"meta":{"rank_math_title":"NEW_TITLE","rank_math_description":"NEW_META"}}' -o /dev/null -w "%{http_code}\n"
```
재조회 검증: 두 값이 새 값이고 `rank_math_focus_keyword` 가 그대로인지. 어긋나면 1회 재시도 → 실패면 백업 값으로 되돌리고 기록.

[8-4] 공개 페이지 `?nc={epoch}` 로 `<title>`·`<meta name="description">`·canonical 확인. 캐시로 다르면 `캐시 반영 대기` 로만 기록.

---

## STEP 9 — 기록

[9-1] 엔진 기록 (잠금의 유일한 근거)
```bash
cat > /tmp/v.json <<'J'
{"slug":"...","status":"applied|proposed|rollback","track":"urgent|normal","date":"{TODAY}",
 "keyword":"{TARGET_QUERY}","ctr_before":{28일 CTR},"impr_before":{28일 노출},"pos_before":{순위},"published":"{발행일}","cause":"A|B|B-geo|C",
 "before":{"title":"...","desc":"...","first_p":"backups/{파일명}"},
 "after":{"title":"...","desc":"...","first_p":"..."},
 "note":"기준CTR·타깃검색어 점수·한국밖 비율·상위8 패턴(n/8)·AIO·재수정 근거 한 줄"}
J
cd $W && python3 gsc_engine.py record --file /tmp/v.json
```
반영에 실패해 원복했으면 기록하지 않는다.

[9-2] `log.md` 맨 위에 추가 — 선정 근거(숫자·기준 CTR) / 검색어 점수표(TARGET·MAIN) / 국가 분포 / 구글 상위8·우리 순위·AIO / **벤치마킹 표·패턴 결론(n/8)** / 원인 / 전·후 표 / 검증.

[9-3] **누적 성적표** 계산 (STEP 10 에 쓴다)
```bash
cd $W && python3 - <<'PY'
import json
st=json.load(open('state.json')); ev=json.load(open('/tmp/plan.json')).get('evaluations',[]) if __import__('os').path.exists('/tmp/plan.json') else []
n=sum(1 for p in st['posts'].values() for v in p['versions'] if v.get('status')=='applied')
vd={}
for p in st['posts'].values():
    for v in p['versions']:
        k=v.get('verdict') or 'WAIT'; vd[k]=vd.get(k,0)+1 if v.get('status')=='applied' else vd.get(k,0)
done=[e for e in ev if e.get('ctr_after') is not None]
b=sum(e['ctr_before'] for e in done)/len(done) if done else None; a=sum(e['ctr_after'] for e in done)/len(done) if done else None
print(json.dumps({'applied_total':n,'verdicts':vd,'avg_ctr_before':b and round(b,2),'avg_ctr_after':a and round(a,2),'measured':len(done)},ensure_ascii=False))
PY
```
(`plan` 출력을 `/tmp/plan.json` 에 저장해 두고 쓴다.)

---

## STEP 10 — 완료 보고 (앞 단계 성공 여부와 무관하게 반드시 실행)

보고는 두 가지를 한다. ① PushNotification(아래 형식 그대로) ② 마지막 응답도 같은 형식.
**전문 용어·영문 키·slug 만 나열하지 않는다. 사용자가 SEO 를 모른다고 가정하고, 숫자와 "그래서 무엇을 어떻게 바꿨는지"를 우리말로 설명한다.** 슬러그는 글 설명 뒤에 괄호로 붙인다.

```
🔎 KoreaPlug 구글 클릭률 개선 {TODAY}

■ 한 줄 요약
{오늘 무엇을 했는지 한 문장. 예: "노출은 많은데 클릭이 거의 없는 글 1편의 제목·설명·첫 문장을 고쳤습니다." / "긴급 글 1편을 바로 고쳤습니다." / "고칠 글이 없어 판정만 했습니다."}

■ 사이트 전체 (최근 28일 {START28}~{LATEST})
구글에 {노출}번 보였고 {클릭}번 클릭됨 → 클릭률 {x}%
우리 사이트 순위별 보통 클릭률: 1~3위 {a}% · 4~6위 {b}% · 7~10위 {c}% · 11위 밖 {d}% (이 수치보다 낮으면 "비정상")

■ 지금까지 성적표 (이 루틴이 고친 글 전체)
고친 글 {n}편 → 좋아짐 {n} · 다시 수정 {n} · 되돌림 {n} · 아직 측정 중 {n}
측정 끝난 글 평균 클릭률: 고치기 전 {a}% → 고친 후 {b}%

■ 지난번 고친 글은 어떻게 됐나
{없으면 "아직 고친 글이 없습니다." / 있으면 글마다 한 줄: "{글 설명}: 고치기 전 {a}% → 고친 후 {b}% (노출 {n}·클릭 {n}) → 유지/다시 수정/되돌림/아직 데이터 부족({n}/{기준})"}

■ 오늘 고른 글: {글 설명} ({slug})
- 왜 이 글인가: {노출}번 보였는데 클릭 {n}번 (클릭률 {x}%) · 구글 {순위}위 → 이 순위면 보통 {기준}%는 클릭되는데 그보다 낮음 · 놓친 클릭 약 {n}번 · {시기성: "○월○일까지 유효한 글이라 급함" / "시기 상관없는 글"}
- 사람들이 뭐라고 검색했나: 가장 많이 보인 검색어 "{MAIN_QUERY}" ({노출}번 · 클릭 {n}번 · {순위}위) / 우리가 잡기로 한 검색어 "{TARGET_QUERY}" ({노출}번 · {순위}위) {둘이 다르면 이유 한 줄}
- 누가 보고 있나: 한국 밖에서 본 비율 {x}% (미국 {n}% · …) → {"한국 글임을 제목에서 바로 보여줘야 함" / "대부분 한국에서 보는 글"}
- 클릭을 가져가는 글들은 어떻게 생겼나: {벤치마킹 결론 1~2줄, "8편 중 n편" 형식. 예: "상위 8편 중 6편이 제목 맨 앞에 도시 이름과 개수(12 Best …)를 넣고, 5편이 첫 문장에서 바로 답을 줍니다. 우리 글은 제목에 지역·가격이 없고 답이 두 번째 문장에 있습니다."}
- 그래서 원인은: {A/B/B-지역/C 를 쉬운 말로. 예: "외국에 있는 사람에게 노출되는데 제목에 '한국'이 안 보이고, 원하는 답이 제목에 없음"}

■ 수정 내용 ({바로 반영함 / 수정안만 저장, 반영 안 함})
- 제목: {전} → {후}
- 설명문: {후 (한 줄)}
- 첫 문단 첫 문장: {후 (한 줄)}
- 바꾼 이유: {한 줄. 예: "제목 맨 앞에 'in Korea'와 답(모든 체인 무료·1,500원)을 넣어 검색한 사람이 바로 알게 함"}
- 효과 확인 예정: {반영 다음날}부터 {기준 노출·클릭}이 쌓이면 자동 판정 (대략 {n}일 뒤)

■ 다음 차례 3편
1. {글 설명}: 노출 {n} · 클릭 {n} · 순위 {x} (기준 {y}%) · 놓친 클릭 {n} · {시기성}
2. …
3. …

■ 제외한 글: 시기 지남 {n}편 · 구글 AI 답변이 이미 답을 보여 줌 {n}편 · 제목만으론 한계(본문 보강 필요) {n}편

■ 확인이 필요한 것
{없으면 "없음". 있으면 쉬운 말로: "크롬에서 구글 로그인이 풀렸습니다" / "구글이 로봇 검사를 띄워 검색 확인을 못 했습니다" / "○○ 글은 제목만으론 한계 — 본문에 가격 정보를 넣어야 합니다" / "워드프레스 로그인 정보가 안 맞아 수정안만 저장했습니다"}
```

---

## 효과 판정 규칙 (gsc_engine.py `evaluate`, 참고용 — 수치는 CFG)

- 반영 후 데이터 = 서치콘솔에서 **반영 다음날 ~ LATEST** 범위를 페이지 필터로 직접 읽은 값(네이버와 달리 누적 차감이 아니라 정확한 구간값).
- 판정 시점: 긴급 = 노출 +400 이상 **그리고** 클릭 +5 이상(데이터 4일 지나면 쌓인 만큼) / 상시 = 노출 +800 **그리고** 클릭 +8(데이터 14일 지나면 쌓인 만큼). 그 전에는 WAIT 로 `노출 n/기준 · 클릭 n/기준 · 데이터 일수` 보고.
- KEEP: 반영 후 CTR ≥ max(이전×1.3, 이전+0.5%p) 또는 ≥ 같은 순위 구간 기준 CTR → 14일 보호(HOLD) 후 재후보.
- REEDIT: 기준 미달 → 재수정. v3 까지 개선 없으면 LIMIT → 30일 닫음.
- ROLLBACK: 반영 후 CTR < 이전×0.7 → 되돌림.
- AIO 확인 결과는 30일 캐시. 이벤트가 지난 글(E3)은 더 고치지 않는다.
- 순위가 반영 전후로 3 이상 움직였으면(예: 6위→12위) CTR 변화는 제목 효과가 아닐 수 있다 → 판정을 WAIT 로 두고 `note` 에 "순위 변동" 을 적는다.

## 오류 처리 요약

| 상황 | 처리 |
|---|---|
| Claude 폴더 미연결 | bash 확인 → 실패 시에만 `device_request_folder_access` 1회 → 실패면 STEP 10 |
| GSC 화면 로그인 풀림·행 0 | 판정·수정 건너뜀, STEP 10에 `GSC 읽기 실패` |
| 5-0 기준 CTR 계산 실패 | 엔진 `queue[]` 순서(고정 목표 2.5%)로 진행하고 STEP 10 에 기록 |
| 검색어 표·국가 표 읽기 실패 | MAIN_QUERY = TARGET_QUERY 로 두고 진행, 국가 판정은 "미확인" |
| 구글 검색 캡차 | 그 회차 AIO 확인·벤치마킹 중단, 해당 글 `미확인` 유지 |
| 벤치마킹 페이지 차단·캡차 | 그 페이지 건너뛰고 다음 후보. 3편 모두 실패면 검색결과 제목·설명만으로 패턴 결론 |
| pw.txt 키 누락·WP 인증 실패 | 반영만 건너뜀(판정·수정안은 진행) |
| 스니펫 4183 미작동(meta 에 rank_math 키 없음) | 제목·메타 반영 중단, 첫 문단은 원복, 엔진 기록 안 함 |
| 07:18 초과 | 벤치마킹은 검색결과 화면만으로 축소 |
| 07:22 초과 | 반영하지 않고 수정안만 log.md |
| 첫 문단 반영 후 불일치 | 백업 raw 로 원복, 기록 |
| 구글 API 접근 | 시도 금지(네트워크 정책 403 확인됨) |
