# Schd_0and1Life-Insta — 발행 글 → 인스타그램 릴스 제작·전달 루틴 (Cowork 예약 작업용, v3.11 2026-10-16)

**v3.11에서 바뀐 것**(지침 v3.11 대응 — 10/16 사용자 검수 "영상만 봐서 무슨 내용인지 모르겠다" · 쇼핑커넥트 연동): ① STEP 5 — **요약어 금지(지침 I-3-11 ⑪)**: 본론 장면마다 글의 실제 숫자·조건·날짜를 화면에(비교는 양쪽 값 나란히, 결과는 금액·기간 그대로, 조건은 목록 그대로, 할 일은 날짜·순서 그대로), 표·카드·일정 장면은 2.6~3.4초·행 4개, 마지막은 가능하면 한 장 정리 카드(`E2`) ② STEP 7 ⑭·⑯ 기준 갱신(장면별 "영상만 본 사람이 말할 수 있는 것"을 `checks.info` 에) ③ **쇼핑커넥트(지침 I-0 v3.11)** — STEP 4에서 글 본문의 쇼핑커넥트 블록을 찾고, STEP 4.5-8에서 세 조건(본문에 블록 있음·글 주제와 직접 연결·영상을 보면 그 물건이 사고 싶어짐)이 **모두** 맞을 때만 허브 카드 `shop` + 캡션 ⑥-2 한 줄. 기본값은 달지 않음. 영상에는 넣지 않음 ④ STEP 8 `meta.json.shop` ⑤ STEP 11 알림 `🛒` 줄. **그 밖의 단계·문구는 v3.10 그대로다.**

**v3.10에서 바뀐 것**(지침 v3.9·v3.10 대응 — 10/10·10/11 실제 회차 방식을 루틴에 맞춤): ① **렌더 기본 = HyperFrames 전체 렌더**(지침 I-3-10, `hf_render.py` + 포맷 템플릿 `instagram\formats\`) — 엔진 v12(`reel_engine.py`)는 HF가 실패했을 때의 **대체 경로**(STEP 6-E). 구 STEP 6-HF(장면 1개 끼우기)는 STEP 6-E 안의 선택 단계로 내려감 ② STEP 4.5 맨 앞에 **글 성격 판정 → 제작 모드 `M1`~`M6`**(지침 I-2-0-E) — 모드가 장면 수·길이·색·움직임·효과음·포맷 후보를 정한다. 틀은 매 회차 바뀌어도 된다 ③ STEP 4.5에 **엔딩 1개 `E1`~`E4`**(지침 I-2-10, `E4` 프로필 유도는 최근 4회차 중 1회 이하) ④ STEP 5에 **읽히는 화면 원칙**(지침 I-3-11) 적용 · **답은 영상 안에서 끝낸다**(지침 I-0 v3.10 — 블로그는 보너스, 영상 안 블로그 유도는 `E4` 일 때만) ⑤ STEP 7 자가검수 **16항목**(⑯ 가독성 `R-READ` · ⑥ 엔딩·유도) + `verify_hf_sync.py` ⑥ STEP 8 `meta.json.mode`·`ending`·`format`·`checks.read` ⑦ STEP 11 알림에 `🎛 모드`·`🔚 엔딩` 줄 ⑧ STEP M 알림 줄에 완주율 ⑨ BGM판 없음(지침 v3.8) 명시.

**v3.4에서 바뀐 것**(지침 v3.4 I-3-9 대응): ① **STEP 6-HF 신설(선택)** — 엔진 렌더 뒤 장면 1개를 HyperFrames 템플릿으로 다시 그려 끼운다(`tools/hf/hf_reel_insert.py`). 실패·검사 불통과·STEP 7 반려면 그 단계만 건너뛰거나 되돌리고 엔진판으로 v3.2와 똑같이 진행한다 ② STEP 0 — 지침 v3.4 미만이면 6-HF 건너뜀 ③ STEP 4.5-7 HF 장면 선택 · STEP 5 `hf_vars.json` ④ STEP 8 `meta.json.hf`·`hf_vars.json` 저장 ⑤ STEP 11 알림 `🎞 HF` 한 줄 ⑥ 실행 자산·오류 처리·전제조건 표에 한 줄씩. **그 밖의 단계·문구는 v3.2 그대로다.**

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
| **HF 키트 (기본 렌더 · v3.10)** | GitHub `leejc0404/blog` 의 `tools/hf/` — STEP 6 에서 클라우드로 `git clone` | `hf_render.py`(템플릿 + 값 → mp4, 실패 시 종료코드 2) · `hf_reel_insert.py`(STEP 6-E 선택 — 엔진판 장면 1개 교체) · `templates/_common` |
| **포맷 게놈 (v3.10)** | `instagram\formats\formats.json` · `formats\{id}_{이름}\index.html·template.json·example.json·preview.jpg` | 지침 I-3-10. STEP 6 에서 고른 포맷 폴더를 클라우드 키트의 `templates\{id}_{이름}\` 로 복사해 렌더. 새 요소·새 포맷은 **새 폴더로** 저장(기존 폴더는 고치지 않는다) |
| **HF 값·검증 (v3.10)** | 회차 폴더 `build_hf_vars.py`(장면 목록 → `hf_vars.json` + `reel-final_timeline.json` 큐) · `verify_hf_sync.py`(큐가 전부 같은 값에서 나왔는지·큐마다 화면이 변하는지·0프레임) | 견본: `instagram\2026-10-11\samsung-bonus-tax-refund\` (F02) · `2026-10-10\church-hacking-data-leak-check\` (F04) |
| **전달 페이지** | `instagram\relay\make_dl_page.py` | `handoff.json` → `reel-dl-latest` 덮어쓰기 |
| **임시 자산 정리** | `instagram\relay\cleanup_reel_temp.py` | 3일 경과분 휴지통 |
| 허브 카드 | `instagram\relay\hub.py` | `add <card.json>` · `seo <seo.json>` · `get` |
| 원장 | `instagram\ledger.json` | `reels.{slug}: {date, status, ig_media_id, ig_url, hub_card, video_media_id, cover_media_id, dur, scenes, hook_type, hook_id, structure_id, stage, concept, mode, ending, format, marketing, fresh}` |
| **성과 기록** | `instagram\metrics.json` | `{slug: {posted, dur, hook_type, stage, mode, ending, format, daily: {YYYY-MM-DD: {...}}}}` |
| 레퍼런스 | `instagram\refs\inbox.md` · `refs\{YYYY-Www}.md` | |
| 회차 폴더 | `instagram\{YYYY-MM-DD}\{slug}\` | `concepts.md` `build_hf_vars.py` `hf_vars.json` `verify_hf_sync.py` `caption.txt` `reel-final.mp4` `reel-final_cover.jpg` `reel-final_timeline.json` `stills.jpg` `meta.json` `hub_card.json` `post_text.txt` `wp_media.json` `handoff.json` (엔진 대체 경로면 `reel_spec.json` 도) |
| (구) v8 자산 | `render_reel_v8.py` `build_reel_sfx.py` `verify_reel_sync.py` | **사용 중지.** 지우지 않고 남겨 둔다(과거 회차 재현용) |
| 엔진 이전 판 | (만들지 않음 — v3.2) | 사용자 지시(10/6)로 사용자 폴더에 백업·이전 판 사본을 만들지 않는다. 회귀 검사용 이전 판은 클라우드 작업 공간에만 둔다 |

설정값: `PUBLISH_MODE = HANDOFF`(기본) · `DAILY_TARGET = 1` · `LOOKBACK_DAYS = 3` · `TOKEN_REFRESH_DAYS = 30` · `IG_API = v23.0` · `REF_SCAN_DAY = 월요일`(KST) · `REF_MAX_POSTS = 6` · `TEMP_KEEP_DAYS = 3` · `CONCEPTS = 3` · `MARKETING_MIN = 3`(지침 I-2-8) · `REEL_MASCOT` **설정하지 않음** · `RENDER = HF 전체(기본) → 엔진 v12(대체)` · `HF_RENDER_TIMEOUT = 540초` · `HF_INSERT = 엔진 대체 경로에서만 선택(최대 1장면, CTA 제외)` · `HF_TIMEOUT = 420초` · `MODES = M1~M6`(지침 I-2-0-E) · `ENDINGS = E1~E4`, `E4_MAX = 최근 4회차 중 1회`(지침 I-2-10) · `BGM = 만들지 않음`(지침 I-3-1 v3.8)

---

## STEP W. 주간 레퍼런스 스캔 (지침 I-3-7 — 월요일 또는 인박스에 미처리 링크가 있을 때만 · Chrome MCP 읽기 전용)

1. **수집 목록**(최대 `REF_MAX_POSTS`): ① `refs/inbox.md`의 `- [ ]` 줄 ② 벤치 계정 최근 **릴스** ③ 탐색·해시태그 상위의 **정보형 릴스**. 지침 I-3-7 "고를 기준"으로 거른다.
2. **읽기 방법**: `…/reel/{code}/` 로 URL 이동 → 5초 대기 → 스크린샷. 30초 타임아웃이면 같은 URL로 1회 재시도, 그래도 실패하면 건너뛴다. 반응 수치는 `get_page_text`로 읽는다. **인스타 화면에서 클릭은 페이지 이동에만 쓴다.**
3. **기록**: `refs/{YYYY-Www}.md`에 지침 I-3-7 "추출 8항목" + 반응 수치 + "차용할 것 / 복제하지 않을 것"을 쓴다. 처리한 인박스 줄은 `[x]`로 바꾼다.
4. **주간 비교**(지침 I-8-3): `metrics.json` 에서 훅 공식별 최신 스킵률 평균을 내 같은 파일 끝에 표로 적는다. **v3.10**: 모드(`M1`~`M6`)·엔딩(`E1`~`E4`)·포맷별로 3초 스킵률·완주율(평균 시청 ÷ 길이)·저장·공유 표를 더한다(지침 I-8-3·I-2-10).
5. **반영**: 새 형식은 지침 I-2-2 표 **행 추가 제안**으로 STEP 11에 남긴다(`🧩 형식 제안`). ⛔ 지침 I-3-5 — 밈·영상의 **이미지·캐릭터·클립·음원 자체는 복제하지 않는다.** 차용은 편집 형식까지다.
6. 열었던 탭은 모두 닫는다.

## STEP 0. 지침 읽기·설정 확인
1. 지침을 `curl -s "...0and1Life-Insta.md?cb=$(date +%s%3N)"` 로 받아 **전체를** 읽는다. **v3.11 기준**: 개정 이력 첫 줄이 **v3.11 이상**이면 이 루틴 전체를 그대로 수행한다. v3.10이면 쇼핑커넥트(STEP 4.5-8)는 건너뛰고(달지 않음) 요약어 금지(⑪)는 이 루틴 STEP 5대로 적용, 알림에 `📐 지침 v3.11 미배포` 한 줄. **v3.10 기준(이전 판)**: 개정 이력 첫 줄이 **v3.10 이상**이면 이 루틴 전체를 그대로 수행한다. v3.8~3.9면 엔딩(I-2-10)·완결 원칙이 없다 — 엔딩은 `E4` 로 고정하고 알림에 `📐 지침 v3.10 미배포` 한 줄. v3.8 미만이면 HF 전체 렌더 대신 STEP 6-E(엔진)로 간다(`📐 지침 v3.8 미배포`). 아래는 이전 판 기준(참고용): Phase I-0~I-9와 반려 코드표가 모두 보이는지, 개정 이력 첫 줄이 **v3.2 이상**인지 확인한다. v3.0~3.1이면 I-2-1-B(쉬운 3초)·5막 구조가 없다 — 이 루틴의 v3.2 항목은 그대로 수행하고 알림에 `📐 지침 v3.2 미배포` 한 줄만 남긴다. v2.x면 **전달하지 않고** 알림(`📐 지침 v3 미배포`). 개정 이력 첫 줄이 **v3.4 미만**이면 STEP 6-HF 만 건너뛴다(지침 I-3-9 미배포 — 알림에 `🎞 HF 건너뜀(지침 v3.4 미배포)` 한 줄).
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
5. **해석은 지침 I-8-2·I-8-3에 따른다.** 매일은 수치만 쌓고, 알림에 **가장 최근 게시 릴스의 스킵률·평균 시청·완주율**만 한 줄로 싣는다(`📊 {slug} 스킵 {n}% · 평균 {n.n}초 · 완주 {n}%`). 지침 I-8-2 v3.10 목표(스킵 70% 이하·완주율 40% 이상)를 넘으면 `🎯` 를 붙인다.

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
- 추출: 제목, Core Fact / Primary Insight / Actionable Tip, 모든 `<table>`, H2 목록(⭐ GAP H2), "근데/다만/함정/실제 예" 문단, `📌`/`*핵심 :` 요약 줄, 출처 명칭, `modified`, 잠정·예정 표현, **네이버 쇼핑커넥트 상품 블록**(v3.11 — 있으면 상품 종류·링크 URL만 메모, 없으면 `shop=없음`).
- HTML을 벗긴 **본문 전체 텍스트**를 `post_text.txt`로 저장(STEP 7 숫자 대조용).
- `<table>` 0개이고 Core Fact에 수치가 없으면 `X-THIN` — ledger 기록 후 다음 후보로(1회).

## STEP 4.5. 기획 — 모드 → 검색 의도 → 콘셉트 3개 → 1개 + 엔딩 (지침 I-2-0-E · I-2-0-A · I-2-0-B · I-2-0-C · I-2-10 · I-3-6 · I-3-10)
1. **글 성격 판정 → 제작 모드**(지침 I-2-0-E): 제목·H2·Core Fact·카테고리로 `M1`~`M6` 중 하나. 두 개에 걸치면 표 위쪽(`M2` 부정적 이슈가 먼저). 애매하면 `M3`. `concepts.md` 맨 위에 `모드: M? — {이유 한 줄}`. **이 회차의 장면 수·장면 길이·색·움직임·효과음·포맷 후보·구성 후보는 모드 행을 따른다.**
2. **검색 의도**(지침 I-2-0-A): 핵심 검색어 → WebSearch 상위 제목 5~10개 → 궁금증 3~4개 순위 → 장면 매핑. `concepts.md` 에 적고 `meta.json.search_intent` 한 줄. 조회가 모두 막히면 제목·H2에서 추정(`🔎 검색 의도 추정`).
3. **콘셉트 3개**(지침 I-2-0-B 서로 다른 그룹 × I-2-2 화면 형식): 콘셉트마다 훅 코드(`H`)·구성 코드(`S`, 모드 후보 우선)·포맷(모드 후보 우선, 검증 1 + 실험 1 — 지침 I-3-10-3)·0~3초 글자 전부(I-2-1-B 검사용)·0초 화면 그림 한 줄(I-3-11 ⑩ 관계가 보이게)·마케팅 장치 3~5개(I-2-8)·새 연출 1개(I-3-8)·넘기지 않을 이유.
4. **순환**(지침 I-3-6): `ledger.reels` 최근 2회차의 `hook_id`·`structure_id`·`format`(실험)·`stage` 와 겹치지 않게. 최근 6회차에 같은 (H, S) 조합 금지. `refs/{YYYY-Www}.md` 주간 비교에서 나쁜 코드는 피한다.
5. **엔딩 1개**(지침 I-2-10): `E1` 루프 · `E2` 저장 · `E3` 댓글 질문 · `E4` 프로필 유도. `ledger` 최근 4회차에 `E4` 가 있으면 `E4` 금지. 같은 엔딩 연속 3회 금지. **훅이 연 질문의 답은 영상 안에서 끝낸다**(지침 I-0 v3.10 · I-2-9 ② — 블로그로 넘기는 고리 금지).
6. 1개를 고르고 `meta.json.hook = {id, format, type, stage, concept, why}`, `structure`, `format = {verified, experiment, note}`, `mode`, `ending`, `marketing`, `fresh` 를 적는다. `concepts.md` 에 열린 고리 표(연 곳·닫는 곳 — 전부 영상 안)·정보 전달 4요소(I-2-0-D)·탈락한 2개와 이유.
7. 고른 포맷에 필요한 요소가 템플릿에 없으면 **새 포맷 폴더**를 만든다(기존 템플릿 복사 + 요소 추가 — 지침 I-3-10). 기존 포맷 폴더·`reel_engine.py` 는 고치지 않는다.
8. **쇼핑커넥트 판단 (v3.11 · 지침 I-0)**: STEP 4에서 블록을 찾았을 때만 본다. ① 본문에 블록이 있다 ② 그 물건이 글이 말하는 문제를 직접 푼다 ③ 고른 콘셉트의 영상을 끝까지 보면 그 물건이 사고 싶어질 장면이 이미 있다 — **셋 다 "예"일 때만** `shop.used=true`. 애매하면 `false`(기본값). 물건을 광고하는 장면을 새로 만들지 않는다. `concepts.md` 에 판단 한 줄.

## STEP 5. 원고 → `build_hf_vars.py`(→ `hf_vars.json` · `reel-final_timeline.json`) · `caption.txt` · `hub_card.json`
- 지침 I-2(쉬운 3초·0프레임·숫자 복사·날짜·잠정 표시·화자·금지·마케팅 장치·지속성)·**I-3-11 읽히는 화면 원칙**·I-4(캡션 500자)를 그대로 적용한다. 장면 수·길이는 **모드 행**(I-2-0-E), 엔딩 장면은 **I-2-10 의 고른 코드**대로.
- **읽히는 화면 (I-3-11) — 원고 단계에서 먼저 지킨다**: 장면마다 "이 장면의 한 문장"을 `concepts.md` 장면 매핑에 적는다 · 글 덩어리 2개(목록 장면만 행 3개) · 영상 숫자 3개(`M1` 4개)·장면당 1개 · 본론에 34px(lv 1) 글자 없음(출처·가정·기준일은 엔딩 한 줄·캡션으로) · 배경 2색·강조색 1개 · 고스트 숫자·티커·장식 스티커 없음(`ghost`·`series` 값을 비운다) · 장면 길이(배속 반영) ≥ 0.8 + 글자 수 × 0.09초 · 장면마다 그림 1개(도식·소품·배치)로 뜻이 보이게.
- **요약어 금지 — 실제 내용을 화면에 (지침 I-3-11 ⑪ · v3.11)**: 사용자 검수(10/16) "영상만 봐서 무슨 내용인지 모르겠다". 본론 장면마다 글의 **실제 숫자·조건·날짜**가 화면에 있어야 한다 — 비교는 양쪽 값을 나란히(`card` 행 또는 `stack` + 값), 결과는 금액·기간 그대로, 조건은 목록 그대로(`seats`·`card` 행 4개까지), 할 일은 날짜·순서 그대로. 그림(저울·기울기·화살표)은 숫자를 돕는 것이지 대신하지 않는다. 표·카드·일정 장면은 2.6~3.4초, 행은 0.15~0.25초 간격으로 차례로 띄운다. 마지막은 가능하면 한 장 정리 카드(`E2`). 기준 회차: `instagram\2026-10-16\youth-leap-to-future-savings-switch\build_hf_vars.py`(v2, 19.9초).
- **답은 영상 안에서 끝낸다**(I-0 v3.10): 영상 안 블로그 문구(`blog_note`·잠긴 표·`프로필 링크 → 맨 위 글` 버튼)는 **엔딩이 `E4` 일 때만**. 다른 엔딩에서도 캡션 2번째 줄(I-4-1 ②)의 블로그 안내는 넣는다.
- `build_hf_vars.py` 구조(견본: `2026-10-11\samsung-bonus-tax-refund\build_hf_vars.py`): `scenes = [dict(dur, bg, amb, els=[dict(kind, lv, y, at, parts|text|rows…, sfx=[[시각, 효과음]])…])…]` · `V = dict(speed, series, foot, scenes)` · 장면 경계에 `whoosh`, 요소의 `sfx` 를 모아 `/speed` 한 큐를 `reel-final_timeline.json` 에 쓴다 — **효과음 큐는 반드시 이 값에서만 만든다**(싱크 구조 보장, I-3-4). `speed` 는 `M6` 이면 0.8, 다른 모드는 모드 행의 장면 길이가 나오게 정한다(보통 1.0, 길이는 `dur` 로 조정).
- 요소 종류(템플릿 공통, `formats\F01·F04·F09·F02` 기준): `text`(lv 1~5 = 34·55·89·144·233, `parts`, `fx`, `split`, `glitch`, `pulse`, `shake`, `punch`) · `sticker` · `card`(`rows`) · `bar`(tease 띠) · `stamp` · `line`(밑줄·동그라미) · `burst` · `invert` · `arrow`(계정 행) · `lock` · `flap`(F09) · `seats`(F04) · `yesbut`(F02). `M2`·`M3` 은 `shake`·`glitch`·`burst`·`punch` 를 쓰지 않는다(I-2-0-E).
- `caption.txt` 는 지침 I-4-1 순서 · `len(strip()) ≤ 480` · 첫 줄·첫 해시태그 = 핵심 검색어. 7번 줄에 보낼 사람과 꺼내 볼 순간.
- `hub_card.json`: `slug, title, date, category, thumb(STEP 9에서 채움), ig_url(""), points[2~3]` · (v3.11, `shop.used=true` 일 때만) `shop: {label: "{물건 종류} 보기", url: "{본문 블록과 같은 URL}"}`.
- (v3.11, `shop.used=true` 일 때만) `caption.txt` ⑥ 바로 아래 한 줄: `🛒 {물건 종류}는 프로필 링크 → 맨 위 글 아래에 같이 뒀어요` — 상품명·가격·할인·"추천" 강조·URL 금지. 480자를 넘으면 이 줄부터 뺀다.

## STEP 6. 렌더 — HyperFrames 전체 렌더 (클라우드 · 지침 I-3-10 · 기본 경로)
Bash 도구 `timeout` 은 **600000ms** 로 지정한다.
```bash
mkdir -p ~/ig_work && cd ~/ig_work && rm -rf hfkit && git clone -q --depth 1 https://github.com/leejc0404/blog hfkit && K=hfkit/tools/hf
# 고른 포맷 폴더(PC instagram\formats\{id}_{이름}\ — device_stage_files)를 $K/templates/{id}_{이름}/ 로 복사
# build_reel_sfx_v2.py(PC relay) · 견본 verify_hf_sync.py(최근 회차 폴더)를 가져온다
cd ~/ig_work/{slug} && python3 build_hf_vars.py                                   # → hf_vars.json + reel-final_timeline.json
timeout 560 python3 ../hfkit/tools/hf/hf_render.py {id}_{이름} hf_vars.json reel-hf.mp4 --timeout 540
python3 build_reel_sfx_v2.py reel-final_timeline.json sfx.wav
ffmpeg -y -v error -i reel-hf.mp4 -i sfx.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -ar 44100 -ac 2 -shortest -movflags +faststart reel-final.mp4
python3 verify_hf_sync.py                                                         # 종료코드 0 이어야 통과
```
- **대표 프레임 먼저 본다**: 장면마다 0초·중간·끝 프레임을 360px 로 뽑아 한 장(`stills.jpg`)으로 이어 붙여 `Read` 로 본다. 요소가 안 보이면 템플릿 복사 누락·JS 오류부터 의심한다(2026-10-11 실측: 템플릿을 고치기 전에 키트로 복사해 새 요소가 안 나온 사례). 디버그가 필요하면 `hf_render.build_project` 로 작업 폴더를 만들고 Playwright로 열어 `pageerror` 를 본다(`page.evaluate` 는 타임라인 객체를 반환하지 않게 `; 0` 을 붙인다).
- 커버: 훅의 사건·자막이 다 보이는 시각(보통 1.6초 안팎)을 `ffmpeg -ss {t} -frames:v 1 -q:v 2 reel-final_cover.jpg`.
- 새 요소를 쓰는 포맷이면 `verify_hf_sync.py` 의 요소별 허용 규칙(예: `yesbut` 의 `but_at`)을 그 회차 사본에 추가한다 — 큐가 같은 값에서 나왔는지·큐마다 화면이 변하는지 검사는 빼지 않는다.
- **BGM판은 만들지 않는다**(지침 I-3-1 v3.8).
- HF 렌더가 2회(값 수정 1회 포함) 실패하거나 시간 초과면 `meta.json.render = {path:"engine", reason}` 을 남기고 **STEP 6-E** 로 간다(반려 아님).

## STEP 6-E. 대체 경로 — 엔진 v12 렌더 (HF 실패 시에만)
```bash
mkdir -p ~/ig_work && cd ~/ig_work && (ls package/dist/public/static/alternative >/dev/null 2>&1 || (npm pack pretendard@1.3.9 >/dev/null && tar xzf pretendard-1.3.9.tgz))
export PRETENDARD_DIR=~/ig_work/package/dist/public/static/alternative
# reel_engine.py · build_reel_sfx_v2.py · verify_reel_v9.py · examples/story_spec.json 을 PC relay 폴더에서 device_stage_files 로 가져온다
python3 verify_reel_v9.py reel_spec.json
python3 reel_engine.py reel_spec.json --stills stills
python3 reel_engine.py reel_spec.json reel-final.mp4
python3 build_reel_sfx_v2.py reel-final_timeline.json sfx.wav
ffmpeg -y -v error -i reel-final.mp4 -i sfx.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -ar 44100 -shortest -movflags +faststart reel-final-sfx.mp4 && mv reel-final-sfx.mp4 reel-final.mp4
```
- `build_hf_vars.py` 의 장면을 `reel_spec.json`(견본 `examples\story_spec.json`)으로 옮긴다 — 같은 문구·같은 숫자. `REEL_MASCOT` 은 설정하지 않는다. 엔진 기본 `BEATS` 는 느리므로 장면마다 `dur`·`beats` 로 모드 행의 길이에 맞춘다.
- (선택) 글자가 움직이는 장면 1개를 HF `reel_scene` 으로 바꿔 끼울 수 있다 — `hf_reel_insert.py --spec reel_spec.json --scene {N} --vars hf_vars.json --video reel-final.mp4 --timeline reel-final_timeline.json --out reel-final-hf.mp4 --stills stills --cover reel-final_cover.jpg --cover-t {초} --engine reel_engine.py` (`timeout 420`). 종료코드 0 이면 `mv reel-final-hf.mp4 reel-final.mp4`, 2·시간 초과면 그대로. CTA 장면은 고르지 않는다. 실패·STEP 7 반려는 **반려 아님**(엔진판으로 되돌림, 수정 1회로 세지 않음). `meta.json.hf = {scene, type, status: applied|skipped|reverted, reason}`.
- 이 경로의 싱크 검사는 `verify_reel_v9.py`(종료코드 0)다.

## STEP 7. 자가검수 (지침 I-5 — 16항목 전부)
```bash
python3 verify_hf_sync.py            # HF 경로 (엔진 경로면 verify_reel_v9.py reel_spec.json) — 종료코드 0 이어야 통과
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt,channels -show_entries format=duration reel-final.mp4
ffmpeg -i reel-final.mp4 -af volumedetect -f null - 2>&1 | grep max_volume
for t in 0.0 0.3 0.6 1.0 1.6 2.2; do ffmpeg -y -v error -ss $t -i reel-final.mp4 -frames:v 1 -vf scale=270:-1 hook_$t.png; done
```
1. **① 숫자 전수 대조**: `hf_vars.json`(엔진이면 `reel_spec.json`)의 모든 `text`·`parts`·`rows`·`tag` 글자와 `caption.txt` 에서 숫자 토큰(`\d[\d,\.]*(억|만원|만|%|년|월|원|가지|개|줄)?`)을 뽑아 `post_text.txt`(공백 제거)에 있는지 본다. 기준일 표기·장면 길이·효과음 시각은 제외. 하나라도 없으면 `R-NUM` → 본문 표현으로 고쳐 재렌더(2026-10-11 실측: '1개'·'2줄' → '1가지'·'따로 적어 두기').
2. **② 안전영역 · ⑩ 겹침·빈 곳**: `stills.jpg` 를 `Read` 로 본다(글자 x 60~1020·y 410~1560, 우측 버튼 구간 x 900~1010·y 700~1500 글자 없음).
3. **③ 규격**: 1080×1920 · 30fps · yuv420p · 모드 행의 총 길이(12~20초 안) · AAC 스테레오 · 피크 ≤ -12dBFS.
4. **④ 커버** `Read`. **⑤ 날짜·잠정**(I-2-4). **⑥ 엔딩·유도**(v3.10): `meta.json.ending` 이 I-2-10 대로 · `E4` 는 최근 4회차 중 1회 이하 · 캡션 2번째 줄 블로그 안내 · `E4` 가 아니면 영상 안에 '블로그에' 문구 없음.
5. **⑦ 화자·금지어·저작권** — I-2-6·I-2-7·I-3-5.
6. **⑧ 싱크** 🚨 · **⑨ 훅** 🚨: 검증 스크립트가 실패하면 **즉시 중단**(`R-SYNC`/`R-HOOK`). `hook_*.png` 를 보고 "넘기지 않을 이유" 한 문장(`meta.json.checks.hook`) · 첫 사건 ≤0.8초 · 쉬운 3초(제도 용어 없음·숫자 1개 이하·문장 2개 이하, 예/아니오 질문 단독 금지) — "초등학교 고학년이 이해하는가" 한 문장(`checks.easy`).
7. **⑪ 속도·장치**: 장면 수·장면 길이·총 길이·엔딩 길이가 `meta.json.mode` 행 범위 안 · 장치 3~5개 · `fresh` 있음 · 글자 크기 34·55·89·144·233 만. 아니면 `R-PACE`.
8. **⑫ 검색 의도·캡션**(`R-INTENT`/`R-CAP`) · **⑬ 지속성**(고리 전부 영상 안에서 닫힘·인터럽트 연속 없음·보상 55~75%·`L`) · **⑭ 정보 전달**(①·④는 영상 안) · **⑮ 포맷**(검증 1 + 실험 1 기록·직전 회차 실험 포맷과 다름·복제 없음·큐가 같은 값에서 생성).
9. **⑭ 요약어 검사 (v3.11)**: 본론 장면마다 "영상만 본 사람이 이 장면에서 말할 수 있는 것(얼마·왜·누가·언제·어떻게)"을 한 줄씩 `meta.json.checks.info` 에 적는다. 그림·기울기만 있고 실제 숫자·조건·날짜가 없는 본론 장면이 있으면 `R-INFO`.
10. **⑯ 가독성** `R-READ`(지침 I-3-11 v3.11): 스크립트로 장면별 글 덩어리 수(표·카드·목록·일정 장면은 제목 1 + 행 ≤4 + 결론 1, 그 밖은 ≤2)·장면당 주인공 숫자(④·⑤단) 1개·본론 lv 1 사용 여부·배경 색 수(≤2)·`ghost`/`series` 장식 여부·`dur/speed ≥ 0.8 + 글자 수 × 0.09` 를 계산하고, 장면마다 대표 프레임의 글자 영역을 가린 사본(흰 박스로 덮기)을 `Read` 로 보며 "그림만으로 무슨 장면인지" 한 줄씩 `meta.json.checks.read` 에 적는다. 글자만 있는 장면이 절반을 넘으면 반려.
11. 반려가 있으면 STEP 4.5(콘셉트 2순위) 또는 STEP 5로 돌아가 **1회만** 수정·재렌더. 다시 실패하면 전달하지 않고 `ledger.reels.{slug} = {status:"held", held:"R-…"}` 기록 후 STEP 8 → 12 → 11.

## STEP 8. PC 저장
- `device_commit_files` 로 `instagram\{TODAY}\{slug}\` 에 `concepts.md build_hf_vars.py hf_vars.json verify_hf_sync.py caption.txt reel-final.mp4 reel-final_cover.jpg reel-final_timeline.json stills.jpg hub_card.json post_text.txt meta.json` 을 저장한다(엔진 경로면 `reel_spec.json` 도).
- `meta.json`: `{blog_post_id, blog_url, blog_modified_at_build, search_intent, persona, mode, ending, hook:{id,format,type,stage,concept,why}, structure, format:{verified,experiment,note}, marketing:[…], fresh, retention:{interrupts,reward_at,loopback}, scenes:[…], dur, speed, engine, render:{path:"hf"|"engine", reason}, hf?, shop:{used, why, label?, url?}, status:"ready"|"held", checks:{num,safe,spec,cover,date,link,voice,sync,hook,easy,typo,pace,intent,retain,info,format,read}}`.
- 새 포맷·새 요소를 만들었으면 `instagram\formats\{id}_{이름}\`(`index.html·template.json·example.json·preview.jpg`)에 저장하고 `formats.json` 의 그 카드(`hf`·`dir`·`uses`·`log`)와 바탕 포맷의 `uses`·`log` 를 갱신한다(`updated` = TODAY). 기존 포맷 폴더는 덮어쓰지 않는다. 사용자 폴더에 백업·이전 판 사본을 만들지 않는다.

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
 "items":[{"label":"{글 제목}","note":"{길이}초 · 모드 {M?} · 훅 {H 코드} · 엔딩 {E 코드}","video_url":"{wp_media.video.url}",
           "filename":"0and1life-reel-{slug}.mp4","caption_file":"{회차폴더}/caption.txt"}]}
```
1. 생성된 페이지 URL이 200인지, `download=` 속성과 복사 버튼이 각각 들어갔는지 `curl | grep -c`로 확인한다. 실패하면 `E-PAGE` — 알림에 영상 URL을 직접 실어 대체한다.
2. `ledger.reels.{slug} = {date:TODAY, status:"handoff", video_media_id, cover_media_id, dur, scenes, hook_type, hook_id, structure_id, stage, concept, mode, ending, format, marketing, fresh, hub_card:false}`.
3. **허브 카드 먼저 추가 (지침 I-6 v3.1.1 · v3.11 `shop` 은 used=true 일 때만 — `hub.py` 가 `shop` 을 모르면 카드에서 빼고 알림 `🛒 허브 shop 미지원`)**: `hub_card.json` 의 `thumb`(STEP 9 커버 URL)을 확인하고 `ig_url` 은 빈 값으로 둔 채 `python3 hub.py add {회차폴더}/hub_card.json` → 8초 뒤 `curl -s https://0and1life.com/ig/?cb=$(date +%s) | grep -c "o1-ig-card:{slug}"` ≥ 1 이면 `ledger.reels.{slug}.hub_card="no_ig_url"`, 아니면 1회 재시도 후 `E-HUB`(전달은 유지). 알림에 `🗂 허브 카드 추가` 한 줄.
4. STEP 11 알림에 **전달 페이지 URL 하나만** 싣는다.
5. **사용자가 게시했다고 알리면** (같은 세션 또는 다음 회차 STEP M에서 자동 확인):
   ```bash
   python3 ig.py my_media 5      # 최근 게시물에서 permalink·media_id 확보
   ```
   → `ledger.reels.{slug}.status="posted"`, `ig_media_id`, `ig_url` 기록 → `metrics.json.{slug}` 에 `posted, dur, hook_type, stage, mode, ending, format` 기록 → `hub_card.json.ig_url` 채우고 `python3 hub.py add hub_card.json`(같은 slug 교체 — `ig_url` 만 채워진다) → 8초 뒤 `curl -s https://0and1life.com/ig/?cb=$(date +%s) | grep -c "o1-ig-card:{slug}"` ≥ 1 이면 `hub_card:true`, 아니면 1회 재시도 후 `E-HUB`.

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
- 덧붙이는 줄(해당 시): `🛒 쇼핑커넥트: {달음 — 물건 종류|안 담 — 사유 한 줄}` · `🎛 모드: {M?} {이유}` · `🔚 엔딩: {E?}` · `🎬 콘셉트: {고른 콘셉트 한 줄}` · `🧬 포맷: {검증 id} + {실험 id}` · `🧲 장치: {장치 이름 나열}` · `✨ 새 연출: {meta.fresh}` · `📊 {slug} 스킵 {n}% · 평균 {n.n}초 {🎯}` · `🔑 토큰 갱신 {성공|실패}` · `🗑 임시 자산 {n}건 정리` · `⏳ pending {n}편` · `🔍 레퍼런스 스캔 {n}편` · `🧩 엔진 확장: {무엇}` · `🧩 형식 제안: {한 줄}` · `🎞 렌더: {HF 전체|엔진 대체(사유)}` · `🎞 HF 장면: s{N} {type} {적용|건너뜀(사유)|되돌림(사유)}`(엔진 경로일 때만) · `📐 지침-루틴 상충: {조항}`

## STEP 12. 임시 자산 정리 (지침 I-9 — 대상 글 유무와 무관하게 매 회차)
```bash
cd "$R" && python3 cleanup_reel_temp.py --days 3 --dry    # 먼저 목록 확인
python3 cleanup_reel_temp.py --days 3                      # dry 목록에 대상이 있을 때만
```
- 대상: 슬러그가 `reel-dl-` 로 시작하는 페이지(단 `reel-dl-latest`는 **제외 — 고정 주소**), 파일명이 `reel-*-final.mp4` / `reel-*-cover.jpg` 인 미디어 중 **생성 후 3일 경과분**.
- **휴지통으로만 보낸다.** `force` 영구 삭제는 어떤 경우에도 하지 않는다.
- `ledger.reels`에 `status="posted"` 기록이 없는 회차의 미디어는 **보류**하고 알림에 남긴다.
- WP 미디어가 휴지통을 지원하지 않아 삭제가 영구 삭제(`force`)로만 되는 경우에는 **실행하지 않고 보류**한다(사용자 지침 ①: 삭제는 사용자 확인 후). 알림에 `🗑 정리 보류({n}건 · 휴지통 미지원)` 한 줄.
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
| **`verify_hf_sync.py` 실패 (HF 경로)** | 🚨 `R-SYNC`/`R-HOOK` — **전달 중단.** `build_hf_vars.py` 의 `at`·`sfx` 수정 → 재렌더 → 재검사 |
| HF 렌더 실패·시간 초과(값 수정 후에도) | **반려 아님** — STEP 6-E 엔진 대체 경로 · 알림 `🎞 렌더: 엔진 대체(사유)` |
| 대표 프레임에 새 요소가 안 보임 | 템플릿 복사 누락·JS 오류 — 키트 `templates\` 에 최신 파일을 다시 복사하고 Playwright `pageerror` 확인 |
| 가독성 기준 불통과 | `R-READ` — 글자 줄이기·장면 나누기·그림 넣기 1회 → 재렌더. 다시 실패면 held |
| **`verify_reel_v9.py` 실패 (엔진 경로)** | 🚨 `R-SYNC`/`R-HOOK` — **전달 중단.** 장면 `beats`·콘셉트 수정 → 재렌더 → 재검사 |
| 장면 수·길이가 모드 행 밖 · 장치 <3개 · `fresh` 없음 | `R-PACE` — spec `dur`·`beats`·콘셉트 수정 1회 → 재렌더. 다시 실패면 held |
| stills에서 아래 절반이 빈 장면 | `R-TYPO` — 지침 I-3-2대로 소품·숫자·카드 확대(엔진 기본 레이아웃이 처리하므로 보통 spec 내용 보강으로 해결) |
| 엔진 확장 후 견본 spec 검사 실패 | `E-ENGINE` — 확장을 되돌리고 기존 장면 유형으로 재구성 |
| HF 장면 끼우기(STEP 6-E 선택) 실패·시간 초과·STEP 7 반려 | **반려 아님** — 엔진판으로 진행(STEP 7 반려면 되돌린 뒤 STEP 7 다시, 수정 1회로 세지 않음) · 알림 `🎞 HF` 한 줄 |
| 렌더·효과음·먹싱 실패 | 글꼴 재설치 1회 → 실패 시 `E-RENDER`로 held |
| 전달 페이지 생성 실패 | `E-PAGE` — 알림에 영상 URL 직접 기재 |
| 허브 카드 검증 실패 | 1회 재시도 → `E-HUB`(게시 유지) |
| STEP W 스크린샷 타임아웃 반복 | 그 회차 스캔 건너뜀, 인박스 `[ ]` 유지 |
| 같은 날 2회 실행 | ledger에 `handoff`/`posted`가 있으면 STEP 3에서 제외되어 "대상 없음"으로 끝난다 |

## ⚠️ 전제조건 (사용자 몫 — 2026-10-12 기준)

| 항목 | 상태 | 비고 |
|---|---|---|
| 지침 `0and1Life-Insta.md` **v3.11** GitHub 커밋 | ⬜ **커밋 필요**(전문 전달 2026-10-16) | STEP 0이 v3.10이면 쇼핑커넥트 건너뜀 + `📐 지침 v3.11 미배포`, v3.8~3.9면 엔딩 `E4` 고정, v3.8 미만이면 엔진 경로 |
| `hub.py` 의 `shop` 필드(허브 카드 아래 작은 링크 + 제휴 고지) | ⬜ 확인 필요(v3.11) | 지원하지 않으면 허브 카드에서 `shop` 을 빼고 캡션 ⑥-2 줄도 넣지 않는다(링크가 없는 안내가 되므로) |
| 포맷 게놈 `instagram\formats\`(F01·F02·F04·F09 템플릿 · `formats.json`) | ✅ 2026-10-11 PC 저장(F02 Yes…but 추가) | 없으면 STEP 6 에서 키트 기본 템플릿 `reel_scene` 대신 STEP 6-E |
| 엔진 v12 `relay\reel_engine.py` · 효과음 v2.1 `build_reel_sfx_v2.py` · `verify_reel_v9.py` · `regress_engine.py` · `examples\bank_spec.json` · `examples\story_spec.json` | ✅ 2026-10-06 PC 저장(v12 — 기존 장면 회귀 동일 확인) | 없으면 STEP 1에서 `MISSING` |
| WPCode 스니펫 `ig-relay` v1.2 (`reel`·`insights`·`my_media`) | ✅ 동작 확인(2026-10-02 insights 응답) | |
| Meta 앱 · 장기 토큰 | ✅ pw.txt 보관, 0and1life(MEDIA_CREATOR) | 60일 토큰, 30일마다 자동 갱신 |
| 프로필 링크 = 허브 `/ig/?utm_...=ig_bio` | ✅ | 모바일 앱에서만 변경 가능 |
| 허브 페이지 1922 공개·index | ✅ | 제목·메타 고정, 카드만 추가 |
| 전달 페이지 `reel-dl-latest` | ✅ page 1980 | 구글 문서가 가리키는 고정 주소 — 삭제 금지 |
| Cowork 예약 `8. 0and1life 인스타 릴스`(매일 07:00 KST, PC 연결, `C:\Users\win\Documents\Claude`·`instagram` 연결) | ✅ 진입점 방식(2026-10-12 확인) — 예약 본문은 이 파일을 끝까지 읽고 수행하라는 짧은 안내뿐 | **이 파일만 고치면 다음 실행부터 반영**된다. 예약 본문은 바꾸지 않는다. 단 지침(`0and1Life-Insta.md`)은 STEP 0이 GitHub에서 읽으므로 **커밋해야** 반영된다 |
| HF 키트 `blog\tools\hf\`(`hf_render.py`·`hf_reel_insert.py`·`templates/_common`) GitHub | ✅ 2026-10-10·10-11 회차에서 clone·렌더 확인 | 없으면 STEP 6-E 엔진 경로 |
| `PUBLISH_MODE` | `HANDOFF` | 유행 음원 때문에 기본은 반자동. AUTO는 회차별 지시로만 |

## Cowork 원라이너

토큰 확인(2) → **전 회차 스킵률·평균 시청·완주율 측정(M)** → 대상 글 1편(3) → 본문 최종본(4) → **글 성격 → 모드 M1~M6 → 검색 의도 → 콘셉트 3개(H·S·포맷 검증 1 + 실험 1·장치·새 연출) → 1개 + 엔딩 E1~E4(E4 는 4회 중 1회 이하)(4.5)** → 읽히는 화면 원칙(한 장면 한 메시지·글 덩어리 2·숫자 3·장식 없음·읽을 시간)·답은 영상 안에서 끝냄 → `build_hf_vars.py`·캡션(5) → **HyperFrames 전체 렌더 + 효과음 v2.1 + 커버 · `verify_hf_sync.py`(6)** — 실패면 엔진 v12 대체(6-E) → **자가검수 16항목, 싱크·훅 실패면 무조건 중단(7)** → PC 저장·포맷 게놈 갱신(8) → WP 업로드(9) → `reel-dl-latest` 덮어쓰기 + 허브 카드(10) → 알림에 URL 하나(11) → 3일 지난 임시 자산 정리(휴지통 미지원이면 보류)(12). 통과 못 하면 **전달하지 말고** held로 남긴다.

---

## 🧾 마지막 STEP — 실행 기록 한 줄 (관제탑용 · 2026-10-12 추가)

이 루틴이 **어떤 경로로 끝나든**(정상 완료 · 대상 없음 · 조기 종료 · 오류 · 마감 중단) 끝내기 직전에 반드시 아래 한 줄을 남긴다. 관제탑이 이 기록으로 실제 성공·실패를 보여 준다. 실행을 시작할 때 KST 시각(HH:MM)을 기억해 둔다.

- 위치: `C:\Users\win\Documents\Claude\control_tower\runs\YYYY-MM.jsonl` (PC 셸 `$HOME/mnt/Claude/control_tower/runs/`, 없으면 만든다)
- 한 회차에 한 줄만 덧붙인다. 기존 줄은 고치거나 지우지 않는다.
- `result`: `성공`(할 일을 다 함) · `부분`(일부만) · `건너뜀`(대상 없음) · `실패`(오류·마감)
- `count`: 이번 회차에 만들어 전달한 릴스 수(코드의 `0`을 그 수로 바꾼다). 없으면 0
- `summary`: 60자 이내 한 줄 / `warnings`: 사용자가 봐야 할 것만, 없으면 빈 목록
- 자격증명 값·URL 쿼리스트링은 넣지 않는다.

```bash
python3 - <<'PY'
import json, os, datetime
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
root = os.path.expanduser("~/mnt/Claude/control_tower/runs")
os.makedirs(root, exist_ok=True)
rec = {"routine": "8. 0and1life 인스타 릴스", "file": "Schd_0and1Life-Insta.md",
       "date": now.strftime("%Y-%m-%d"), "start": "{시작 HH:MM}",
       "end": now.strftime("%H:%M"), "result": "{성공|부분|건너뜀|실패}",
       "count": 0, "summary": "{한 줄 요약}", "warnings": []}
with open(os.path.join(root, now.strftime("%Y-%m") + ".jsonl"), "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
PY
```
