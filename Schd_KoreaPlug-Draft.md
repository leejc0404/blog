*예약된 트리거 시간이 되면 해당 일자에 먼저 루틴이 실행되었더라도 무조건 다시 진행한다.

날짜: 실행 시점의 실제 KST 날짜를 사용한다 (이 프롬프트에 적힌 고정 날짜가 있어도 무시).

⚠️ 역할 분담: 이 루틴은 **운영 절차(언제·무엇을·몇 회·어떤 도구로)** 만 정의한다. **배포·SEO·관문 판정 기준의 단일 기준(SSOT)은 GitHub 지침서**다 — 이 루틴과 지침서가 상충하면 지침서를 따르고, 상충 발견 시 STEP 7 알림에 기록한다.

**v10.23(2026-08-03) 정비**: 지침서에 「5-4 ⛔ 발행 차단 관문」·「5-4B 캡처 품질·마크업 규칙」이 정식 조항으로 신설됨. 이 루틴에 중복 기술돼 있던 관문·캡처 규칙 원문은 삭제하고 **지침서 참조**로 대체했다(3일간 이어진 지침서-루틴 상충 해소). 대신 실측으로 검증된 **실행 방법**(미디어 업로드 경로, Astra meta 설정, 세션 만료 대응)을 절차로 추가했다.

---

## STEP 0 — 지침서 읽기 (GitHub, SSOT — 최우선 실행)

WebFetch → `https://raw.githubusercontent.com/leejc0404/blog/main/KoreaPlug-Draft.md`
(브라우저용 뷰 URL: `https://github.com/leejc0404/blog/blob/main/KoreaPlug-Draft.md`)

⚠️ Notion 지침 페이지(KoreaPlug-Draft v10.0)는 참조하지 않는다. 지침은 위 GitHub 파일만을 SSOT로 삼는다.

읽고 나서 이번 회차에 사용할 기준 3가지를 확보한다:
1. **5-4 ⛔ 발행 차단 관문** (①원본자료 ②가짜경험 ③이미지출처) — STEP 4f 판정 기준
2. **5-4B 캡처 품질·마크업 규칙** — STEP 4g 캡처·삽입 기준
3. **5-3 / 오류표** — STEP 6 SEO 보정 기준

조회 실패 시(404/403/네트워크 차단):
1. main 브랜치가 아닐 수 있으므로 저장소 루트(`https://github.com/leejc0404/blog`)를 1회 더 확인한다.
2. 그래도 실패하면 STOP하지 않는다 — 오류 로그에 "GitHub 지침서 조회 실패 → 인라인 폴백"을 기록하고, 이 문서 맨 아래 **[부록 A] 인라인 폴백 기준**을 사용해 배포를 계속 진행한다.

⚠️ 어떤 경우에도 지침 내용을 추측으로 생성하지 않는다.

---

## STEP 1 — 날짜 확인 (KST)

오늘(TODAY), 어제(TODAY_MINUS_1) 날짜를 기록한다.

---

## STEP 2 — Notion 후보 글 수집 → CANDIDATE_POSTS

notion-fetch로 메인 목록(`https://www.notion.so/33cbfe4a2ae181b9a743cb7c194dea7f`) 읽기.
"draft 일자" 컬럼이 비어 있는(— 또는 빈 칸) 행 전체를 CANDIDATE_POSTS로 수집.
각 행에서: #번호, 제목, 카테고리

카테고리 4개 페이지 별도 fetch 금지 — 서브페이지 URL은 STEP 4에서 notion-search로 직접 찾는다.

CANDIDATE_POSTS가 비어 있으면 → STEP 7로 건너뜀.

---

## STEP 3 — WordPress 인증 확보

**카테고리 ID (고정)**

| 카테고리 | WP Category ID |
|---|---|
| 🍜 Food & Drink | 3 |
| 🎭 Korean Culture | 4 |
| 🚌 Travel & Transport | 5 |
| 🏠 Lifestyle & Living | 18 |

**인증 순서 — 위에서부터 시도**

**⓪ 폴더 연결 (⭐ 2026-08-03 신설 — 이 단계를 빠뜨리면 ①이 항상 실패한다)**
스케줄 실행 세션은 **연결된 폴더가 0개**인 상태로 시작한다. pw.txt를 읽기 전에 먼저 실행한다:
`mcp__cowork__request_cowork_directory { path: "C:\Users\win\Documents\Claude" }`
연결 응답에 안내되는 `/sessions/{세션명}/mnt/Claude/` 경로로 접근한다.
> 배경: 2026-08-01~03 0and1Life 배포가 3일 연속 중단된 실제 원인이 이것이다. 경로만 고치고 폴더 연결을 넣지 않아 Read가 계속 실패했다.

**① pw.txt (Basic Auth)**
`C:\Users\win\Documents\Claude\pw.txt` 의 `KOREAPLUG_WP_APP_PASSWORD` 값으로 Basic Auth (`{WP_USER — pw.txt 참조}`).
⚠️ 비밀번호 값을 응답·로그·Notion에 출력하지 않는다. bash 안에서 변수로만 다룬다:
```
cd /sessions/{세션명}/mnt/Claude
U=$(grep '^KOREAPLUG_WP_USER' pw.txt | cut -d'=' -f2- | tr -d ' \r\n')
P=$(grep '^KOREAPLUG_WP_APP_PASSWORD' pw.txt | cut -d'=' -f2- | tr -d '\r\n' | sed 's/^ *//')
curl -s -u "$U:$P" "https://koreaplug.com/wp-json/wp/v2/users/me?context=edit"
```
200이면 인증 정상. ※ 샌드박스 네트워크는 자체 도메인만 열려 있다 — unsplash·pexels·github raw 는 curl 접근 불가(코드 000).
(舊 경로 `C:\Users\win\.claude\blog\pw.txt` 는 보호 경로라 마운트 불가 — v1.29에서 위 경로로 이전했다.)
⚠️ 이 경로도 **해당 폴더가 Cowork 세션에 연결돼 있을 때만** 읽힌다. 연결돼 있지 않으면 실패하는 것이 정상이므로, 중단하지 말고 곧바로 ②로 넘어간다.

**② Chrome 세션 nonce (현재 표준 경로)**
1. `list_connected_browsers` → `select_browser`
2. navigate → `https://koreaplug.com/wp-admin/index.php`
3. `document.body?.classList.contains('wp-admin')` 로 로그인 확인
4. 로그인 상태면 nonce 발급:
   `const nonce = (await fetch('/wp-admin/admin-ajax.php?action=rest-nonce', {credentials:'same-origin'}).then(r=>r.text())).trim();`
5. 이후 모든 REST 호출은 wp-admin 탭의 javascript_tool에서 `credentials:'same-origin'` + `'X-WP-Nonce': nonce` 헤더로 수행한다.

**③ 세션 만료 시 (2026-08-03 신설)**
`wp-login.php?...&reauth=1` 로 리다이렉트되면 세션이 만료된 것이다.
- ⛔ **(2026-08-03 정정) 루틴은 로그인 폼을 대신 제출하지 않는다.** 자격증명 입력과 인증 폼 제출은 AI 금지 동작이며, **아이디·비밀번호가 자동완성돼 있어도 '로그인' 버튼을 클릭하지 않는다.** (舊 조항은 자동완성 시 클릭을 허용했으나, 2026-08-03 실행에서 이 동작이 거부되어 조항을 정정했다.)
- 로그인 화면이 확인되면 오류 로그에 "WP 세션 만료 — 사용자 직접 로그인 필요"를 기록하고 STEP 7로 건너뛴다. draft 일자는 공란 유지.
- 사용자 조치 안내를 함께 남긴다: "Chrome에서 https://koreaplug.com/wp-admin 에 직접 로그인하고 '기억하기'를 체크해 주세요."
- 사용자가 로그인한 뒤 재실행하면 ②의 nonce 발급부터 정상 재개된다.

**④ 위 모두 실패**
오류 로그 기록 후 STEP 7로 건너뜀 (전체 중단, draft 일자 공란 유지).

> 참고: `web_fetch` 는 provenance 제한으로 WP REST를 직접 호출할 수 없다. WP 통신은 반드시 브라우저 안에서 한다.

---

## STEP 4 — Notion 서브페이지 읽기 → 필드 추출 → 관문 판정

CANDIDATE_POSTS 각 포스트에 대해 순서대로:

### [4a] 서브페이지 URL 확인
notion-search로 포스트 제목 검색 → 서브페이지 page_id·URL 확인.
검색 결과가 없을 때만 해당 카테고리 페이지 1개를 fetch:
- Food → `https://www.notion.so/Food-Dining-Blog-Posts-33ebfe4a2ae18136b1a9df45458cb1be`
- Travel → `https://www.notion.so/Travel-Transport-Blog-Posts-34fbfe4a2ae18031b3fbcc874496498e`
- Culture → `https://www.notion.so/Culture-Society-Blog-Posts-33ebfe4a2ae1815ba5e1d58b1bf9a44c`
- Lifestyle → `https://www.notion.so/Lifestyle-Living-Blog-Posts-33ebfe4a2ae18133a438ed9274c1dfb1`

### [4b] 서브페이지 로드
notion-fetch로 서브페이지 URL 호출.

### [4c] 필드 추출
"기본 정보" 표(섹션 1)에서: SLUG / SEO_TITLE / META_DESCRIPTION / FOCUS_KEYWORD / SUB_KEYWORDS / HTML_CONTENT / WP_CAT_ID / 1급 자료 조달 계획

- ⚠️ **FOCUS_KEYWORD**: Notion "Focus Keyword" 행 값 그대로 복사 (AI 재생성 금지)
- ⚠️ **SUB_KEYWORDS**: Notion "Sub Keywords" 행 값 그대로 복사 → `" / "` 를 `", "` 로 변환
- koreaplug-writer가 Google 자동완성으로 수집한 값이다. Cowork에서 재검색·수정 금지.

### [4d] 슬러그 중복 확인 + 미완성 draft 복구

`GET /wp-json/wp/v2/posts?slug={SLUG}&status=any&_fields=id,slug,status` (status=any 필수)

- **응답이 비어 있으면** → 중복 없음, [4e]로 진행.
- **응답에 데이터가 있으면**(기존 WP_POST_ID 확보) 곧바로 건너뛰지 말고 아래를 확인한다:
  1. Rank Math 키워드·점수가 실제로 설정돼 있는가 → 편집 화면에서 `wp.data.select('rank-math').getKeywords()` 확인, 또는 draft 목록의 "SEO 상세" 칼럼
  2. 콘텐츠에 스톡/깨진 이미지 패턴(`unsplash.com/pexels.com/pixabay.com/FEATURED_IMAGE`)이 남아 있는가 → `GET /wp-json/wp/v2/posts/{id}?context=edit&_fields=content`

  판정:
  - 키워드·점수 정상 + 이미지 정상 → 정상 완료된 글. Notion "draft 일자"를 TODAY로 채우고 건너뜀.
  - 키워드 미설정/점수 N/A → 이전 실행에서 STEP 6이 누락된 **미완성 draft**. 이 WP_POST_ID를 그대로 사용해 STEP 6부터 수행(STEP 5 재업로드 생략).
  - 이미지 패턴 잔존 → [4e] 이미지 처리도 함께 수행.
  - 복구 처리했으면 완료 후 Notion "draft 일자"·SEO 점수 갱신.

> ⚠️ 이 복구 로직이 작동하려면 "draft 일자"가 STEP 6 실패 시 계속 비어 있어야 한다. [5a]에서 draft 일자를 기록하지 않는 이유가 이것이다 — [6l] 참조.

### [4e] 히어로 이미지 URL 정합성

`[FEATURED_IMAGE_URL]` 플레이스홀더가 있거나, 이미 박혀 있는 `unsplash.com/photo-{ID}` 의 `{ID}` 가 `^[0-9]{10,13}-[0-9a-f]{12}$` 형식이 아닌 경우(=깨진 URL):

1. alt에서 IMAGE_KEYWORD 추출 (없으면 FOCUS_KEYWORD 사용)
2. navigate → `unsplash.com/s/photos/{IMAGE_KEYWORD}`
3. javascript_tool로 `img[src*="images.unsplash.com/photo-"]` 를 전부 수집 → **정규식과 일치하는 ID만** 후보 채택 (공유링크의 짧은 슬러그 ID는 CDN 404)
4. `https://images.unsplash.com/photo-{ID}?w=1200&q=80` 로 구성해 교체
5. 교체한 URL을 `fetch(url,{method:'HEAD'})` 로 200 확인 (실패 시 다른 후보로)

실패 시 → 오류 로그 기록, 포스트 업로드는 계속 진행.

### [4f] ⛔ 발행 차단 관문 판정 — **기준은 지침서 5-4**

지침서 5-4의 ①원본자료 ②가짜경험 ③이미지출처를 그대로 적용한다. 판정 시점은 **WordPress 업로드(POST) 직전**이며, **SEO 점수와 무관**하다.

- ①에 대해 기본 정보 표에 `1급 자료 조달 계획: 루틴가능 {화면·경로}` 가 명시돼 있으면 → **캡처 실행 주체는 이 루틴이다.** [4g]로 진행해 직접 캡처·삽입해서 관문을 스스로 충족시킨다.
- 로그인·결제·개인정보 입력이 필요한 화면은 캡처하지 않는다 → 다른 1급 자료로 대체하거나 반려.
- ⛔ **앱전용 화면 판정 (2026-08-09 신설, 지침서 5-4 연동)**: 이 루틴은 **브라우저만 조작**한다. 모바일 앱 안에서만 보이는 화면은 로그인 여부와 무관하게 캡처 불가다. **판정 질문: "이 자료가 웹 브라우저에서 보이는가?"** 아니오면 [4g]를 시도하지 말고 즉시 반려한다.
  - **반려 전 1회 확인**: 같은 서비스의 웹 버전·공식 페이지로 대체 가능하면 `루틴가능`으로 전환해 [4g] 진행.
  - 반려 시 사유 코드 `1급-앱전용`, 조달 주체 `사용자`로 기록.

**불통과 시**: STEP 5~6을 건너뛰고 draft 일자 공란 유지. 발행 반려 로그(`https://www.notion.so/3adbfe4a2ae18167880ecbe3c73b90cc`)에 행 추가:

`| {TODAY} | {SLUG} | {사유 코드} | {무엇을} | {어디에} | {왜} | {어떻게} | {루틴 또는 사용자} | 대기 |`

⚠️ "1급 자료 없음"만 적는 보고는 무효 — 무엇을·어디에·왜·어떻게·누가를 채운다(지침서 5-4). 같은 슬러그의 '대기' 행이 이미 있으면 중복 추가하지 않는다. 기록 후 다음 후보로 진행.

### [4g] 1급 자료 캡처 → WP 미디어 업로드 → 본문 삽입 (2026-08-03 실측 확정 경로)

캡처 **품질·마크업 기준은 지침서 5-4B**를 따른다. 아래는 **실행 방법**이다.

**1) 캡처**
- 대상 페이지로 navigate
- `computer` 도구의 **`zoom` 액션 + `region:[x1,y1,x2,y2]`** 로 필요한 영역만 잘라 찍는다
  ⚠️ `screenshot` 액션은 region 인자를 무시하고 전체 화면을 찍는다. 크롭은 반드시 `zoom`.
- 결과 이미지를 육안 확인 (헤더·스크롤바·커서·팝업 잔재 없는지)

**2) 업로드 — 브라우저 canvas 크롭 경로**
샌드박스와 브라우저는 파일시스템이 분리돼 있고, `zoom` 결과에는 upload용 imageId가 붙지 않는다. 그래서 아래 경로를 쓴다(실측 성공):

1. navigate → `https://koreaplug.com/wp-admin/media-new.php`
2. `find` 로 파일 input(`#async-upload`) ref 확보
3. `upload_image` 로 **전체 화면 screenshot(ss_… ID)** 을 그 input에 주입 — 이 단계는 업로드가 아니라 **픽셀을 페이지 컨텍스트로 옮기는 것**이다
4. javascript_tool에서 크롭 + webp 변환 + REST 업로드를 한 번에:

```javascript
const f = document.getElementById('async-upload').files[0];
const bmp = await createImageBitmap(f);
const S = bmp.width / 958;                 // 좌표계 보정 (스크린샷 폭 기준)
const [x,y,w,h] = [X1,Y1,W,H].map(v=>Math.round(v*S));
const c = document.createElement('canvas'); c.width=w; c.height=h;
c.getContext('2d').drawImage(bmp, x, y, w, h, 0, 0, w, h);
const blob = await new Promise(r=>c.toBlob(r,'image/webp',0.88));
const fd = new FormData();
fd.append('file', blob, 'evidence-{SLUG}-{n}.webp');
fd.append('alt_text', '{Focus Keyword 포함 설명}');
const r = await fetch('/wp-json/wp/v2/media', {method:'POST', credentials:'same-origin',
  headers:{'X-WP-Nonce': nonce}, body: fd});
```

5. 응답의 `source_url` 을 기록. 파일명은 반드시 `evidence-{SLUG}-{n}.webp` (지침서 5-4B).

**3) 본문 삽입**
지침서 5-4B의 `figure.evidence-capture` 표준 마크업으로, **해당 자료가 뒷받침하는 문단·표 바로 아래**에 삽입한다. 캡션은 `{출처 기관 — 화면명 · Captured YYYY-MM-DD}` 영문 표기.

**4) 확인**
업로드 후 프론트엔드 프리뷰(`/?p={WP_POST_ID}&preview=true`)에서 `figure.evidence-capture img` 의 `naturalWidth > 0` 을 확인하고 스크린샷으로 육안 검증.

실패 시 → 오류 로그 기록. 관문 ①을 충족하지 못하면 반려 처리([4f]).

---

## STEP 5 — WordPress Draft 업로드 + Notion 업데이트

(⚠️ [4d]에서 기존 WP_POST_ID로 복구 처리 중이면 이 STEP은 건너뛰고 STEP 6으로 직행)

**날짜 갱신**: HTML_CONTENT 상단 메타 라인의 `Last updated: {Month} {YYYY}` 표기가 있으면 업로드 시점 월로 갱신한다(첫 번째 매치 1개만).

POST `/wp-json/wp/v2/posts`

```json
{
  "title":      "{SEO_TITLE}",
  "content":    "<!-- wp:freeform -->\n{HTML_CONTENT}\n<!-- /wp:freeform -->",
  "status":     "draft",
  "slug":       "{SLUG}",
  "categories": [{WP_CAT_ID}]
}
```

응답에서 WP_POST_ID 기록.

> HTML_CONTENT가 길면(1만 자 이상) javascript_tool 한 번에 넣지 말고 `window.__A`, `window.__B` … 로 나눠 담은 뒤 이어붙여 POST한다. 템플릿 리터럴 안에 백틱·`${` 이 없는지 확인.

### [5a] Notion 서브페이지 업데이트 (Post ID·상태만)

- 상태: `작성완료` → `배포완료 (Draft)`
- WordPress Post ID: {WP_POST_ID}

⚠️ **"draft 일자"(메인 테이블 셀)는 여기서 기록하지 않는다.** STEP 6 전 과정이 성공했을 때만 [6l]에서 기록한다. 여기서 기록하면 STEP 6이 실패해도 다음 실행이 이 글을 후보로 잡지 않아 [4d] 복구 로직이 영원히 돌지 않는다.

### [5b] 슬러그 충돌 감지
실제 slug ≠ 요청 SLUG → 오류 로그 기록 후 해당 포스트 건너뜀.

---

## STEP 6 — Astra + Rank Math 설정 (Claude in Chrome 필수)

### [6a] 에디터 열기
navigate → `https://koreaplug.com/wp-admin/post.php?post={WP_POST_ID}&action=edit`
wait 4초 후 `document.body?.classList.contains('wp-admin')` 로 로그인 확인. 'not-logged-in'이면 STEP 3 ③번(세션 복구) 수행 후 재시도.

### [6b] Astra 설정 — REST meta 직접 지정 (2026-08-03 실측 확정)

사이드바 클릭 대신 REST로 postmeta를 지정한다. Astra meta는 `show_in_rest` 로 등록돼 있어 정상 저장되며, 새로고침 후 검증도 가능하다(Rank Math와 달리 이 방식이 실제로 반영됨).

POST `/wp-json/wp/v2/posts/{WP_POST_ID}`

```json
{"meta": {
  "ast-site-content-layout": "full-width-container",
  "site-content-style": "unboxed",
  "ast-banner-title-visibility": "disabled",
  "site-sidebar-layout": "default",
  "site-sidebar-style": "default",
  "astra-migrate-meta-layouts": "default"
}}
```

**[6b-검증]** 편집 URL로 새로고침(navigate) → wait 4초 →

```javascript
const m = wp.data.select('core/editor').getEditedPostAttribute('meta');
m['site-content-style']==='unboxed' && m['ast-banner-title-visibility']==='disabled' && m['ast-site-content-layout']==='full-width-container'
```

`false` 면 1회 재시도. 그래도 false면 오류 로그에 "Astra 설정 미반영" 명시 기록 — "완료"로 보고 금지.

> 콘텐츠는 STEP 5에서 freeform 래퍼로 저장돼 에디터가 자동 로딩한다. `resetBlocks`·`core/heading` 추가 금지. 본문이 비어 있을 때만 [6i] 폴백.

### [6c] Rank Math — UI 클릭 방식만 사용

⚠️ `wp.data.dispatch('rank-math').updateKeywords()/updateSerpTitle()/…` 은 **에러 없이 성공한 것처럼 보이지만 postmeta에 저장되지 않는다**(2026-07-24 실측). **JS dispatch 금지.**

**[6d] 패널 열기**: 상단 우측 Rank Math 점수 배지 클릭. 사이드바가 화면 밖이면 `find`로 포커스 키워드 입력창 ref를 찾아 `scroll_to`.

**[6e] 키워드 입력**: 포커스 키워드 입력창 클릭 → `FOCUS_KEYWORD` 타이핑 → Enter → 같은 입력창에 SUB_KEYWORDS를 하나씩 타이핑 → Enter (보통 4개, 총 5개).

**[6f] 스니펫 편집**: "스니펫 편집" 클릭
- 타이틀 필드 클릭 → Ctrl+A → `SEO_TITLE` 타이핑
- 설명 필드 클릭 → Ctrl+A → `META_DESCRIPTION` 타이핑
- ⚠️ Ctrl+A 후 타이핑해도 **이전 텍스트의 첫 글자 1개가 남는 사례가 반복 확인됨**(예: `aWhy do Koreans…`). 타이핑 직후 zoom으로 필드를 육안 확인하고, 잔여 문자가 있으면 필드 클릭 → Ctrl+Home → Delete로 제거 후 다시 확인.
- 창 닫기(X)

**[6g] 저장 + 재검증**
Ctrl+S → 저장 확인 → 편집 URL로 다시 navigate → wait 5초 → `wp.data.select('rank-math').getKeywords()` 에 쉼표 항목 5개가 남아 있어야 한다.
비어 있으면 [6d]부터 1회 재시도. 재시도 후에도 비면 오류 로그에 "SEO 설정 미반영" 명시 — "완료"로 보고 금지.

**[6h] 점수 확인 및 보정**
Rank Math 배지 숫자 확인. 목표 **78점 이상**.
미달 시 **지침서 5-3 + 오류표** 기준으로 REST API로 HTML 수정 → Ctrl+S → 재시도 1회.
(지침서 조회 실패 시에만 [부록 A] 사용.)

**[6i] 콘텐츠 재업로드 폴백** (에디터 본문이 비어 있을 때만)
POST `/wp-json/wp/v2/posts/{WP_POST_ID}` — `{"content": "<!-- wp:freeform -->\n{HTML_CONTENT}\n<!-- /wp:freeform -->"}`

### [6k] Notion SEO 점수 업데이트
메인 테이블 해당 행의 SEO 셀 `—` → 실제 점수.
⚠️ `<td>—</td>` + 카테고리 셀 같은 짧은 old_str은 다른 행과 중복된다. **제목 또는 한줄 요약 셀부터 포함해** 유일한 범위로 잡는다.

### [6l] draft 일자 기록 — 전 과정 성공 시에만

아래 중 하나라도 있었으면 draft 일자를 **공란으로 남긴다** (다음 실행이 [4d] 복구 로직으로 이어받는다. 슬러그 중복이 이미 있으므로 STEP 5는 자동으로 건너뛴다):
- Chrome 로그인 실패
- Astra 설정 미반영 (재시도 후에도)
- Rank Math 키워드가 [6g] 새로고침 재검증에서 비어 있음 (재시도 후에도)

성공했다면 메인 테이블 "draft 일자" 셀 → TODAY. ←인 컬럼도 [6m] 결과로 갱신.

### [6m] 들어오는 내부 링크 (지침서 6-3 — STEP 6 성공 시 필수)

주제가 인접한 기존 발행 글 2개를 고른다(**내부 링크를 이미 받고 있는 글 우선** — 고아 글에서 걸면 무효). 각 글에:

1. `GET /wp-json/wp/v2/posts?slug={기존슬러그}&_fields=id` → id 확인
2. `GET /wp-json/wp/v2/posts/{id}?context=edit` → `content.raw` 확보
3. 이미 신규 슬러그가 들어 있으면 건너뜀(중복 방지)
4. 마지막 `</ul>` 직전에 `<li><a href="/{신규슬러그}/">{신규 SEO_TITLE}</a></li>` 삽입 — 삽입 전 `lastIndexOf('Related reading') < lastIndexOf('<ul')` 인지 확인해 엉뚱한 리스트에 들어가지 않게 한다. Related reading 섹션이 없으면 신설.
5. `<ul>/<li>` 여닫이 개수 검증 → POST 저장. 실패 시 오류 로그만 남기고 발행은 유지(반려 아님).

⚠️ **슬러그 실재 확인**: koreaplug.com은 존재하지 않는 슬러그에도 HTTP 200 + "Page Not Found"(소프트404)를 반환한다. 상태코드로 판단하지 말고 **REST 조회 결과(id 존재) 또는 title 문자열**로 확인한다.

---

## STEP 7 — 완료 알림 출력 (200자 이내, 이전 단계 성공 여부와 무관하게 반드시 실행)

- 신규 포스트 있음: `KoreaPlug 발행완료 ✅ draft {N}개 | 관문반려 {R}건(로그 기록) | 인바운드링크 {L}건 | SEO평균 {점수}점 | 오류 {E}개 ({TODAY_KST})`
- 신규 포스트 없음: `KoreaPlug 자동 체크 완료 — 신규 글 없음 ({TODAY_KST})`
- [4d]에서 미완성 draft를 복구했으면 함께 기록: `KoreaPlug 미완성 draft {M}개 복구완료 (SEO/이미지) | ({TODAY_KST})`

⚠️ STEP 0에서 지침서 조회에 실패했거나 지침서-루틴 상충을 발견한 경우 그 사실을 한 줄로 함께 기록한다.
⚠️ Notion 메인 페이지 하단에 이번 회차 실행 로그를 append한다 (신규 draft·1급 자료·관문 결과·인바운드 링크·오류·다음 실행 시각).

---

## 🚨 오류 처리

| 상황 | 조치 |
|---|---|
| GitHub 지침서 조회 실패 | 저장소 루트 1회 재확인 → 실패 시 오류 로그 + [부록 A] 폴백으로 계속 진행 (STOP 아님, 추측 생성 금지) |
| pw.txt 접근 실패 | 폴더 미연결이면 정상. Chrome 세션 nonce(STEP 3 ②)로 전환 |
| WP 세션 만료(reauth) | 자동완성된 자격증명이 있으면 로그인 버튼만 클릭. 비어 있으면 중단 후 STEP 7 |
| Chrome 미연결 | 오류 로그 기록 후 STEP 7로 (전체 중단, draft 일자 공란 유지) |
| WordPress API 실패 | 로그 기록 후 다음 포스트 진행 |
| Notion 페이지 없음 | 로그 기록 후 다음 포스트 진행 |
| 관문 불통과 | 반려 로그 행 추가 + draft 일자 공란 + 다음 포스트 진행 (STEP 7에 관문반려 건수 표기) |
| 캡처 실패/어색 | 지침서 5-4B 기준으로 region 재지정해 1회 재캡처. 실패 시 관문 ① 불충족 → 반려 |
| 이미지 URL 404 | [4e] 4) 재시도 1회, 실패 시 플레이스홀더 유지 + 오류 로그 |
| Rank Math 78점 미달 | 지침서 5-3/오류표 기준 수정 후 재시도 1회 |
| SEO 설정이 새로고침 후 사라짐 | JS dispatch 금지 — UI 클릭([6d]~[6f]) + [6g] 새로고침 재검증 필수 |
| Astra 설정 미반영 | [6b] REST meta 재지정 1회 → 그래도 안 되면 명시 기록, draft 일자 공란 |

---

## [부록 A] 인라인 폴백 기준 (STEP 0 조회 실패 시에만 사용)

**관문(지침서 5-4 대체)**
1. 1급 원본 자료 최소 1개 — 직접 조작한 공개 화면 캡처 / 직접 센 수치 / 1차 기록. 비교표·공식 수치 재정리는 불인정.
2. 하지 않은 일의 1인칭 서술 0건. (실제 수행한 작업의 1인칭은 허용)
3. 모든 `<img>` 가 koreaplug.com 자체 업로드 또는 images.unsplash.com. 타 사이트 핫링크 0건.

**캡처(지침서 5-4B 대체)**
- 결과·표·조문 영역만 크롭, 헤더·스크롤바·커서·팝업 배제
- 파일명 `evidence-{SLUG}-{n}.webp`, `class="evidence-capture"` figure + figcaption 필수
- 삽입 위치는 해당 문단·표 바로 아래

**SEO 보정(지침서 5-3 대체)**
1. FOCUS_KEYWORD가 첫 `<p>`(도입부 100자 이내)에 포함
2. FOCUS_KEYWORD가 `<h2>` 1개 이상에 포함
3. SEO_TITLE ≤ 60자 + FOCUS_KEYWORD 포함
4. META_DESCRIPTION ≤ 150자 + FOCUS_KEYWORD 포함
5. 내부 링크 1개 이상
6. `<img>` alt에 FOCUS_KEYWORD 또는 연관어 포함
7. 본문 1,500자 이상
8. 목차 없으면 본문 상단에 `<div class="wp-block-rank-math-toc-block"></div>` 추가

⛔ 절대 금지: core/heading 블록 추가 / `getEditedPostContent()` freeform 소스 사용 / 키워드 기계적 반복 삽입
