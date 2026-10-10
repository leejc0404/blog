# Schd_0and1Life-Revenue — 0and1Life 수익 루틴 (네이버 쇼핑커넥트 · 수익 레이더) — Cowork 예약 작업용 v1.0 (2026-10-10)

*매일 06:40 KST 실행. 예약 시각이 되면 같은 날 이미 실행됐더라도 다시 진행한다(글별 상태는 `0and1life-revenue\state.json` 이 막아 주므로 같은 글에 블록을 두 번 넣지 않는다).

날짜: 실행 시점의 실제 KST 날짜를 쓴다. 이 프롬프트에 적힌 고정 날짜는 무시한다.

> **이 루틴이 `Schd_0and1Life-NaverCTR`(네이버 CTR 개선)을 대체한다 — 2026-10-10 사용자 지시.**
> 근거(09-24~10-09 실측): CTR 수정 10편 가운데 클릭이 늘어난 글은 재산세 1편(+66회)뿐이고 나머지는 합쳐서 ±0, 10/3 이후 8일 동안은 고칠 글 자체가 0편이었다. 같은 기간 클릭은 대부분 **검색 최고점 전에 새로 쓴 글**(아이폰 패닉풀·예초기 대여·추석 택배·재산세)에서 나왔고, 그중 다수가 **물건 구매로 이어지는 주제**였다. 사이트 클릭은 하루 40회 안팎이라 CTR을 0.5%p 올려도 하루 몇 클릭이다.
> 그래서 이 루틴의 목적은 **"이미 들어오는 독자 1명당 수익을 올리고(쇼핑커넥트), 앞으로 돈이 되는 주제를 미리 찾는 것(수익 레이더)"** 이다. 제목·메타 다듬기(CTR 수정)는 하지 않는다.

이 루틴이 하는 일:
1. **기존 글 수익화** — 클릭이 들어오는 글 중 물건과 연결되는 글을 골라 네이버 쇼핑커넥트 상품을 찾고(확장 `connect_search`), 전용 링크를 발급받아(확장 `connect_links`) 글에 **상품 블록**을 넣는다.
2. **수익 레이더** — 검색 최고점 2~6주 전이면서 물건과 연결되는 키워드를 찾아 Notion 키워드 백로그에 `💰수익 레이더` 출처로 올린다. 글은 Writer 루틴이 쓴다(작성 지침 0-10).
3. **주간 수익 리포트**(월요일) — 글별 유입과 상품 블록 현황, 쇼핑커넥트 실적(사용자가 넣어 준 파일이 있으면)을 한 표로 보고한다.

⚠️ **역할 경계 — 이 루틴은 도구다.** 어떤 글이 물건과 연결되는지(구매 연결 등급), 상품을 고르는 기준, 상품 블록의 위치·문구·고지 문구의 **기준(SSOT)은 작성 지침 `0and1Life-Writer.md` 0-10·2-10** 이다. 이 루틴은 운영 절차와 실행 자산만 정의하고 조항 번호로 참조한다. 상충이 보이면 지침을 따르고 STEP 10에 기록한다.
- 지침 출처: `C:\Users\win\Documents\Claude\blog\0and1Life-Writer.md`(PC 셸로 읽는다 — 사용자가 커밋하기 전의 최신본이 여기 있다). 읽지 못하면 STEP 4(회수)와 STEP 9·10만 하고 반영·새 슬롯은 하지 않는다.

---

## 실행 자산 (경로·도구)

| 무엇 | 어디 | 비고 |
|---|---|---|
| 작업 폴더 | `C:\Users\win\Documents\Claude\0and1life-revenue\` (PC 셸 `$HOME/mnt/Claude/0and1life-revenue`) | blog 저장소 밖 — 커밋되지 않는다. ⛔ `revenue\`·`koreaplug-revenue\`(KoreaPlug 수익 루틴 폴더)는 쓰지 않는다 — 2026-10-10 두 루틴이 같은 폴더를 써서 상태 파일이 덮인 사고 |
| 글별 상태 | `0and1life-revenue\state.json` | `{"posts": {slug: {...}}, "radar": {키워드: {...}}, "weekly_last": "YYYY-MM-DD"}` — **같은 글에 두 번 넣지 않는 유일한 근거** |
| 기록 | `0and1life-revenue\log.md`(사람이 읽는 기록, 맨 위에 추가) · `0and1life-revenue\backups\{slug}-{날짜}.json`(반영 전 원본) · `0and1life-revenue\weekly\{날짜}.md` · `0and1life-revenue\inbox\`(사용자가 넣는 쇼핑커넥트 실적 파일) | |
| 유입 데이터 | `naver-ctr\ctr_engine.py ingest` → `naver-ctr\snapshots\{날짜}.json` | 서치어드바이저 TOP30 CSV(확장 `naver-advisor-export`가 06:00 수집). CTR 판정·plan 기능은 쓰지 않는다 |
| 수요 조회 | `naver-ctr\naver_volume.py`(월간 검색수·연관어) · `naver-ctr\naver_trend.py`(검색어트렌드) | 사이트 릴레이 경유 |
| 상위 글 조사 | 사이트 릴레이 `o1/v1/naver-check`(스니펫 1692) | `q`·`type=webkr|blog`·`display` |
| **쇼핑커넥트 수집·링크 발급** | AIPick 확장 큐 `C:\Users\win\Documents\Claude\naver_blog\tasks\pending\` | 확장이 1분마다 읽어 실행하고 결과를 `naver_blog\inbox\{inbox}\connect.json`·`links.json` 에 쓴 뒤 작업 파일을 `tasks\done\` 으로 옮긴다(AIPick 루틴과 같은 큐 — 한 번에 하나씩 순서대로 처리) |
| 쇼핑 인기검색어 | `naver_blog\radar\{RUN}_rank.json`·`_rank.md`(AIPick 월·목 회차가 만든 것 — 있으면 읽기만) | 레이더 보조 신호 |
| 키워드 백로그 | Notion `3a9bfe4a2ae181e08fc9dc8e035388af` | 레이더 결과를 행으로 추가(맨 위 = 최신) |
| 자격증명 | `C:\Users\win\Documents\Claude\pw.txt` | 값 출력 금지 |

**이 루틴의 작업 이름 접두어는 `REV_`** 다. 큐 작업 파일 `tasks\pending\REV_{RUN}_{n}_{connect|links}.json`, 결과 폴더 `naver_blog\inbox\REV_{RUN}_{n}_{slug 앞 20자}\`. AIPick 작업(`{RUN}_{n}_…`)과 섞이지 않게 한다. `RUN = YYYYMMDD`.

---

⚠️ [무인 실행 원칙 — 최우선]
사람이 없는 시간에 실행된다. 승인이 필요한 도구 호출은 "그것 없이는 진행할 수 없음을 실측으로 확인한 뒤"에만 한다. 폴더 접근 요청은 하지 않는다. 승인 창이 응답 없이 닫히면 재시도하지 않고 오류로 기록한 뒤 STEP 10으로 간다.

⚠️ [PC 시간대] 사용자 PC·크롬·큐 서버는 새벽에만 켜져 있고 08:00 전후 꺼진다. 확장 작업은 **넣어 두고 다음 회차에 회수하는 방식**이 기본이다(STEP 4). 같은 회차 대기는 `WAIT_MIN` 분까지만 한다. **07:40 KST가 지나면 새 작업을 넣지 않고 STEP 9·10으로 간다.**

⚠️ [에디터·REST 충돌 규약 — Schd_0and1Life-Draft.md [6m-0]과 같다] 이 루틴은 **에디터(post.php)를 열지 않고 REST로만** 본문을 고친다. 반영 직전에 글의 `modified` 를 다시 읽어 회수 시점과 다르면(다른 루틴·사용자가 방금 고침) 그 글은 반영하지 않고 다음 회차로 넘긴다.

⚠️ 삭제 금지: 글·리비전·파일·Notion 행·큐 작업 파일을 삭제하지 않는다. 필요하면 STEP 10에 "삭제 필요 — 사용자 확인"으로만 남긴다.
⚠️ 변경 금지(항상): 글의 status·**슬러그**·카테고리·발행일·제목·SEO 제목·메타 설명·Focus Keyword·기존 문단·기존 이미지·FAQ·ld+json. **이 루틴이 본문에 하는 일은 "상품 블록 삽입"과 "고지 한 줄 삽입" 두 가지뿐이다.**
⚠️ 사실: 상품명·가격·리뷰 수·평점은 **이번 회차에 회수한 `connect.json` 값만** 쓴다. 써 보지 않은 체험·효능·순위 단정은 쓰지 않는다(지침 2-10).
⚠️ git commit·push 하지 않는다 — 사용자가 직접 한다.
⛔ 루틴이 직접 네이버·브랜드커넥트·쇼핑 화면을 열거나 조작하지 않는다(전부 확장이 한다). searchadvisor.naver.com · search.naver.com · datalab.naver.com 은 브라우저에서 막혀 있다 — 열지 않는다.
⛔ openapi.naver.com · api.searchad.naver.com 직접 호출 금지 — 사이트 릴레이·`naver-ctr` 스크립트만 쓴다.

---

## STEP 0 — 설정값 (사용자만 수정)

```
APPLY_MODE      = AUTO   # 링크까지 준비된 글에 상품 블록 넣기: AUTO = 바로 반영 / SAMPLE = 블록 HTML만 0and1life-revenue\proposals\ 에 저장하고 알림
APPLY_PER_DAY   = 3      # 하루 반영 글 수
SLOT_NEW_PER_DAY = 2     # 하루 새로 상품 검색(connect_search)을 시작할 글 수
RADAR_PER_DAY   = 3      # 하루 백로그에 올리는 레이더 키워드 수(최대)
RADAR_WINDOW    = 14-45  # 작년 검색 최고점이 오늘+14~45일인 키워드만
WAIT_MIN        = 10     # 같은 회차 안에서 확장 결과를 기다리는 최대 분
TASK_STALE_DAYS = 3      # 큐에 넣은 작업이 이 일수 동안 done 이 안 되면 '확장 멈춤'으로 보고
REVISIT_DAYS    = 60     # 등급 C·보류 글을 다시 볼 때까지 일수
CUTOFF_KST      = 07:40  # 이 시각 이후 새 큐 작업 금지
```

---

## STEP 1 — 날짜·폴더

```bash
TODAY=$(TZ=Asia/Seoul date +%F); RUN=$(TZ=Asia/Seoul date +%Y%m%d); NOW=$(TZ=Asia/Seoul date +%H:%M)
B="$HOME/mnt/Claude"; R="$B/0and1life-revenue"; NB="$B/naver_blog"; W="$B/naver-ctr"; NAVER_IN=$(ls -d $HOME/mnt/네이버_수집 2>/dev/null | head -1)
ls "$B/pw.txt" "$B/blog/0and1Life-Writer.md" "$W/ctr_engine.py" "$W/naver_volume.py" "$W/naver_trend.py" >/dev/null || echo MISSING
mkdir -p "$R/backups" "$R/weekly" "$R/inbox" "$R/proposals"
[ -f "$R/state.json" ] || echo '{"posts":{},"radar":{},"weekly_last":""}' > "$R/state.json"
ls "$NB/tasks/pending" "$NB/tasks/done" >/dev/null 2>&1 && echo "queue=있음" || echo "queue=없음"
echo "$TODAY $NOW naver_in=${NAVER_IN:-없음}"
```
- PC 셸(`device_bash`)로 실행한다. 셸이 없거나 `MISSING` 이면 STEP 10에 사유를 적고 종료한다(이 루틴은 PC 파일·확장 큐가 핵심이라 클라우드 폴백을 하지 않는다).
- `queue=없음` 이면 STEP 4~6의 확장 관련 부분을 건너뛰고 STEP 7(레이더)·STEP 9·10만 한다.
- ⚠️ bash는 매 호출이 새 셸이다. 위 변수 줄을 bash 호출마다 맨 앞에 다시 넣는다.
- 작성 지침 `0and1Life-Writer.md` 의 **0-10·2-10** 을 읽는다(`sed -n '/^### 0-10/,/^### 0-11\|^---/p'`, `sed -n '/^### 2-10/,/^## Phase 3/p'`). 두 조항이 없으면 STEP 5·6을 건너뛰고 STEP 10에 `📐 지침 0-10·2-10 없음` 을 적는다.

## STEP 2 — 자격증명 (값은 절대 출력하지 않는다)

pw.txt는 BOM이 있고 앱 비밀번호에 공백이 있다. `set -a; . pw.txt` 로 읽지 않는다.
```bash
cd $B
get(){ grep "^$1=" pw.txt | head -1 | cut -d'=' -f2- | tr -d '\r\n' | sed 's/^\xEF\xBB\xBF//; s/^ *//; s/ *$//'; }
U=$(get ONEANDZERO_WP_USER); P=$(get ONEANDZERO_WP_APP_PASSWORD); NKID=$(get NAVER_APIGW_KEY_ID); NKEY=$(get NAVER_APIGW_KEY)
for k in U P NKID NKEY; do [ -n "${!k}" ] && echo "$k=있음" || echo "$k=없음"; done
curl -s -o /dev/null -w "WP %{http_code}\n" --max-time 20 -u "$U:$P" "https://0and1life.com/wp-json/wp/v2/users/me?context=edit"
```
- U·P 가 없거나 WP가 200이 아니면 STEP 5(반영)를 건너뛴다. NKID·NKEY 가 없으면 상위 글 조사(STEP 6-2·7)를 `미검증` 으로 둔다. 종료하지는 않는다.

## STEP 3 — 유입 데이터와 글 목록

[3-1] CSV 읽기 — `cd $W && python3 ctr_engine.py ingest ${NAVER_IN:+"$NAVER_IN"}` (새 CSV만 `snapshots/` 에 저장). 최신 스냅샷 `snapshots/{가장 최근 날짜}.json` 의 `docs[]`(slug·clicks·impr — 최근 30일 누적)를 `TRAFFIC` 으로 쓴다. 최신 스냅샷이 3일 이상 묵었으면 STEP 10에 `CSV 미수집 {n}일` 을 적고 그대로 진행한다(순위 근거가 조금 낡을 뿐 작업은 가능하다).

[3-2] 글 목록 `WP_CORPUS` — `GET /wp-json/wp/v2/posts?status=publish,future,draft&per_page=100&page={n}&_fields=id,slug,status,date,modified,title,categories` 를 `x-wp-totalpages` 까지. 세션당 1회.

## STEP 4 — 지난 작업 회수 (매 회차 가장 먼저)

`state.json.posts` 중 상태가 `searching`·`linking` 인 글마다:
1. `naver_blog\tasks\done\{작업 파일명}` 이 있으면 `result.status` 를 읽는다.
   - `ok` + `connect_search` → `naver_blog\inbox\{inbox}\connect.json` 의 `items[]` 를 읽어 **지침 2-10 상품 고르기**로 1~3개를 고른다 → 고른 상품명(`name` 원문 그대로)으로 `connect_links` 작업을 넣고(STEP 6-4 형식) 상태 `linking`. 조건에 맞는 상품이 0개면 상태 `skip` · 사유 `상품 없음({검색어})`.
   - `ok` + `connect_links` → `links.json` 의 `links{상품명: URL}` 을 상품에 붙인다. 링크가 1개 이상이면 상태 `ready`, 0개면 `failed` 목록과 함께 `skip`.
   - `err` 또는 `failed` → 같은 작업을 **1회만** 다시 넣는다(`retry: 1` 기록). 두 번째도 실패면 `hold` · 사유 그대로.
2. done 이 없고 넣은 지 `TASK_STALE_DAYS` 일이 지났으면 STEP 10에 `⏳ 확장 큐 멈춤 의심 — {작업 파일} {n}일` 을 적는다(작업 파일은 지우지 않는다).
3. AIPick 큐 서버 상태가 궁금하면 `naver_blog\upload_logs\{오늘}.log` 최근 10분 기록을 본다. 루틴이 서버를 재시작하지 않는다.

## STEP 5 — 상품 블록 반영 (`ready` 글, 하루 APPLY_PER_DAY 편)

대상: `state.json.posts` 의 `ready` 글. 우선순위 = ① 시즌 글(지침 0-4 창 안·최고점 전) ② `TRAFFIC` 30일 클릭 큰 순 ③ `future`(예약) 글.

[5-1] 백업 — `GET /wp-json/wp/v2/posts/{id}?context=edit` 응답(title·content.raw·modified·status·slug)을 `0and1life-revenue\backups\{slug}-{TODAY}.json` 에 저장. 저장 실패면 반영하지 않는다.

[5-2] 블록 만들기 — **지침 2-10 템플릿 그대로**. python으로 `content.raw` 를 읽어:
- 넣을 위치 = 지침 2-10 위치 규칙. `state.posts[slug].slot.h2` 문구를 가진 `<h2` 가 **정확히 1개**인지 assert → 그 H2 섹션의 끝(다음 `<h2` 직전, FAQ H2면 그 앞). 없거나 2개 이상이면 반영하지 않고 `hold · H2 위치 불명`.
- 고지 한 줄 = 지침 2-10 고지 문구. 첫 `</figure>`(히어로) 직후에 **정확히 1번**. 이미 `o1-sc-note` 가 있으면 넣지 않는다.
- 이미 `o1-sc-box` 가 2개 있으면 넣지 않는다(지침 2-10 글당 최대 2블록).
- 기대값은 손으로 잡지 않고 **코드로 센다**: 기대 개수 = 백업 content의 태그 수 + 이번에 넣는 블록·고지 HTML 문자열에서 센 태그 수(`<div`·`<p`·`<a `·`<ul`·`<li`). `<img`·`<h2`·`<table`·`<figure`·`application/ld+json`·`wp:freeform` 은 변화 0이어야 한다(2026-09-24 CTR 루틴에서 기대값을 손으로 잡아 정상 반영을 원복한 사고가 있었다).

[5-3] 반영 — `APPLY_MODE=SAMPLE` 이면 새 content를 `0and1life-revenue\proposals\{slug}-{TODAY}.html` 에 저장만 하고 상태 `proposed` 로 둔다. `AUTO` 면:
1. 반영 직전 `modified` 재조회 → [5-1] 값과 다르면 중단(다음 회차).
2. `POST /wp-json/wp/v2/posts/{id}` `{"content": "{새 content.raw}"}` — **content 하나만** 보낸다.
3. 8초 뒤 재조회 → [5-4] 검사.

[5-4] 반영 후 검사 — 하나라도 실패하면 백업 `content.raw` 로 즉시 되돌리고 `반영 실패 — 원복: {항목}` 기록(상태 `hold`).
| 구분 | 기준 |
|---|---|
| 상태 | `status`·`slug`·`date`·`categories`·제목 불변 |
| 구조 | `<p`·`<h2`·`<div`·`<a `·`<img`·`<table`·`<figure` 개수 = [5-2] 기대값 · freeform 마커 수 불변 · 여닫이 짝(div·ul·p·a·figure, `<ul[\s>]` 정규식) |
| 스키마 | ld+json 개수 불변 · 전부 JSON 파싱 성공 |
| 블록 | `o1-sc-box` 안의 링크가 전부 `rel="sponsored nofollow noopener"` · 링크 URL = `links.json` 원문 · 고지 문구 2곳(상단 1·블록 1) |
| 공개 페이지 | `publish` 글만: `https://0and1life.com/{slug}/?nc={epoch}` 200 · 블록 문구 보임 · `<meta name="robots">` 에 noindex 없음. 캐시로 안 보이면 `캐시 반영 대기` 로만 기록 |
| 링크 | 상품 링크마다 `curl -s -o /dev/null -w "%{http_code}" -I --max-time 15` → 200·301·302 면 정상 · 404·410 이면 그 상품 줄을 빼고 다시 반영(1회) · **000(연결 거부)은 네트워크 정책 탓이므로 `링크 확인 불가` 로만 기록하고 그대로 둔다**(2026-10-10 실측: naver.me 는 PC 셸·클라우드 모두 프록시가 막는다. 링크는 커넥트가 방금 발급한 원문이라 반영을 막지 않는다) |

[5-5] 성공하면 상태 `applied` · `applied_at` · `products[]`(name·link·price_won·commission_pct·review_count·rating·checked) · `backup` 경로를 기록한다.

## STEP 6 — 새 수익 슬롯 (하루 SLOT_NEW_PER_DAY 편 — CUTOFF_KST 전까지만)

[6-1] 후보 — `WP_CORPUS` 의 `publish`·`future`·`draft` 글 중 `state.json.posts` 에 없거나, `skip`·`hold` 후 `REVISIT_DAYS` 가 지난 글.
- 정렬: ① `future`·`draft` 이면서 지침 0-4 시즌 창 안(발행 전에 블록을 넣어 둔다) ② `TRAFFIC` 30일 클릭 큰 순 ③ 최근 발행 순.
- 위에서부터 글을 하나씩 열어(`context=edit`) **지침 0-10 구매 연결 등급**을 판정한다. Notion 기본 정보 표에 `수익 연결` 행이 있으면 그 값을 먼저 쓰고, 본문과 맞는지만 확인한다.
  - `C` → 상태 `skip` · `grade: C` · 사유 한 줄. 다음 글로.
  - `A`·`B` → `slot` 을 정한다: `{"grade":"A","group":"{상품군}","query":"{커넥트 검색어 — 상품군 이름 1~3어절}","h2":"{넣을 H2 문구 원문}","criteria":["본문의 고르는 기준 1","2","3"]}`. `criteria` 는 **본문에 실제로 있는 기준 문장**에서만 뽑는다(지어내지 않는다). 기준이 본문에 없으면 `criteria: []` 로 두고, 블록 이유 줄은 지침 2-10 대체 문구를 쓴다.
- `SLOT_NEW_PER_DAY` 편을 채우거나 후보가 끝나면 멈춘다. 등급 판정은 하루 최대 8편까지만 연다.

[6-2] (선택) 검색어 확인 — `query` 가 넓으면(예: `보호장비`) `python3 $W/naver_volume.py --related 10 "{query}"` 로 쇼핑에서 실제로 쓰는 표기를 1회 확인해 더 구체적인 표기로 바꾼다. 수치는 기록만 한다.

[6-3] `connect_search` 작업 넣기
```bash
n={그날 REV 작업 순번}; INBOX="REV_${RUN}_${n}_{slug 앞 20자}"
cat > "$NB/tasks/pending/REV_${RUN}_${n}_connect.json" <<J
{"type":"connect_search","keyword":"{query}","inbox":"$INBOX"}
J
```
상태 `searching` · `tasks: ["REV_{RUN}_{n}_connect.json"]` · `inbox` · `queued_at`.

[6-4] `connect_links` 작업 형식(STEP 4에서 상품을 고른 뒤 쓴다)
```json
{"type":"connect_links","models":["{connect.json items[].name 원문}", "..."],"inbox":"{같은 inbox}"}
```
파일명 `REV_{RUN}_{n}_links.json`. 상태 `linking`.

[6-5] 같은 회차 대기 — 작업을 넣었고 `NOW < CUTOFF_KST` 면 60초 간격으로 `tasks\done\` 을 확인하며 최대 `WAIT_MIN` 분 기다린다. 결과가 오면 STEP 4의 처리(상품 고르기 → links 작업 → 회수)를 이어서 하고, `ready` 가 되면 STEP 5를 그 글에 바로 적용한다(APPLY_PER_DAY 안에서). 시간 안에 안 오면 다음 회차가 회수한다. **월·목은 AIPick이 03:00~07:30 큐를 쓰므로 대기하지 않고 바로 다음 STEP으로 간다.**

## STEP 7 — 수익 레이더 (매일 · 글은 쓰지 않는다)

목표: **작년 검색 최고점이 오늘+14~45일(RADAR_WINDOW)이고, 구매 연결 A·B이며, 블로그가 이길 수 있는 키워드**를 하루 최대 `RADAR_PER_DAY` 개 백로그에 올린다.

[7-1] 후보 모으기 (중복 제거, 20개 이내)
- 지침 0-4 시즌 캘린더에서 오늘+14~45일에 시작하거나 최고점이 오는 이벤트의 **물건 쪽 헤드**(예: 김장 → `김장매트`·`절임배추` / 수능 → `보온도시락`·`수능 간식` / 첫 한파 → `전기요` / 블프 → `직구`).
- `naver_blog\radar\` 의 최신 `*_rank.md` 가 7일 이내면 **🔥 신규·상승** 줄의 제품군(쇼핑 인기검색어).
- 최근 `TRAFFIC` 상위 글 헤드의 연관어 중 물건 표기(`naver_volume.py --related 10 "{헤드}"`).
- 이미 `state.json.radar` 에 있거나 `WP_CORPUS` 제목·슬러그와 겹치는 키워드는 뺀다(의미 대조).

[7-2] 수요·시기 — `python3 $W/naver_volume.py "{k1}" "{k2}" …` 로 월간 검색수(월 1,000 미만은 뺀다). 남은 후보를 5개씩 `python3 $W/naver_trend.py {작년 오늘} {작년 오늘+60일} "A=…" …` 로 재서 **작년 최고점 날짜**를 본다. 최고점이 RADAR_WINDOW 밖이면 뺀다. 상시 키워드는 최근 90일 흐름이 오르는 것만(`naver_trend.py {90일 전} {어제}` 최근 7일 ÷ 이전 7일 ≥ 1).

[7-3] 경쟁 — 남은 후보마다 릴레이 `naver-check` `type=webkr` `display=10` 1회. 상위 10 중 공식 사이트·브랜드·쇼핑몰·네이버 서비스가 **7곳 이상**이면 뺀다(작성 지침 0-6 구조 독점과 같은 기준). 개인 블로그·카페 수와 우리가 줄 수 있는 차별 답(지침 0-9 렌즈)을 한 줄로 적는다.

[7-4] 백로그에 올리기 — 통과 후보를 점수(월 검색수 × 구매 연결 A=1·B=0.6 × 최고점까지 남은 일수가 21~35일이면 1.2)로 정렬해 상위 `RADAR_PER_DAY` 개. Notion 키워드 백로그를 **re-fetch** → 기존 행·`WP_CORPUS` 중복을 다시 확인 → **표의 첫 데이터 행 앞**(머리행 바로 뒤)에 행을 추가한다. 번호는 현재 최대 번호 + 1.
```
| {번호} | {키워드} | 💰수익 레이더 | 월 {n}회(검색광고, {TODAY}) · 작년 최고점 {MM-DD}(D-{n}) · webkr {total} · 상위10 공식·쇼핑 {n}/개인 {n} · 구매 연결 {A|B}({상품군}) · 레인 {S|L} · 각도 메모: {렌즈 한 줄} · 자동완성 미확인(writer 1-T에서 확인) | {클러스터} / {카테고리(WP n)} · {S|L} | — | {TODAY} | 대기 |
```
- D(데이터랩 계기판)는 writer 엔진 D가 잰다 — 여기서 적지 않는다. 자동완성(1-T)도 writer가 확인한다.
- `state.json.radar[키워드] = {date, volume, peak, grade, backlog_no}` 로 남겨 같은 키워드를 다시 올리지 않는다.
- Notion 실패 → 45초 뒤 1회 재시도 → 실패면 `0and1life-revenue\log.md` 와 STEP 10에만 남긴다.

## STEP 8 — 주간 수익 리포트 (월요일, 또는 `weekly_last` 가 7일 이상 지났을 때)

`0and1life-revenue\weekly\{TODAY}.md` 를 쓰고 STEP 10 알림에 표를 그대로 붙인다.
1. **유입** — 최신 스냅샷과 7일 전 스냅샷(없으면 가장 가까운 것)의 `docs` 클릭·노출 차이로 글별 7일 증감(근사 — 서치어드바이저 30일 누적값의 차이). 상위 10편.
2. **상품 블록 현황** — `applied`·`ready`·`linking`·`searching`·`hold`·`skip` 수 · 이번 주 새로 넣은 글 · `applied` 글 링크 상태(STEP 5-4 링크 검사를 다시 1회).
3. **쇼핑커넥트 실적** — `0and1life-revenue\inbox\` 에 사용자가 넣은 파일(CSV·XLSX·이미지)이 있으면 읽어 상품·글별 클릭·구매·수수료를 표로 옮긴다(이미지는 클라우드로 stage 해 Read). 없으면 표 대신 `🙋 쇼핑커넥트 실적 파일을 0and1life-revenue\inbox 에 넣어 주세요(브랜드커넥트 > 성과 화면 내보내기 또는 캡처)` 한 줄.
4. **판단 재료** — 블록을 넣은 글과 안 넣은 글의 클릭 추이, 상품별 클릭 대비 구매(실적이 있을 때). 수치가 없으면 판단을 쓰지 않는다.
5. **오래된 블록** — `applied_at` 이 45일 지난 글은 STEP 6-3부터 다시 돌려 가격·품절을 갱신 대상으로 표시한다(`refresh: true`). 갱신 반영은 STEP 5와 같은 절차로 **기존 블록을 같은 위치에서 교체**한다(블록 수가 늘지 않게).
6. `weekly_last = TODAY`.

## STEP 9 — 기록

[9-1] `state.json` 저장(파이썬으로 읽고-고치고-쓰기 · 들여쓰기 1).
[9-2] `0and1life-revenue\log.md` 맨 위에 추가:
```
## {TODAY} · 수익 루틴 ({HH:MM} KST)
- 데이터: 스냅샷 {날짜}(stale {n}일) · 글 {n}편
- 회수: {slug — connect {n}건 → 상품 {n}개 선택 | links {n}/{n} | 실패(사유)} …
- 반영: {slug — {H2} 아래 상품 {n}개 · 검사 OK · 공개 {OK|캐시 대기}} … / 원복 {slug — 항목}
- 새 슬롯: {slug — 등급 A·{상품군}·검색어 '{query}' → REV_{RUN}_{n}} … / 건너뜀 {slug — C(사유)}
- 레이더: {키워드 월 n · 작년 최고 MM-DD(D-n) · 구매 A · 상위10 공식 n → 백로그 #n} … / 탈락 {키워드 — 사유}
- 큐: pending {n} · 오늘 done {n} · 멈춤 의심 {n}
```

## STEP 10 — 완료 알림 (앞 단계 성공 여부와 무관하게 반드시 실행)

PushNotification 1회. `<routine_summary>` 의 **첫 문장**(휴대폰 배너)은 그날 가장 중요한 한 줄(예: `상품 블록 2편 반영 — 예초기 대여·김장 글`, 또는 `반영 없음 — 커넥트 결과 대기 2편`), 그 뒤에 아래 형식 전체. 아무 일도 없던 날도 보낸다(확장 큐가 멈췄는지 알 수 있는 유일한 경로다).
```
💰 0and1Life 수익 루틴 {TODAY}
- 반영: {n}편 — {slug: 상품 {n}개({상품명 짧게}) · {H2}} … (APPLY_MODE {AUTO|SAMPLE})
- 진행 중: 상품 검색 {n} · 링크 발급 {n} · 준비 완료(내일 반영) {n}
- 새 슬롯: {slug(A·상품군)} … / 건너뜀(C) {n}
- 🆕 레이더 → 백로그: {키워드 월 n회 · 작년 최고 MM-DD(D-n) · 구매 A·B · 상위10 공식 n} … (글 작성은 writer 루틴)
- 📊 주간(월요일만): STEP 8 표 그대로
- 🙋 사용자 할 일: {실적 파일 요청 | 큐 서버·확장 확인 | 보류 글 확인} (없으면 줄 생략)
- ⚠️ 조치 필요: {CSV 미수집 n일 · 큐 멈춤 의심 · 지침 0-10·2-10 없음 · WP 인증 · Notion 기록 실패 · 원복 발생} (없으면 줄 생략)
```

---

## 🚨 오류 처리

| 상황 | 처리 |
|---|---|
| PC 셸 없음·`MISSING` | STEP 10에 사유만 적고 종료(클라우드 폴백 없음) |
| 확장 큐 폴더 없음 | STEP 4~6 확장 부분 건너뜀 → 레이더·기록·알림만 |
| 작업이 `TASK_STALE_DAYS` 넘게 done 안 됨 | `큐 멈춤 의심` 보고. 작업 파일 유지(지우지 않음). 큐 서버·확장은 사용자 확인 |
| `connect_search` 결과 0건·조건 맞는 상품 0개 | 그 글 `skip` · `상품 없음({검색어})` → REVISIT_DAYS 뒤 다른 검색어로 재시도 |
| `connect_links` 일부 실패 | 받은 링크만으로 진행(1개 이상이면 `ready`) |
| H2 위치를 못 찾음·2곳 이상 | 반영 안 함 · `hold · H2 위치 불명` |
| 반영 직전 `modified` 가 바뀜 | 그 글은 다음 회차로 |
| 반영 후 검사 실패 | 백업 `content.raw` 로 즉시 원복 · `hold` · STEP 10 `원복 발생` |
| 상품 링크가 404·410 | 그 상품 줄을 빼고 1회 재반영 → 0개면 원복 (000 연결 거부는 `링크 확인 불가` 기록만) |
| WP 인증 실패 | STEP 5 건너뜀(회수·슬롯·레이더는 진행) |
| 릴레이·수요 조회 실패 | 1회 재시도 → 레이더 그 후보 `미검증` 으로 빼고 진행 |
| Notion 백로그 실패 | 45초 뒤 1회 재시도 → `log.md`·알림에만 기록 |
| 07:40 KST 경과 | 새 큐 작업 금지 → STEP 9·10 |
| 사용자가 블록을 손으로 지웠음(`applied` 인데 `o1-sc-box` 없음) | 다시 넣지 않는다 · 상태 `removed_by_user` · 알림 한 줄 |

## ⚠️ 전제조건 (사용자 몫 — 2026-10-10 기준)

| 항목 | 상태 | 비고 |
|---|---|---|
| 작성 지침 `0and1Life-Writer.md` **0-10·2-10** | ⬜ blog 폴더에 저장됨 · 커밋 필요 | 루틴은 PC 폴더 판을 읽으므로 커밋 전에도 동작한다 |
| 브랜드커넥트 가입·로그인(확장이 쓰는 크롬 프로필) | ✅ 사용자 확인(10/10) | 로그인이 풀리면 확장 작업이 `err` 로 돌아온다 |
| AIPick 확장·큐 서버(`naver_blog\uploader\server.py`) | ✅ 10/8 `connect_search`·`connect_links` 실측 동작 | 새벽에 PC·크롬·서버가 켜져 있어야 한다 |
| 서치어드바이저 CSV 확장(`naver-advisor-export`) 06:00 | ✅ | 유입 순위 근거 |
| Cowork 예약 `6. 0and1life 수익 루틴` 06:40 KST · 폴더 `C:\Users\win\Documents\Claude`·`다운로드\네이버_수집` | ✅ 2026-10-10 교체(이전 이름 `6. 0and1life 네이버 CTR 개선` 06:00) | 다음 개정 때 이 파일 전문으로 다시 교체 |
| (구) `Schd_0and1Life-NaverCTR.md` · `naver-ctr\` 엔진 | 폐지 — 파일은 남겨 둠 | `ctr_engine.py ingest`·`naver_volume.py`·`naver_trend.py` 만 계속 쓴다. 파일 정리는 사용자 판단 |

## Cowork 원라이너

날짜·폴더(1) → 자격증명(2) → CSV·글 목록(3) → **지난 확장 작업 회수 → 상품 1~3개 선택 → 링크 발급 작업(4)** → **준비된 글에 상품 블록 + 고지 한 줄, 백업·검사·원복 규칙(5)** → 새 글 2편 구매 연결 등급 판정 → `connect_search` 작업(6) → **최고점 14~45일 전 · 물건 연결 키워드 → 백로그 `💰수익 레이더`(7)** → 월요일 주간 수익 리포트(8) → 기록(9) → 알림(10). 제목·메타·기존 문단은 건드리지 않는다.
