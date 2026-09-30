# Schd_0and1Life-Insta — 발행 글 → 인스타그램 릴스 제작·전달 루틴 (Cowork 예약 작업용, v2.0 2026-10-01)

**v2.0에서 바뀐 것**: 캐러셀 폐지 → **릴스 전용**. 게시는 **반자동(HANDOFF)** — 루틴이 영상·커버·캡션·전달 페이지까지 만들고, 유행 음원을 붙이는 게시만 사용자가 앱에서 한다. **싱크 검증**이 게시 관문에 들어왔고, **일간 성과 측정**과 **3일 임시 자산 정리**가 신설됐다.

⚠️ **역할 경계 — 이 루틴은 도구다.** 릴스 구성·문구·영상 문법·품질의 판정 기준(SSOT)은 전적으로 GitHub 지침 `0and1Life-Insta.md`다. 이 루틴은 **운영 절차**(언제·무엇을·어디에 기록)와 **실행 자산**(파일 경로·릴레이·스크립트·알림 형식)만 정의한다. 규칙을 가리킬 때는 조항 번호로 참조한다(예: "지침 I-3-1"). 상충이 보이면 지침을 따르고 STEP 11에 기록한다.

사람이 없는 시간에 실행된다. **사용자 승인이 필요한 도구 호출을 불필요하게 하지 않는다.** 폴더 접근 요청은 하지 않는다.

이 루틴은 **WP 글(post)의 본문·상태·슬러그·카테고리·대표이미지를 절대 바꾸지 않는다.** 쓰는 곳은 네 군데뿐이다: ① WP 미디어(릴스 mp4·커버 JPEG) ② 전달 페이지 `reel-dl-latest` ③ 허브 페이지 `page 1922` 본문(카드 1장) ④ `instagram\` 폴더. **게시된 인스타 게시물은 어떤 경우에도 삭제하지 않는다.**

- **일간 흐름(STEP 0~12)은 Chrome MCP·브라우저 조작을 쓰지 않는다.** 예외는 STEP W 주간 레퍼런스 스캔뿐이며, 이때만 Chrome MCP로 인스타를 읽는다(읽기 전용 — 좋아요·팔로우·댓글·DM 금지).
- 인스타 API는 클라우드·PC 모두 `graph.instagram.com`이 차단이라 **사이트 릴레이 `POST https://0and1life.com/wp-json/o1/v1/ig`**(WPCode 스니펫 `ig-relay`)로만 호출한다. 토큰은 헤더 `X-O1-IGT`로만 전달되고 서버에 저장되지 않는다.

⚠️ [지침 출처] `https://raw.githubusercontent.com/leejc0404/blog/main/0and1Life-Insta.md?cb={epoch_ms}` — STEP 0에서 매번 `web_fetch`로 읽고 세션 내 재사용한다. 캐시버스터 없이 조회하지 않는다. 조항이 안 보이면 Draft 지침 5-0-A 3단 검증을 준용하고, 그래도 없으면 전달하지 않고 알림한다.

---

## 실행 자산 (경로·스크립트)

| 무엇 | 어디 | 비고 |
|---|---|---|
| 자격증명 | `C:\Users\win\Documents\Claude\pw.txt` | `ONEANDZERO_WP_USER` `ONEANDZERO_WP_APP_PASSWORD` `IG_USER_ID` `IG_ACCESS_TOKEN` — **값 출력 금지** |
| 릴레이 호출 | `instagram\relay\ig.py` | `me / limit / refresh / container / carousel / reel / status / media / publish / insights / my_media` |
| **릴스 렌더러** | `instagram\relay\render_reel_v8.py` | `reel_spec.json` → mp4 + `_timeline.json` + `_cover.jpg` |
| **효과음 합성** | `instagram\relay\build_reel_sfx.py` | `_timeline.json` → wav (전부 합성음) |
| **싱크 검증** | `instagram\relay\verify_reel_sync.py` | `reel_spec.json` 검사 · 종료코드 0만 통과 |
| **전달 페이지** | `instagram\relay\make_dl_page.py` | `handoff.json` → `reel-dl-latest` 덮어쓰기 |
| **임시 자산 정리** | `instagram\relay\cleanup_reel_temp.py` | 3일 경과분 휴지통 |
| 허브 카드 | `instagram\relay\hub.py` | `add <card.json>` · `seo <seo.json>` · `get` |
| 원장 | `instagram\ledger.json` | `reels.{slug}: {date, status, ig_media_id, ig_url, hub_card, video_media_id, cover_media_id, dur, techniques}` |
| **성과 기록** | `instagram\metrics.json` | `{slug: {posted, dur, techniques, daily: {YYYY-MM-DD: {...}}}}` |
| 레퍼런스 | `instagram\refs\inbox.md` · `refs\{YYYY-Www}.md` | |
| 회차 폴더 | `instagram\{YYYY-MM-DD}\{slug}\` | `reel_spec.json` `caption.txt` `reel-final.mp4` `*_cover.jpg` `*_timeline.json` `meta.json` |

설정값: `PUBLISH_MODE = HANDOFF`(기본) · `DAILY_TARGET = 1` · `LOOKBACK_DAYS = 3` · `TOKEN_REFRESH_DAYS = 30` · `IG_API = v23.0` · `REF_SCAN_DAY = 월요일`(KST) · `REF_MAX_POSTS = 6` · `TEMP_KEEP_DAYS = 3`

---

## STEP W. 주간 레퍼런스 스캔 (지침 I-3-5 — 월요일 또는 인박스에 미처리 링크가 있을 때만 · Chrome MCP 읽기 전용)

1. **수집 목록**(최대 `REF_MAX_POSTS`): ① `refs/inbox.md`의 `- [ ]` 줄 ② 벤치 계정 최근 **릴스** ③ 탐색·해시태그 상위의 **정보형 릴스**. 지침 I-3-5 "고를 기준"(저장÷좋아요 높은 것)으로 거른다.
2. **읽기 방법**: `…/reel/{code}/` 로 URL 이동 → 5초 대기 → 스크린샷. 30초 타임아웃이면 같은 URL로 1회 재시도, 그래도 실패하면 건너뛴다. 반응 수치는 `get_page_text`로 읽는다. **인스타 화면에서 클릭은 페이지 이동에만 쓴다.**
3. **기록**: `refs/{YYYY-Www}.md`에 지침 I-3-5 "추출 8항목" + 반응 수치 + "차용할 것 / 복제하지 않을 것"을 쓴다. 처리한 인박스 줄은 `[x]`로 바꾼다.
4. **반영**: 새 기법은 지침 I-3-2 표에 **행 추가 제안**으로 STEP 11에 남긴다(`🧩 기법 제안`). 렌더러 수정이 필요하면 코드를 고치지 말고 제안만 한다. ⛔ 지침 I-3-4 — 밈·영상의 **이미지·캐릭터·클립·음원 자체는 복제하지 않는다.** 차용은 편집 문법까지다.
5. 열었던 탭은 모두 닫는다.

## STEP 0. 지침 읽기·설정 확인
1. 지침을 `?cb=` 붙여 읽는다. Phase I-0~I-9와 반려 코드표가 모두 보이는지 확인한다.
2. 설정값을 세션 변수로 둔다. `PUBLISH_MODE`는 이 프롬프트의 값이 기준이며 지침·ledger에서 바꾸지 않는다.

## STEP 1. 날짜·폴더·자격증명
```bash
TODAY=$(TZ=Asia/Seoul date +%F); D1=$(TZ=Asia/Seoul date -d "yesterday" +%F); D3=$(TZ=Asia/Seoul date -d "3 days ago" +%F)
B="$HOME/mnt/Claude"; R="$B/instagram/relay"
ls "$B/pw.txt" "$R/ig.py" "$R/hub.py" "$R/render_reel_v8.py" "$R/build_reel_sfx.py" \
   "$R/verify_reel_sync.py" "$R/make_dl_page.py" "$R/cleanup_reel_temp.py" >/dev/null || echo "MISSING"
for k in ONEANDZERO_WP_USER ONEANDZERO_WP_APP_PASSWORD IG_USER_ID IG_ACCESS_TOKEN; do grep -q "^$k=" "$B/pw.txt" && echo "$k=있음" || echo "$k=없음"; done
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
python3 ig.py insights {media_id} views,likes,comments,shares,saved,reach,total_interactions
python3 ig.py insights {media_id} profile_visits,profile_activity
```
1. `ledger.reels` 중 `status="posted"` 인 전 회차를 대상으로 한다(게시 후 30일까지).
2. `metrics.json`의 `{slug}.daily[TODAY]`에 기록: `views, likes, comments, shares, saved, reach, profile_visits, external_link_taps`. **덮어쓰지 말고 날짜별로 누적**한다.
3. `insights`가 `bad_action`이면 스니펫 미배포다 — 측정을 건너뛰고 STEP 11에 `📊 측정 건너뜀(스니펫 insights 미배포)` 한 줄만 남긴다. 중단하지 않는다.
4. **길이·기법 판단은 여기서 하지 않는다.** 수치만 쌓고, 해석과 반영은 지침 I-8-2·I-8-3에 따라 월간에 한다. 단, 게시 3편 이상이 쌓였고 최근 3편의 `shares` 합이 직전 3편보다 **50% 이상 낮으면** STEP 11에 `⚠️ 공유 하락 — 구성 재검토 필요`를 붙인다.

## STEP 3. 대상 글 선정 (지침 I-1)
```bash
curl -s "https://0and1life.com/wp-json/wp/v2/posts?status=publish&after=${D3}T00:00:00&before=${D1}T23:59:59&per_page=20&orderby=date&order=desc&_fields=id,slug,date,modified,title,categories,link"
```
1. `ledger.reels`에 있는 slug는 `X-LEDGER`로 제외. 지침 I-1-3의 나머지 코드를 순서대로 판정(`X-THIN`은 STEP 4에서 확정).
2. 우선순위 I-1-4로 1편 선정. 나머지는 `ledger.reels.{slug}.status="pending"`으로만 기록.
3. 대상이 없으면 `log.md`에 한 줄 남기고 **STEP 12 → STEP 11**로 간다(정리와 측정은 대상이 없어도 돈다).
4. 회차 폴더 `instagram\{TODAY}\{slug}\` 생성.

## STEP 4. 본문 최종본 확보·구조 추출
```bash
curl -s "https://0and1life.com/wp-json/wp/v2/posts/{ID}?_fields=id,slug,title,date,modified,content,categories,featured_media" -o /tmp/post.json
```
- 추출: 제목, Core Fact / Primary Insight / Actionable Tip, 모든 `<table>`, H2 목록(⭐ GAP H2), `📌`/`*핵심 :` 요약 줄, 출처 명칭, `modified`.
- HTML을 벗긴 **본문 전체 텍스트**를 `post_text.txt`로 저장(STEP 7 숫자 대조용).
- `<table>` 0개이고 Core Fact에 수치가 없으면 `X-THIN` — ledger 기록 후 다음 후보로(1회).

## STEP 4.5. 페르소나·연출 선택 (지침 I-2-1 · I-3-2)
1. **페르소나를 먼저 적는다.** 글의 검색 의도에서 "누가 지금 이 정보를 필요로 하는가"를 한 문장으로 → `reel_spec.json` 최상위 `persona`.
2. 그 페르소나의 **12자 내외 호명구**를 1장면 `persona` 필드에 넣는다(예: `10월 연차 아직 안 냈다면`).
3. **연출 기법을 3개 이상 고른다**(지침 I-3-2 표). `ledger.reels` 최근 회차의 `techniques`를 읽어 **직전 회차와 같은 조합이 되지 않게** 한다.
4. 이번 주 `refs/{YYYY-Www}.md`가 있으면 반응 좋은 훅 유형을 우선한다.
5. 선택 결과를 `meta.json.persona`, `meta.json.techniques`에 적는다.

## STEP 5. 원고 작성 → `reel_spec.json` · `caption.txt`
- 지침 I-2(OREO 4단·3초 법칙·숫자 복사·날짜 문구·유도 문구)와 I-4(캡션·해시태그)를 그대로 적용한다.
- `reel_spec.json`: 최상위 `brand` `source` `persona` `structure`, `scenes[4]` = `hook / (compare|big) / bars / cta`.
  - 장면 길이 기본 **2.8 / 3.0 / 3.4 / 4.0**(지침 I-2-0). **CTA 4.0은 줄이지 않는다.**
  - E 장면에 `blog_note`(`전체 표는 블로그에`)를 **반드시** 넣는다(지침 I-3-2c).
- `caption.txt`는 지침 I-4-1 순서를 그대로 따른다.
- `hub_card.json`: `slug, title, date, category, thumb(커버 URL — STEP 9에서 채움), ig_url(게시 후), points[2~3]`.

## STEP 6. 렌더 (클라우드)
```bash
mkdir -p ~/ig_work && cd ~/ig_work && (ls package/dist/public/static/alternative >/dev/null 2>&1 || (npm pack pretendard@1.3.9 >/dev/null && tar xzf pretendard-1.3.9.tgz))
export PRETENDARD_DIR=~/ig_work/package/dist/public/static/alternative
# render_reel_v8.py · build_reel_sfx.py · verify_reel_sync.py 를 PC relay 폴더에서 device_stage_files 로 가져온다
python3 render_reel_v8.py reel_spec.json reel-final.mp4          # → mp4(무음) + _timeline.json + _cover.jpg
python3 build_reel_sfx.py reel-final_timeline.json sfx.wav
ffmpeg -y -v error -i reel-final.mp4 -i sfx.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 160k -ar 44100 -shortest -movflags +faststart reel-final-sfx.mp4
mv reel-final-sfx.mp4 reel-final.mp4
```
- 산출: `reel-final.mp4`(효과음 포함), `reel-final_cover.jpg`, `reel-final_timeline.json`.
- **커버는 2.6초 지점 자동 추출이다.** 첫 프레임은 카운트업 시작점이라 비어 있다(지침 I-3-1).

## STEP 7. 자가검수 (지침 I-5 — 9항목 전부)
```bash
python3 verify_reel_sync.py reel_spec.json     # 종료코드 0 이어야 통과
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate -show_entries format=duration reel-final.mp4
```
1. **① 숫자 전수 대조**: `reel_spec.json`·`caption.txt`의 모든 숫자 토큰을 뽑아 `post_text.txt`에 있는지 확인. 기준일 표기·장면 번호는 제외. 하나라도 없으면 `R-NUM`.
2. **② 안전영역**: 대표 프레임 3장(훅·E·CTA)을 뽑아 `Read`로 보고, 글자가 **x 60~1020 · y 410~1560** 밖으로 나가지 않았는지 본다. 넘으면 `R-SAFE`.
3. **③ 규격**: 1080×1920 · 30fps · 오디오 트랙 존재. 아니면 `R-SPEC`.
4. **④ 커버**: `_cover.jpg`를 `Read`로 열어 훅 문구와 숫자가 보이는지. 비어 있으면 `R-COVER`.
5. **⑤ 날짜 문구** — 지침 I-2-4. **⑥ 유도 문구 3곳** — 지침 I-2-5.
6. **⑦ 화자·금지어·저작권** — 지침 I-2-6 · I-2-7 · I-3-4.
7. **⑧ 싱크** 🚨: `verify_reel_sync.py` 종료코드가 0이 아니면 **`R-SYNC`로 즉시 중단.** 수정 후 재검사해 통과하기 전에는 어떤 경우에도 전달하지 않는다. (2026-10-01 사고: 모션 속도를 바꾸며 큐 표를 안 고쳐 450ms 어긋남)
8. **⑨ 연출 다양성**: `meta.techniques`가 3개 이상이고 직전 회차와 동일 조합이 아닌지. 같으면 `R-SAME`.
9. 반려가 있으면 STEP 5로 돌아가 **1회만** 수정·재렌더. 다시 실패하면 전달하지 않고 `ledger.reels.{slug} = {status:"held", held:"R-…"}` 기록 후 STEP 8 → 12 → 11.

## STEP 8. PC 저장
- `device_commit_files`로 `instagram\{TODAY}\{slug}\`에 `reel_spec.json caption.txt reel-final.mp4 reel-final_cover.jpg reel-final_timeline.json hub_card.json post_text.txt`를 저장한다.
- `meta.json`: `{blog_post_id, blog_url, blog_modified_at_build, persona, techniques, dur, scenes, status:"ready"|"held", checks:{...}}`.

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
- 업로드 후 `curl -sI {url}`로 200을 확인한다. 실패하면 `E-UPLOAD`.

## STEP 10. 전달 (지침 I-7-1 · `PUBLISH_MODE=HANDOFF`)
```bash
cd "$R" && python3 make_dl_page.py {회차폴더}/handoff.json
```
`handoff.json`은 슬러그를 **항상 `reel-dl-latest`** 로 둔다(구글 문서가 가리키는 고정 주소 — 새로 만들지 않고 덮어쓴다).
```json
{"slug":"reel-dl-latest","title":"0and1life 릴스 저장 (최신)",
 "items":[{"label":"{글 제목}","note":"{길이}초","video_url":"{wp_media.video.url}",
           "filename":"0and1life-reel-{slug}.mp4","caption_file":"{회차폴더}/caption.txt"}]}
```
1. 생성된 페이지 URL이 200인지, `download=` 속성과 복사 버튼이 각각 들어갔는지 `curl | grep -c`로 확인한다. 실패하면 `E-PAGE` — 알림에 영상 URL을 직접 실어 대체한다.
2. `ledger.reels.{slug} = {date:TODAY, status:"handoff", video_media_id, cover_media_id, dur, techniques, hub_card:false}`.
3. STEP 11 알림에 **전달 페이지 URL 하나만** 싣는다.
4. **사용자가 게시했다고 알리면** (같은 세션 또는 다음 회차):
   ```bash
   python3 ig.py my_media 5      # 최근 게시물에서 permalink·media_id 확보
   ```
   → `ledger.reels.{slug}.status="posted"`, `ig_media_id`, `ig_url` 기록 → `hub_card.json.ig_url` 채우고 `python3 hub.py add hub_card.json` → 8초 뒤 `curl -s https://0and1life.com/ig/?cb=$(date +%s) | grep -c "o1-ig-card:{slug}"` ≥ 1 이면 `hub_card:true`, 아니면 1회 재시도 후 `E-HUB`.

**`PUBLISH_MODE=AUTO` (예외 — 사용자가 그 회차에 명시 지시했을 때만)**
```bash
python3 ig.py reel {video_url} caption.txt {cover_url}   # → creation_id
python3 ig.py status {creation_id}                        # FINISHED 까지 5초 간격
IG_PUBLISH_APPROVED=yes python3 ig.py publish {creation_id}
```
- `bad_action`이면 스니펫에 `reel` 미배포다 → `E-REEL` 기록 후 **HANDOFF로 전환해 계속 진행**한다. 중단하지 않는다.
- ⚠️ AUTO로 올리면 **유행 음원이 붙지 않는다.** 기본값으로 두지 않는다.

## STEP 11. 완료 알림 (앞 단계 성공 여부와 무관하게 반드시 실행)
PushNotification 1회. 첫 문장은 한 줄 요약, 그 뒤 표. 모두 한글.
- 전달함: `📱 인스타 릴스 {TODAY} — {slug} 준비 완료 · {길이}초 · 싱크 검증 통과 · 저장 https://0and1life.com/reel-dl-latest/`
- 대상 없음: `📱 인스타 릴스 {TODAY} — 대상 글 없음`
- 반려·오류: `📱 인스타 릴스 {TODAY} — {slug} 보류({코드}) · {한 줄 원인}`
- 덧붙이는 줄(해당 시): `🔑 토큰 갱신 {성공|실패}` · `📊 어제 대비 조회 {n} · 공유 {n}` · `⚠️ 공유 하락 — 구성 재검토 필요` · `🗑 임시 자산 {n}건 정리` · `⏳ pending {n}편` · `🎬 기법 {a·b·c}` · `🔍 레퍼런스 스캔 {n}편` · `🧩 기법 제안: {한 줄}` · `📐 지침-루틴 상충: {조항}`

## STEP 12. 임시 자산 정리 (지침 I-9 — 대상 글 유무와 무관하게 매 회차)
```bash
cd "$R" && python3 cleanup_reel_temp.py --days 3 --dry    # 먼저 목록 확인
python3 cleanup_reel_temp.py --days 3
```
- 대상: 슬러그가 `reel-dl-` 로 시작하는 페이지(단 `reel-dl-latest`는 **제외 — 고정 주소**), 파일명이 `reel-*-final.mp4` / `reel-*-cover.jpg` 인 미디어 중 **생성 후 3일 경과분**.
- **휴지통으로만 보낸다.** `force` 영구 삭제는 어떤 경우에도 하지 않는다.
- `ledger.reels`에 `status="posted"` 기록이 없는 회차의 미디어는 **보류**하고 알림에 남긴다(아직 안 올린 것을 지우지 않기 위해).
- 정리 건수를 STEP 11에 `🗑 임시 자산 {n}건 정리`로 붙인다.

---

## 🚨 오류 처리

| 상황 | 조치 |
|---|---|
| PC 미연결·pw.txt 없음 | 즉시 중단, STEP 11 알림. 폴더 접근 요청 금지 |
| `me` username ≠ 0and1life | `E-TOKEN` 전면 중단(다른 계정 게시 방지) |
| 릴레이 401/404 | `E-RELAY` — 스니펫 활성·이름 확인 요청 |
| 릴레이 502(`upstream`) | 30초 후 1회 재시도 → 실패 시 준비 단계까지만 |
| `insights` `bad_action` | 측정만 건너뛰고 계속 진행 (`📊 측정 건너뜀`) |
| `reel` `bad_action` (AUTO 시도 시) | `E-REEL` 기록 후 HANDOFF로 전환해 계속 |
| **`verify_reel_sync.py` 실패** | 🚨 `R-SYNC` — **전달 중단.** 타이밍 표 `T` 수정 → 재렌더 → 재검사 |
| 렌더·효과음·먹싱 실패 | 글꼴 재설치 1회 → 실패 시 `E-RENDER`로 held |
| 전달 페이지 생성 실패 | `E-PAGE` — 알림에 영상 URL 직접 기재 |
| 허브 카드 검증 실패 | 1회 재시도 → `E-HUB`(게시 유지) |
| STEP W 스크린샷 타임아웃 반복 | 그 회차 스캔 건너뜀, 인박스 `[ ]` 유지 |
| 같은 날 2회 실행 | ledger에 `handoff`/`posted`가 있으면 STEP 3에서 제외되어 "대상 없음"으로 끝난다 |

## ⚠️ 전제조건 (사용자 몫 — 2026-10-01 기준)

| 항목 | 상태 | 비고 |
|---|---|---|
| WPCode 스니펫 `ig-relay` **v1.2** | ⬜ **배포 필요** | `reel` · `insights` · `my_media` 3개 추가됨. `relay\wpcode_ig-relay.php` 전문으로 교체 |
| Meta 앱 · 장기 토큰 | ✅ pw.txt 보관, 0and1life(MEDIA_CREATOR) | 60일 토큰, 30일마다 자동 갱신 |
| 프로필 링크 = 허브 `/ig/?utm_...=ig_bio` | ✅ | 모바일 앱에서만 변경 가능 |
| 허브 페이지 1922 공개·index | ✅ | 제목·메타 고정, 카드만 추가 |
| 전달 페이지 `reel-dl-latest` | ✅ 생성됨(page 1980) | 구글 문서가 가리키는 고정 주소 — 삭제 금지 |
| 상시 전달 구글 문서 | ✅ | 링크가 `reel-dl-latest` 고정이라 갱신 불필요 |
| Cowork 예약 `0and1life 인스타 릴스`(03:30 KST, PC 연결, `C:\Users\win\Documents\Claude` 연결) | ⬜ **프롬프트 교체 필요** | 이 파일 전문으로 교체 |
| `PUBLISH_MODE` | `HANDOFF` | 유행 음원 때문에 기본은 반자동. AUTO는 회차별 지시로만 |

## Cowork 원라이너

토큰 확인(2) → **전 회차 성과 측정(M)** → 대상 글 1편 선정(3) → 본문 최종본(4) → 페르소나·기법 선택(4.5) → OREO 4장면 원고·캡션(5) → 렌더+효과음+커버(6) → **자가검수 9항목, 싱크 실패면 무조건 중단(7)** → PC 저장(8) → WP 업로드(9) → `reel-dl-latest` 덮어쓰기(10) → 알림에 URL 하나(11) → 3일 지난 임시 자산 정리(12). 통과 못 하면 **전달하지 말고** held로 남긴다.
