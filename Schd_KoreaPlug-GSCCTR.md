# Schd_KoreaPlug-GSCCTR — 구글 "노출 많고 CTR 낮은 글" 개선 루틴 (Cowork 예약 작업용)

*매일 07:20 KST 실행. 예약 시각이 되면 같은 날 이미 실행됐더라도 다시 진행한다(판정·잠금은 `state.json` 이 막아 주므로 같은 글을 두 번 고치지 않는다).

날짜: 실행 시점의 실제 KST 날짜를 쓴다. 이 프롬프트에 적힌 고정 날짜는 무시한다.

이 루틴이 하는 일 (0and1life 네이버 루틴 `Schd_0and1Life-NaverCTR.md` 와 같은 구조, 데이터 원천만 다르다):
1. **서치콘솔 실적 화면을 Claude in Chrome 으로 읽는다** — CSV·API 키·네트워크 설정 없이 로그인된 크롬으로 본다. 날짜 범위를 지정할 수 있어 "고친 다음날 이후"만 잘라 정확히 잰다
2. **이미 고친 글의 효과를 매일 판정**한다 → 개선이면 유지, 개선이 없으면 재수정, 나빠졌으면 되돌림
3. 새 대상 1편을 고른다 → 시기성 글(긴급)은 그날 바로 수정, 상시 글은 NORMAL_MODE 에 따른다
4. 수정은 버전(v1·v2·v3)으로 기록해 다음 날 같은 글을 다시 고치지 않는다

작업 폴더: `C:\Users\win\Documents\Claude\gsc-ctr\` (blog 저장소 밖)
- `gsc_engine.py` — 계산 엔진(대상 선정·잠금·효과 판정·기록). 판단이 필요 없는 계산은 전부 이 스크립트가 한다
- `state.json` — 이벤트 날짜, AI Overview 확인 결과, 글별 버전 이력(잠금의 유일한 근거)
- `snapshots/{데이터 종료일}.json` — 28일 페이지 표 · `after/` — 반영 후 구간 조회값 · `backups/` — 수정 전 원본 · `log.md` — 사람이 읽는 기록

⚠️ [무인 실행 원칙 — 최우선] 사람이 없는 시간에 실행된다. 승인이 필요한 도구 호출은 "그것 없이는 진행할 수 없음을 실측으로 확인한 뒤"에만 한다. 승인 창이 응답 없이 닫히면 재시도하지 않고 오류로 기록한 뒤 STEP 10으로 간다.
⚠️ [시간 제한] **07:45까지 끝낸다.** 06:30 0and1life 루틴·06:51 이미지 루틴이 같은 크롬을 쓰므로 07:20 전에는 시작하지 않는다. 07:42가 지났는데 STEP 8에 들어가지 못했으면 반영하지 않고 수정안만 `log.md` 에 남긴다(엔진 기록 안 함 → 다음 날 다시 뽑힌다).
⚠️ 삭제 금지: 글·리비전·파일·Notion 행을 삭제하지 않는다.
⚠️ 변경 금지 항목: status·**슬러그(URL)**·Focus Keyword(`rank_math_focus_keyword`)·카테고리·발행일·H1·H2·도입 첫 문단 외 본문.
⚠️ git commit·push 하지 않는다 — 사용자가 직접 한다. pw.txt 값은 절대 출력하지 않는다.
⛔ 구글 API(`*.googleapis.com`)는 이 환경에서 네트워크 정책으로 막혀 있다(2026-09-24 실측 403). **API 호출을 시도하지 않는다.** 데이터는 크롬 화면으로만 읽는다.

---

## STEP 0 — 설정값 (사용자만 수정)

```
URGENT_MODE    = AUTO      # 시기성 긴급 글(이벤트 3~14일 남음): 그날 바로 반영
NORMAL_MODE    = SAMPLE    # 상시 글: SAMPLE = 수정안만 기록 / AUTO = 바로 반영
REEDIT_MODE    = AUTO      # 효과 판정이 "개선 없음"이면 재수정
NEW_PER_DAY    = 1
REEDIT_PER_DAY = 1
```
판정 기준값(노출 하한 300, 목표 CTR 2.5~4.0%, 긴급 창 14일, 효과 판정 노출·클릭 기준, 데이터 지연 2일, 재수정 한도 3차)은 `gsc_engine.py` 상단 `CFG` 에 있다.

---

## STEP 1 — 날짜와 폴더

1) TODAY(KST) 기록. 서치콘솔은 최근 2일치가 비어 있으므로 **LATEST = TODAY − 2일**, **START28 = LATEST − 27일** 을 계산한다(YYYYMMDD 형식도 함께).
2) bash 로 마운트를 찾는다. `request_cowork_directory` 는 아래가 실패했을 때만 1회.
```bash
CLAUDE_DIR=$(ls -d /sessions/*/mnt/Claude 2>/dev/null | head -1)
W=$CLAUDE_DIR/gsc-ctr
echo "claude=$CLAUDE_DIR"; ls $W/gsc_engine.py
```
- 없으면 `request_cowork_directory { path: "C:\Users\win\Documents\Claude" }` 1회 → 실패 시 STEP 10.
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
({rows:window.__rows.length, kept:window.__rows.filter(r=>r.impr>=100).length, len:window.__f.length})
```
이어서 `window.__f.slice(0,900)`, `slice(900,1800)`, … 을 `len` 까지 차례로 호출해 이어 붙인다. 행 형식 `slug|clicks|impr|pos`. 같은 slug 가 여러 행이면(URL 변형) 엔진이 합친다.

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
탭은 이후 STEP 4·6 에서 계속 쓴다.

---

## STEP 4 — 반영한 글의 "반영 후" 구간 읽기

```bash
cd $W && python3 gsc_engine.py need-after --today {TODAY}
```
`need[]` 의 각 글에 대해 크롬으로 **페이지 필터 + 날짜 범위** 화면을 열어 총 클릭수·총 노출수를 읽는다:
`…/search-analytics?resource_id=https%3A%2F%2Fkoreaplug.com%2F&breakdown=query&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION&page=*https%3A%2F%2Fkoreaplug.com%2F{slug}%2F&start_date={start}&end_date={end}`
```javascript
await new Promise(r=>setTimeout(r,6000));
const t=document.body.innerText; const m=t.match(/총 클릭수\s*\n?\s*([\d,]+)[\s\S]{0,60}?총 노출수\s*\n?\s*([\d,]+)/);
const top=[...document.querySelectorAll('table tbody tr')].slice(0,5).map(r=>[...r.querySelectorAll('td')].map(td=>td.innerText.trim().split('\n')[0]).join('|'));
({clicks:m&&m[1], impr:m&&m[2], top})
```
`after/{TODAY}.json` 에 `{"slug": {"start","end","impr","clicks"}}` 로 모아 저장한다. 조회 실패한 글은 넣지 않는다(엔진이 WAIT 처리).

---

## STEP 5 — 오늘 계획 받기

```bash
cd $W && python3 gsc_engine.py plan --today {TODAY} --after after/{TODAY}.json
```
| 키 | 뜻 |
|---|---|
| `stale` | true 면 최신 스냅샷이 LATEST 보다 오래됐다(STEP 3 실패) → 판정·수정 건너뛰고 STEP 10 |
| `evaluations[]` | KEEP / HOLD / WAIT / REEDIT / ROLLBACK / LIMIT. 각 행에 `ctr_before`·`ctr_after`·`impr_after`·`clicks_after`·`window` |
| `queue[]` | 새 대상 후보(우선순위 정렬). `track`, `days_left`, `lost_clicks`, `pos`, `aio`(yes/no/미확인) |
| `excluded[]` | E3 내년용 / E4 AI Overview 선점 |
| `need_event_date[]` | 이벤트 날짜를 모르는 글 |
| `need_aio_check[]` | 대기열 상위 중 AI Overview 를 아직 확인하지 않은 글(최대 5) |

[5-1] `need_event_date`: 글 본문(REST `content.rendered`)에서 독자 행동을 막는 날짜(명절 당일·예매 오픈·마감·시행일)를 찾는다. 여러 개면 아직 지나지 않은 가장 이른 것. 없거나 상시 정보면 none. 추정 금지.
```bash
python3 gsc_engine.py set-event {slug} 2026-10-03   # 또는 none
```
[5-2] `need_aio_check`: 그 글의 대표 검색어를 먼저 얻는다 — STEP 4 의 페이지 필터 URL(날짜는 START28~LATEST)로 검색어 표 상위 3개를 읽는다(노출 1위 = MAIN_QUERY). 그다음 크롬으로 `https://www.google.com/search?q={MAIN_QUERY 인코딩}&hl=en&gl=us` 를 열고:
```javascript
await new Promise(r=>setTimeout(r,3000));
const t=document.body.innerText; const aio=/AI Overview|AI 개요/.test(t);
const links=[...document.querySelectorAll('a h3')].map(h=>(h.closest('a')||{}).href||'').filter(u=>u.startsWith('http')&&!u.includes('google.com'));
({aio, aioText: aio? t.slice(t.search(/AI Overview|AI 개요/),t.search(/AI Overview|AI 개요/)+250).replace(/\n+/g,' '):'', ours: links.findIndex(u=>u.includes('koreaplug.com'))+1, top: links.slice(0,8), captcha:/unusual traffic|로봇이 아닙니다/.test(t)})
```
- `aio` 가 true 이고 **aioText 가 그 검색어의 핵심 답(정의·가부·날짜)을 이미 말하고 있으면** `set-aio {slug} yes` (GSC-Weekly-Report-Routine.md 의 AIO 규칙 — 제목·메타로 회수되지 않으므로 개선 대상 아님). 아니면 `set-aio {slug} no`.
- `captcha` 가 true 면 더 검색하지 않고 그 글은 `미확인` 으로 둔 채 진행한다(STEP 10 기록).
- 검색은 회차당 **최대 5회**. `top`(상위 8 도메인)과 `ours`(우리 순위)는 STEP 7 근거로 쓴다.
[5-3] 5-1·5-2 에서 하나라도 설정했으면 `plan` 을 다시 실행한다.

---

## STEP 6 — 오늘 할 일 정하기 (이 순서, 이 한도)

1. **되돌림** `rollback[]` — 백업의 직전 버전 값으로 REST 되돌리고 `status: "rollback"` 기록.
2. **재수정** `reedit[]` — REEDIT_MODE=AUTO 면 1편. 긴급 우선.
3. **LIMIT** — `python3 gsc_engine.py close {slug} "3차까지 개선 없음 — 제목·메타로 한계"`, STEP 10에 "본문 보강·각도 재타겟 후보"로 올린다.
4. **새 대상** `queue[]` 맨 위부터 NEW_PER_DAY 편. `aio` 가 `미확인` 인 글은 5-2 를 거친 뒤에만 고른다.
   - urgent → 바로 반영 / normal → NORMAL_MODE(SAMPLE 이면 `status: "proposed"` 로 기록만, 14일 잠금)
5. 할 일이 없으면 STEP 10.

---

## STEP 7 — 원인 분류와 수정안

[7-1] 우리 글 현재 값 (REST)
```bash
curl -s -u "$U:$P" "https://koreaplug.com/wp-json/wp/v2/posts?slug={slug}&context=edit&_fields=id,date,meta,content"
```
- `meta.rank_math_title` · `meta.rank_math_description` · `meta.rank_math_focus_keyword`(변경 금지)
- **도입 첫 문단 = `<p><!-- INTRO --></p>` 바로 다음 `<p>…</p>`**. 마커가 없으면 `style` 속성이 없고 텍스트 80자 이상인 첫 `<p>`. 히어로 블록 안의 `<h1>`·"Last updated" 줄은 건드리지 않는다(2026-09-24 실측).
- 검색어 표(STEP 5-2 에서 읽은 것): MAIN_QUERY 와 그 순위·CTR.

[7-2] 원인 분류
| 분류 | 판단 근거 | 처방 |
|---|---|---|
| A 제목·메타 약함 | 순위 4~10위인데 CTR 이 낮다 | 제목·메타·첫 문단 |
| B 검색의도 불일치 | MAIN_QUERY 가 묻는 것(가부·방법·비용·목록)과 제목 앞부분이 다르다 | 제목 앞부분을 질문에 대한 답 형태로, 첫 문단에서 답을 먼저 |
| C 순위·영역 문제 | 평균 순위 11위 밖, 또는 상위 8이 Reddit·정부·대형 매체로 채워짐 | 제목·메타는 고치되 "제목만으로 한계" 기록 |
| E4 AIO 선점 | 5-2 에서 yes | 고치지 않는다(제외) |

[7-3] 작성 규칙 (영문 — 기준은 `KoreaPlug-Draft.md` 5-3·5-6)
- **rank_math_title**: MAIN_QUERY 원문(또는 Focus Keyword)을 맨 앞에. **60자 이하**. 질문형 검색어면 제목이 답의 방향을 보여 준다(예: `Can You Vape in Korea? Yes — But You Can't Buy Liquid`). 본문에 있는 구체값(금액·연도·장소) 1개. 상위 8 제목과 겹치지 않는 우리 글만의 각도. 낚시·과장 금지.
- **rank_math_description**: **150자 이하**, Focus Keyword 포함, 첫 문장에 답. 
- **도입 첫 문단**: 첫 문장에 Focus Keyword 와 답. 길이 기존 ±30%, 문체 유지. `&#8217;` 같은 엔티티는 기존 표기 그대로.
- ⛔ 금지: 본문에 없는 사실 / 키워드 반복 / 슬러그·H1·H2·Focus Keyword 변경 / 첫 문단 외 본문 수정.
- 재수정(v2·v3)은 `state.json` 의 이전 버전과 **다른 각도**로 쓰고, 판정 수치를 `note` 에 남긴다.

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
 "keyword":"{MAIN_QUERY}","ctr_before":{28일 CTR},"impr_before":{28일 노출},"pos_before":{순위},"published":"{발행일}","cause":"A|B|C",
 "before":{"title":"...","desc":"...","first_p":"backups/{파일명}"},
 "after":{"title":"...","desc":"...","first_p":"..."},
 "note":"상위8 구성·AIO·재수정 근거 한 줄"}
J
cd $W && python3 gsc_engine.py record --file /tmp/v.json
```
반영에 실패해 원복했으면 기록하지 않는다.

[9-2] `log.md` 맨 위에 추가 — 0and1life 루틴 9-2 와 같은 형식(선정 근거 / MAIN_QUERY / 구글 상위8·우리 순위·AIO / 원인 / 전·후 표 / 검증).

---

## STEP 10 — 완료 알림 (앞 단계 성공 여부와 무관하게 반드시 실행)

```
🔎 KoreaPlug 구글 CTR 루틴 {TODAY}
- 데이터: 28일 {START28}~{LATEST} · 페이지 {n} · 클릭 {n} / 노출 {n} · 목표 CTR {x}%
- 효과 판정: {slug v1 — KEEP 1.39%→2.2% (반영 후 노출 +900 · 클릭 +20, 9/25~10/8)} / {slug — WAIT 노출 420/800 · 클릭 6/8 · 4/14일} …
- 오늘 작업: {재수정·되돌림·새 반영·제안} — {slug} — {원인}
  제목: {전} → {후}
- 대기열 다음 3편: {slug(놓친 클릭 n · 순위 x · AIO yes/no)} …
- 제외: 내년용 {n} · AIO 선점 {n}
- ⚠️ 조치 필요: {GSC 로그인 · 구글 캡차 · 스니펫 4183 · LIMIT 글 본문 보강}
```

---

## 효과 판정 규칙 (gsc_engine.py `evaluate`, 참고용 — 수치는 CFG)

- 반영 후 데이터 = 서치콘솔에서 **반영 다음날 ~ LATEST** 범위를 페이지 필터로 직접 읽은 값(네이버와 달리 누적 차감이 아니라 정확한 구간값).
- 판정 시점: 긴급 = 노출 +400 이상 **그리고** 클릭 +5 이상(데이터 4일 지나면 쌓인 만큼) / 상시 = 노출 +800 **그리고** 클릭 +8(데이터 14일 지나면 쌓인 만큼). 그 전에는 WAIT 로 `노출 n/기준 · 클릭 n/기준 · 데이터 일수` 보고.
- KEEP: 반영 후 CTR ≥ max(이전×1.3, 이전+0.5%p) 또는 ≥ 2.5% → 14일 보호(HOLD) 후 재후보.
- REEDIT: 기준 미달 → 재수정. v3 까지 개선 없으면 LIMIT → 30일 닫음.
- ROLLBACK: 반영 후 CTR < 이전×0.7 → 되돌림.
- AIO 확인 결과는 30일 캐시. 이벤트가 지난 글(E3)은 더 고치지 않는다.

## 오류 처리 요약

| 상황 | 처리 |
|---|---|
| Claude 폴더 미연결 | bash 확인 → 실패 시에만 폴더 요청 1회 → 실패면 STEP 10 |
| GSC 화면 로그인 풀림·행 0 | 판정·수정 건너뜀, STEP 10에 `GSC 읽기 실패` |
| 구글 검색 캡차 | 그 회차 AIO 확인 중단, 해당 글 `미확인` 유지 |
| pw.txt 키 누락·WP 인증 실패 | 반영만 건너뜀(판정·수정안은 진행) |
| 스니펫 4183 미작동(meta 에 rank_math 키 없음) | 제목·메타 반영 중단, 첫 문단은 원복, 엔진 기록 안 함 |
| 07:42 초과 | 반영하지 않고 수정안만 log.md |
| 첫 문단 반영 후 불일치 | 백업 raw 로 원복, 기록 |
| 구글 API 접근 | 시도 금지(네트워크 정책 403 확인됨) |
