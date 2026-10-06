# Schd_0and1Life-Insta — 발행 글 → 인스타그램 릴스 제작·전달 루틴 (Cowork 예약 작업용, v3.2 2026-10-06)

**v3.2에서 바뀐 것**(지침 v3.2 대응): ① **쉬운 3초 훅**(지침 I-2-1-B) — 첫 3초는 일상어·숫자 1개 이하·문장 2개 이하, 대상은 넓게 ② **5막 구조**(쉬운 훅 → 답 하나 → 반전 → 내 경우 → CTA, 지침 I-2-0) ③ 엔진 **v12** — 콜라주 장면 `hook_story`·`story`·`cta(style: paper)`, 견본 `relay\examples\story_spec.json` ④ STEP 7 ⑨에 쉬운 말 검사 ⑤ **사용자 폴더에 백업·보관 사본을 만들지 않는다**(사용자 지시 10/6) — 엔진을 바꿀 때 이전 판은 클라우드 작업 공간에만 두고 회귀 검사에 쓴다.

**v3.1.1에서 바뀐 것**(지침 v3.1.1 대응): 허브 카드를 **전달할 때(STEP 10-3) 먼저 넣고**, 게시가 확인되면(STEP 10-5) 같은 카드에 `ig_url` 만 채운다. 근거: 10/6 사용자 지적 — 게시 당일 프로필 링크 페이지에 그 글이 없었다. 알림에 `🗂 허브 카드` 줄 추가.

**v3.1에서 바뀐 것**(지침 v3.1 대응): ① **캐릭터 없음** — 엔진 v11은 `REEL_MASCOT` 미설정 시 마스코트를 그리지 않고 소품·숫자·카드로 화면을 채운다(지침 I-3-2). `robot.py`·`clay.py` 같은 3D 캐릭터 코드는 쓰지 않는다 ② **속도** — 매 회차 spec의 `dur`·`beats` 로 비트를 앞당긴다(지침 I-3-4) ③ STEP 4.5 콘셉트에 **마케팅 장치 3개(지침 I-2-8)·새 연출 1개(지침 I-3-8)** 를 적고 `meta.json.marketing`·`meta.json.fresh` 에 기록 ④ STEP 7 자가검수 **11항목**(⑪ 속도·장치 `R-PACE`) ⑤ 효과음 `build_reel_sfx_v2.py` v2.1(부드러운 소리, 피크 -12dBFS) ⑥ CTA 화살표가 인스타 계정 이름 행을 수직으로 가리킴(엔진 처리, 지침 I-2-5④) ⑦ 알림에 `🧲 장치` `✨ 새 연출` 줄 추가.

**v3.0에서 바뀐 것**: "블로그 표 → 카드 → 모션"을 버리고 **훅 퍼스트 숏폼**으로 바꿨다. 렌더러가 `render_reel_v8.py` → **장면 엔진 `reel_engine.py`(v9)** 로, 효과음이 `build_reel_sfx.py` → **`build_reel_sfx_v2.py`(16종)** 로, 싱크 검증이 `verify_reel_sync.py` → **`verify_reel_v9.py`(싱크+0프레임+훅 시각+CTA 길이)** 로 바뀌었다. 자체 마스코트 **공일이**가 상황극을 연기한다. 매 회차 **상황극 콘셉트 3개 → 1개 선택**(STEP 4.5)이 들어왔고, 측정에 **스킵률·평균 시청시간**이 추가됐다(STEP M). 근거는 지침 v3.0 개정 이력.

⚠️ **역할 경계 — 이 루틴은 도구다.** 릴스 구성·문구·영상 문법·품질의 판정 기준(SSOT)은 전적으로 GitHub 지침 `0and1Life-Insta.md`다. 이 루틴은 **운영 절차**(언제·무엇을·어디에 기록)와 **실행 자산**(파일 경로·릴레이·스크립트·알림 형식)만 정의한다. 규칙을 가리킬 때는 조항 번호로 참조한다(예: "지침 I-2-1"). 상충이 보이면 지침을 따르고 STEP 11에 기록한다.

사람이 없는 시간에 실행된다. **사용자 승인이 필요한 도구 호출을 불필요하게 하지 않는다.** 폴더 접근 요청은 하지 않는다.

이 루틴은 **WP 글(post)의 본문·상태·슬러그·카테고리·대표이미지를 절대 바꾸지 않는다.** 쓰는 곳은 네 군데뿐이다: ① WP 미디어(릴스 mp4·커버 JPEG) ② 전달 페이지 `reel-dl-latest` ③ 허브 페이지 `page 1922` 본문(카드 1장) ④ `instagram\` 폴더. **게시된 인스타 게시물은 어떤 경우에도 삭제하지 않는다.**

- **일간 흐름(STEP 0~12)은 Chrome MCP·브라우저 조작을 쓰지 않는다.** 예외는 STEP W 주간 레퍼런스 스캔뿐이며, 이때만 Chrome MCP로 인스타를 읽는다(읽기 전용 — 좋아요·팔로우·댓글·DM 금지).
- 인스타 API는 클라우드·PC 모두 `graph.instagram.com`이 차단이라 **사이트 릴레이 `POST https://0and1life.com/wp-json/o1/v1/ig`**(WPCode 스니펫 `ig-relay`)로만 호출한다. 토큰은 헤더 `X-O1-IGT`로만 전달되고 서버에 저장되지 않는다.

⚠️ [지침 출처] `https://raw.githubusercontent.com/leejc0404/blog/main/0and1Life-Insta.md?cb={epoch_ms}` — STEP 0에서 매번 읽고 세션 내 재사용한다. 캐시버스터 없이 조회하지 않는다. 조항이 안 보이면 Draft 지침 5-0-A 3단 검증을 준용하고, 그래도 없으면 전달하지 않고 알림한다. **요약 모델을 거치는 `web_fetch` 대신 `curl` 로 원문을 받아 전체를 읽는다.**

---

## 실행 자산 (경로·스크립트)

| 무엇 | 어디 | 비고 |
|---|---|---|
| 자격증명 | `C:\Users\win\Documents\Claude\pw.txt` | `ONEANDZERO_WP_USER` `ONEANDZERO_WP_APP_PASSWORD` `IG_USER_ID` `IG_ACCESS_TOKEN` — **값 출력 금지** |
| 릴레이 호출 | `instagram\relay\ig.py` | `me / limit / refresh / container / carousel / reel / status / media / publish / insights / my_media` |
| **장면 엔진 v12** | `instagram\relay\reel_engine.py` | `reel_spec.json` → mp4(무음) + `_timeline.json` + `_cover.jpg` · `--stills <dir>` 로 장면별 대표 프레임 · **캐릭터 없음 레이아웃이 기본**(`REEL_MASCOT=gongil` 은 과거 회차 재현에만) |
| **효과음 v2.1** | `instagram\relay\build_reel_sfx_v2.py` | `_timeline.json` → wav (16종, 전부 합성음 · 노이즈·사각파 없음 · 피크 -12dBFS) |
| **검증 v9** | `instagram\relay\verify_reel_v9.py` | `reel_spec.json` 검사 · 종료코드 0만 통과 (싱크·0프레임·훅 사건 시각·CTA·총 길이) |
| 견본 spec | `instagram\relay\examples\bank_spec.json` | v9 첫 시안(은행 영업시간 편) — 장면 유형별 필드 예시 |
| **전달 페이지** | `instagram\relay\make_dl_page.py` | `handoff.json` → `reel-dl-latest` 덮어쓰기 |
| **임시 자산 정리** | `instagram\relay\cleanup_reel_temp.py` | 3일 경과분 휴지통 |
| 허브 카드 | `instagram\relay\hub.py` | `add <card.json>` · `seo <seo.json>` · `get` |
| 원장 | `instagram\ledger.json` | `reels.{slug}: {date, status, ig_media_id, ig_url, hub_card, video_media_id, cover_media_id, dur, scenes, hook_type, stage, concept}` |
| **성과 기록** | `instagram\metrics.json` | `{slug: {posted, dur, hook_type, stage, daily: {YYYY-MM-DD: {...}}}}` |
| 레퍼런스 | `instagram\refs\inbox.md` · `refs\{YYYY-Www}.md` | |
| 회차 폴더 | `instagram\{YYYY-MM-DD}\{slug}\` | `reel_spec.json` `concepts.md` `caption.txt` `reel-final.mp4` `*_cover.jpg` `*_timeline.json` `stills.jpg` `meta.json` `wp_media.json` `handoff.json` |
| (구) v8 자산 | `render_reel_v8.py` `build_reel_sfx.py` `verify_reel_sync.py` | **사용 중지.** 지우지 않고 남겨 둔다(과거 회차 재현용) |
| 엔진 이전 판 | (만들지 않음 — v3.2) | 사용자 지시(10/6)로 사용자 폴더에 백업·이전 판 사본을 만들지 않는다. 회귀 검사용 이전 판은 클라우드 작업 공간에만 둔다 |

설정값: `PUBLISH_MODE = HANDOFF`(기본) · `DAILY_TARGET = 1` · `LOOKBACK_DAYS = 3` · `TOKEN_REFRESH_DAYS = 30` · `IG_API = v23.0` · `REF_SCAN_DAY = 월요일`(KST) · `REF_MAX_POSTS = 6` · `TEMP_KEEP_DAYS = 3` · `CONCEPTS = 3` · `MARKETING_MIN = 3`(지침 I-2-8) · `REEL_MASCOT` **설정하지 않음**

---

## STEP W. 주간 레퍼런스 스캔 (지침 I-3-7 — 월요일 또는 인박스에 미처리 링크가 있을 때만 · Chrome MCP 읽기 전용)

1. **수집 목록**(최대 `REF_MAX_POSTS`): ① `refs/inbox.md`의 `- [ ]` 줄 ② 벤치 계정 최근 **릴스** ③ 탐색·해시태그 상위의 **정보형 릴스**. 지침 I-3-7 "고를 기준"으로 거른다.
2. **읽기 방법**: `…/reel/{code}/` 로 URL 이동 → 5초 대기 → 스크린샷. 30초 타임아웃이면 같은 URL로 1회 재시도, 그래도 실패하면 건너뛴다. 반응 수치는 `get_page_text`로 읽는다. **인스타 화면에서 클릭은 페이지 이동에만 쓴다.**
3. **기록**: `refs/{YYYY-Www}.md`에 지침 I-3-7 "추출 8항목" + 반응 수치 + "차용할 것 / 복제하지 않을 것"을 쓴다. 처리한 인박스 줄은 `[x]`로 바꾼다.
4. **주간 비교**(지침 I-8-3): `metrics.json` 에서 훅 공식별 최신 스킵률 평균을 내 같은 파일 끝에 표로 적는다.
5. **반영**: 새 형식은 지침 I-2-2 표 **행 추가 제안**으로 STEP 11에 남긴다(`🧩 형식 제안`). ⛔ 지침 I-3-5 — 밈·영상의 **이미지·캐릭터·클립·음원 자체는 복제하지 않는다.** 차용은 편집 형식까지다.
6. 열었던 탭은 모두 닫는다.

## STEP 0. 지침 읽기·설정 확인
1. 지침을 `curl -s "...0and1Life-Insta.md?cb=$(date +%s%3N)"` 로 받아 **전체를** 읽는다. Phase I-0~I-9와 반려 코드표가 모두 보이는지, 개정 이력 첫 줄이 **v3.2 이상**인지 확인한다. v3.0~3.1이면 I-2-1-B(쉬운 3초)·5막 구조가 없다 — 이 루틴의 v3.2 항목은 그대로 수행하고 알림에 `📐 지침 v3.2 미배포` 한 줄만 남긴다. v2.x면 **전달하지 않고** 알림(`📐 지침 v3 미배포`).
2. 설정값을 세션 변수로 둔다. `PUBLISH_MODE`는 이 프롬프트의 값이 기준이며 지침·ledger에서 바꾸지 않는다.

## STEP 1. 날짜·폴더·자격증명
```bash
TODAY=$(TZ=Asia/Seoul date +%F); D1=$(TZ=Asia/Seoul date -d "yesterday" +%F); D3=$(TZ=Asia/Seoul date -d "3 days ago" +%F)
B="$HOME/mnt/Claude"; R="$B/instagram/relay"
ls "$B/pw.txt" "$R/ig.py" "$R/hub.py" "$R/reel_engine.py" "$R/build_reel_sfx_v2.py" \
   "$R/verify_reel_v9.py" "$R/make_dl_page.py" "$R/cleanup_reel_temp.py" >/dev/null || echo "MISSING"
for k in ONEANDZERO_WP_USER ONEANDZERO_WP_APP_PASSWORD IG_USER_ID IG_ACCESS_TOKEN; do grep -q "^\(\xef\xbb\xbf\)\?$k=" "$B/pw.txt" && echo "$k=있음" || echo "$k=없음"; done
[ -f "$B/instagram/ledger.json" ] || echo '{"token_refreshed":"","reels":{}}' > "$B/instagram/ledger.json"
[ -f "$B/instagram/metrics.json" ] || echo '{}' > "$B/instagram/metrics.json"
```
- `MISSING`이거나 키가 하나라도 `없음`이면 중단·알림. 폴더 접근 요청은 호출하지 않는다.
- pw.txt는 BOM과 값 내 공백이 있다 — `cred()`만 쓰고 `source`하지 않는다.

## STEP 2. 토큰·계정·한도 확인
```bash
cd "$R" && python3 ig.py me && python3 ig.py limit
```
- `me.username`이 `0and1life`가 아니면 **전면 중단**(`E-TOKEN`). 401/404면 `E-RELAY`.
- `ledger.token_refreshed`가 `TOKEN_REFRESH_DAYS`보다 오래됐으면 `ig.py refresh` → `access_token`을 pw.txt에 **교체 저장**(sed, 값 출력 금지) → `me` 재확인 → `token_refreshed=TODAY`. 실패해도 계속 진행하고 STEP 11에 기록.

## STEP M. 일간 성과 측정 (지침 I-8-1 — 대상 글 유무와 무관하게 매 회차 실행)
```bash
cd "$R" && python3 ig.py my_media 25
python3 ig.py insights {media_id} views,reach,likes,comments,shares,saved,total_interactions,ig_reels_avg_watch_time,ig_reels_video_view_total_time
python3 ig.py insights {media_id} reels_skip_rate
```
1. `ledger.reels` 중 `status="posted"` 인 전 회차를 대상으로 한다(게시 후 30일까지). `my_media` 에 있는데 ledger에 `posted` 가 없는 릴스는 permalink로 slug를 찾아 `posted` 로 고친다(사용자가 게시 후 알리지 않은 경우).
2. `metrics.json`의 `{slug}.daily[TODAY]`에 기록: `views, reach, likes, comments, shares, saved, avg_watch_ms, skip_rate, total_watch_ms`. **덮어쓰지 말고 날짜별로 누적**한다. 같은 날 두 번 재면 나중 값으로 그날 칸만 갱신한다.
3. `profile_visits` 는 릴스에서 API 미지원이라 조회하지 않는다.
4. `insights`가 `bad_action`이면 스니펫 미배포다 — 측정을 건너뛰고 STEP 11에 `📊 측정 건너뜀(스니펫 insights 미배포)` 한 줄만 남긴다. 중단하지 않는다.
5. **해석은 지침 I-8-2·I-8-3에 따른다.** 매일은 수치만 쌓고, 알림에 **가장 최근 게시 릴스의 스킵률·평균 시청**만 한 줄로 싣는다(`📊 {slug} 스킵 {n}% · 평균 {n.n}초`). v3 1차 목표(지침 I-8-2)를 넘으면 `🎯` 를 붙인다.

## STEP 3. 대상 글 선정 (지침 I-1)
```bash
curl -s "https://0and1life.com/wp-json/wp/v2/posts?status=publish&after=${D3}T00:00:00&before=${D1}T23:59:59&per_page=20&orderby=date&order=desc&_fields=id,slug,date,modified,title,categories,link"
```
1. 지침 I-1-1·I-1-3 순서로 판정한다(`ledger.reels` 의 `pending` 은 후보에 포함, 그 밖의 상태는 `X-LEDGER`). `X-THIN`은 STEP 4에서 확정.
2. 우선순위 I-1-4로 1편 선정. 나머지는 `ledger.reels.{slug}.status="pending"`으로만 기록.
3. 대상이 없으면 `log.md`에 한 줄 남기고 **STEP 12 → STEP 11**로 간다(정리와 측정은 대상이 없어도 돈다).
4. 회차 폴더 `instagram\{TODAY}\{slug}\` 생성.

## STEP 4. 본문 최종본 확보·구조 추출
```bash
curl -s "https://0and1life.com/wp-json/wp/v2/posts/{ID}?_fields=id,slug,title,date,modified,content,categories,featured_media" -o post.json
```
- 추출: 제목, Core Fact / Primary Insight / Actionable Tip, 모든 `<table>`, H2 목록(⭐ GAP H2), "근데/다만/함정/실제 예" 문단, `📌`/`*핵심 :` 요약 줄, 출처 명칭, `modified`, 잠정·예정 표현.
- HTML을 벗긴 **본문 전체 텍스트**를 `post_text.txt`로 저장(STEP 7 숫자 대조용).
- `<table>` 0개이고 Core Fact에 수치가 없으면 `X-THIN` — ledger 기록 후 다음 후보로(1회).

## STEP 4.5. 훅 기획 — 콘셉트 3개 → 1개 (지침 I-0 · I-2-2 · I-3-6)
1. 세 가지를 고른다(지침 I-0·I-2-0): ⓐ **쉬운 질문 1개** — 이 글을 누구나 아는 말로 물으면?(지침 I-2-1-B, 예: "밥값 20만원, 세금 안 붙는 거 알아요?") ⓑ **답 하나** — 영상만 보고도 써먹을 한 줄(예: "명세서 '식대' 칸 확인") ⓒ **가장 의외인 사실 1개** — 뉴스 제목이 말하지 않는 숫자, 본문 "근데/함정" 문단. 이것이 ③ 반전이 된다.
2. **페르소나**를 한 문장으로 → `reel_spec.json` 최상위 `persona`. 훅의 대상 스티커는 **넓게**("월급 받는 사람이라면") — 좁은 조건은 ④에서(지침 I-2-2).
3. **훅 콘셉트 `CONCEPTS`개**를 `concepts.md` 에 쓴다. 콘셉트마다: 훅 공식(지침 I-2-2, 기본은 '쉬운 질문'·'몰랐던 사실') · **0~3초 글자 전부**(지침 I-2-1-B 검사용) · 무대 · 0초 화면 한 줄(캐릭터 없이 무엇으로 아래 절반을 채우나 — 지침 I-3-2) · 사건(몇 초에 무엇이 바뀌나, ≤0.8초) · 리액션(집중선·펀치·흔들림·"!?") · tease · **마케팅 장치 `MARKETING_MIN`개 이상**(지침 I-2-8 표에서) · **이번 회차에 처음 쓰는 연출 1개**(지침 I-3-8) · 이 페르소나가 넘기지 않을 이유. **세 개는 공식이나 무대가 서로 달라야 한다.**
4. `ledger.reels` 최근 2회차의 `hook_type`·`stage` 를 읽어 **직전 회차와 같은 공식·같은 무대는 고르지 않는다**(지침 I-3-6). 이번 주 `refs/{YYYY-Www}.md` 의 스킵률 비교가 있으면 나쁜 공식을 피한다.
5. 1개를 고르고 이유를 `meta.json.hook = {type, stage, concept, why}` 에 적는다. 고른 콘셉트의 장치를 `meta.json.marketing = ["열린 고리", "내 경우는?", …]`, 새 연출을 `meta.json.fresh = "한 줄"` 에 적는다.
6. 기존 장면 유형으로 안 되면 **엔진 확장**(지침 I-3-6): 클라우드 작업 사본 `reel_engine.py` 에 무대·장면·소품·효과음을 추가한다(캐릭터·포즈는 추가하지 않는다 — 지침 I-3-2). 추가했으면 STEP 6에서 클라우드에 둔 **이전 판 엔진과 `regress_engine.py`** 로 견본 spec(`examples\bank_spec.json`·`examples\story_spec.json`)과 직전 3회차 spec을 비교해 기존 결과가 그대로인지 확인하고, STEP 8에서 `relay\reel_engine.py` 를 덮어쓴다. **사용자 폴더에 이전 판 사본·백업을 만들지 않는다.**

## STEP 5. 원고 작성 → `reel_spec.json` · `caption.txt`
- 지침 I-2(5막·쉬운 3초·0프레임·숫자 복사·날짜·잠정 표시·유도 4곳·화자·**I-2-8 마케팅 장치**)와 I-4(캡션)를 그대로 적용한다. 캡션 7번 줄에는 보낼 사람과 나중에 꺼내 볼 순간을 함께 적는다.
- `reel_spec.json` 구조 — 장면 유형별 필드는 지침 I-3-3 표, 실제 예시는 `examples\story_spec.json`(v12 기본) · `examples\bank_spec.json`(v9 4막, 과거형):
  ```json
  {"source": "{원문 명칭} · {modified YYYY.M.D} 기준", "persona": "...", "structure": "쉬운 훅/답 하나/반전/내 경우/CTA",
   "scenes": [ {"type":"hook_story", "bg":"paper", "series":"{시리즈} 0n", "dur":2.8, "beats":{"start":[0,"pop"],"trigger":[0.5,"ding"],"react":[0.8,"scratch"],"tease":[1.4,"pop"]}, "els":[...]},
               {"type":"story", "bg":"paper", ...(답 하나)}, {"type":"story", "bg":"dark", ...(반전 · blog_note)},
               {"type":"story", ...(checks — 내 경우는?)}, {"type":"cta", "style":"paper", "btn":"프로필 링크 → 맨 위 글", "handle":"@0and1life", ...} ]}
  ```
  - 장면 5~6개, 총 12~16초(지침 I-2-0). 훅 2.4~3.0초·CTA **4.0초**(줄이지 않음). **엔진 기본 `BEATS` 는 느리다(v9 값) — 매 회차 장면마다 `"dur"` 와 `"beats": {"이름": [시각, "효과음"]}` 로 앞당긴다**(지침 I-3-4: 훅 사건 ≤0.8초, 본론 장면 1.6~2.8초, 0.1초 격자). 참고값 — hook_pov `trigger 0.5 · react 0.8 · slam 0.9 · tease 1.6`, slam `label 0.3 · sub 0.7`, versus `right 0.1 · vs 0.3 · delta 0.8 · blog 1.5`, checklist `i0 0.0 · i1 0.2 · i2 0.4 · i3 0.6 · verdict 1.2 · blog 1.8`, cta `h2 0.1 · lock 0.4 · pt0 0.7 · pt1 0.9 · btn 1.2 · handle 1.6`.
  - `mascot` `pose` `mascot_x` `mascot_scale` `mascot_xy` 필드는 쓰지 않는다(써도 무시됨).
  - ③·④ 장면 중 하나에 `blog_note`. CTA(`style: paper`)에는 `doc`(흐린 자료 문서 + `lock_at`) 요소와 `disclaimer` 를 대신하는 `text` 요소(잠정·YMYL 한 줄) 필수.
  - 훅 장면(`hook_story`)의 글자는 지침 I-2-1-B를 지킨다 — 제도 용어 없음, 숫자 1개 이하, 문장 2개 이하.
  - 커버 시점을 바꿀 때만 최상위 `cover_at`(초).
- `caption.txt`는 지침 I-4-1 순서를 그대로 따른다.
- `hub_card.json`: `slug, title, date, category, thumb(커버 URL — STEP 9에서 채움), ig_url(게시 후), points[2~3]`.

## STEP 6. 렌더 (클라우드)
```bash
mkdir -p ~/ig_work && cd ~/ig_work && (ls package/dist/public/static/alternative >/dev/null 2>&1 || (npm pack pretendard@1.3.9 >/dev/null && tar xzf pretendard-1.3.9.tgz))
export PRETENDARD_DIR=~/ig_work/package/dist/public/static/alternative
# reel_engine.py · build_reel_sfx_v2.py · verify_reel_v9.py · examples/bank_spec.json 을 PC relay 폴더에서 device_stage_files 로 가져온다
python3 verify_reel_v9.py reel_spec.json                         # 먼저 검사 (렌더 전에 실패를 잡는다)
python3 reel_engine.py reel_spec.json --stills stills            # 장면별 0초·중간·끝 프레임 PNG
python3 reel_engine.py reel_spec.json reel-final.mp4             # → mp4(무음) + _timeline.json + _cover.jpg
python3 build_reel_sfx_v2.py reel-final_timeline.json sfx.wav
ffmpeg -y -v error -i reel-final.mp4 -i sfx.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 160k -ar 44100 -shortest -movflags +faststart reel-final-sfx.mp4
mv reel-final-sfx.mp4 reel-final.mp4
```
- **stills를 먼저 보고 고친 뒤** 본 렌더를 돌린다(본 렌더는 14초 기준 약 1분). stills 단계에서 겹침·잘림·**아래 절반이 빈 장면**(지침 I-3-2)을 잡는다. `REEL_MASCOT` 환경변수를 설정하지 않는다.
- 산출: `reel-final.mp4`(효과음 포함), `reel-final_cover.jpg`(훅 `slam` 직후 자동 추출), `reel-final_timeline.json`, `stills\`.

## STEP 7. 자가검수 (지침 I-5 — 11항목 전부)
```bash
python3 verify_reel_v9.py reel_spec.json     # 종료코드 0 이어야 통과
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate -show_entries format=duration reel-final.mp4
for t in 0.0 0.5 1.0 1.5 2.5; do ffmpeg -y -v error -ss $t -i reel-final.mp4 -frames:v 1 -vf scale=360:-1 hook_$t.jpg; done
```
1. **① 숫자 전수 대조**: `reel_spec.json`·`caption.txt`의 모든 숫자 토큰을 뽑아 `post_text.txt`에 있는지 확인. 기준일 표기·장면 길이·beats 시각은 제외. 하나라도 없으면 `R-NUM`.
2. **② 안전영역** · **⑩ 겹침·빈 곳**: `stills\` 전부를 한 장으로 이어 붙여 `Read`로 본다. 글자가 지침 I-3-1 범위 밖이거나(CTA 화살표 머리는 예외), 글자끼리·글자와 소품이 겹쳐 안 읽히거나, 화면 아래 절반이 빈 장면이 있으면 `R-SAFE`/`R-TYPO`.
3. **③ 규격**: 1080×1920 · 30fps · 12~20초(목표 12~16) · 오디오 트랙 · 효과음 피크 ≤ -12dBFS(`ffmpeg -af volumedetect`). 아니면 `R-SPEC`.
4. **④ 커버**: `_cover.jpg`를 `Read`로 열어 사건·자막이 다 보이는지. 아니면 `cover_at` 조정 → `R-COVER`.
5. **⑤ 날짜·잠정** — 지침 I-2-4. **⑥ 유도 4곳** — 지침 I-2-5.
6. **⑦ 화자·금지어·저작권** — 지침 I-2-6 · I-2-7 · I-3-5. 실존 기관·기업 로고·간판 문구가 무대에 없는지 본다.
7. **⑧ 싱크** 🚨 · **⑨ 훅** 🚨: `verify_reel_v9.py` 가 실패하면 **즉시 중단**(`R-SYNC`/`R-HOOK`). 추가로 `hook_0.0~2.5.jpg` 5장을 `Read`로 보고, **"이 페르소나가 0.5초 안에 넘기지 않을 이유"를 한 문장으로** `meta.json.checks.hook` 에 쓴다. 한 문장이 안 나오면 `R-HOOK`. 훅의 첫 사건(`trigger`/`m2`/`lock`/`stamp`/`check`)이 0.8초보다 늦어도 `R-HOOK`. **쉬운 3초 검사**(지침 I-2-1-B): 훅 장면 spec의 글자를 모두 뽑아 제도 용어 목록(비과세·통상임금·기준소득월액·보수월액·원천징수·결정세액·비급여·본인부담률 등)이 있거나, 숫자 토큰이 2개 이상이거나, 문장이 3개 이상이면 `R-HOOK`. 통과하면 "초등학교 고학년이 이해하는가"를 한 문장으로 `meta.json.checks.easy` 에 쓴다.
8. **⑪ 속도·장치**: `_timeline.json` 과 spec으로 본론 장면(CTA 제외)이 전부 ≤2.8초인지, `meta.json.marketing` 이 `MARKETING_MIN`개 이상이고 각 장치가 실제 장면·캡션에 있는지, `meta.json.fresh` 가 비어 있지 않은지 본다. 아니면 `R-PACE` — beats·spec 수정 1회.
9. 반려가 있으면 STEP 4.5(콘셉트 2순위) 또는 STEP 5로 돌아가 **1회만** 수정·재렌더. 다시 실패하면 전달하지 않고 `ledger.reels.{slug} = {status:"held", held:"R-…"}` 기록 후 STEP 8 → 12 → 11.

## STEP 8. PC 저장
- `device_commit_files`로 `instagram\{TODAY}\{slug}\`에 `reel_spec.json concepts.md caption.txt reel-final.mp4 reel-final_cover.jpg reel-final_timeline.json hub_card.json post_text.txt meta.json`과 `stills\` 를 이어 붙인 `stills.jpg` 1장을 저장한다.
- `meta.json`: `{blog_post_id, blog_url, blog_modified_at_build, persona, hook:{type,stage,concept,why}, marketing:[장치...], fresh:"새 연출 한 줄", scenes:[유형...], dur, engine:"v11.x", status:"ready"|"held", checks:{num,safe,spec,cover,date,link,voice,sync,hook,typo,pace}}`.
- 엔진을 확장했다면(STEP 4.5-6) 회귀 검사 통과 후 `relay\reel_engine.py` 를 덮어쓴다. 이전 판 사본은 사용자 폴더에 만들지 않는다.

## STEP 9. WP 업로드 (PC)
```bash
cd "$B/instagram/{TODAY}/{slug}"
curl -s -u "$U:$P" -H "Content-Disposition: attachment; filename=reel-{slug}-final.mp4" -H "Content-Type: video/mp4" \
     --data-binary @reel-final.mp4 https://0and1life.com/wp-json/wp/v2/media
curl -s -u "$U:$P" -H "Content-Disposition: attachment; filename=reel-{slug}-cover.jpg" -H "Content-Type: image/jpeg" \
     --data-binary @reel-final_cover.jpg https://0and1life.com/wp-json/wp/v2/media
```
- 파일명은 반드시 `reel-` 로 시작하고 `-final.mp4` / `-cover.jpg` 로 끝나야 한다 — STEP 12 정리 대상 판별 기준이다.
- 결과를 `wp_media.json {video:{id,url}, cover:{id,url}}`에 저장하고 `hub_card.json.thumb`에 커버 URL을 채운다.
- 업로드 후 `curl -s -o /dev/null -w "%{http_code}" {url}` 로 200을 확인한다(프록시 `Connection Established` 줄에 속지 않는다). 실패하면 `E-UPLOAD`.

## STEP 10. 전달 (지침 I-7-1 · `PUBLISH_MODE=HANDOFF`)
```bash
cd "$R" && python3 make_dl_page.py {회차폴더}/handoff.json
```
`handoff.json`은 슬러그를 **항상 `reel-dl-latest`** 로 둔다(구글 문서가 가리키는 고정 주소 — 새로 만들지 않고 덮어쓴다).
```json
{"slug":"reel-dl-latest","title":"0and1life 릴스 저장 (최신)",
 "items":[{"label":"{글 제목}","note":"{길이}초 · 훅 {공식}","video_url":"{wp_media.video.url}",
           "filename":"0and1life-reel-{slug}.mp4","caption_file":"{회차폴더}/caption.txt"}]}
```
1. 생성된 페이지 URL이 200인지, `download=` 속성과 복사 버튼이 각각 들어갔는지 `curl | grep -c`로 확인한다. 실패하면 `E-PAGE` — 알림에 영상 URL을 직접 실어 대체한다.
2. `ledger.reels.{slug} = {date:TODAY, status:"handoff", video_media_id, cover_media_id, dur, scenes, hook_type, stage, concept, marketing, fresh, hub_card:false}`.
3. **허브 카드 먼저 추가 (지침 I-6 v3.1.1)**: `hub_card.json` 의 `thumb`(STEP 9 커버 URL)을 확인하고 `ig_url` 은 빈 값으로 둔 채 `python3 hub.py add {회차폴더}/hub_card.json` → 8초 뒤 `curl -s https://0and1life.com/ig/?cb=$(date +%s) | grep -c "o1-ig-card:{slug}"` ≥ 1 이면 `ledger.reels.{slug}.hub_card="no_ig_url"`, 아니면 1회 재시도 후 `E-HUB`(전달은 유지). 알림에 `🗂 허브 카드 추가` 한 줄.
4. STEP 11 알림에 **전달 페이지 URL 하나만** 싣는다.
5. **사용자가 게시했다고 알리면** (같은 세션 또는 다음 회차 STEP M에서 자동 확인):
   ```bash
   python3 ig.py my_media 5      # 최근 게시물에서 permalink·media_id 확보
   ```
   → `ledger.reels.{slug}.status="posted"`, `ig_media_id`, `ig_url` 기록 → `metrics.json.{slug}` 에 `posted, dur, hook_type, stage` 기록 → `hub_card.json.ig_url` 채우고 `python3 hub.py add hub_card.json`(같은 slug 교체 — `ig_url` 만 채워진다) → 8초 뒤 `curl -s https://0and1life.com/ig/?cb=$(date +%s) | grep -c "o1-ig-card:{slug}"` ≥ 1 이면 `hub_card:true`, 아니면 1회 재시도 후 `E-HUB`.

**`PUBLISH_MODE=AUTO` (예외 — 사용자가 그 회차에 명시 지시했을 때만)**
```bash
python3 ig.py reel {video_url} caption.txt {cover_url}   # → creation_id
python3 ig.py status {creation_id}                        # FINISHED 까지 5초 간격
IG_PUBLISH_APPROVED=yes python3 ig.py publish {creation_id}
```
- `bad_action`이면 스니펫에 `reel` 미배포다 → `E-REEL` 기록 후 **HANDOFF로 전환해 계속 진행**한다.
- ⚠️ AUTO로 올리면 **유행 음원이 붙지 않는다.** 기본값으로 두지 않는다.

## STEP 11. 완료 알림 (앞 단계 성공 여부와 무관하게 반드시 실행)
PushNotification 1회. 첫 문장은 한 줄 요약, 그 뒤 줄들. 모두 한글.
- 전달함: `📱 인스타 릴스 {TODAY} — {slug} 준비 완료 · {길이}초 · 훅 {공식}/{무대} · 검증 통과 · 저장 https://0and1life.com/reel-dl-latest/`
- 대상 없음: `📱 인스타 릴스 {TODAY} — 대상 글 없음`
- 반려·오류: `📱 인스타 릴스 {TODAY} — {slug} 보류({코드}) · {한 줄 원인}`
- 덧붙이는 줄(해당 시): `🎬 콘셉트: {고른 콘셉트 한 줄}` · `🧲 장치: {장치 이름 나열}` · `✨ 새 연출: {meta.fresh}` · `📊 {slug} 스킵 {n}% · 평균 {n.n}초 {🎯}` · `🔑 토큰 갱신 {성공|실패}` · `🗑 임시 자산 {n}건 정리` · `⏳ pending {n}편` · `🔍 레퍼런스 스캔 {n}편` · `🧩 엔진 확장: {무엇}` · `🧩 형식 제안: {한 줄}` · `📐 지침-루틴 상충: {조항}`

## STEP 12. 임시 자산 정리 (지침 I-9 — 대상 글 유무와 무관하게 매 회차)
```bash
cd "$R" && python3 cleanup_reel_temp.py --days 3 --dry    # 먼저 목록 확인
python3 cleanup_reel_temp.py --days 3                      # dry 목록에 대상이 있을 때만
```
- 대상: 슬러그가 `reel-dl-` 로 시작하는 페이지(단 `reel-dl-latest`는 **제외 — 고정 주소**), 파일명이 `reel-*-final.mp4` / `reel-*-cover.jpg` 인 미디어 중 **생성 후 3일 경과분**.
- **휴지통으로만 보낸다.** `force` 영구 삭제는 어떤 경우에도 하지 않는다.
- `ledger.reels`에 `status="posted"` 기록이 없는 회차의 미디어는 **보류**하고 알림에 남긴다.
- 정리 건수를 STEP 11에 `🗑 임시 자산 {n}건 정리`로 붙인다.

---

## 🚨 오류 처리

| 상황 | 조치 |
|---|---|
| PC 미연결·pw.txt 없음 | 즉시 중단, STEP 11 알림. 폴더 접근 요청 금지 |
| 작업 중 PC 연결이 끊김 | 클라우드 산출물은 그대로 두고 30초 뒤 1회 재시도 → 실패 시 STEP 11에 "PC 저장·업로드 미완료, 영상은 세션에 있음" 기록 |
| 지침이 v3.0 미만 | 전달하지 않고 `📐 지침 v3 미배포` 알림 |
| `me` username ≠ 0and1life | `E-TOKEN` 전면 중단(다른 계정 게시 방지) |
| 릴레이 401/404 | `E-RELAY` — 스니펫 활성·이름 확인 요청 |
| 릴레이 502(`upstream`) | 30초 후 1회 재시도 → 실패 시 준비 단계까지만 |
| `insights` `bad_action` | 측정만 건너뛰고 계속 진행 (`📊 측정 건너뜀`) |
| `reel` `bad_action` (AUTO 시도 시) | `E-REEL` 기록 후 HANDOFF로 전환해 계속 |
| **`verify_reel_v9.py` 실패** | 🚨 `R-SYNC`/`R-HOOK` — **전달 중단.** 장면 `beats`·콘셉트 수정 → 재렌더 → 재검사 |
| 본론 장면 >2.8초 · 장치 <3개 · `fresh` 없음 | `R-PACE` — spec `dur`·`beats`·콘셉트 수정 1회 → 재렌더. 다시 실패면 held |
| stills에서 아래 절반이 빈 장면 | `R-TYPO` — 지침 I-3-2대로 소품·숫자·카드 확대(엔진 기본 레이아웃이 처리하므로 보통 spec 내용 보강으로 해결) |
| 엔진 확장 후 견본 spec 검사 실패 | `E-ENGINE` — 확장을 되돌리고 기존 장면 유형으로 재구성 |
| 렌더·효과음·먹싱 실패 | 글꼴 재설치 1회 → 실패 시 `E-RENDER`로 held |
| 전달 페이지 생성 실패 | `E-PAGE` — 알림에 영상 URL 직접 기재 |
| 허브 카드 검증 실패 | 1회 재시도 → `E-HUB`(게시 유지) |
| STEP W 스크린샷 타임아웃 반복 | 그 회차 스캔 건너뜀, 인박스 `[ ]` 유지 |
| 같은 날 2회 실행 | ledger에 `handoff`/`posted`가 있으면 STEP 3에서 제외되어 "대상 없음"으로 끝난다 |

## ⚠️ 전제조건 (사용자 몫 — 2026-10-03 기준)

| 항목 | 상태 | 비고 |
|---|---|---|
| 지침 `0and1Life-Insta.md` **v3.2** GitHub 커밋 | ⬜ **커밋 필요**(blog 폴더에 전문 저장됨, 2026-10-06) | STEP 0이 v3.0 미만이면 전달하지 않는다, v3.0~3.1이면 이 루틴의 v3.2 항목을 그대로 수행하고 알림에 `📐 지침 v3.2 미배포` 한 줄 |
| 엔진 v12 `relay\reel_engine.py` · 효과음 v2.1 `build_reel_sfx_v2.py` · `verify_reel_v9.py` · `regress_engine.py` · `examples\bank_spec.json` · `examples\story_spec.json` | ✅ 2026-10-06 PC 저장(v12 — 기존 장면 회귀 동일 확인) | 없으면 STEP 1에서 `MISSING` |
| WPCode 스니펫 `ig-relay` v1.2 (`reel`·`insights`·`my_media`) | ✅ 동작 확인(2026-10-02 insights 응답) | |
| Meta 앱 · 장기 토큰 | ✅ pw.txt 보관, 0and1life(MEDIA_CREATOR) | 60일 토큰, 30일마다 자동 갱신 |
| 프로필 링크 = 허브 `/ig/?utm_...=ig_bio` | ✅ | 모바일 앱에서만 변경 가능 |
| 허브 페이지 1922 공개·index | ✅ | 제목·메타 고정, 카드만 추가 |
| 전달 페이지 `reel-dl-latest` | ✅ page 1980 | 구글 문서가 가리키는 고정 주소 — 삭제 금지 |
| Cowork 예약 `0and1life 인스타 릴스`(03:30 KST, PC 연결, `C:\Users\win\Documents\Claude` 연결) | ✅ 2026-10-03 v3.1 전문으로 교체(이름도 '인스타 릴스'로) | 다음 개정 때 이 파일 전문으로 다시 교체 |
| `PUBLISH_MODE` | `HANDOFF` | 유행 음원 때문에 기본은 반자동. AUTO는 회차별 지시로만 |

## Cowork 원라이너

토큰 확인(2) → **전 회차 스킵률·평균 시청 측정(M)** → 대상 글 1편(3) → 본문 최종본(4) → **쉬운 질문 + 답 하나 + 의외인 사실 1개 → 훅 콘셉트 3개(장치 3개·새 연출 1개 포함) → 1개(4.5)** → 쉬운 훅/답 하나/반전/내 경우/CTA 원고·캡션, 비트 앞당김(5) → 검사 → stills(빈 곳 확인) → 엔진 v12 렌더 + 효과음 v2.1 + 커버(6) → **자가검수 11항목, 싱크·훅 실패면 무조건 중단(7)** → PC 저장(8) → WP 업로드(9) → `reel-dl-latest` 덮어쓰기(10) → 알림에 URL 하나(11) → 3일 지난 임시 자산 정리(12). 통과 못 하면 **전달하지 말고** held로 남긴다.
