# Schd_0and1Life-Insta — 발행 글 → 인스타그램 캐러셀 게시 루틴 (Cowork 예약 작업용, v1.1 2026-09-30 — STEP W 주간 레퍼런스 스캔·STEP 4.5 스킨 선택 신설)

*매일 03:30 KST 실행(Cowork 예약 `0and1life 인스타 캐러셀`, 2026-09-30 등록 — 전날 발행 글을 다루므로 Draft 04:00·Image 05:30·NaverCTR 06:30보다 앞에 둔다). 예약 시각이 되면 같은 날 이미 실행됐더라도 다시 진행한다(`ledger.json`이 같은 글을 두 번 올리지 않게 막는다).
날짜: 실행 시점의 실제 KST 날짜를 쓴다. 이 프롬프트에 적힌 고정 날짜는 무시한다.

⚠️ **역할 경계 — 이 루틴은 도구다.** 캐러셀 구성·문구·품질·허브 카드의 판정 기준(SSOT)은 전적으로 GitHub 지침 `0and1Life-Insta.md`다. 이 루틴은 **운영 절차**(언제·무엇을·어디에 기록)와 **실행 자산**(파일 경로·릴레이·스크립트·알림 형식)만 정의한다. 규칙을 가리킬 때는 조항 번호로 참조한다(예: "지침 I-2-3"). 상충이 보이면 지침을 따르고 STEP 11에 기록한다.

⚠️ [무인 실행 원칙 — 최우선]
사람이 없는 시간에 실행된다. **사용자 승인이 필요한 도구 호출을 불필요하게 하지 않는다.** `PUBLISH_MODE=APPROVE`일 때의 "게시" 대기는 예외이며, 그 외 승인 창이 필요한 호출(폴더 접근 요청·삭제)은 하지 않는다.

⚠️ [블로그 글은 읽기 전용]
이 루틴은 **WP 글(post)의 본문·상태·슬러그·카테고리·대표이미지를 절대 바꾸지 않는다.** 쓰는 곳은 세 군데뿐이다: ① WP 미디어(캐러셀 JPEG 업로드) ② 허브 페이지 `page 1922` 본문(카드 1장 추가) ③ 인스타그램(게시). 미디어·게시물 삭제는 어떤 경우에도 하지 않는다.

⚠️ [에디터·REST 충돌 규약 — Draft 지침 5-1과 같다]
허브 페이지(`post.php?post=1922`) 편집 화면이 열려 있으면 REST로 본문을 쓰지 않는다. Chrome MCP를 쓰지 않는 루틴이라 탭을 직접 확인할 수 없으므로, STEP 10-B에서 카드 추가 **직후 8초 뒤 재조회**로 카드 존재를 검증하고, 사라졌으면 `E-HUB`로 알림한다(재시도는 1회).

⚠️ [실행 환경]
- Cowork 예약 작업 + **PC 연결 필수**(`C:\Users\win\Documents\Claude` 폴더가 연결돼 있어야 한다 — pw.txt·instagram·blog가 모두 이 아래에 있다). 연결이 없으면 STEP 1에서 즉시 중단·알림한다.
- PC 쪽 명령은 `device_bash`(`$HOME/mnt/Claude/...`)로, 이미지 렌더링은 **클라우드 컨테이너**(Playwright·Chromium 내장)에서 한다. 결과 파일은 `device_commit_files`로 PC에 저장한다.
- **일간 게시 흐름(STEP 0~11)은 Chrome MCP·브라우저 조작을 쓰지 않는다.** 예외는 **STEP W 주간 레퍼런스 스캔**뿐이며, 이때만 Chrome MCP로 인스타그램을 읽는다(읽기 전용 — 좋아요·팔로우·댓글·DM 어떤 상호작용도 하지 않는다). 인스타 API는 클라우드·PC 모두 `graph.instagram.com`이 차단이라 **사이트 릴레이 `POST https://0and1life.com/wp-json/o1/v1/ig`**(WPCode 스니펫 `ig-relay`)로만 호출한다. 토큰은 요청 헤더 `X-O1-IGT`로만 전달되고 서버에 저장되지 않는다.
- `npm`은 클라우드에서 동작한다(Pretendard 글꼴 조달용).

⚠️ [지침 출처] `https://raw.githubusercontent.com/leejc0404/blog/main/0and1Life-Insta.md?cb={epoch_ms}` — STEP 0에서 매번 `web_fetch`로 읽고 세션 내 재사용한다. 캐시버스터 없이 조회하지 않는다. 조항이 안 보이면 Draft 지침 5-0-A 3단 검증을 준용하고, 그래도 없으면 게시하지 않고 알림한다(이 루틴은 자기보완 조항을 쓰지 않는다 — 게시는 되돌릴 수 없기 때문).

⚠️ 이 프롬프트가 실행되는 유일한 원본이다. 다른 위치의 사본을 참조하지 않는다. git commit·push는 하지 않는다 — 사용자가 직접 한다.

---

## 실행 자산 (경로·스크립트)

| 자산 | 경로 (PC) | 역할 |
|---|---|---|
| 자격증명 | `C:\Users\win\Documents\Claude\pw.txt` | `ONEANDZERO_WP_USER` `ONEANDZERO_WP_APP_PASSWORD` `IG_USER_ID` `IG_ACCESS_TOKEN` — **값 출력 금지** |
| 릴레이 호출 | `instagram\relay\ig.py` | `me / limit / refresh / container / carousel / status / media / publish` |
| 허브 카드 | `instagram\relay\hub.py` | `add <card.json>` · `seo <seo.json>` · `get` |
| 렌더러 | `instagram\relay\render_carousel.py` | `carousel.json` → JPEG 9장 + `contact.png` + `render_report.json` (`"skin"` 키로 스킨 선택) |
| 스킨 등록부 | `instagram\relay\styles.json` | `active_skin` · `by_type` · `skins{}`(토큰) · `bench_accounts[]` — 렌더러와 같은 폴더에 있어야 읽힌다 |
| 레퍼런스 | `instagram\refs\inbox.md`(사용자 링크 인박스) · `instagram\refs\{YYYY-Www}.md`(주간 스캔 노트) | STEP W가 쓰고, STEP 4.5·5가 읽는다 |
| 스니펫 원본 | `instagram\relay\wpcode_ig-relay.php` | 사이트에 설치된 WPCode 스니펫과 같아야 함(사용자가 교체) |
| 예시 원고 | `instagram\2026-09-30\october-holidays-2026-annual-leave\carousel.json` | 템플릿 6종 사용 예 |
| 원장 | `instagram\ledger.json` | `posts.{slug}: {date, status, ig_media_id, ig_url, hub_card, held}` · `token_refreshed` |
| 로그 | `instagram\log.md` | 회차별 블록(최신이 위) |
| 회차 폴더 | `instagram\{YYYY-MM-DD}\{slug}\` | `carousel.json` `caption.txt` `*.jpg` `contact.png` `render_report.json` `wp_media.json` `ig_containers.json` `hub_card.json` `meta.json` |

설정값: `PUBLISH_MODE = APPROVE`(사용자 지시로만 `AUTO`) · `DAILY_TARGET = 1` · `LOOKBACK_DAYS = 3` · `TOKEN_REFRESH_DAYS = 30` · `IG_API = v23.0`(릴레이 내부) · `REF_SCAN_DAY = 월요일`(KST) · `REF_MAX_POSTS = 6`

실행 순서: **STEP W(월요일 또는 `refs/inbox.md`에 `[ ]` 미처리 링크가 있을 때만) → STEP 0 → … → STEP 11.** STEP W가 실패해도 일간 흐름은 계속한다(스킨은 직전 `styles.json` 그대로).

---

## STEP W. 주간 레퍼런스 스캔 (지침 I-3-3 — 월요일 또는 인박스에 미처리 링크가 있을 때만 · Chrome MCP 읽기 전용)
1. **수집 목록 만들기** (최대 `REF_MAX_POSTS`): ① `refs/inbox.md`의 `- [ ]` 줄 전부 → ② `styles.json.bench_accounts` 각 계정 프로필의 최근 캐러셀 1편 → ③ 남는 자리는 `https://www.instagram.com/explore/tags/{키워드}/`(`카드뉴스` + 이번 주 대상 글 키워드 1개)의 인기 게시물 중 텍스트 중심 캐러셀. 지침 I-3-3 "고를 기준"(공유÷좋아요 ≥ 10% 또는 댓글 '저장' 언급)으로 거른다.
2. **읽기 방법** (2026-09-30 실측 기준): 게시물은 `…/p/{code}/?img_index={n}` 으로 **URL 이동 → 5초 대기 → 스크린샷**. 화살표 클릭 후 스크린샷은 렌더러 타임아웃이 잦다. 스크린샷이 30초 타임아웃되면 같은 URL로 1회 재시도하고, 그래도 실패하면 그 장은 건너뛴다. 좋아요·댓글·공유 수와 댓글 반응은 `get_page_text`로 읽는다. 장수는 하단 점(dot) 개수 또는 `img_index` 최대값으로 센다. **인스타 화면에서 클릭은 페이지 이동에만 쓴다.**
3. **기록**: `refs/{YYYY-Www}.md`에 게시물마다 지침 I-3-3 "추출 8항목" + 반응 수치 + "차용할 것 / 복제하지 않을 것"을 쓴다. 처리한 인박스 줄은 `[x]`로 바꾸고 노트 파일명을 덧붙인다.
4. **스킨 반영**: 토큰으로 표현되는 기법이면 `styles.json.skins`에 **새 이름으로 추가**(`origin` 필수, 기존 스킨 수정 금지, `active_skin`·`by_type`은 건드리지 않는다). 렌더러로 예시 원고(`2026-09-30/october-holidays-2026-annual-leave/carousel.json`)에 새 스킨을 넣어 1회 시험 렌더해 `refs/{YYYY-Www}_{스킨}_시험렌더.png`로 남기고, `overflow`가 비어 있으면 STEP 11에 `🎨 새 스킨 후보 {이름} — 시험렌더 확인 후 채택 여부 알려주세요`로 보고만 한다. 채택(`by_type` 변경)은 사용자가 한다. 템플릿 추가가 필요한 기법은 STEP 11에 "템플릿 제안"으로만 남긴다.
5. 열었던 탭은 모두 닫는다. 이 단계에서 생성·수정한 파일: `refs/*.md`, `styles.json`뿐.

## STEP 0. 지침 읽기·설정 확인
1. 지침을 `?cb=` 붙여 읽는다. Phase I-0~I-8과 반려 코드표가 모두 보이는지 확인한다.
2. 설정값(위 표)을 세션 변수로 둔다. `PUBLISH_MODE`는 이 프롬프트의 값이 기준이며, 지침·ledger에서 바꾸지 않는다.

## STEP 1. 날짜·폴더·자격증명
```bash
TODAY=$(TZ=Asia/Seoul date +%F); D1=$(TZ=Asia/Seoul date -d "yesterday" +%F); D3=$(TZ=Asia/Seoul date -d "3 days ago" +%F)
B="$HOME/mnt/Claude"; ls "$B/pw.txt" "$B/instagram/relay/ig.py" "$B/instagram/relay/hub.py" "$B/instagram/relay/render_carousel.py" >/dev/null || echo "MISSING"
for k in ONEANDZERO_WP_USER ONEANDZERO_WP_APP_PASSWORD IG_USER_ID IG_ACCESS_TOKEN; do grep -q "^$k=" "$B/pw.txt" && echo "$k=있음" || echo "$k=없음"; done
[ -f "$B/instagram/ledger.json" ] || echo '{"token_refreshed":"","posts":{}}' > "$B/instagram/ledger.json"
```
- `MISSING`이거나 키가 하나라도 `없음`이면 중단·알림(`E-TOKEN` 또는 자산 누락). `request_cowork_directory`·폴더 접근 요청은 호출하지 않는다.
- pw.txt는 BOM과 값 내 공백이 있다 — `ig.py`/`hub.py`의 `cred()`만 쓰고 `source`하지 않는다.

## STEP 2. 토큰·계정·한도 확인
```bash
cd "$B/instagram/relay" && python3 ig.py me && python3 ig.py limit
```
- `me`의 `username`이 `0and1life`가 아니면 **모든 단계 중단**(`E-TOKEN`). 401/404면 `E-RELAY`(스니펫 비활성 가능성) 알림.
- `limit.quota_usage` ≥ 99면 게시 단계를 건너뛰고 준비까지만 한다.
- `ledger.token_refreshed`가 `TOKEN_REFRESH_DAYS`보다 오래됐으면 `python3 ig.py refresh` → 응답 `access_token`을 pw.txt의 `IG_ACCESS_TOKEN=` 줄에 **교체 저장**(sed, 값은 출력하지 않음) → `me`로 재확인 → `ledger.token_refreshed=TODAY`. 실패해도 기존 토큰으로 계속 진행하고 STEP 11에 기록한다.

## STEP 3. 대상 글 선정 (지침 I-1)
```bash
curl -s "https://0and1life.com/wp-json/wp/v2/posts?status=publish&after=${D3}T00:00:00&before=${D1}T23:59:59&per_page=20&orderby=date&order=desc&_fields=id,slug,date,modified,title,categories,link"
```
1. 후보 중 `ledger.posts`에 있는 slug는 `X-LEDGER`로 제외. 지침 I-1-3의 나머지 코드를 순서대로 판정한다(`X-THIN`은 STEP 4에서 본문을 본 뒤 확정).
2. 우선순위 I-1-4로 1편을 고른다(`DAILY_TARGET`). 나머지 후보는 `ledger.posts.{slug}.status="pending"`으로만 기록한다(다음 회차가 집는다).
3. 대상이 없으면 `log.md`에 `## {TODAY} · 대상 없음` 한 줄을 남기고 STEP 11로 간다.
4. 회차 폴더 `instagram\{TODAY}\{slug}\`를 만든다(PC).

## STEP 4. 본문 최종본 확보·구조 추출
```bash
curl -s "https://0and1life.com/wp-json/wp/v2/posts/{ID}?_fields=id,slug,title,date,modified,content,categories,featured_media" -o /tmp/post.json
```
- `content.rendered`에서 추출: 제목, `ai-knowledge-snippet`의 Core Fact / Primary Insight / Actionable Tip, 모든 `<table>`(행 단위 텍스트), H2 목록(⭐ GAP H2 표시), `📌`/`*핵심 :` 요약 줄, FAQ(`<p><strong>Q.`), 출처 명칭(figcaption·본문의 규정·법령명), `modified` 날짜.
- HTML을 벗긴 **본문 전체 텍스트**를 `post_text.txt`로 저장한다(STEP 7 숫자 대조용).
- `<table>` 0개이고 Core Fact에 수치가 없으면 `X-THIN` — ledger 기록 후 STEP 3의 다음 후보로 돌아간다(1회).
- 카테고리 ID는 Draft 지침 7-1 표로 이모지+이름을 얻는다(허브 카드 `category`).

## STEP 4.5. 스킨·훅 선택 (지침 I-3-2 · I-2-0)
1. 글 유형을 정한다: 달력·표 중심 → `calendar`, 계산·비교 → `calc`, 제도·규정 설명 → `rule`, 체크리스트 → `checklist`, 💍 → `wedding`, 🤖 → `ai`.
2. `styles.json.by_type[유형]`을 그대로 쓴다(2026-09-30 기준 전부 `clean-data`). 자동으로 다른 스킨으로 바꾸지 않는다 — 스킨 교체는 사용자가 시험 렌더를 보고 `styles.json`을 고쳤을 때만 일어난다.
3. 이번 주 `refs/{YYYY-Www}.md`가 있으면 거기 기록된 **훅 유형·밀도** 메모를 읽고 STEP 5에서 1장 훅 유형(ⓐ/ⓑ/ⓒ)을 고른다. 없으면 ⓐ 결론 숫자형.
4. 선택 결과를 `meta.json.skin`, `meta.json.hook`에 적는다.

## STEP 5. 원고 작성 → `carousel.json` · `caption.txt` · `alts.json` · `hub_card.json`
- 지침 I-2(구성·한도·숫자 복사·날짜 문구·유도 문구)와 I-4(캡션·해시태그·alt)를 그대로 적용한다. `carousel.json` 최상위에 `"skin": "{STEP 4.5 결과}"`를 넣는다.
- `carousel.json` 형식은 `render_carousel.py` 머리말 주석과 예시 원고(2026-09-30)를 따른다. `prefix`는 `0and1life-{slug}-ig`, `source`는 `{원문 명칭} · {modified를 YYYY.M.D} 기준`.
- `hub_card.json`: `slug, title(글 제목 그대로), date(TODAY를 YYYY.MM.DD), category, thumb(1장 표지 URL — STEP 9 업로드 후 채움), ig_url(게시 후 채움), points[2~3]`.
- 파일은 클라우드 작업 폴더에 먼저 쓰고, STEP 8에서 PC로 옮긴다.

## STEP 6. 렌더 (클라우드)
```bash
mkdir -p ~/ig_work && cd ~/ig_work && (ls package/dist/web/static/woff2 >/dev/null 2>&1 || (npm pack pretendard@1.3.9 >/dev/null && tar xzf pretendard-1.3.9.tgz))
# render_carousel.py 와 styles.json 을 PC의 relay 폴더에서 device_stage_files 로 가져와 ~/ig_work 에 둔다 (package 폴더와 같은 위치 — styles.json 이 없으면 내장 스킨 3종만 쓰인다)
python3 render_carousel.py carousel.json out
```
- 산출: `out/{prefix}-01..NN.jpg`, `out/contact.png`, `out/render_report.json`.

## STEP 7. 자가검수 (지침 I-5 — 7항목 전부)
1. **① 숫자 전수 대조**: `carousel.json`·`caption.txt`의 모든 숫자 토큰(`[0-9][0-9.,/~:]*`)을 뽑아 `post_text.txt`에 존재하는지 확인한다. 페이지 번호·연도 표기(`YYYY.M.D 기준`)·`n/9`는 제외. 하나라도 없으면 `R-NUM`.
2. **②** `render_report.json.overflow`가 비어 있고, `contact.png`를 `Read`로 열어 겹침·잘림이 없는지 본다.
3. **③~⑦** 지침 I-5 표대로 판정한다.
4. 반려가 있으면 STEP 5로 돌아가 **1회만** 수정·재렌더한다. 다시 실패하면 게시하지 않고 `ledger.posts.{slug} = {status:"held", held:"R-…"}` 기록 후 STEP 8→11로 간다(파일은 남긴다).

## STEP 8. PC 저장
- `device_commit_files`로 `instagram\{TODAY}\{slug}\`에 `carousel.json caption.txt alts.json hub_card.json *.jpg contact.png render_report.json post_text.txt`를 저장한다.
- `meta.json`을 쓴다: `{blog_post_id, blog_url, blog_modified_at_build, slides, status:"ready"|"held", checks:{...}}`.

## STEP 9. 인스타 컨테이너 준비 (PC · 릴레이)
```bash
cd "$B/instagram/{TODAY}/{slug}"
# 9-1 WP 미디어 업로드 (공개 URL 확보) → wp_media.json {n:{id,url}}
curl -s -u "$U:$P" -H "Content-Disposition: attachment; filename={파일명}" -H "Content-Type: image/jpeg" --data-binary @{파일명} https://0and1life.com/wp-json/wp/v2/media
# 9-2 자식 컨테이너 9장 (alt 포함) → 9-3 각각 status가 FINISHED 될 때까지 5초 간격 확인
python3 ../../relay/ig.py container {url} "{alt}"        # → {"id": ...}
python3 ../../relay/ig.py status {child_id}
# 9-4 부모 캐러셀 → FINISHED 확인 → ig_containers.json {children[], carousel, created_utc}
python3 ../../relay/ig.py carousel caption.txt {id1,...,id9}
python3 ../../relay/ig.py status {carousel_id}
```
- 부모가 `ERROR`면 **자식 9장을 전부 새로 만들어** 1회 재시도한다(기존 자식 재사용 금지 — 2026-09-30 실측 ERROR). 다시 실패하면 `E-CONTAINER`로 알림하고 게시하지 않는다.
- `hub_card.json.thumb`에 1장 표지 URL을 채운다.

## STEP 10. 게시 관문 (지침 I-7)
**10-A `APPROVE`(기본)**: `meta.status="ready"`로 두고 STEP 11 알림을 **먼저** 보낸다(콘택트시트 경로·캡션 전문·"게시하려면 이 세션에 '게시'라고 답하세요"). 사용자가 이 세션에서 `게시`라고 답하면 10-B를 실행한다. 컨테이너는 24시간 유효 — 지나면 다음 회차가 STEP 9부터 새로 만든다(ledger `pending` 유지).
**10-B 게시 실행** (`AUTO`면 즉시):
```bash
IG_PUBLISH_APPROVED=yes python3 ../../relay/ig.py publish {carousel_id}    # → {"id": media_id}
python3 ../../relay/ig.py media {media_id}                                   # → permalink
```
1. `publish_result.json` 저장 → `ledger.posts.{slug} = {date:TODAY, status:"published", ig_media_id, ig_url, hub_card:false, skin, hook}`.
2. `hub_card.json.ig_url`에 permalink를 채우고 `python3 ../../relay/hub.py add hub_card.json` → 출력 `ok:true` 확인 → 8초 뒤 `curl -s https://0and1life.com/ig/?cb=$(date +%s) | grep -c "o1-ig-card:{slug}"`가 1 이상이면 `hub_card:true`. 아니면 1회 재시도, 실패 시 `E-HUB`(게시는 유지).
3. `log.md` 맨 위에 블록 추가: `## {TODAY} · {slug} · 게시 완료` + `WP {id} → 캐러셀 {N}장 · 컨테이너 {carousel_id} → IG {media_id} ({permalink})` + 허브 카드 결과.
4. `meta.json.status="published"`, `published_utc` 기록.

## STEP 11. 완료 알림 (앞 단계 성공 여부와 무관하게 반드시 실행)
PushNotification 1회. 첫 문장은 한 줄 요약, 그 뒤 표 형식. 모두 한글, 중요하지 않은 것은 생략.
- 게시함: `📱 인스타 캐러셀 {TODAY} — {slug} 게시 완료 · {N}장 · 허브 카드 {OK|실패} · IG {permalink}`
- 승인 대기: `📱 인스타 캐러셀 {TODAY} — {slug} 게시 준비 완료(승인 대기) · 콘택트시트 instagram\{TODAY}\{slug}\contact.png · 이 세션에 '게시'라고 답하면 올립니다`
- 대상 없음: `📱 인스타 캐러셀 {TODAY} — 대상 글 없음`
- 반려·오류: `📱 인스타 캐러셀 {TODAY} — {slug} 보류({코드}) · {한 줄 원인}`
- 덧붙이는 줄(해당 시): `🔑 토큰 갱신 {성공|실패}` · `📐 지침-루틴 상충: {조항}` · `⏳ pending {n}편` · `🎨 스킨 {이름} · 훅 {ⓐ|ⓑ|ⓒ}` · `🔍 레퍼런스 스캔 {n}편 → 새 스킨 {이름|없음}` · `🧩 템플릿 제안: {한 줄}`

---

## 🚨 오류 처리
| 상황 | 조치 |
|---|---|
| PC 미연결·pw.txt 없음 | 즉시 중단, STEP 11 알림. 폴더 접근 요청 호출 금지 |
| `me` username ≠ 0and1life | `E-TOKEN` 전면 중단(다른 계정 게시 방지) |
| 릴레이 401/404 | `E-RELAY` — 스니펫 활성·이름 확인 요청 |
| 릴레이 502(`upstream`) | 30초 후 1회 재시도 → 실패 시 준비 단계까지만 |
| 부모 컨테이너 ERROR | 자식 전부 재생성 1회 → `E-CONTAINER` |
| 허브 카드 검증 실패 | 1회 재시도 → `E-HUB`(게시 유지, 사용자에게 편집 화면 열림 여부 확인 요청) |
| Playwright 렌더 실패 | 글꼴·패키지 재설치 1회 → 실패 시 `R-LAYOUT`로 held |
| STEP W 스크린샷 타임아웃 반복·Chrome 미연결 | 그 회차 스캔을 건너뛰고 인박스는 `[ ]` 유지, STEP 11에 `🔍 레퍼런스 스캔 건너뜀` |
| 새 스킨 시험 렌더 overflow | 채택하지 않고 `skins`에 `retired:true`로만 남김 |
| 같은 날 2회 실행 | ledger에 `published`/`ready`가 있으면 STEP 3에서 제외되어 "대상 없음"으로 끝난다 |

## ⚠️ 전제조건 (사용자 몫 — 2026-09-30 기준 상태)
| 항목 | 상태 | 비고 |
|---|---|---|
| WPCode 스니펫 `ig-relay` 활성 | ✅ 8동작 전부 설치·`media` 실측 확인(2026-09-30) | `relay\wpcode_ig-relay.php`와 동일본 |
| Meta 앱 `Instar_API` · 장기 토큰 | ✅ pw.txt 보관, 계정 0and1life(MEDIA_CREATOR) 확인 | 60일 토큰, 30일마다 자동 갱신 |
| 프로필 링크 = 허브 `/ig/?utm_...=ig_bio` | ✅ 설정 완료(2026-09-30) | 모바일 앱에서만 변경 가능 |
| 허브 페이지 1922 공개·index·Rank Math 78점 | ✅ | 제목·메타는 고정, 카드만 추가 |
| Cowork 예약 `0and1life 인스타 캐러셀`(03:30 KST, PC 연결, `C:\Users\win\Documents\Claude` 연결) | ✅ 등록(2026-09-30) | 프롬프트는 이 파일 전문 — 파일을 고치면 예약 프롬프트도 같은 전문으로 교체 |
| `PUBLISH_MODE` | `APPROVE` | 샘플 3회 검토 후 사용자 지시로 `AUTO` 전환 |
