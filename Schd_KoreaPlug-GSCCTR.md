# Schd_KoreaPlug-GSCCTR — 구글 "노출 많고 CTR 낮은 글" 개선 루틴 (Cowork 예약 작업용)

*매일 07:00 KST 실행 (2026-09-24 개정: 편수 고정 폐지 · 본문 재작성 허용 · 검색봇 점검 후 공개 · 시간 마감 폐지 · Rank Math 점수 유지 의무 · 수정 후 7일 일자별 모니터링 · 제외·건너뜀·보류 폐지 / 2026-09-26 개정: **찾은 원인은 그 회차에 모두 고친다(원인-수정 대응표 의무)** · 수정 수준은 원인이 정한다(L1 은 '빠진 것 0건'이 증명될 때만) · 롱테일은 대부분을 뜯어고쳐서라도 CTR 을 올린다 · 숏테일은 수요가 끝나기 전 조기 재수정 · 트래킹 표는 데이터가 없어도 매 보고에 포함 · GA4 방문 수를 조기 신호로 추가 · 수정 전 기준 구간 통일). 예약 시각이 되면 같은 날 이미 실행됐더라도 다시 진행한다(판정·잠금은 `state.json` 이 막아 주므로 같은 글을 두 번 고치지 않는다).

날짜: 실행 시점의 실제 KST 날짜를 쓴다. 이 프롬프트에 적힌 고정 날짜는 무시한다.

이 루틴이 하는 일 (0and1life 네이버 루틴 `Schd_0and1Life-NaverCTR.md` 와 같은 구조, 데이터 원천만 다르다):
1. **서치콘솔 실적 화면을 Claude in Chrome 으로 읽는다** — CSV·API 키·네트워크 설정 없이 로그인된 크롬으로 본다. 날짜 범위를 지정할 수 있어 "고친 다음날 이후"만 잘라 정확히 잰다
2. **우리 사이트 자체 데이터로 "순위별 정상 CTR"을 매일 계산**하고, 같은 순위 구간의 평균보다 낮은 글을 "비정상"으로 잡는다 (고정 목표값이 아니라 우리 데이터가 기준)
3. **이미 고친 글의 효과를 매일 판정**한다 → 개선이면 유지, 개선이 없으면 재수정, 나빠졌으면 되돌림
4. 새 대상을 고른다 → **우선순위 규칙(아래)** 대로 줄을 세우고, **수정이 필요하다고 판단되는 글은 모두** 고친다(1편 고정 아님, 회차 상한 MAX_EDITS_PER_RUN). 시기성·상시 구분 없이 판단되면 그날 반영한다
5. 그 글의 **검색어 표를 점수화해 진짜 타깃 검색어**를 고르고, **국가별 노출**로 "누가 보고 있는지"를 확인한다
6. 고치기 전에 **그 검색어로 실제 클릭을 가져가는 글(상위 노출 글)을 본문까지 열어 벤치마킹**한다 — 제목·설명·첫 문단뿐 아니라 H2 구성·다루는 항목·분량·답을 주는 위치를 비교하고, 그 근거로 **글을 다시 작성**한다(수준: L1 제목·메타·도입부 / L2 섹션 보강·재배치 / L3 전면 재작성). **찾은 원인은 원인-수정 대응표(7-3b)로 한 줄씩 적고 그 회차에 전부 고친다** — 원인을 알면서 제목만 고치는 부분 수정은 반영 금지
7. 다시 쓴 글은 **검색봇·SEO 점검(STEP 8-0)** 을 통과해야만 반영·공개하고, 반영 후 공개 페이지를 구글봇으로 다시 점검한다(8-4). 문제가 있으면 백업으로 되돌린다
8. 수정은 버전(v1·v2·v3)으로 기록해 다음 날 같은 글을 다시 고치지 않는다
9. **수정한 모든 글은 최소 7일간 매일 트래킹**한다 — **같은 글을 한 표에 날짜순으로 이어서**(수정 전 7일 → 수정일 → 수정 후 D+1, D+2 …) 클릭(조회)·노출·CTR·순위를 보여 주고, **날마다 수정 전 7일 평균과 비교해 ▲좋아짐/▼나빠짐/≈비슷을 표시**하며, 수정 후 누적값으로 '현재 판정'을 매일 갱신한다(`track.py`, `monitor/_daily.md`). 또 1·3·7일째에 "잘 수정됐는지" 품질 확인(구글에 새 제목이 뜨는지·순위·색인 상태)을 하고, 7일째에 수정 전 7일과 비교한 **요약과 판정(좋아짐/비슷/나빠짐 + 다음 조치)** 을 남긴다(STEP 4-B, `monitor/{slug}.md`, 전체 요약판 `monitor/_summary.md`). 데이터가 모자라면 14일·28일째에 다시 요약한다
10. **Rank Math 점수를 떨어뜨리지 않는다** — 제목·본문이 바뀌면 Focus Keyword·서브 키워드와의 매칭(제목·설명·첫 문단·소제목·밀도)을 같이 맞춘다. 수정 전·후를 `rm_check.py` 로 비교해 통과 수가 줄면 반영하지 않는다(STEP 8-0)
11. 결과는 **누적 성적표가 붙은 쉬운 한글 보고(STEP 10)** 로 끝낸다

### 이 시스템의 원칙 (2026-09-24 사용자 확정)
**기본은 노출·클릭·CTR 이다.** 데이터로 "클릭이 낮은 글" 을 찾고, 시기성으로 순서를 정해, **그 글의 검색어를 기준으로 잘 되는 글을 벤치마킹해 더 클릭되고 더 노출되도록 고친다.** 고친 뒤에는 트래킹으로 결과를 확인하고 다시 피드백한다.
- ⛔ **제외·건너뜀·보류는 없다.** 클릭이 낮은 글은 전부 수정 대상이다. 어려운 사정(구글 AI 답변, 시기 지남, 검색어가 가려짐, 순위 낮음)은 **빼는 이유가 아니라 수정 방법을 바꾸는 이유**다(STEP 7-3 표).
- 유일한 대기: **이미 고친 글이 트래킹·판정 중일 때**(측정이 끝나야 다음 수정의 근거가 생긴다). 단, **이벤트가 10일 이내로 남은 숏테일 글은 기다리지 않는다** — 수정 후 데이터 2일치로 바로 재수정한다(STEP 6-2b). 판정이 나면(좋아짐=유지 후 14일 뒤 다시 후보 / 비슷=재수정 / 나빠짐=되돌림 후 재수정) 곧바로 다시 흐름에 들어간다.
- 하루에 고치는 편수는 처리량(MAX_EDITS_PER_RUN)일 뿐이다. 남은 글은 다음 회차에 같은 순서로 이어서 고친다.

### 원인을 알면 그 원인을 고친다 (2026-09-26 사용자 확정)
**교훈 — 0and1life '9월 재산세 카드 혜택' 글**: 09-24 v1 에서 벤치마킹으로 "상위 글은 카드사별 비교 목록형인데 우리 본문엔 카드사별 표가 없다" 는 원인을 이미 찾고도, 제목·메타·첫 문단만 고치고 표는 '보강 후보' 로 미뤘다. 그 결과 CTR 이 0.83% → 0.29% 로 오히려 떨어졌고, 납부 마감(9/30)을 나흘 앞둔 09-26 에야 사용자 지시로 표를 넣었다(v2). **알고 있는 원인을 남겨 둔 부분 수정은 하루치 기회를 버리는 것**이다.

이 루틴을 **매일** 돌리는 이유는 두 가지다.
1. **숏테일(시기성, track=urgent/날짜가 있는 글)** — 수요가 끝나는 날(마감·시행일·행사일) **전에** CTR 을 올려야 한다. 수요 창이 짧으므로 "고치고 7일 기다리기" 가 아니라 **첫 수정부터 원인 전부를 고치고**, 효과가 없으면 **데이터 2일치로 바로 한 단계 더 고친다**(STEP 6-2b).
2. **롱테일(상시 글)** — 수요가 오래가므로 **글의 대부분을 뜯어고치더라도(L3)** CTR 을 올린다. 제목만 바꿔서 안 되는 글을 제목만 반복해서 바꾸지 않는다.

따라서 다음을 지킨다.
- **원인-수정 대응표(STEP 7-3b)** 를 글마다 만든다. 7-2 벤치마킹·항목 대조표·검색어 표·AI 답변 비교에서 찾은 **원인(빠진 항목·답의 위치·답의 형식·검색의도·지역·날짜 등)을 한 줄씩 적고, 각 줄마다 이번 수정에서 무엇으로 고쳤는지** 적는다. **'미해결'·'보강 후보'·'다음에' 로 남기는 줄은 0개여야 반영할 수 있다**(8-0 점검 항목). 1차 출처로 사실을 확인하지 못해 못 채우는 줄만 예외이며, 그 경우 "확인 불가 — 출처 시도 내역" 을 적고 그 항목 대신 할 수 있는 구조적 수정(답 위치 이동·형식 변경 등)을 한다.
- **수정 수준은 원인이 정한다.** 편한 수준을 먼저 고르지 않는다. L1(제목·메타·첫 문단만)은 항목 대조표에서 **빠진 항목 0개 · 답이 이미 첫 문단/첫 H2 에 있음 · 답의 형식(목록·표·단계·금액)이 상위 과반과 같음** 이 모두 증명될 때만 허용한다.
- 재수정은 **직전 수정에서 건드리지 않은 원인**을 반드시 포함한다. 같은 원인에 제목만 다시 바꾸는 재수정은 금지.

### 우선순위 규칙 (순서만 정한다 — 빼지 않는다)
- **1차 — 데이터**: 최근 28일에 **노출은 많은데 같은 순위 구간의 우리 평균보다 CTR 이 낮은 글**. `놓친 클릭 = 노출 × (순위 구간 기준 CTR − 현재 CTR)` 큰 순서(STEP 5-0, 엔진 `queue[]` 가 같은 계산). 노출 100 미만 글은 데이터가 적어 맨 뒤로.
- **2차 — 시기성**: **이벤트가 3~14일 남은 글(track=urgent)** 은 맨 앞으로. 시기가 이미 지난 글(track=past)은 맨 뒤로 — 빼지 않고, 다음 회차(내년 날짜) 또는 상시 정보 각도로 고친다.
- 같은 조건이면 순위 4~10위 글 먼저(효과가 빨리 나는 자리). 수정 수준은 순위가 아니라 **원인(7-3)** 이 정한다 — 4~10위라도 빠진 항목이 있으면 L2·L3 로 고친다. 11위 밖 글은 L3(본문 재작성)로 고친다.
- 모든 선정 이유는 숫자(노출·클릭·CTR·기준 CTR·순위·놓친 클릭·남은 일수)로 `log.md` 와 STEP 10 에 적는다. 감으로 고르지 않는다.

작업 폴더: `C:\Users\win\Documents\Claude\gsc-ctr\` (blog 저장소 밖)
- `gsc_engine.py` — 계산 엔진(잠금·효과 판정·기록·기본 대기열). 판단이 필요 없는 계산은 전부 이 스크립트가 한다
- `state.json` — 이벤트 날짜, AI Overview 확인 결과, 글별 버전 이력(잠금의 유일한 근거)
- `rm_check.py` — Rank Math 테스트 20항목 근사 점검(브라우저 불필요). 수정 전·후 비교용
- `monitor/{slug}.md` — 수정한 글의 수정 내용·품질 확인·7일 요약
- `track.py` · `monitor/data/{slug}.json` · `monitor/_daily.md` — **일자별 트래킹**: 글마다 하루치 값을 쌓고(add), 같은 글을 날짜순 한 표로 보여 주며 매일 좋아졌는지 표시(report)
- `snapshots/{데이터 종료일}.json` — 28일 페이지 표 · `after/` — 반영 후 구간 조회값 · `backups/` — 수정 전 원본 · `bench/` — 기준 CTR·검색어 점수·국가 분포·벤치마킹 기록 · `log.md` — 사람이 읽는 기록

⚠️ [무인 실행 원칙 — 최우선] 사람이 없는 시간에 실행된다. 승인이 필요한 도구 호출은 "그것 없이는 진행할 수 없음을 실측으로 확인한 뒤"에만 한다. 승인 창이 응답 없이 닫히면 재시도하지 않고 오류로 기록한 뒤 STEP 10으로 간다.
⚠️ [시간] 06:30 0and1life 루틴·06:51 이미지 루틴이 같은 크롬을 쓰므로 07:00 전에는 시작하지 않는다. **끝나는 시각 마감은 없다** — 늦게 실행돼도 벤치마킹(본문까지)·점검·반영을 모두 한다. 한 글의 작업은 STEP 7 → 8 → 9 를 끝낸 뒤 다음 글로 넘어간다(중간에 끊겨도 반영된 글은 모두 기록돼 있도록).
⚠️ 삭제 금지: 글·리비전·파일·Notion 행을 삭제하지 않는다.
⚠️ 변경 금지 항목: status(공개 글은 공개 유지)·**슬러그(URL)**·Focus Keyword(`rank_math_focus_keyword` 의 **첫 항목**)·카테고리·발행일·대표 이미지·H1. 기존 1급 자료·캡처·표·내부 링크·이미지는 삭제하지 않는다(위치 이동은 가능).
✅ 변경 가능 항목: rank_math_title·rank_math_description·도입 첫 문단·H2/H3·본문(STEP 7-3 의 수정 수준 L1/L2/L3 안에서, 7-4 규칙대로) · 서브 키워드(`rank_math_focus_keyword` 2~5번째 항목 — 새 제목·TARGET_QUERY 와 맞추기 위해서만, 총 5개 유지).
⚠️ [수정의 뜻] "글 전체 수정" 은 전부 갈아엎는 것이 아니다. CTR 개선 방향으로 필요한 곳을 고치되, **그 수정 때문에 생길 문제(키워드 매칭 누락·중복 소제목·FAQ 스키마 불일치·날짜 표기·내부 링크 등)를 같은 회차에 미리 함께 고친다.** (2026-09-24 사례: 제목을 'Where to Buy Yakgwa…' 로 바꾸면서 Focus Keyword 'yakgwa korea' 가 제목·설명에서 빠져 Rank Math 근사 점검이 14→10/20 으로 떨어짐 → 같은 날 v2 로 복구)
⚠️ git commit·push 하지 않는다 — 사용자가 직접 한다. pw.txt 값은 절대 출력하지 않는다.
⛔ 구글 API(`*.googleapis.com`)는 이 환경에서 네트워크 정책으로 막혀 있다(2026-09-24 실측 403). **API 호출을 시도하지 않는다.** 데이터는 크롬 화면으로만 읽는다.
⚠️ [작업 공간 대체] device_bash 가 `Workspace unavailable`(PC 안의 Cowork 리눅스 작업 공간 기동 실패)을 내면 재시도하지 말고 **대체 경로**로 진행한다: `device_stage_files` 로 gsc-ctr 폴더 파일(gsc_engine.py·state.json·snapshots·log.md)과 pw.txt 를 클라우드로 가져와 클라우드 `Bash` 에서 같은 명령을 실행하고, 바뀐 파일은 `device_commit_files`(`expectedMtimeMs` 지정)로 되돌려 쓴다. koreaplug.com REST 는 클라우드에서도 접근된다(2026-09-24 실측). pw.txt 값은 여기서도 출력하지 않는다.

---

## STEP 0 — 설정값 (사용자만 수정)

```
URGENT_MODE    = AUTO      # 시기성 긴급 글(이벤트 3~14일 남음): 그날 바로 반영
NORMAL_MODE    = AUTO      # 상시 글: SAMPLE = 수정안만 기록 / AUTO = 바로 반영 (2026-09-24 AUTO 로 변경)
REEDIT_MODE    = AUTO      # 효과 판정이 "개선 없음"이면 재수정
MAX_EDITS_PER_RUN = 3      # 하루 처리량(대기열 위에서부터 이 수만큼 고치고, 나머지는 다음 회차에 이어서). 늘리려면 이 값만 바꾼다
REEDIT_PER_DAY = 제한 없음 # 재수정 판정이 난 글은 모두
BENCH_PAGES    = 3         # 벤치마킹으로 본문까지 여는 상위 페이지 수(시간과 무관하게 항상)
MIN_IMPR       = 100       # 이 미만은 데이터가 적어 대기열 맨 뒤로(빼지 않음)
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
- device_bash 가 `Workspace unavailable` 이면 상단 **[작업 공간 대체]** 경로로 전환한다(폴더 접근 요청을 하지 않는다 — 폴더 연결 문제가 아니다).
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

[4-B] **수정 글 트래킹 (필수 — 수정일 다음날부터 최소 7일, 측정 연장이면 28일까지)**
대상: `monitor/*.md` 중 상태가 `트래킹 중` 인 글 전부. 글마다 ①~⑤ 를 한다.

① **일자별 지표** — 크롬으로 날짜별 화면(`breakdown=date`, 수정일 −14일 ~ LATEST):
`…/search-analytics?resource_id=https%3A%2F%2Fkoreaplug.com%2F&breakdown=date&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION&page=*https%3A%2F%2Fkoreaplug.com%2F{slug}%2F&start_date={수정일-14}&end_date={LATEST}`
```javascript
await new Promise(r=>setTimeout(r,7000));
[...document.querySelectorAll('table tbody tr')].map(r=>[...r.querySelectorAll('td')].map(td=>td.innerText.trim().split('\n')[0])).filter(r=>r.length>=5).map(r=>r.join('|')).join('\n')
```
- 행 형식 `2026. 9. 22.|클릭|노출|CTR|순위`. **읽은 날마다 전부** 저장한다(이미 있는 날도 다시 저장 — 늦게 집계된 값으로 덮어씀). 표에 없는 날(노출 0)은 `0 0 0` 으로 저장:
```bash
cd $W && python3 track.py add {slug} 2026-09-22 {클릭} {노출} {순위}
```
- 모든 트래킹 글을 저장한 뒤 한 번 실행한다:
```bash
cd $W && python3 track.py report --today {TODAY}
```
  → `monitor/_daily.md` 가 만들어진다. **같은 글을 한 표에 날짜순으로**: 수정 전 7일(기준) → 수정일(비교 제외) → 수정 후 D+1 ~ D+7(이후 계속). 수정 후 각 날에 **CTR 비교·노출 비교(▲ 좋아짐 / ▼ 나빠짐 / ≈ 비슷, 기준 = 수정 전 7일 평균)** 과 **누적 CTR** 이 붙고, 글마다 맨 아래 한 줄 "수정 전 7일 → 수정 후 n일 누적 → 현재 판정(좋아짐/비슷/나빠짐/측정 부족/데이터 대기)" 이 붙는다. 하루치 ▲▼ 는 흔들리므로 **판정은 누적 기준**으로만 한다(④ 와 같은 기준).
- 구글 데이터가 약 2일 늦으므로 최근 이틀은 "데이터 대기" 로 표시된다(오류 아님).

② **타깃 검색어 추적** (3일째·7일째, 이후 14·28일째) — 같은 화면을 `breakdown=query`, 기간 = 수정 다음날 ~ LATEST 로 열어 TARGET_QUERY 와 상위 5개 검색어의 클릭·노출·순위를 읽고, 수정 전(수정일 −7일 ~ −1일) 같은 검색어 값과 나란히 적는다. → "노리던 검색어에서 실제로 클릭이 늘었나" 를 본다.

③ **수정 품질 확인 — "잘 고쳐졌나"** (1일째·3일째·7일째)
- 공개 페이지(구글봇 UA): 200 · index · canonical · 새 title/description 유지 · JSON-LD 파싱 · H1 1개 (8-4 와 같은 스크립트). 누군가 에디터에서 덮어써 값이 바뀌었으면 즉시 기록하고 STEP 10 "확인 필요" 에 올린다.
- `rm_check.py` 재실행 → 반영 당시 점수와 같은지.
- **구글 검색 결과 확인**: TARGET_QUERY 로 `google.com/search?…&hl=en&gl=us` 1회 — 우리 순위, **구글이 보여 주는 제목·설명이 새 것인지**(구글이 제목을 다시 써서 보여 주면 그 문구를 그대로 적는다), AI 개요가 새로 생겼는지. (검색 상한 10회 안에서, 트래킹 글이 많으면 3·7일째만)
- **구글 반영 여부**는 위 검색 결과의 표시 제목·설명으로 판단한다(새 문구가 보이면 "구글 반영됨"). 새 문구가 안 보이는 날은 "구글 미반영" 으로 표시하고, 효과 계산에서 따로 표시한다. (서치콘솔 URL 검사 화면은 직접 주소로 열면 404 — 2026-09-24 실측. 쓰지 않는다. '색인 생성 요청' 버튼도 누르지 않는다.)

④ **7일째 요약과 판정** (수정 후 7일치 데이터가 다 나온 회차 = 수정일 +9일 전후)
"7일 요약" 표를 채운다: 수정 전 7일 vs 수정 후 7일 — 클릭 · 노출 · CTR · 평균 순위 · 타깃 검색어 클릭/노출/순위 · 구글 표시 제목 반영 여부(처음 반영된 날).
판정(숫자로):
| 판정 | 조건 | 다음 조치 |
|---|---|---|
| 좋아짐 | 수정 후 CTR ≥ max(전×1.3, 전+0.5%p) 그리고 클릭 ≥ 전 | 유지. 트래킹 종료(엔진 HOLD 14일) |
| 나빠짐 | CTR < 전×0.7, 또는 노출이 비슷한데(±30%) 클릭 < 전×0.7, 또는 평균 순위 2 이상 하락 | 원인 한 줄 + 엔진 규칙대로 되돌림 후보(STEP 6-1). 되돌림은 엔진이 ROLLBACK 을 낸 경우에만 실행 |
| 비슷 | 위 둘 다 아님 | 재수정 후보(다음 수준 L1→L2→L3). 엔진 REEDIT 와 함께 본다 |
| 측정 연장 | 수정 후 7일 노출 < 200, 또는 7일째에도 구글 검색 결과에 옛 제목이 보임(구글 미반영), 또는 순위가 3 이상 변동 | 14일째·28일째에 같은 표로 다시 요약. 28일째엔 반드시 위 셋 중 하나로 판정 |
- 요약 아래에 **"잘 수정됐나" 한 단락**을 쓴다: 무엇을 바꿨는지 → 지표가 어떻게 움직였는지 → 노리던 검색어에서 효과가 있었는지 → 다음에 무엇을 할지. 숫자로.
- 판정이 나면 파일 상태를 `트래킹 종료({판정})` 로 바꾼다. 측정 연장이면 `트래킹 중(14일 요약 대기)` 처럼 둔다.

⑤ **전체 요약판 `monitor/_summary.md` 갱신** — 트래킹 중·종료된 모든 글을 한 표로:
```
| 글 | 수정일 | 수준 | 상태 | N일째 | 수정 전 7일 CTR | 수정 후 누적 CTR | 클릭 전(7일)→후(누적) | 순위 전→후 | 타깃 검색어 순위 전→후 | 구글 새 제목 반영 | 판정 | 다음 조치 |
```
맨 위에 "마지막 갱신: {TODAY}" 와 한 줄 총평(예: "트래킹 중 3편 · 좋아짐 1 · 비슷 1 · 측정 연장 1").

- **글을 새로 반영할 때마다 `monitor/{slug}.md` 를 만든다**(STEP 9-1b). 같은 글을 재수정하면 기존 파일 아래에 "v{n} 수정" 구간을 새로 붙이고 N일째를 0 부터 다시 센다.
- 조회수 = 서치콘솔 클릭 수(구글 검색 유입). 판정은 서치콘솔 기준으로만 한다.
- **수정 전 기준 구간은 하나로 통일한다: `수정일 −7일 ~ −1일`**(track.py 와 같은 정의). `_summary.md`·`monitor/{slug}.md`·`_daily.md`·STEP 10 모두 이 구간의 클릭·노출·CTR·순위를 쓴다. 수정일 −1일 데이터가 아직 없으면(2일 지연) 들어오는 회차에 다시 계산해 세 파일을 함께 고친다. 수정 전 7일 값이 파일마다 다르면 오류로 보고 STEP 10 "확인 필요" 에 올린다.

⑥ **GA4 방문 수 — 조기 신호 (판정에는 쓰지 않는다)** — 서치콘솔은 2일 늦지만 GA4 는 당일까지 나온다. 트래킹 중인 글의 **수정 전 7일 ~ 오늘** 방문 수를 매일 읽어 `monitor/_daily.md` 각 글 표 옆에 "GA4 방문" 열로 붙인다(오늘 값은 '집계 중' 표시).
- 속성: KoreaPlug (계정 WP_분석 a393066616 · 속성 p535142552). 방문 페이지 보고서를 하루 단위로 연다(`{YYYYMMDD}` 를 날짜마다 바꿈):
  `https://analytics.google.com/analytics/web/#/a393066616p535142552/reports/explorer?r=landing-page&params=_u..nav%3Dmaui%26_u.date00%3D{YYYYMMDD}%26_u.date01%3D{YYYYMMDD}%26_r.explorerCard..rowsPerPage%3D250`
```javascript
await new Promise(r=>setTimeout(r,7000));
const S=[/* 트래킹 중인 slug 목록 */];
const d=(document.body.innerText.match(/\d+월 \d+일~2026년 \d+월 \d+일/)||[''])[0];
const rows=[...document.querySelectorAll('[role=row]')].map(r=>r.innerText.replace(/\s+/g,' ').trim());
d+' | '+S.map(s=>{const r=rows.find(x=>x.includes('/'+s+' ')||x.endsWith('/'+s));return s+':'+(r?r.split(' ')[2]:0)}).join(' ')
```
- 값은 '세션수(모든 유입 경로 합계)' 다. 구글 검색 유입만의 값이 아니므로 추세(늘었나·줄었나)만 본다. 서치콘솔에 노출이 있는데 GA4 방문이 계속 0 인 글은 추적 누락 의심으로 STEP 10 "확인 필요" 에 올린다(2026-09-26 실측: koreans-cover-their-mouth 가 10일간 GA4 0건).
- GA4 화면이 열리지 않으면(로그인 풀림) 이 항목만 건너뛰고 STEP 10 에 적는다.

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
FLOOR=2.5; MIN_IMPR=100
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
| `baseline_ctr` | 순위 구간별 기준 CTR(5-0 과 같은 값) |
| `evaluations[]` | KEEP / HOLD / WAIT / REEDIT / ROLLBACK (3차까지 개선 없으면 REEDIT + level L3). 각 행에 `ctr_before`·`ctr_after`·`impr_after`·`clicks_after`·`window` |
| `queue[]` | 수정 대기열 — 순서 = urgent → normal → past, 그 안에서 노출 100 미만은 뒤로, 나머지는 `lost_clicks` 큰 순. 각 행에 `track`·`ref_ctr`·`lost_clicks`·`aio`. **빠지는 글 없음** |
| `tracking[]` | 이미 고쳐서 트래킹·판정 중인 글(판정 날 때까지 새 수정 대기) |
| `need_event_date[]` | 이벤트 날짜를 모르는 글 |
| `need_aio_check[]` | 대기열 상위 중 AI Overview 를 아직 확인하지 않은 글(최대 5) |

[5-2] `need_event_date` — **시기성 판별(우선순위 2차의 근거)**. 재정렬된 대기열 상위 5편은 반드시, 나머지는 시간이 남는 만큼. 글 본문(REST `content.rendered`)에서 독자 행동을 막는 날짜(명절 당일·예매 오픈·마감·시행일·행사 종료)를 찾는다. 여러 개면 아직 지나지 않은 가장 이른 것. 없거나 상시 정보면 none. **추정 금지 — 본문에 날짜가 없으면 none.** 슬러그에 chuseok·strike·festival·ticket 같은 시기성 단어가 있으면 먼저 확인한다.
```bash
python3 gsc_engine.py set-event {slug} 2026-10-03   # 또는 none
```

[5-3] **검색어 점수화 → 타깃 검색어 결정** (STEP 6 에서 고르는 글마다)
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

[5-4] **국가별 노출 — "누가 보고 있나"** (5-3 을 한 글마다)
`…/search-analytics?resource_id=https%3A%2F%2Fkoreaplug.com%2F&breakdown=country&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION&page=*https%3A%2F%2Fkoreaplug.com%2F{slug}%2F&start_date={START28}&end_date={LATEST}`
```javascript
await new Promise(r=>setTimeout(r,6000));
const n=s=>parseFloat(String(s).replace(/[,%]/g,''))||0;
const c=[...document.querySelectorAll('table tbody tr')].slice(0,8).map(r=>[...r.querySelectorAll('td')].map(td=>td.innerText.trim().split('\n')[0])).filter(r=>r.length>=3).map(r=>({country:r[0],clicks:n(r[1]),impr:n(r[2])}));
const tot=c.reduce((s,x)=>s+x.impr,0); const kr=c.find(x=>/대한민국|한국|Korea/.test(x.country))||{impr:0,clicks:0};
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
- `aio` 가 true 이고 **aioText 가 그 검색어의 핵심 답(정의·가부·날짜)을 이미 말하고 있으면** `set-aio {slug} yes`, 아니면 `no`. **yes 여도 빼지 않는다** — STEP 7-3 의 'AIO' 수정 방법으로 고친다(AI 답변이 주지 못하는 것을 제목·도입부에서 약속하고, 롱테일 검색어를 함께 노린다). aioText 는 그대로 `bench/` 에 적어 7-4 에서 "AI 답변과 겹치지 않는 각도" 를 고르는 근거로 쓴다.
- TARGET_QUERY 가 MAIN_QUERY 와 다르면 TARGET_QUERY 로도 1회 더 검색해 상위 8 을 읽는다(벤치마킹은 이 결과를 우선).
- `captcha` 가 true 면 더 검색하지 않고 그 글은 `미확인` 으로 둔 채 진행한다(STEP 10 기록).
- 검색은 회차당 **최대 10회**. `top`(상위 8 의 URL·**검색결과에 표시된 제목·설명**)과 `ours`(우리 순위)는 STEP 7 벤치마킹의 1차 자료다. `bench/{slug}-{TODAY}.md` 에 그대로 적는다.
[5-6] 5-2·5-5 에서 하나라도 설정했으면 `plan` 을 다시 실행한다.

---

## STEP 6 — 오늘 할 일 정하기 (이 순서. 제외·건너뜀 없음 · 하루 처리량 MAX_EDITS_PER_RUN)

1. **되돌림** `rollback[]` — 백업의 직전 버전 값으로 REST 되돌리고 `status: "rollback"` 기록. 되돌린 글은 원인을 적고 같은 회차 또는 다음 회차에 다른 각도로 재수정한다. (처리량에 포함하지 않는다)
2. **재수정** `reedit[]` — 해당 글 **전부**. 직전 버전보다 한 단계 높은 수준(L1→L2→L3). 엔진이 `level: L3` 를 준 글은 검색어 각도까지 바꿔 전면 재작성한다. 직전 버전의 원인-수정 대응표(bench 파일)를 다시 열어 **그때 건드리지 않은 원인·새로 보인 원인을 이번 대응표에 반드시 넣는다**(같은 원인에 제목만 다시 바꾸는 재수정 금지).
   2b. **숏테일 조기 재수정 (엔진 판정을 기다리지 않는다)** — 트래킹 중인 글 중 이벤트(마감·시행일·행사일)가 **10일 이내**로 남은 글은, 수정 후 데이터가 **2일치** 쌓인 회차에 수정 후 누적 CTR 을 수정 전 7일 CTR 과 비교한다. `수정 후 누적 CTR ≤ 수정 전 CTR` 이거나 `수정 후 노출 ≥ 100 인데 클릭 0` 이면 그 회차에 **한 단계 높은 수준으로 즉시 재수정**한다(처리량에 포함하지 않는다). 수요가 끝난 뒤의 판정은 쓸모가 없기 때문이다. 이벤트 3일 전까지만 적용하고, 그 뒤엔 다음 회차(내년) 각도로 넘긴다(7-3 P).
   2c. **롱테일 재수정** — 7일 판정이 '비슷'·'나빠짐' 이면 다음 수준으로 가되, 한 번 L2 를 한 글은 재수정 시 **L3(대부분 재작성)를 기본**으로 한다. 상위 글 구조(H2 흐름·답 형식·분량)를 기준으로 글 전체를 다시 설계하고, 기존 1급 자료·이미지·내부 링크만 유지한다.
3. **새 대상** — 엔진 `queue[]` 를 **위에서부터 그대로** MAX_EDITS_PER_RUN 편 고른다. 고른 글은 반드시 STEP 7 → 8 → 9 까지 간다.
   - `aio` 가 `미확인` 이면 5-5 를 먼저 거친다(순서는 바뀌지 않는다 — 수정 방법을 정하기 위한 것).
   - 검색어가 서치콘솔에서 대부분 가려져 보이는 검색어가 적어도 빼지 않는다 → 보이는 검색어 + 글의 주제어로 구글 검색해 **자동완성·"People also ask"·관련 검색어** 에서 TARGET_QUERY 를 정한다(bench 에 근거 기록).
   - 고른 이유를 글마다 한 줄로 적는다. 예: `노출 11,160 · CTR 0.06% · 순위 9.1(7-10 구간 기준 2.5%) · 놓친 클릭 272 · 시기 무관 · AI 답변 없음`
4. 대기열이 비었으면(클릭이 낮은 글이 없으면) STEP 10.

모드: URGENT_MODE·NORMAL_MODE 가 AUTO 면 STEP 8 점검 통과 즉시 반영·공개한다. SAMPLE 이면 `status: "proposed"` 로 기록만 한다(잠금 없음 — 다음 회차에 다시 올라온다).

---

## STEP 7 — 벤치마킹 → 원인 분류 → 글 다시 쓰기 (모두 데이터 근거)

글마다 7-1 ~ 7-5 를 반복한다.

[7-1] 우리 글 현재 값 (REST)
```bash
curl -s -u "$U:$P" "https://koreaplug.com/wp-json/wp/v2/posts?slug={slug}&context=edit&_fields=id,date,status,meta,content,categories,featured_media"
```
- `meta.rank_math_title` · `meta.rank_math_description` · `meta.rank_math_focus_keyword`(변경 금지 — 쉼표 앞 첫 항목이 Focus Keyword)
- `content.raw` 전체. 구조를 기록한다: H1·H2 목록, 단어 수, `<p` 개수, 내부 링크(`href="https://koreaplug.com/…"`) 목록, `<img>` 목록(src·alt), 표·FAQ 블록 유무, JSON-LD(FAQ) 유무.
- **도입 첫 문단** = `<p><!-- INTRO --></p>` 바로 다음 `<p>…</p>`. 마커가 없으면 히어로 블록 다음의 **텍스트 80자 이상인 첫 `<p>`**(style 속성이 있어도 됨). 히어로 블록 안의 `<h1>`·부제·"Last updated" 줄은 손대지 않는다(날짜는 L2·L3 수정 시 "Last updated: {Month YYYY}" 로만 갱신 가능).
- 5-3 검색어 점수표(TARGET_QUERY·MAIN_QUERY)와 **나머지 검색어 목록** · 5-4 국가 분포.

[7-2] **벤치마킹 — 그 검색어의 클릭을 실제로 가져가는 글을 본문까지 연다** (시간과 무관하게 항상 수행)
1. 5-5 의 `top` 상위 8(TARGET_QUERY 결과 우선) 중 **글 형태의 페이지**(Reddit·Quora·Facebook·Instagram·X·YouTube·Yelp·지도·쇼핑·예약 상품 제외) 위에서부터 `BENCH_PAGES` 편을 크롬으로 연다(같은 탭, 각 4초 대기). 캡차·차단·로그인 페이지는 건너뛰고 다음 후보로.
```javascript
await new Promise(r=>setTimeout(r,4000));
const t=document.body.innerText; const g=s=>(document.querySelector(s)||{}).content||'';
const root=document.querySelector('article, main, .entry-content')||document.body;
const h1=(document.querySelector('h1')||{}).innerText||'';
const ps=[...root.querySelectorAll('p')].map(p=>p.innerText.trim()).filter(x=>x.length>=80);
const h2=[...root.querySelectorAll('h2')].map(h=>h.innerText.trim()).slice(0,15);
const h3=[...root.querySelectorAll('h3')].map(h=>h.innerText.trim()).slice(0,20);
({url:location.href, title:document.title, desc:g('meta[name="description"]')||g('meta[property="og:description"]'), h1, first_p:(ps[0]||'').slice(0,400), h2, h3,
  words:root.innerText.split(/\s+/).length, tables:root.querySelectorAll('table').length, lists:root.querySelectorAll('ul,ol').length, imgs:root.querySelectorAll('img').length,
  faq:/FAQ|Frequently Asked/i.test(t), updated:(t.match(/(Updated|Last updated)[^\n]{0,40}/i)||[''])[0],
  prices:(root.innerText.match(/(₩|KRW|\$)\s?[\d,]+|[\d,]+\s?won/gi)||[]).slice(0,8), places:(root.innerText.match(/\b[A-Z][a-z]+-(dong|gu|ro|gil)\b/g)||[]).slice(0,10)})
```
2. 표로 정리해 `bench/{slug}-{TODAY}.md` 에 저장한다:
```
| 순위 | 도메인 | 검색결과 제목 | 단어 수 | H2 수 | 표 | FAQ | 가격 | 지명 | 첫 문장이 답인가 |
```
그리고 **항목 대조표** — 상위 글들의 H2·H3 에서 다루는 주제를 모아 "상위 n편이 다룸 / 우리 글에 있음·없음" 으로 적는다.
3. **패턴 결론** (수정의 근거) — "8편 중 n편", "본문을 연 3편 중 n편" 형식으로:
   - 제목·설명의 공통 형태
   - 답을 주는 위치(첫 문장 / 첫 H2 / 중간)
   - 상위 글이 다루는데 우리 글에 없는 항목(가격·지역·영업시간·비교표·단계별 방법·FAQ 등)과 우리 글에만 있는 강점
4. 벤치마킹 페이지는 읽기만 한다. **문장을 베끼지 않는다**(구조·다루는 항목만 참고). 상위 글에만 있는 **사실**을 우리 글에 넣으려면 그 사실을 1차 출처(공식 사이트·기관 페이지·지도)에서 직접 확인한 뒤에만 쓴다. 확인 못 한 사실은 쓰지 않는다.

[7-3] 원인 분류 → **수정 수준 결정** (수준은 원인이 정한다. 해당하는 분류가 여러 개면 **가장 높은 수준**을 쓴다)
| 분류 | 판단 근거 | 수정 수준 |
|---|---|---|
| A 제목·메타 약함 | 순위 4~10위, 검색의도는 상위 글과 같고, **항목 대조표에서 빠진 주제 0개 · 답이 이미 첫 문단/첫 H2 에 있음 · 답의 형식(목록·표·단계·금액)이 상위 과반과 같음** — 셋 다 bench 에 근거를 적어 증명 | **L1** 제목·메타·첫 문단 (셋 중 하나라도 증명 못 하면 L1 불가) |
| F 답의 형식 불일치 | 상위 과반이 표·목록·단계·가격표·비교표로 답하는데 우리는 문단으로만 답함 (예: 재산세 글 — 상위는 '카드사별 비교표', 우리는 계산 문단) | **L2 이상** 그 형식의 블록(표·목록)을 첫 화면(첫 또는 두 번째 H2)에 만든다 |
| B 검색의도 불일치 | TARGET_QUERY 가 묻는 것(가부·방법·장소·비용·목록)에 대한 답이 제목·첫 문단에 없거나 본문 뒤쪽에 짧게만 있음 | **L2** L1 + 그 답을 다루는 섹션을 앞쪽으로 옮기고 보강, 필요한 H2 추가 |
| B-지역 | 5-4 에서 한국 밖 노출 ≥ 70% 이고 검색어에 지역 의도 | L1 또는 L2 + 제목 맨 앞 `in Korea/Seoul`, 첫 문장 "In Korea, …" |
| C 내용 부족·순위 문제 | 평균 순위 11위 밖, 또는 항목 대조표에서 상위 과반이 다루는 주제가 우리 글에 2개 이상 없음, 또는 우리 단어 수 < 상위 글 중앙값의 60% | **L3** 전면 재작성(구조 재설계) |
| AIO — 구글 AI 답변이 기본 답을 보여 줌 | 5-5 에서 yes | **L2 이상.** AI 답변(aioText)이 말하지 않는 것 — 구체 수치·장소·단계·예외·최신 날짜·1급 자료·현지 사정 — 을 제목 앞부분과 첫 문단에서 약속하고, 본문에 그 항목 섹션을 둔다. 5-3 표의 롱테일 검색어(질문형·상황형)를 H2/H3·FAQ 로 함께 노린다 |
| P 시기 지남 | track=past | 다음 회차(내년) 날짜가 공식 발표돼 있으면 그 날짜로 갱신, 없으면 "매년 반복되는 정보" 각도(예년 날짜 패턴·준비 방법)로 제목·도입부를 바꾼다. 확인 안 된 내년 날짜는 쓰지 않는다 |
재수정(v2·v3)은 직전 버전보다 한 단계 높은 수준으로 한다(L1→L2→L3). 분류 근거는 숫자와 벤치마킹 표를 인용해 적는다. 예: `B — TARGET 'where to buy yakgwa in seoul' 187노출/0클릭/9.4위, 상위 8 중 4편이 가게 이름으로 즉답, 우리 글은 '어디서 사나' 섹션이 본문 끝 3문장`
- **롱테일(상시 글) 기본값**: 기준 CTR 미달이고 AIO=yes 이거나 항목 대조표에서 빠진 주제가 1개 이상이면 **L2 이상**, 빠진 주제 2개 이상·답 형식 불일치(F)와 빠진 주제가 함께 있음·재수정 2차 이상이면 **L3**. L3 는 "대부분을 뜯어고쳐도 된다" 는 뜻이다 — 상위 글 구조를 기준으로 H2 흐름·답 블록·FAQ 를 다시 설계하고, 기존 문단은 새 구조에 맞는 것만 옮겨 쓴다(1급 자료·이미지·내부 링크는 유지).
- **숏테일(이벤트 날짜가 있는 글)**: 수요가 끝나기 전 기회가 한두 번뿐이므로 **첫 수정부터 대응표의 원인을 전부** 고친다. 답 형식이 다르면(F) 첫 수정에서 표·목록을 만든다 — 재산세 글처럼 '다음에 보강' 으로 미루지 않는다.

[7-3b] **원인-수정 대응표 (필수 — 없으면 반영 금지)** — `bench/{slug}-{TODAY}.md` 에 표로 쓴다:
```
| # | 찾은 원인 (근거: 숫자·상위 n편) | 이번 수정에서 고친 것 (위치·H2·블록) | 상태 |
|---|---|---|---|
| 1 | 상위 3편 중 3편이 카드사별 비교표, 우리는 없음 | 두 번째 H2 '카드사 7곳 비교' + 표 7행(ETAX 공지 출처) | 해결 |
| 2 | TARGET 답이 본문 4번째 H2 중간 | 첫 문단 첫 문장 + 첫 H2 로 이동 | 해결 |
| 3 | 상위 과반이 FAQ, 우리는 없음 | FAQ 3문항 + FAQPage 스키마 | 해결 |
```
- 원인 목록은 **항목 대조표의 "우리 글에 없음" 줄 전부 + 답의 위치 + 답의 형식 + 검색의도(5-3 상위 검색어별) + AI 답변이 못 주는 것(5-5) + 지역(5-4) + 날짜·최신성** 에서 빠짐없이 옮긴다.
- 상태는 `해결` 또는 `확인 불가(1차 출처 시도: …)` 만 쓴다. `보강 후보`·`다음에`·`미해결` 은 쓰지 않는다. `확인 불가` 줄은 그 사실 대신 할 수 있는 구조적 수정을 같은 줄에 적는다.
- 대응표의 '해결' 줄 수가 많아 글의 대부분이 바뀌어도 된다(롱테일 원칙). 분량 상한(L2 ±40%)을 넘으면 L3 로 올려 기록한다.

[7-4] **다시 쓰기 규칙** (영문. 기준은 `KoreaPlug-Draft.md` 5-3·5-4·5-6. 작성은 `backups/` 에 저장한 원본을 복사한 **로컬 파일**에서 한다 — 사이트에서 직접 고치지 않는다)
- **Rank Math 키워드 매칭 (필수)**: Focus Keyword(첫 항목) 원문이 **제목·설명·첫 문단 첫 10%·H2 1개 이상**에 들어가야 한다(대소문자 무시, 부분 문자열 일치 — 예: 'yakgwa korea' 는 'Yakgwa Korean…' 에 포함). 제목은 Focus Keyword 로 시작하는 것을 기본으로 하고, TARGET_QUERY 의 핵심어(where to buy·in Seoul 등)를 뒤에 붙인다. 제목에 숫자(연도·개수) 1개, 파워/감성 단어(best·easy·real 등) 1개를 넣는다. 제목에 새로 들어간 표현이 서브 키워드와 어긋나면 서브 키워드 1개를 그 표현으로 바꿀 수 있다(첫 항목은 절대 불변, 총 5개 유지).
- **rank_math_title**: 위 매칭을 지키면서 TARGET_QUERY 의 의도가 드러나게. **60자 이하**(python `len()`). 질문형 검색어면 답의 방향을 보여 준다. 본문에 있는 구체값 1개. 벤치마킹 "과반" 요소는 따르고, 상위 8 제목과 겹치지 않는 우리만의 각도 1개. 낚시·과장 금지.
- **rank_math_description**: **150자 이하**, Focus Keyword(첫 항목 또는 그 핵심어) 포함, 첫 문장에 답.
- **도입 첫 문단**: 첫 문장에 TARGET_QUERY 의 답 + Focus Keyword. 문체 유지.
- **L2·L3 본문**:
  - TARGET_QUERY 에 답하는 H2 를 **첫 번째 또는 두 번째 H2** 로 둔다. 나머지 상위 검색어(5-3 표)에도 H2 또는 H3 로 답한다.
  - 항목 대조표에서 상위 과반이 다루고 우리에게 없는 주제를 채운다 — 단, 1차 출처로 확인된 사실만.
  - 기존 글의 **1급 자료·캡처·표·내부 링크·이미지(src·alt)·FAQ** 는 전부 유지한다(위치 이동은 가능, 삭제 금지). FAQ 문항을 바꾸면 FAQ JSON-LD 도 같은 내용으로 맞춘다.
  - 기존 HTML 래퍼(`max-width:820px…`)·인라인 스타일·TOC 블록 구조를 그대로 쓴다. 새 문단·H2 는 기존 문단·H2 의 태그·style 을 복사해 만든다.
  - 분량: L2 는 기존 ±40%, L3 는 **기존 이상 그리고 상위 글 단어 수 중앙값의 80% 이상**(단, 채우기용 문장 금지).
  - `KoreaPlug-Draft.md` 5-4 관문 준수: 가짜 경험 0건, 본문 삽입 금지 자료(SEO 리서치·SERP·검색량·서치콘솔 이야기) 0건, 이미지 출처 규칙.
  - H2 가 바뀌면 TOC 는 플러그인이 자동 생성하므로 수동 목차 텍스트가 있으면 그것도 맞춘다.
- ⛔ 금지: 본문에 없고 1차 출처로 확인도 안 된 사실 / 키워드 반복(Focus Keyword 밀도 2.5% 초과) / 슬러그·Focus Keyword·카테고리·발행일·대표 이미지 변경 / 벤치마킹 문장 복사(연속 8단어 이상 일치 금지) / 기존 1급 자료·내부 링크·이미지 삭제.
- 결과물: `work/{slug}-{TODAY}-v{n}.html`(새 content.raw) 과 `work/{slug}-{TODAY}-v{n}.json`(`{"title","desc"}`).

[7-5] 수정안 요약을 `bench/{slug}-{TODAY}.md` 끝에 붙인다 — 수준(L1/L2/L3), **원인-수정 대응표(7-3b) 최종본**, 바뀐 H2 전·후, 추가한 항목과 각 항목의 1차 출처, 단어 수 전·후. 쓰기를 마친 뒤 대응표의 '해결' 줄마다 새 본문(work 파일)에서 해당 H2·블록이 실제로 있는지 다시 확인한다.

---

## STEP 8 — 검색봇·SEO 점검 → 반영·공개 → 공개 페이지 재점검 (REST, 크롬 불필요)

[8-0] **반영 전 점검 (로컬 파일 기준 — 하나라도 실패하면 7-4 로 돌아가 1회 고치고, 그래도 실패면 그 글은 반영하지 않고 `proposed` 로 기록)**
```bash
cd $W && python3 - <<'PY'
import json,re,html,sys
slug='{slug}'; n='{n}'; T='{TODAY}'
old=json.load(open(f'backups/{slug}-{T}-v{int(n)-1}.json')); raw0=old['content']['raw']
raw=open(f'work/{slug}-{T}-v{n}.html').read(); m=json.load(open(f'work/{slug}-{T}-v{n}.json'))
fk=old['meta']['rank_math_focus_keyword'].split(',')[0].strip().lower()
txt=lambda h: html.unescape(re.sub(r'<[^>]+>',' ',re.sub(r'<script.*?</script>','',h,flags=re.S)))
w0=len(txt(raw0).split()); w1=len(txt(raw).split())
links=lambda h:set(re.findall(r'href="(https://koreaplug\.com/[^"#?]+)',h))
imgs=lambda h:set(re.findall(r'<img[^>]+src="([^"]+)"',h))
h1e=raw.find('</h1>'); aft=raw[h1e:] if h1e>=0 else raw; aft=aft[aft.find('</p>')+4:] if h1e>=0 else aft   # 히어로 부제 건너뜀
first_p=next((txt(p) for p in re.findall(r'<p[^>]*>(.*?)</p>',aft,re.S) if len(txt(p).strip())>=80),'')
h2=[txt(x).lower() for x in re.findall(r'<h2[^>]*>(.*?)</h2>',raw,re.S)]
chk={
 'title<=60':len(m['title'])<=60, 'desc<=150':len(m['desc'])<=150,
 'fk_in_title_or_desc':any(k in (m['title']+' '+m['desc']).lower() for k in [fk]+fk.split()[:1]),
 'fk_in_first_p_100':fk.split()[0] in first_p.lower()[:160],
 'fk_in_h2':any(fk.split()[0] in h for h in h2),
 'h1_count_same':raw.count('<h1')==raw0.count('<h1'),
 'no_h1_added':raw.count('<h1')<=1 or raw.count('<h1')==raw0.count('<h1'),
 'internal_links_kept':links(raw0)<=links(raw),
 'images_kept':imgs(raw0)<=imgs(raw),
 'img_alt_present':all('alt="' in t and 'alt=""' not in t for t in re.findall(r'<img[^>]*>',raw)),
 'tags_balance_not_worse':all(raw.count(f'<{t}')-raw.count(f'</{t}>')==raw0.count(f'<{t}')-raw0.count(f'</{t}>') for t in ['p','h2','h3','ul','ol','li','table','div']),   # 원본의 짝 상태와 같아야 함
 'jsonld_valid':all((json.loads(s) or True) for s in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>',raw,re.S)),
 'words_ok':w1>=w0*0.7,
 'no_seo_talk':not re.search(r'search console|autocomplete|search volume|SERP|ranking on google',txt(raw),re.I),
 'no_external_img':all(re.match(r'https://(koreaplug\.com|images\.unsplash\.com)/',s) for s in imgs(raw)),
 'kw_density<=2.5%':txt(raw).lower().count(fk)*len(fk.split())/max(w1,1)<=0.025,
 'no_fake_testimonial':not re.search(r'Verified (Traveler|Visitor|Reader)|— (A |Our )?(reader|traveler), 20\d\d',txt(raw),re.I),
}
# 원인-수정 대응표(7-3b): 표가 있고, 모든 줄의 상태가 '해결' 또는 '확인 불가' 여야 한다
bench=open(f'bench/{slug}-{T}.md').read() if __import__('os').path.exists(f'bench/{slug}-{T}.md') else ''
rows=[r for r in re.findall(r'^\|\s*\d+\s*\|.*\|\s*([^|]+?)\s*\|\s*$',bench,re.M)]
chk['gap_table_exists']=len(rows)>0
chk['gap_all_resolved']=all(s.startswith('해결') or s.startswith('확인 불가') for s in rows)
level=m.get('level','')
if level=='L1': chk['L1_allowed(빠진 항목 0 증명)']=('빠진 항목 0' in bench and '답 위치 OK' in bench and '답 형식 OK' in bench)
print(json.dumps({'words':[w0,w1],'fail':[k for k,v in chk.items() if not v]},ensure_ascii=False))
PY
```
- **Rank Math 비교 (필수)**: 
```bash
cd $W && python3 rm_check.py backups/{slug}-{TODAY}-v{n-1}.raw.html "{이전 title}" "{이전 desc}" "{focus 목록}" {slug}
cd $W && python3 rm_check.py work/{slug}-{TODAY}-v{n}.html "{새 title}" "{새 desc}" "{focus 목록}" {slug}
```
  새 `pass` 가 이전보다 **작으면 반영 금지** → 7-4 로 돌아가 떨어진 항목(`fail`)을 고친다. B1~B5(제목·설명·URL·앞 10%·본문 키워드)는 하나라도 실패하면 반영 금지. (Rank Math 편집기 점수는 편집 화면 저장 때만 갱신되고, 크롬에서 wp-admin 편집 화면이 열리지 않는 경우가 있어(2026-09-24 실측) 이 근사 점검을 기준으로 한다. 편집 화면이 열리면 점수만 읽고 저장하지 않는다.)
- 벤치마킹 복사 검사: 7-2 에서 읽은 상위 글 첫 문단·H2 와 우리 새 본문을 비교해 **연속 8단어 일치 0건**인지 python 으로 확인한다.
- L1 은 `<p` 개수가 원본과 같아야 한다. L2·L3 은 `fail` 목록이 비어 있으면 통과.
- `work/{slug}-{TODAY}-v{n}.json` 에 `"level":"L1|L2|L3"` 를 함께 적는다. L1 이면 bench 파일에 `빠진 항목 0 · 답 위치 OK · 답 형식 OK` 세 문구와 각각의 근거가 있어야 통과한다(7-3 A).
- `gap_table_exists`·`gap_all_resolved` 실패 = 원인을 남긴 부분 수정 → **반영 금지**, 7-4 로 돌아가 남은 원인을 고친다.

[8-1] 백업 — `backups/{slug}-{TODAY}-v{n-1}.json` 에 REST `context=edit` 응답(meta·content·modified·status)을 저장하고, `content.raw` 만 따로 `backups/{slug}-{TODAY}-v{n-1}.raw.html` 로도 저장(rm_check 비교용). 실패면 반영하지 않는다. (8-0 보다 먼저 해도 된다)
- ⚠️ 크롬에 `koreaplug.com/wp-admin/post.php` 탭이 열려 있으면 먼저 `https://koreaplug.com/` 으로 옮긴다(에디터 자동저장이 REST 결과를 덮어쓴다).

[8-2] 본문 반영 — `POST /wp-json/wp/v2/posts/{id}` `{"content": <work 파일>}`. **status 는 보내지 않는다**(공개 글은 공개 그대로). 8초 후 재조회: `status=publish` · 새 본문과 `content.raw` 가 같음. 어긋나면 백업 raw 로 원복하고 기록, 8-3 건너뜀.

[8-3] 제목·메타 — REST `meta` (JS dispatch 는 저장되지 않으므로 쓰지 않는다)
```bash
curl -s -u "$U:$P" "https://koreaplug.com/wp-json/wp/v2/posts/{id}?context=edit&_fields=meta" | grep -c rank_math_focus_keyword   # 0 이면 스니펫 4183 미작동 → 본문 원복·반영 중단·기록
curl -s -u "$U:$P" -X POST -H "Content-Type: application/json" "https://koreaplug.com/wp-json/wp/v2/posts/{id}" \
  --data-binary @work/{slug}-{TODAY}-v{n}.meta.json -o /dev/null -w "%{http_code}\n"   # {"meta":{"rank_math_title":..,"rank_math_description":..}}
```
재조회 검증: 두 값이 새 값이고 `rank_math_focus_keyword` 가 그대로인지. 어긋나면 1회 재시도 → 실패면 본문·메타 모두 백업 값으로 되돌리고 기록.

[8-4] **공개 페이지 재점검 (검색봇 관점)** — 구글봇 UA 로 `?nc={epoch}` 요청:
```bash
curl -s -D /tmp/h.txt -A "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" "https://koreaplug.com/{slug}/?nc=$(date +%s)" -o /tmp/pub.html
```
확인 항목(python): HTTP 200 · `X-Robots-Tag` 에 noindex 없음 · `<meta name="robots">` 에 `index` 있고 `noindex` 없음 · canonical = 글 주소 · `<title>`·description = 새 값 · H1 정확히 1개 · JSON-LD 전부 파싱 성공(BlogPosting 포함, FAQ 가 있으면 FAQPage 포함) · 새 첫 문장이 HTML 에 있음 · 본문 이미지 URL 전부 200(koreaplug.com 은 curl HEAD, unsplash 는 ID 형식만) · robots.txt 가 글 경로를 막지 않음.
- 캐시 때문에 title·첫 문장만 다르면 `캐시 반영 대기` 로 기록(원복하지 않음).
- noindex·canonical 불일치·JSON-LD 파싱 실패·H1 개수 이상은 **즉시 백업으로 원복**하고 기록.

---

## STEP 9 — 기록

[9-1] 엔진 기록 (잠금의 유일한 근거) — 반영한 글마다 1건
```bash
cat > /tmp/v.json <<'J'
{"slug":"...","status":"applied|proposed|rollback","track":"urgent|normal","date":"{TODAY}",
 "keyword":"{TARGET_QUERY}","ctr_before":{28일 CTR},"impr_before":{28일 노출},"pos_before":{순위},"published":"{발행일}","cause":"A|B|B-geo|C",
 "level":"L1|L2|L3",
 "before":{"title":"...","desc":"...","first_p":"backups/{파일명}"},
 "after":{"title":"...","desc":"...","first_p":"...","content":"work/{파일명}"},
 "gaps":[{"cause":"찾은 원인","fix":"고친 것","status":"해결|확인 불가"}],
 "note":"기준CTR·타깃검색어 점수·한국밖 비율·상위8 패턴(n/8)·항목 대조 결과·단어 수 전후·AIO·재수정 근거 한 줄"}
J
cd $W && python3 gsc_engine.py record --file /tmp/v.json
```
반영에 실패해 원복했으면 기록하지 않는다.

[9-1b] **모니터링 파일 생성** — 반영한 글마다 4-B ① 화면으로 읽은 수정 전 14일을 `track.py add` 로 저장하고(`monitor/data/{slug}.json` 생성, 파일 맨 처음엔 `python3 track.py seed` 도 가능), `monitor/{slug}.md` 를 만든다: 상태 `트래킹 중` · 수정 내용 요약(전·후 제목·설명·바꾼 소제목·분량) · rm_check 전·후 점수 · TARGET_QUERY 와 수정 전 7일 검색어 표 · **수정 전 14일 일자별 표**(4-B ①과 같은 화면) · 수정 후 경과 빈 표(1~7일) · 품질 확인 빈 표(1·3·7일) · 7일 요약·판정 빈 칸. 그리고 `monitor/_summary.md` 에 한 줄 추가.

[9-2] `log.md` 맨 위에 추가 — 글마다: 선정 근거(숫자·기준 CTR) / 검색어 점수표(TARGET·MAIN) / 국가 분포 / 구글 상위8·우리 순위·AIO / **벤치마킹 표·항목 대조표·패턴 결론** / 원인·수정 수준 / **원인-수정 대응표(남긴 원인 0건 확인)** / 전·후(제목·메타·첫 문장·H2 목록·단어 수) / 8-0·8-4 점검 결과. 오늘 처리량을 넘어 다음 회차로 넘어간 글은 순서만 한 줄로.

[9-3] **누적 성적표** 계산 (STEP 10 에 쓴다)
```bash
cd $W && python3 - <<'PY'
import json,os
st=json.load(open('state.json')); ev=json.load(open('/tmp/plan.json')).get('evaluations',[]) if os.path.exists('/tmp/plan.json') else []
n=sum(1 for p in st['posts'].values() for v in p['versions'] if v.get('status')=='applied')
vd={}
for p in st['posts'].values():
    for v in p['versions']:
        if v.get('status')=='applied':
            k=v.get('verdict') or 'WAIT'; vd[k]=vd.get(k,0)+1
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
{오늘 무엇을 했는지 한 문장. 예: "클릭이 적은 글 2편을 상위 글과 비교해 다시 쓰고, 검색봇 점검을 통과해 공개 반영했습니다." / "고칠 필요가 있는 글이 없어 판정만 했습니다."}

■ 사이트 전체 (최근 28일 {START28}~{LATEST})
구글에 {노출}번 보였고 {클릭}번 클릭됨 → 클릭률 {x}%
우리 사이트 순위별 보통 클릭률: 1~3위 {a}% · 4~6위 {b}% · 7~10위 {c}% · 11위 밖 {d}%

■ 지금까지 성적표 (이 루틴이 고친 글 전체)
고친 글 {n}편 → 좋아짐 {n} · 다시 수정 {n} · 되돌림 {n} · 아직 측정 중 {n}
측정 끝난 글 평균 클릭률: 고치기 전 {a}% → 고친 후 {b}%

■ 수정 글 트래킹 요약판 (monitor/_summary.md 그대로 — ⚠️ 트래킹 중인 글이 1편이라도 있으면 **수정 후 데이터가 아직 없어도 반드시 넣는다**. 데이터가 없으면 각 행에 수정 전 7일 값 + '수정 후 첫 데이터 {날짜} 회차 · 7일 요약 {날짜} 회차' 를 적는다)
{표: 글 · N일째 · 수정 전 7일 CTR → 수정 후 누적 CTR · 클릭 전→후 · 순위 전→후 · 구글 새 제목 반영 · 판정/상태}

■ 트래킹 중인 글 일자별 경과 (monitor/_daily.md 그대로 — 글마다 한 표, 날짜순)
{맨 위 "한눈에" 표: 글 · 수정일 · 경과(D+n) · 수정 전 7일 CTR · 수정 후 누적 CTR · 순위 전→후 · 현재 판정}
{글마다 표: | 날짜 | 구분(수정 전 D-7…D-1 / 수정일 / 수정 후 D+1…) | 클릭 | 노출 | CTR | 순위 | CTR 비교 ▲▼≈ | 노출 비교 ▲▼≈ | 누적 CTR |
 + 맨 아래 한 줄: 수정 전 7일 → 수정 후 n일 누적 → 현재 판정}
{오늘 새로 들어온 날은 그 행 끝에 "(오늘 추가)" 를 붙여 말로 한 줄 설명: 예 "회식 글 D+3: 노출 60·클릭 2(3.3%) — 수정 전 평균 0.25%보다 ▲, 누적 3.3%로 좋아지는 중"}
{GA4 방문(조기 신호): 글마다 수정 전 7일 일평균 → 수정 후 일별 방문 수 (오늘은 집계 중)}
{숏테일 조기 재수정(6-2b)을 한 글: 이벤트까지 남은 일수 · 수정 후 2일 CTR vs 수정 전 · 무엇을 더 고쳤는지}
{오늘 품질 확인을 한 글: "구글 표시 제목: 새 제목 반영됨/아직 옛 제목 · 우리 순위 {n}위"}
{오늘 7일 요약·판정이 난 글: 판정 + "잘 수정됐나" 한 단락}

■ 지난번 고친 글은 어떻게 됐나
{없으면 "아직 판정할 글이 없습니다." / 있으면 글마다 한 줄: "{글 설명}: 고치기 전 {a}% → 고친 후 {b}% (노출 {n}·클릭 {n}) → 유지/다시 수정/되돌림/아직 데이터 부족({n}/{기준})"}

■ 오늘 고친 글 {n}편
[1] {글 설명} ({slug}) — {바로 반영·공개함 / 점검 실패로 반영 안 함}
- 왜 이 글인가: {노출}번 보였는데 클릭 {n}번 (클릭률 {x}%) · 구글 {순위}위 → 이 순위면 보통 {기준}% · 놓친 클릭 약 {n}번 · {시기성}
- 사람들이 뭐라고 검색했나: "{TARGET_QUERY}" ({노출}번 · 클릭 {n}번 · {순위}위){MAIN 과 다르면 한 줄}
- 누가 보고 있나: 한국 밖 {x}% ({상위 국가})
- 잘 되는 글과 비교: {예: "상위 8편 중 4편이 가게 이름으로 바로 답함. 본문을 연 3편은 평균 2,100단어에 가격표·위치를 다룸. 우리 글은 '어디서 사나'가 끝에 3문장뿐이었음"}
- 원인과 수정 수준: {쉬운 말 + 제목만/일부 섹션/전면 재작성} — 왜 이 수준인지(원인이 정함) 한 줄
- 찾은 원인 → 고친 것 (원인-수정 대응표 그대로, 줄마다): {예: "① 상위 3편이 카드사별 비교표 → 두 번째 소제목에 7곳 비교표 추가 ② 답이 본문 중간 → 첫 문장으로 이동 ③ FAQ 없음 → 3문항 추가"} · 남긴 원인 {0}건 (있으면 '확인 불가' 사유)
- 바꾼 것: 제목 {전} → {후} / 설명문 {후} / 첫 문장 {후} / 새로 넣은 소제목 {목록} / 분량 {전}→{후}단어
- Rank Math 점검: 수정 전 {a}/20 → 수정 후 {b}/20 (떨어진 항목 없음 / {있으면 무엇})
- 검색봇 점검: {통과 항목 수}/{전체} 통과 {실패가 있었으면 무엇을 어떻게 고쳤는지}
- 효과 확인 예정: 약 {n}일 뒤 자동 판정
[2] …

■ 트래킹 중이라 대기 중인 글
{글 설명}: 수정일 · N일째 · 판정 예정일

■ 다음 차례 3편
1. {글 설명}: 노출 {n} · 클릭 {n} · 순위 {x} (기준 {y}%) · 놓친 클릭 {n} · {시기성}
2. …
3. …

■ 확인이 필요한 것
{없으면 "없음". 있으면 쉬운 말로}
```

---

## 효과 판정 규칙 (gsc_engine.py `evaluate`, 참고용 — 수치는 CFG)

- 반영 후 데이터 = 서치콘솔에서 **반영 다음날 ~ LATEST** 범위를 페이지 필터로 직접 읽은 값(네이버와 달리 누적 차감이 아니라 정확한 구간값).
- 판정 시점: 긴급 = 노출 +400 이상 **그리고** 클릭 +5 이상(데이터 4일 지나면 쌓인 만큼) / 상시 = 노출 +800 **그리고** 클릭 +8(데이터 14일 지나면 쌓인 만큼). 그 전에는 WAIT 로 `노출 n/기준 · 클릭 n/기준 · 데이터 일수` 보고.
- KEEP: 반영 후 CTR ≥ max(이전×1.3, 이전+0.5%p) 또는 ≥ 같은 순위 구간 기준 CTR → 14일 보호(HOLD) 후 재후보.
- REEDIT: 기준 미달 → 재수정. v3 까지 개선 없으면 REEDIT(level L3) → 전면 재작성·검색어 각도 변경(닫지 않는다).
- ROLLBACK: 반영 후 CTR < 이전×0.7 → 되돌림.
- AIO 확인 결과는 30일 캐시(수정 방법 선택용). 이벤트가 지난 글은 track=past 로 대기열 뒤쪽에서 계속 고친다.
- 순위가 반영 전후로 3 이상 움직였으면(예: 6위→12위) CTR 변화는 제목 효과가 아닐 수 있다 → 판정을 WAIT 로 두고 `note` 에 "순위 변동" 을 적는다. 단 L2·L3(본문 재작성)은 순위 상승 자체가 목표이므로, 순위가 3 이상 **올랐으면** 클릭 수 증가로 KEEP 여부를 판단한다.

## 오류 처리 요약

| 상황 | 처리 |
|---|---|
| Claude 폴더 미연결 | bash 확인 → 실패 시에만 `device_request_folder_access` 1회 → 실패면 STEP 10 |
| GSC 화면 로그인 풀림·행 0 | 판정·수정 건너뜀, STEP 10에 `GSC 읽기 실패` |
| 5-0 기준 CTR 계산 실패 | 엔진 `queue[]` 순서(고정 목표 2.5%)로 진행하고 STEP 10 에 기록 |
| 검색어 표·국가 표 읽기 실패 | MAIN_QUERY = TARGET_QUERY 로 두고 진행, 국가 판정은 "미확인" |
| 구글 검색 캡차 | 그 회차 AIO 확인·벤치마킹 중단, 해당 글 `미확인` 유지 |
| 벤치마킹 페이지 차단·캡차 | 그 페이지 건너뛰고 다음 후보(상위 8 밖 9~15위까지 내려가 본다). 끝내 본문을 1편도 못 열면 검색결과 제목·설명·AI 답변·"People also ask"·5-3 검색어 표로 대조표를 만들고, 거기서 찾은 원인에 맞는 수준으로 수정한다(L1 로 낮추지 않는다). bench 에 "본문 벤치 0편" 을 적는다 |
| 원인-수정 대응표에 '해결'·'확인 불가' 아닌 줄이 있음 | 반영 금지 → 7-4 로 돌아가 그 원인을 고친다. 그래도 남으면 `proposed` 기록 + STEP 10 "확인 필요" |
| pw.txt 키 누락·WP 인증 실패 | 반영만 건너뜀(판정·수정안은 진행) |
| 스니펫 4183 미작동(meta 에 rank_math 키 없음) | 제목·메타 반영 중단, 본문은 원복, 엔진 기록 안 함 |
| device_bash `Workspace unavailable` | 상단 [작업 공간 대체] — 스테이징 + 클라우드 Bash + 커밋으로 계속 진행 |
| rm_check 통과 수 감소·B1~B5 실패 | 반영 금지, 7-4 로 돌아가 1회 수정 → 그래도 실패면 `proposed` 기록 |
| 8-0 반영 전 점검 실패 | 7-4 로 돌아가 1회 수정 → 그래도 실패면 반영 안 함, `proposed` 기록 |
| 본문 반영 후 불일치 | 백업 raw 로 원복, 기록 |
| 8-4 공개 페이지 noindex·canonical·JSON-LD·H1 이상 | 즉시 백업(본문·메타)으로 원복, 기록 |
| 8-4 캐시로 title·첫 문장만 다름 | `캐시 반영 대기` 기록(원복 안 함) |
| 구글 API 접근 | 시도 금지(네트워크 정책 403 확인됨) |
