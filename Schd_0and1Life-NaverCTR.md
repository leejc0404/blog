# Schd_0and1Life-NaverCTR — 네이버 "노출 많고 CTR 낮은 글" 개선 루틴 (Cowork 예약 작업용)

*매일 06:30 KST 실행. 예약 시각이 되면 같은 날 이미 실행됐더라도 다시 진행한다(판정·잠금은 `state.json` 이 막아 주므로 같은 글을 두 번 고치지 않는다).

날짜: 실행 시점의 실제 KST 날짜를 쓴다. 이 프롬프트에 적힌 고정 날짜는 무시한다.

이 루틴이 하는 일:
1. 서치어드바이저 TOP30 CSV를 읽는다(크롬 확장 `C:\Users\win\Documents\Claude\naver-advisor-export` v1.2.0이 매일 06:00에 백그라운드 탭으로 자동 수집해 `다운로드\네이버_수집\naver_search_report_full_30_{KST 날짜}.csv` 로 저장)
2. **이미 고친 글의 효과를 매일 판정**한다 → 개선이면 유지, 개선이 없으면 재수정, 나빠졌으면 되돌림
3. 새 대상 1편을 고른다 → **시기성 글(긴급)은 그날 바로 수정**, 상시 글은 NORMAL_MODE에 따른다
4. 모든 수정은 버전(v1·v2·v3)으로 기록해 다음 날 같은 글을 다시 고치지 않는다

작업 폴더: `C:\Users\win\Documents\Claude\naver-ctr\` (blog 저장소 밖 — 데이터는 커밋되지 않는다)
- `ctr_engine.py` — 계산 엔진(수집·선정·잠금·효과 판정·기록). **판단이 필요 없는 계산은 전부 이 스크립트가 한다.** 루틴은 결과(JSON)를 읽고 문구 작성과 WP 반영만 한다
- `state.json` — 키워드→글 연결, 이벤트 날짜, 글별 버전 이력(잠금의 유일한 근거)
- `snapshots/{날짜}.json` — 날짜별 TOP30 · `backups/` — 수정 전 원본 · `log.md` — 사람이 읽는 기록 · `inbox/` — 수동으로 넣은 CSV

⚠️ [무인 실행 원칙 — 최우선]
사람이 없는 시간에 실행된다. 승인이 필요한 도구 호출은 "그것 없이는 진행할 수 없음을 실측으로 확인한 뒤"에만 한다. 승인 창이 응답 없이 닫히면 재시도하지 않고 오류로 기록한 뒤 STEP 10으로 간다.

⚠️ [시간 제한]
06:51에 `0and1life-auto-image-insert` 가 같은 Chrome에서 에디터를 연다. **06:48까지 끝낸다.** 06:45가 지났는데 STEP 8에 들어가지 못했으면 반영하지 않고 수정안만 `log.md` 에 남긴다(기록하지 않았으므로 다음 날 다시 1순위로 뽑힌다).

⚠️ [에디터·REST 충돌 규약 — Schd_0and1Life-Draft.md [6m-0]과 같다]
에디터 탭이 열려 있는 동안에는 REST로 본문을 쓰지 않는다. 본문 REST 수정은 ① post.php 탭이 없는지 확인 → ② REST POST → ③ 8초 후 재조회 검증 순서를 지킨다.

⚠️ 삭제 금지: 글·리비전·파일·Notion 행을 삭제하지 않는다. 필요하면 STEP 10에 "삭제 필요 — 사용자 확인"으로만 남긴다.
⚠️ 변경 금지 항목: 글의 status(publish/draft/private)·**슬러그(URL)**·Focus Keyword·카테고리·발행일·H2·첫 문단 외 본문.
⚠️ git commit·push 하지 않는다 — 사용자가 직접 한다.
⛔ searchadvisor.naver.com · search.naver.com · datalab.naver.com 은 Claude in Chrome과 내장 브라우저 모두에서 "안전 제한"으로 막혀 있다(2026-09-24 실측). **열려고 시도하지 않는다.** 데이터는 CSV로만 받는다.

---

## STEP 0 — 설정값 (사용자만 수정)

```
URGENT_MODE  = AUTO      # 시기성 긴급 글(이벤트 3~14일 남음): 그날 바로 반영
NORMAL_MODE  = SAMPLE    # 상시 글: SAMPLE = 수정안만 기록 / AUTO = 바로 반영
REEDIT_MODE  = AUTO      # 효과 판정이 "개선 없음"이면 재수정(반영했던 글만 대상)
NEW_PER_DAY  = 1         # 하루 새로 고치는 글 수(상위부터)
REEDIT_PER_DAY = 1       # 하루 재수정·되돌림 글 수
```
판정 기준값(노출 하한 300, 목표 CTR, 긴급 창 14일, 효과 판정 노출·클릭 기준, 재수정 한도 3차 등)은 `ctr_engine.py` 상단 `CFG` 에 있다. 바꿀 때는 그 파일만 고친다.

---

## STEP 1 — 날짜와 폴더

1) TODAY(KST)를 기록한다.
2) bash로 마운트를 찾는다. `request_cowork_directory` 는 아래가 실패했을 때만 1회.
```bash
CLAUDE_DIR=$(ls -d /sessions/*/mnt/Claude 2>/dev/null | head -1)      # pw.txt, naver-ctr
NAVER_IN=$(ls -d /sessions/*/mnt/네이버_수집 2>/dev/null | head -1)      # 다운로드\네이버_수집
W=$CLAUDE_DIR/naver-ctr
echo "claude=$CLAUDE_DIR naver_in=${NAVER_IN:-없음}"; ls $W/ctr_engine.py
```
- CLAUDE_DIR이 없으면 `request_cowork_directory { path: "C:\Users\win\Documents\Claude" }` 1회 → 실패 시 STEP 10.
- NAVER_IN이 없으면 `request_cowork_directory { path: "C:\Users\win\Downloads\네이버_수집" }` 1회 → 실패해도 계속(기존 inbox만 읽는다).
- ⚠️ bash는 매 호출이 새 셸이다. 위 세 줄(CLAUDE_DIR·NAVER_IN·W)을 이후 bash 호출마다 맨 앞에 다시 넣는다.

---

## STEP 2 — 자격증명 확인 (값은 절대 출력하지 않는다)

pw.txt는 BOM이 있고 앱 비밀번호에 공백이 있다. `set -a; . pw.txt` 로 읽지 않는다.
```bash
cd $CLAUDE_DIR
get(){ grep "^$1=" pw.txt | head -1 | cut -d'=' -f2- | tr -d '\r\n' | sed 's/^\xEF\xBB\xBF//; s/^ *//; s/ *$//'; }
U=$(get ONEANDZERO_WP_USER); P=$(get ONEANDZERO_WP_APP_PASSWORD); NKID=$(get NAVER_APIGW_KEY_ID); NKEY=$(get NAVER_APIGW_KEY)
for k in U P NKID NKEY; do [ -n "${!k}" ] && echo "$k=있음" || echo "$k=없음"; done
curl -s -o /dev/null -w "WP %{http_code}\n" -u "$U:$P" "https://0and1life.com/wp-json/wp/v2/users/me?context=edit"
```
- 하나라도 "없음" → STEP 10에 `pw.txt에 {키 이름} 없음` 을 적고 종료.
- WP가 200이 아니면 → Schd_0and1Life-Draft.md [3-2] nonce 폴백. 그것도 실패하면 반영 단계만 건너뛰고(판정·수정안은 진행) STEP 10에 기록.
- 이후 REST·릴레이 호출마다 `get` 함수와 변수 줄을 같은 명령 안에 다시 넣는다.

---

## STEP 3 — CSV 읽기

```bash
cd $W && python3 ctr_engine.py ingest ${NAVER_IN:+"$NAVER_IN"}
```
- `inbox/` 와 `네이버_수집` 의 CSV 중 **처음 보는 파일만** `snapshots/{파일명의 날짜}.json` 으로 저장한다(이미 처리한 파일은 건너뛴다).
- CSV 형식: 확장 프로그램 "서치어드바이저 TOP30 내보내기" 출력(`--- 검색 키워드 TOP 30 ---` / `--- 검색 웹문서 TOP 30 ---` 두 표). 요약 행은 단위가 잘려 있어("7.4" = 7.4백) **쓰지 않는다.** 합계는 엔진이 TOP30에서 직접 계산한다.
- 결과에 `error` 가 있으면 STEP 10에 파일명과 함께 기록.

---

## STEP 4 — 오늘 계획 받기

```bash
cd $W && python3 ctr_engine.py plan --today {TODAY}
```
출력 JSON에서 읽을 것:
| 키 | 뜻 |
|---|---|
| `stale_days` | 최신 스냅샷이 며칠 전 것인지. **0이 정상**(06:00 자동 수집분). **1 이상이면 오늘 CSV가 없는 것** → 효과 판정·재수정·새 수정을 모두 건너뛰고(어제 데이터로 같은 판단을 반복하지 않는다) STEP 10에 `CSV 미수집 — 확장 팝업의 오류 메시지 확인(로그인 풀림·크롬 꺼짐)` 기록 |
| `evaluations[]` | 반영한 글의 효과 판정. verdict = KEEP(개선) / HOLD(개선 후 보호 기간) / WAIT(데이터 대기) / REEDIT(개선 없음) / ROLLBACK(악화) / LIMIT(3차까지 개선 없음) / NO_DATA(TOP30 밖) |
| `reedit[]`, `rollback[]` | 오늘 재수정·되돌림할 글 |
| `queue[]` | 새 대상 후보(이미 우선순위 정렬됨). `track`=urgent/normal, `days_left`, `lost_clicks`(놓친 클릭), `main_kw` |
| `excluded[]` | E3 내년용(이벤트 종료·2일 이내) / E4 네이버 즉답(키워드 CTR 0.3% 미만) |
| `need_event_date[]` | 이벤트 날짜를 아직 모르는 글 |
| `unmapped_keywords[]` | 어느 글과 연결할지 모르는 키워드 |

[4-1] `unmapped_keywords` 가 있으면: WP_CORPUS(`GET /wp-json/wp/v2/posts?status=publish&per_page=100&_fields=id,slug,title` 끝 페이지까지)의 제목·슬러그와 의미로 대조해 한 편을 고른다. 없으면 none.
```bash
python3 ctr_engine.py set-map "키워드" 슬러그        # 또는 none
```
[4-2] `need_event_date` 가 있으면: 그 글 본문(REST `content.rendered`)에서 독자 행동을 막는 날짜(납부·신청 마감, 사전예약 마감, 시행일, 출시일, 명절 당일)를 찾는다. 여러 개면 **아직 지나지 않은 가장 이른 마감**을 쓴다. 날짜가 없거나 상시 정보면 none. 추정하지 않는다.
```bash
python3 ctr_engine.py set-event 슬러그 2026-09-30   # 또는 none
```
[4-3] 4-1·4-2에서 하나라도 설정했으면 `plan` 을 다시 실행해 최종 계획을 받는다(연결·날짜는 캐시되므로 다음 날부터는 새 글·새 키워드만 묻는다).

---

## STEP 5 — 오늘 할 일 정하기 (이 순서, 이 한도)

1. **되돌림** `rollback[]` — REEDIT_PER_DAY 한도 안에서 가장 먼저. 백업의 직전 버전 값(제목·메타·첫 문단)으로 되돌리고 `status: "rollback"` 으로 기록. 되돌린 글은 다음 날 새 수정 후보로 돌아온다.
2. **재수정** `reedit[]` — REEDIT_MODE=AUTO면 남은 한도 안에서 1편. 긴급 트랙 글 우선.
3. **LIMIT** 글 — 고치지 않는다. `python3 ctr_engine.py close 슬러그 "3차까지 개선 없음 — 제목·메타로 한계"` 로 30일 닫고, STEP 10에 "본문 보강 또는 각도 재타겟 신규 글 후보"로 올린다.
4. **새 대상** `queue[]` 맨 위부터 NEW_PER_DAY 편.
   - `track=urgent` → URGENT_MODE(AUTO)로 **그날 바로 반영**
   - `track=normal` → NORMAL_MODE(SAMPLE이면 수정안만 기록, `status: "proposed"` → 14일 동안 다시 제안하지 않음)
5. 할 일이 없으면 STEP 10으로.

⚠️ 같은 글이 되돌림·재수정·새 대상에 동시에 걸릴 수 없다(엔진이 잠금으로 막는다). 엔진 출력에 없는 글은 손대지 않는다.

---

## STEP 6 — 네이버 상위 글 조사 (사이트 릴레이)

대상 글의 `main_kw` (+ 노출 2위 연결 키워드가 있으면 그것까지)로 `webkr`·`blog` 조회. 최대 4회, 0.5초 간격.
```bash
curl -s --max-time 20 -u "$U:$P" -H "X-O1-NKID: $NKID" -H "X-O1-NKEY: $NKEY" \
  -G "https://0and1life.com/wp-json/o1/v1/naver-check" \
  --data-urlencode "q={키워드}" -d "type=webkr" -d "display=10"
# 파라미터 이름은 q (query로 보내면 400). type=blog 로 한 번 더.
```
기록: WT/BT(total) · 상위10 제목·요약·도메인 · 우리 글 포함 여부와 순위 · 구성(개인 블로그·카페 n / 기관·카드사·언론 n).
- 실패(401·5xx·타임아웃·HTML) → 1회 재시도 → 그래도 실패면 `네이버 경쟁도 미검증` 으로 두고 우리 글만 보고 진행. STOP 아님.
- 통합검색 순위·검색량을 지식으로 추정해 적지 않는다.

---

## STEP 7 — 원인 분류와 수정안

[7-1] 우리 글 현재 값
- REST `GET /wp-json/wp/v2/posts/{id}?context=edit` → `content.raw`
- **도입 첫 문단 = `style` 속성이 없는 첫 `<p>`**. 맨 위의 `<p style=...>2026년 9월 1일 작성 · 읽는 시간…</p>` 는 메타 줄이므로 건드리지 않는다(2026-09-24 실측).
- 현재 SEO 제목·메타: 공개 페이지 `<title>`·`<meta name="description">` (반영할 때는 STEP 8-3에서 에디터 값으로 다시 확인).

[7-2] 원인 분류
| 분류 | 판단 근거 | 처방 |
|---|---|---|
| A 제목·메타 약함 | 우리 글이 webkr 상위10 안인데 CTR이 낮다 | 제목·메타·첫 문단 |
| B 검색의도 불일치 | 키워드가 묻는 것(날짜·금액·방법·목록)과 제목 앞부분 각도가 다르다 | 제목 앞부분을 키워드 의도에 맞추고 첫 문단에서 답을 먼저 |
| C 노출 영역 문제 | 상위10 밖이거나 기관·카드사·언론이 채우고 있다 | 제목·메타는 고치되 "제목만으로 한계" 기록. 본문 보강 필요 사항을 STEP 10에 적는다 |

[7-3] 작성 규칙
- **SEO 제목**: 대표 키워드 원문을 맨 앞에 그대로. 25~45자. 본문에 있는 구체값(마감일·금액·수치) 1~2개. 시기성 글은 마감일을 제목에 넣는다(예: `9/30 마감 전`). 상위10 제목과 겹치지 않는 우리 글만의 정보를 드러낸다. 부정형 훅("~해도 0원")을 앞에 두지 않는다.
- **메타 설명**: 110~155자. 첫 문장에 대표 키워드 + 마감/핵심 답. `keywordInMetaDescription` 유지.
- **도입 첫 문단**: 첫 문장에 `<strong>{Focus Keyword}</strong>` 와 결론(날짜·금액·조건). 길이는 기존 ±30%. 문체(~요/~습니다 혼용)는 기존 글과 같게. 본문 뒤쪽 꼭지를 안내할 때는 실제 H2 순서를 확인하고 쓴다.
- ⛔ 금지: 본문에 없는 사실·수치 / 과장·낚시 / 키워드 반복 / 슬러그·H2·Focus Keyword 변경 / 첫 문단 외 본문 수정.

[7-4] 재수정(v2·v3) 규칙
- `state.json` 의 이전 버전(before/after)을 읽고, **이전 버전과 다른 각도**로 쓴다. 같은 문장 순서만 바꾸는 수정은 금지.
- v1이 A·B 처방이었다면 v2는 상위10에서 클릭을 받는 제목 유형(목록형·마감형·계산형 중 우리 본문이 뒷받침하는 것)으로 바꾼다.
- 재수정은 판정 결과(`ctr_before → ctr_after`, 반영 후 노출)를 근거로 `note` 에 한 줄 적는다.

---

## STEP 8 — 반영 (반영 모드일 때만. SAMPLE이면 STEP 9로)

[8-1] 백업 — `backups/{slug}-{TODAY}-v{n-1}.json` 에 REST `context=edit` 응답(title·content·modified)을 저장한다. 저장 실패면 반영하지 않는다.

[8-2] 첫 문단 교체 (REST, 에디터 탭 없음)
1) Chrome MCP 탭 중 `post.php` 가 있으면 `https://0and1life.com/` 로 이동(about:blank는 이동 불가 — 2026-09-24 실측).
2) python으로 `content.raw` 의 **style 없는 첫 `<p>…</p>`** 하나만 새 문단으로 바꿔 `POST /wp-json/wp/v2/posts/{id}` `{"content": ...}`. 원래 문단에 기대한 문구가 있는지 assert 후 교체한다.
3) 8초 후 재조회: `status=publish` 유지 · `<p` 개수 백업과 같음 · 새 문장 포함 · 옛 문장 없음. 하나라도 어긋나면 백업 raw로 즉시 되돌리고 `첫 문단 반영 실패 — 원복` 기록, 8-3은 건너뛴다.

[8-3] SEO 제목·메타 (Claude in Chrome 에디터)
navigate `https://0and1life.com/wp-admin/post.php?post={id}&action=edit` 후:
```javascript
await new Promise(r=>setTimeout(r,3000));
if (!document.body?.classList.contains('wp-admin')) throw new Error('not-logged-in');
if (!wp.data.select('rank-math')) { await new Promise(r => setTimeout(r, 3000)); }
const s = wp.data.select('rank-math'), ed = wp.data.select('core/editor');
// ① 현재 값 확인 — before 로 기록, 에디터 본문에 8-2 새 문장이 들어왔는지 확인
({ title: s.getSerpTitle(), desc: s.getSerpDescription(),
   p: (ed.getEditedPostContent().match(/<p/g)||[]).length, dirty: ed.isEditedPostDirty() })
```
```javascript
// ② 반영 — savePost 는 한 번만
const T='NEW_SEO_TITLE', M='NEW_META';
const rm = wp.data.dispatch('rank-math');
rm.updateTitle(T); rm.updateSerpTitle(T); rm.updateDescription(M); rm.updateSerpDescription(M);
await new Promise(r=>setTimeout(r,1500));
await wp.data.dispatch('core/editor').savePost();
await new Promise(r=>setTimeout(r,4000));
({ dirty: wp.data.select('core/editor').isEditedPostDirty(), title: s.getSerpTitle(), desc: s.getSerpDescription(), score: s.getAnalysisScore?.() })
```
- ①에서 `p` 가 REST 개수와 다르거나 새 문장이 없으면 저장하지 않는다(에디터가 구버전을 들고 있음) → 새로고침 1회 후 재확인, 그래도 다르면 중단·기록.
- ⛔ 재분석 트리거를 돌리지 않는다(Draft 루틴 [6j]).
- 저장 후 탭을 `https://0and1life.com/` 로 옮긴다.

[8-4] 검증
- REST 재조회: `status=publish` · `<p` 개수 유지 · ld+json 유지. `<p` 가 줄었으면 백업 raw로 원복하고 `저장 중 <p> 소실 — 원복` 기록.
- 공개 페이지 `?nc={epoch}` 로 `<title>`·`<meta name="description">`·`canonical` 확인. 캐시로 다르면 `캐시 반영 대기` 로만 기록.

---

## STEP 9 — 기록

[9-1] 엔진에 기록 (잠금의 유일한 근거 — 반드시 실행)
```bash
cat > /tmp/v.json <<'J'
{"slug":"...","status":"applied|proposed|rollback","track":"urgent|normal","date":"{TODAY}",
 "keyword":"{main_kw}","ctr_before":{판정 시점 CTR},"impr_before":{노출},"published":"{발행일}","cause":"A|B|C",
 "before":{"title":"...","desc":"...","first_p":"backups/{파일명}"},
 "after":{"title":"...","desc":"...","first_p":"..."},
 "note":"상위10 구성·재수정 근거 한 줄"}
J
cd $W && python3 ctr_engine.py record --file /tmp/v.json
```
- `snapshot` 은 비워 두면 최신 스냅샷이 들어간다. 효과 판정은 이 스냅샷 이후 증가분으로 계산된다.
- 반영에 실패해 원복했으면 기록하지 않는다(다음 날 다시 뽑힌다).

[9-2] `log.md` 맨 위에 추가
```
## {TODAY} · {v1 반영 | v2 재수정 | 되돌림 | 제안(SAMPLE)} · {slug}
- 선정: {긴급 D-n | 놓친 클릭 n} / 노출 {n} · CTR {x}% (목표 {target}%)
- 대표 키워드: {kw} (노출 {n} · CTR {x}%)
- 네이버: WT {n} / BT {n} / 우리 글 webkr {순위|밖} / 상위10 {구성}
- 원인: {A|B|C} — {근거}
| 항목 | 전 | 후 |
|---|---|---|
| SEO 제목 | … | … |
| 메타 설명 | … | … |
| 첫 문단 | (백업 파일) | … |
- 검증: REST p {n}→{n} · 공개 title {일치|캐시 대기} · Rank Math {점수}
```

---

## STEP 10 — 완료 알림 (앞 단계 성공 여부와 무관하게 반드시 실행)

```
🔎 네이버 CTR 루틴 {TODAY}
- 데이터: {스냅샷 날짜} (stale {n}일) · TOP30 클릭 {n} / 노출 {n} · 목표 CTR {x}%
- 효과 판정: {slug v1 — KEEP CTR 0.83%→1.5% (반영 후 노출 +535 · 클릭 +8)} / {slug — WAIT 노출 335/400 · 클릭 3/5 · 1/4일} …
  ※ CTR과 함께 **반영 후 클릭 수**를 반드시 적는다(검색량 변화로 클릭이 늘어난 것과 구분하기 위해)
- 오늘 작업: {재수정·되돌림·새 반영·제안} — {slug} — {원인}
  제목: {전} → {후}
- 대기열 다음 3편: {slug(긴급 D-n | 놓친 클릭 n)} …
- 제외: 내년용 {n} · 네이버 즉답 {n}
- ⚠️ 조치 필요: {CSV 미수집 · pw.txt · 로그인 · LIMIT 글 본문 보강 · 우리 글 없는 키워드}
```

---

## 효과 판정 규칙 (ctr_engine.py `evaluate`, 참고용 — 수치는 CFG)

- 반영 후 데이터 = **오늘 스냅샷 − 반영 당일 스냅샷**(노출·클릭 증가분). 서치어드바이저 조회 기간(WINDOW_DAYS=30) 안에 발행된 글은 정확하고, 그보다 오래된 글은 누적 CTR 비교로 근사한다(출력에 `method` 로 표시).
- 판정 시점(2026-09-24 개정 — 노출 150에서는 클릭 1~2번 차이로 결과가 뒤집혀 운에 가까웠다):
  - 긴급 = 반영 후 **노출 +400 이상 그리고 클릭 +5 이상**. 4일이 지나면 쌓인 만큼으로 판정
  - 상시 = 반영 후 **노출 +800 이상 그리고 클릭 +8 이상**. 14일이 지나면 쌓인 만큼으로 판정
  - 판정 전에는 WAIT로 두고 `노출 n/기준 · 클릭 n/기준 · 경과일/기한` 을 보고한다
- KEEP: 반영 후 CTR ≥ max(이전×1.3, 이전+0.5%p) 또는 ≥ 목표 CTR → 14일 보호(HOLD), 그 뒤 목표 미달이면 다시 후보.
- REEDIT: 기준 미달 → 재수정(버전 +1). 3차(v3)까지 개선이 없으면 LIMIT → 30일 닫음.
- ROLLBACK: 반영 후 CTR < 이전×0.7 → 직전 값으로 되돌림.
- 이벤트가 지난 글(E3)은 판정 결과와 무관하게 더 고치지 않는다.

## 색인 영향 메모

제목·메타·첫 문단만 바꾸고 **URL(슬러그)·canonical·본문 구조는 유지**하므로 네이버·구글은 같은 문서의 갱신으로 처리한다(수정일 갱신 → 재수집). 오류가 되는 경우는 URL 변경, 본문 대량 교체, 짧은 간격의 반복 변경인데, 이 루틴은 URL을 바꾸지 않고 재수정 간격(긴급 노출 +400·클릭 +5 또는 4일, 상시 노출 +800·클릭 +8 또는 14일)과 3차 한도로 반복 변경을 막는다.

---

## 오류 처리 요약

| 상황 | 처리 |
|---|---|
| Claude 폴더 미연결 | bash 확인 → 실패 시에만 폴더 요청 1회 → 실패면 STEP 10 |
| 네이버_수집 폴더 미연결 | 요청 1회 → 실패해도 inbox만으로 진행 |
| 새 CSV 없음(stale ≥ 1) | 판정·수정 건너뜀, STEP 10에 `CSV 미수집` |
| pw.txt 키 누락 | 키 이름만 적고 종료(값 출력 금지) |
| 릴레이 실패 | 1회 재시도 → `네이버 경쟁도 미검증` 으로 계속 |
| 06:45 초과 | 반영하지 않고 수정안만 log.md, 엔진 기록 안 함 |
| 첫 문단 반영 후 불일치 | 백업 raw로 원복, 제목·메타 반영 안 함, 엔진 기록 안 함 |
| 에디터가 구버전 본문 보유 | 저장하지 않음 → 새로고침 1회 → 실패 시 중단·기록 |
| 저장 후 `<p>` 소실 | 백업 raw로 원복, 기록 |
| 서치어드바이저·네이버 검색 접근 | 시도 금지(안전 제한 확인됨) |
