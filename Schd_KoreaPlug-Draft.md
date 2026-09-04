[루틴 : KoreaPlug-Draft — v11.0 · 2026-09-04]

*예약된 트리거 시간이 되면 해당 일자에 먼저 루틴이 실행되었더라도 무조건 다시 진행한다.

날짜: 실행 시점의 실제 KST 날짜를 사용한다 (이 프롬프트에 적힌 고정 날짜가 있어도 무시).

⚠️ 역할 분담: 이 루틴은 **운영 절차(언제·무엇을·몇 회·어떤 도구로)** 만 정의한다. **배포·SEO·관문 판정 기준의 단일 기준(SSOT)은 GitHub 지침서**다 — 이 루틴과 지침서가 상충하면 지침서를 따르고, 상충 발견 시 STEP 7 알림에 기록한다.

---

## ⛔ STEP -1 — AdSense 보호 규칙 (모든 STEP에 우선하는 불변 규약)

이 사이트의 광고 수익은 **자동 광고(Auto ads) 로더 스크립트 하나**에 전부 의존한다. 수동 광고 유닛(`class="adsbygoogle"`)은 0개이므로, 이 태그가 사라지면 광고가 통째로 멈추고 중복되면 무의미한 중복 로드가 발생한다.

**현재 구성 (2026-09-04 확정)**

| 항목 | 값 |
|---|---|
| 로더 위치 | **WPCode 스니펫 ID `999` "AdSense - KoreaPlug"** (HTML · 사이트 전체 헤더 · 활성) |
| 로더 태그 | `<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4305580463524328" crossorigin="anonymous"></script>` |
| 페이지당 개수 | **정확히 1개** |
| `ads.txt` | `google.com, pub-4305580463524328, DIRECT, f08c47fec0942fa0` |
| 광고 모드 | 자동 광고 (수동 유닛 0개) |
| WPCode 「헤더 및 푸터」 전역 헤더 | **AdSense 코드를 넣지 않는다** — 여기 있던 중복분을 제거해 스니펫 999로 일원화했다 |

**규칙**

1. ⛔ **WPCode 「헤더 및 푸터」 전역 헤더 블록에 AdSense 태그를 다시 넣지 않는다.** 그 블록은 18KB 규모의 CSS·JS 혼합 덩어리라 수익 코드가 묻히면 실수로 삭제되기 쉽다
2. ⛔ **스니펫 999를 비활성화하지 않는다.** 이 스니펫이 꺼지면 사이트 전체 광고가 즉시 중단된다
3. **헤더 영역(스니펫·전역 헤더·테마)을 건드린 회차는 반드시 아래를 검증**하고 STEP 7에 결과를 적는다:

```bash
# 홈 + 최신 글 3편에서 로더 개수와 퍼블리셔 ID를 확인한다
curl -s -A "Mozilla/5.0" "https://koreaplug.com/?nocache=$(date +%s%N)" -o /tmp/ad.html
grep -c 'pagead/js/adsbygoogle.js' /tmp/ad.html        # 반드시 1
grep -oc 'ca-pub-4305580463524328' /tmp/ad.html        # 반드시 1
curl -s -A "Mozilla/5.0" https://koreaplug.com/ads.txt # 위 표와 동일해야 한다
```

   - **0개** → 즉시 스니펫 999를 다시 활성화하고 STEP 7에 🔴로 보고한다
   - **2개 이상** → 어느 쪽이 추가됐는지 찾아 제거한다. 제거 순서는 **먼저 남길 쪽을 확인한 뒤 지운다** — 0개가 되는 순간을 만들지 않는다
4. ⚠️ **URL을 만들 때 이중 슬래시(`//`)를 만들지 않는다.** `https://koreaplug.com//?nc=` 는 301을 반환하고, `-L` 없는 curl은 빈 본문을 받아 **로더 0개로 오판**한다

---

## STEP 0 — 지침서 읽기 + 무결성 검증 (GitHub, SSOT — 최우선 실행)

### [0-1] 1차 조회 — 캐시버스터 필수

WebFetch → `https://raw.githubusercontent.com/leejc0404/blog/main/KoreaPlug-Draft.md?cb={epoch_ms}`
(브라우저용 뷰 URL: `https://github.com/leejc0404/blog/blob/main/KoreaPlug-Draft.md`)

⚠️ **`?cb=` 없이 조회하지 않는다.** 캐시된 구버전 사본이 반환되면 실재하는 조항을 "없다"고 오판하고 허위 상충을 보고하게 된다.
⚠️ Notion 지침 페이지는 참조하지 않는다. 지침은 위 GitHub 파일만을 SSOT로 삼는다.

### [0-2] 본문 자가검증

받은 문서에서 아래를 **문자열로 확인**하고 결과를 기록한다:
- `5-4. ⛔ 발행 차단 관문` 포함 여부
- `5-4B. 캡처 품질·마크업 규칙` 포함 여부
- 문서 문자 수 / 최신 개정 이력 줄

셋 다 정상이면 이번 회차 기준 3가지를 확보하고 STEP 1로 간다:
1. **5-4 ⛔ 발행 차단 관문** (①원본자료 ②가짜경험 ③이미지출처) — STEP 4f 판정 기준
2. **5-4B 캡처 품질·마크업 규칙** — STEP 4g 캡처·삽입 기준
3. **5-3 / 오류표** — STEP 6 SEO 보정 기준

### [0-3] 조항이 안 보이면 — 3단 검증

"없다"고 판정하기 **전에** 아래를 전부 밟는다:
1. 같은 URL에 **새** `?cb={epoch_ms}` 를 붙여 1회 더 조회
2. Claude in Chrome 에서 `fetch(rawURL + '?cb=' + Date.now())` 로 재조회 — 샌드박스 fetch 도구와 브라우저는 캐시 계층이 다르다
3. 그래도 없으면 **결번 확정**

어느 단계에서든 조항을 찾으면 **그것이 진짜 지침서다.** 이미 폴백으로 판정을 시작했더라도 되돌려 다시 판정한다.
⚠️ 이 경우는 **상충이 아니다.** STEP 7에 "지침서-루틴 상충"으로 쓰지 말고 **"지침서 조회 캐시 사고 — {단계}에서 조항 확인"** 으로 기록한다.

### [0-4] 결번 확정 시 — 조항 자기보완 후 계속 진행

**STOP하지 않는다.** 아래를 수행하고 draft 를 계속한다:

1. **작성** — 결번 조항의 초안을 쓴다. 근거는 ⓐ 이 문서 **[부록 A]** → ⓑ `0and1Life-Draft.md` 의 대응 조항 → ⓒ 최근 7일 반려 로그·실행 로그의 실측 사실 **순서로만** 삼는다. 근거 없는 창작 금지
2. **반영** — `C:\Users\win\Documents\Claude\blog\KoreaPlug-Draft.md` 에 **직접 써 넣는다.** 조항 제목에 `(자동 신설 {TODAY}, 루틴 작성)` 표기
   - ⛔ **추가만 한다.** 기존 조항 삭제·번호 변경 금지
3. **커밋 금지** — git commit·push 는 **하지 않는다.** 사용자가 직접 한다
4. **즉시 적용** — 신설 조항을 그 회차 판정 기준으로 바로 적용한다
5. **보고** — STEP 7 알림과 Notion 실행 로그에 `조항 자동 신설 {조항번호}` 표기 + **신설 조항 전문**을 남긴다

### [0-5] 조회 자체가 실패할 때 (404/403/네트워크 차단)

1. 저장소 루트(`https://github.com/leejc0404/blog`)를 1회 확인
2. Claude in Chrome 으로 1회 확인
3. 그래도 실패하면 STOP하지 않는다 — 오류 로그에 "GitHub 지침서 조회 실패 → 인라인 폴백"을 기록하고 **[부록 A]** 로 배포를 계속한다
   ⚠️ 이 경우는 **조항 자기보완을 하지 않는다.** 문서를 못 읽은 것이지 결번이 확인된 것이 아니다

⚠️ 어떤 경우에도 지침 내용을 **추측으로** 생성하지 않는다. 자기보완([0-4])은 ⓐⓑⓒ 근거가 있을 때만 허용되는 예외다.

---

## STEP 1 — 날짜 확인 (KST)

오늘(TODAY), 어제(TODAY_MINUS_1) 날짜를 기록한다.

---

## STEP 2 — Notion 후보 글 수집 → CANDIDATE_POSTS

notion-fetch로 메인 목록(`https://www.notion.so/33cbfe4a2ae181b9a743cb7c194dea7f`) 읽기.
"draft 일자" 컬럼이 비어 있는(— 또는 빈 칸) 행 전체를 CANDIDATE_POSTS로 수집.
각 행에서: #번호, 제목, 카테고리

카테고리 4개 페이지 별도 fetch 금지 — 서브페이지 URL은 STEP 4에서 notion-search로 직접 찾는다.

CANDIDATE_POSTS가 비어 있으면 → **STEP 6m-Q(예약 큐 처리)를 먼저 수행한 뒤** STEP 7로 건너뜀.
> 후보가 없는 날에도 `[6m-Q]` 인바운드 링크 예약 큐는 비워야 한다. 신규 글이 발행(`future` → `publish`)되는 날은 대개 신규 후보가 없는 날이기 때문이다.

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

**⓪ 폴더 연결 (이 단계를 빠뜨리면 ①이 항상 실패한다)**
스케줄 실행 세션은 **연결된 폴더가 0개**인 상태로 시작한다. pw.txt를 읽기 전에 먼저 실행한다:
`mcp__cowork__request_cowork_directory { path: "C:\Users\win\Documents\Claude" }`
연결 응답에 안내되는 `/sessions/{세션명}/mnt/Claude/` 경로로 접근한다.

**① pw.txt (Basic Auth)**
`C:\Users\win\Documents\Claude\pw.txt` 의 `KOREAPLUG_WP_APP_PASSWORD` 값으로 Basic Auth.
⚠️ 비밀번호 값을 응답·로그·Notion에 출력하지 않는다. bash 안에서 변수로만 다룬다:
```bash
cd /sessions/{세션명}/mnt/Claude
U=$(grep '^KOREAPLUG_WP_USER' pw.txt | cut -d'=' -f2- | tr -d ' \r\n')
P=$(grep '^KOREAPLUG_WP_APP_PASSWORD' pw.txt | cut -d'=' -f2- | tr -d '\r\n' | sed 's/^ *//')
curl -s -u "$U:$P" "https://koreaplug.com/wp-json/wp/v2/users/me?context=edit"
```
200이면 인증 정상. ※ 샌드박스 네트워크는 자체 도메인만 열려 있다 — unsplash·pexels·github raw 는 curl 접근 불가(코드 000).
⚠️ 이 경로도 **해당 폴더가 세션에 연결돼 있을 때만** 읽힌다. 연결돼 있지 않으면 실패하는 것이 정상이므로, 중단하지 말고 곧바로 ②로 넘어간다.

> ⭐ **Basic Auth가 살아 있으면 STEP 5·6m·6n은 curl로 처리한다.** 앱 비밀번호 Basic Auth로 `GET/POST /wp-json/wp/v2/posts` 가 정상 동작한다. **Rank Math 설정(`[6c]`~`[6g]`)과 WPCode 조작만 브라우저 UI가 필요**하고, 나머지 REST 작업은 브라우저 없이 끝난다.

**② Chrome 세션 nonce (Rank Math UI 작업의 표준 경로)**
1. `list_connected_browsers` → `select_browser`
2. navigate → `https://koreaplug.com/wp-admin/index.php`
3. `document.body?.classList.contains('wp-admin')` 로 로그인 확인
4. 로그인 상태면 nonce 발급:
   `const nonce = (await fetch('/wp-admin/admin-ajax.php?action=rest-nonce', {credentials:'same-origin'}).then(r=>r.text())).trim();`
5. 이후 브라우저 경유 REST 호출은 wp-admin 탭의 javascript_tool에서 `credentials:'same-origin'` + `'X-WP-Nonce': nonce` 헤더로 수행한다

**③ 세션 만료 시**
`wp-login.php?...&reauth=1` 로 리다이렉트되면 세션이 만료된 것이다.
- ⛔ **루틴은 로그인 폼을 대신 제출하지 않는다.** 자격증명 입력과 인증 폼 제출은 AI 금지 동작이며, **아이디·비밀번호가 자동완성돼 있어도 '로그인' 버튼을 클릭하지 않는다**
- 로그인 화면이 확인되면 오류 로그에 "WP 세션 만료 — 사용자 직접 로그인 필요"를 기록한다
- **①(Basic Auth)이 살아 있으면 STEP 5까지는 계속 진행**하고, Rank Math 설정만 미완으로 남긴 뒤 draft 일자를 공란으로 둔다(`[6l]`). 다음 실행이 `[4d]` 복구 로직으로 이어받는다
- ①도 죽어 있으면 STEP 7로 건너뛴다. draft 일자는 공란 유지
- 사용자 조치 안내를 함께 남긴다: "Chrome에서 https://koreaplug.com/wp-admin 에 직접 로그인하고 '기억하기'를 체크해 주세요."

**④ 위 모두 실패**
오류 로그 기록 후 STEP 7로 건너뜀 (전체 중단, draft 일자 공란 유지).

> 참고: `web_fetch` 는 provenance 제한으로 WP REST를 직접 호출할 수 없다. WP 통신은 **curl(Basic Auth)** 또는 **브라우저 안**에서 한다.

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
- writer 루틴이 Google 자동완성으로 수집한 값이다. 재검색·수정 금지

### [4d] 슬러그 중복 확인 + 미완성 draft 복구

`GET /wp-json/wp/v2/posts?slug={SLUG}&status=any&_fields=id,slug,status` (status=any 필수)

- **응답이 비어 있으면** → 중복 없음, [4e]로 진행
- **응답에 데이터가 있으면**(기존 WP_POST_ID 확보) 곧바로 건너뛰지 말고 아래를 확인한다:
  1. Rank Math 키워드·점수가 실제로 설정돼 있는가 → 편집 화면에서 `wp.data.select('rank-math').getKeywords()` 확인
  2. 콘텐츠에 스톡/깨진 이미지 패턴(`unsplash.com/pexels.com/pixabay.com/FEATURED_IMAGE`)이 남아 있는가 → `GET /wp-json/wp/v2/posts/{id}?context=edit&_fields=content`
  3. **구조 결함이 남아 있는가** → `[6n]` 검사 9종을 그대로 1회 돌린다. 하나라도 걸리면 미완성으로 본다

  판정:
  - 키워드·점수 정상 + 이미지 정상 + **구조 검사 통과** → 정상 완료된 글. Notion "draft 일자"를 TODAY로 채우고 건너뜀
  - 키워드 미설정/점수 N/A → 이전 실행에서 STEP 6이 누락된 **미완성 draft**. 이 WP_POST_ID를 그대로 사용해 STEP 6부터 수행(STEP 5 재업로드 생략)
  - 이미지 패턴 잔존 → [4e] 이미지 처리도 함께 수행
  - **구조 결함 잔존 → `[6m-R]` 복구 절차를 수행**한다
  - 복구 처리했으면 완료 후 Notion "draft 일자"·SEO 점수 갱신

> ⚠️ 이 복구 로직이 작동하려면 "draft 일자"가 STEP 6 실패 시 계속 비어 있어야 한다. [5a]에서 draft 일자를 기록하지 않는 이유가 이것이다 — [6l] 참조.

### [4e] 히어로 이미지 URL 정합성

`[FEATURED_IMAGE_URL]` 플레이스홀더가 있거나, 이미 박혀 있는 `unsplash.com/photo-{ID}` 의 `{ID}` 가 `^[0-9]{10,13}-[0-9a-f]{12}$` 형식이 아닌 경우(=깨진 URL):

1. alt에서 IMAGE_KEYWORD 추출 (없으면 FOCUS_KEYWORD 사용)
2. navigate → `unsplash.com/s/photos/{IMAGE_KEYWORD}`
3. javascript_tool로 `img[src*="images.unsplash.com/photo-"]` 를 전부 수집 → **정규식과 일치하는 ID만** 후보 채택 (공유링크의 짧은 슬러그 ID는 CDN 404)
4. `https://images.unsplash.com/photo-{ID}?w=1200&q=80` 로 구성해 교체
5. 교체한 URL을 `fetch(url,{method:'HEAD'})` 로 200 확인 (실패 시 다른 후보로)

실패 시 → 오류 로그 기록, 포스트 업로드는 계속 진행.

> 본문에 `images.unsplash.com` 직링크가 남은 채로 배포되면 **WP 미디어에 사본이 없는 상태**다. 외부 CDN 의존 자산이므로 배포 후 오류 로그에 `Unsplash 핫링크 {n}건 — 이미지 루틴 업로드 대상`으로 남긴다. 교체는 이미지 루틴 소관이며 이 루틴은 **기록만** 한다.

### [4f] ⛔ 발행 차단 관문 판정 — **기준은 지침서 5-4**

지침서 5-4의 ①원본자료 ②가짜경험 ③이미지출처를 그대로 적용한다. 판정 시점은 **WordPress 업로드(POST) 직전**이며, **SEO 점수와 무관**하다.

- ①에 대해 기본 정보 표에 `1급 자료 조달 계획: 루틴가능 {화면·경로}` 가 명시돼 있으면 → **캡처 실행 주체는 이 루틴이다.** [4g]로 진행해 직접 캡처·삽입해서 관문을 스스로 충족시킨다
- 로그인·결제·개인정보 입력이 필요한 화면은 캡처하지 않는다 → 다른 1급 자료로 대체하거나 반려
- ⛔ **앱전용 화면 판정**: 이 루틴은 **브라우저만 조작**한다. 모바일 앱 안에서만 보이는 화면은 로그인 여부와 무관하게 캡처 불가다. **판정 질문: "이 자료가 웹 브라우저에서 보이는가?"** 아니오면 [4g]를 시도하지 말고 즉시 반려한다
  - **반려 전 1회 확인**: 같은 서비스의 웹 버전·공식 페이지로 대체 가능하면 `루틴가능`으로 전환해 [4g] 진행
  - 반려 시 사유 코드 `1급-앱전용`, 조달 주체 `사용자`로 기록

**불통과 시**: STEP 5~6을 건너뛰고 draft 일자 공란 유지. 발행 반려 로그(`https://www.notion.so/3adbfe4a2ae18167880ecbe3c73b90cc`)에 행 추가:

`| {TODAY} | {SLUG} | {사유 코드} | {무엇을} | {어디에} | {왜} | {어떻게} | {루틴 또는 사용자} | 대기 |`

⚠️ "1급 자료 없음"만 적는 보고는 무효 — 무엇을·어디에·왜·어떻게·누가를 채운다. 같은 슬러그의 '대기' 행이 이미 있으면 중복 추가하지 않는다.

### [4g] 1급 자료 캡처 → WP 미디어 업로드 → 본문 삽입

캡처 **품질·마크업 기준은 지침서 5-4B**를 따른다. 아래는 **실행 방법**이다.

**1) 캡처**
- 대상 페이지로 navigate
- `computer` 도구의 **`zoom` 액션 + `region:[x1,y1,x2,y2]`** 로 필요한 영역만 잘라 찍는다
  ⚠️ `screenshot` 액션은 region 인자를 무시하고 전체 화면을 찍는다. 크롭은 반드시 `zoom`
- 결과 이미지를 육안 확인 (헤더·스크롤바·커서·팝업 잔재 없는지)

**2) 업로드 — 브라우저 canvas 크롭 경로**
샌드박스와 브라우저는 파일시스템이 분리돼 있고, `zoom` 결과에는 upload용 imageId가 붙지 않는다. 그래서 아래 경로를 쓴다:

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

5. 응답의 `source_url` 을 기록. 파일명은 반드시 `evidence-{SLUG}-{n}.webp` (지침서 5-4B)

**3) 본문 삽입**
지침서 5-4B의 `figure.evidence-capture` 표준 마크업으로, **해당 자료가 뒷받침하는 문단·표 바로 아래**에 삽입한다. 캡션은 `{출처 기관 — 화면명 · Captured YYYY-MM-DD}` 영문 표기.
⚠️ 삽입 지점은 반드시 **본문 래퍼 안**이어야 한다 — [부록 B] 판정식 ①로 확인한다.

**4) 확인**
업로드 후 프론트엔드 프리뷰(`/?p={WP_POST_ID}&preview=true`)에서 `figure.evidence-capture img` 의 `naturalWidth > 0` 을 확인하고 스크린샷으로 육안 검증.

실패 시 → 오류 로그 기록. 관문 ①을 충족하지 못하면 반려 처리([4f]).

---

## STEP 5 — WordPress Draft 업로드 + Notion 업데이트

(⚠️ [4d]에서 기존 WP_POST_ID로 복구 처리 중이면 이 STEP은 건너뛰고 STEP 6으로 직행)

### [5-0] 업로드 전 HTML 정규화·검증 (업로드 POST 직전 필수)

Notion에서 받은 HTML_CONTENT를 **그대로 올리지 않는다.** 아래를 순서대로 적용하고, 각 항목의 처리 건수를 오류 로그에 남긴다.

**1) ⛔ 금지 블록 검사 — 걸리면 업로드 중단**

```
HTML_CONTENT 에 아래 문자열이 있으면 업로드하지 않는다:
  <!-- wp:post-content    ← 본문 안에 본문을 다시 렌더 = 글 전체 2회 출력
  <!-- wp:template-part
  <!-- wp:query
```
발견 시 해당 문자열을 제거하고, 제거 후에도 본문이 정상인지 [부록 B] 판정식 ②(H1 1개)로 확인한다. 판단이 서지 않으면 업로드를 중단하고 반려 로그에 사유 코드 `구조-금지블록`으로 기록한다.

**2) 태그 개폐 균형 검사 — 걸리면 업로드 중단**

`div` / `table` / `ul` / `figure` 각각 여는 태그 수 == 닫는 태그 수. 불일치 시 반려 로그 사유 코드 `구조-태그불균형`.

**3) 미치환 플레이스홀더 검사 — 걸리면 업로드 중단**

`UNSPLASH_URL` `SEO_TITLE` `THEME_COLOR` `WRAPPER_ID` `ALT_TEXT` `INTRO_PARAGRAPH` `SECTION_TITLE` `FOOTER_CTA_TEXT` `EXTERNAL_URL` `AUTHORITY_SOURCE` `RELATED_SLUG` `[FEATURED_IMAGE_URL]` `MONTH YEAR` — 하나라도 남아 있으면 사유 코드 `구조-플레이스홀더`.

**4) 내부 링크 절대경로 → 상대경로 정규화 (자동 수정)**

`href="https://koreaplug.com/{slug}/"` → `href="/{slug}/"` 로 치환한다. 지침서가 상대경로를 규정하고 있고, 절대경로는 외부 링크로 인식돼 SEO 감점이다.

**5) 표 가로 넘침 방지 래퍼 (자동 수정)**

`<table>` 중 **최대 열 수가 4 이상**인데 상위에 `overflow-x` 컨테이너가 없으면 다음으로 감싼다:
```html
<div style="overflow-x:auto;">…<table>…</table>…</div>
```

**6) 본문 래퍼 존재 확인**

`max-width:\s*\d+px` 를 가진 최상위 `<div>` 가 있어야 한다. 없으면 사유 코드 `구조-래퍼없음`으로 반려(모든 후속 삽입 위치 판정의 기준점이 사라진다).

**날짜 갱신**: HTML_CONTENT 상단 메타 라인의 `Last updated: {Month} {YYYY}` 표기가 있으면 업로드 시점 월로 갱신한다(첫 번째 매치 1개만).

### [5-1] 업로드

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

> HTML_CONTENT가 길면(1만 자 이상) javascript_tool 한 번에 넣지 말고 `window.__A`, `window.__B` … 로 나눠 담은 뒤 이어붙여 POST한다. 템플릿 리터럴 안에 백틱·`${` 이 없는지 확인. **Basic Auth(curl) 경로를 쓰면 분할이 불필요하다** — `--data-binary @payload.json` 으로 한 번에 올린다.

### [5a] Notion 서브페이지 업데이트 (Post ID·상태만)

- 상태: `작성완료` → `배포완료 (Draft)`
- WordPress Post ID: {WP_POST_ID}

⚠️ **"draft 일자"(메인 테이블 셀)는 여기서 기록하지 않는다.** STEP 6 전 과정이 성공했을 때만 [6l]에서 기록한다. 여기서 기록하면 STEP 6이 실패해도 다음 실행이 이 글을 후보로 잡지 않아 [4d] 복구 로직이 영원히 돌지 않는다.

### [5b] 슬러그 충돌 감지
실제 slug ≠ 요청 SLUG → 오류 로그 기록 후 해당 포스트 건너뜀.

---

## STEP 6 — Astra + Rank Math 설정 (Rank Math 구간은 Claude in Chrome 필수)

### [6a] 에디터 열기
navigate → `https://koreaplug.com/wp-admin/post.php?post={WP_POST_ID}&action=edit`
wait 4초 후 `document.body?.classList.contains('wp-admin')` 로 로그인 확인. 'not-logged-in'이면 STEP 3 ③번(세션 복구) 수행 후 재시도.

### [6b] Astra 설정 — REST meta 직접 지정

사이드바 클릭 대신 REST로 postmeta를 지정한다. Astra meta는 `show_in_rest` 로 등록돼 있어 정상 저장되며, 새로고침 후 검증도 가능하다.

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

⚠️ `wp.data.dispatch('rank-math').updateKeywords()/updateSerpTitle()/…` 은 **에러 없이 성공한 것처럼 보이지만 postmeta에 저장되지 않는다**. **JS dispatch 금지.**

**[6d] 패널 열기**: 상단 우측 Rank Math 점수 배지 클릭. 사이드바가 화면 밖이면 `find`로 포커스 키워드 입력창 ref를 찾아 `scroll_to`.

**[6e] 키워드 입력**: 포커스 키워드 입력창 클릭 → `FOCUS_KEYWORD` 타이핑 → Enter → 같은 입력창에 SUB_KEYWORDS를 하나씩 타이핑 → Enter (보통 4개, 총 5개).

**[6f] 스니펫 편집**: "스니펫 편집" 클릭
- 타이틀 필드 클릭 → Ctrl+A → `SEO_TITLE` 타이핑
- 설명 필드 클릭 → Ctrl+A → `META_DESCRIPTION` 타이핑
- ⚠️ Ctrl+A 후 타이핑해도 **이전 텍스트의 첫 글자 1개가 남는 사례가 반복 확인됨**(예: `aWhy do Koreans…`). 타이핑 직후 zoom으로 필드를 육안 확인하고, 잔여 문자가 있으면 필드 클릭 → Ctrl+Home → Delete로 제거 후 다시 확인
- 창 닫기(X)

**[6g] 저장 + 재검증**
Ctrl+S → 저장 확인 → 편집 URL로 다시 navigate → wait 5초 → `wp.data.select('rank-math').getKeywords()` 에 쉼표 항목 5개가 남아 있어야 한다.
비어 있으면 [6d]부터 1회 재시도. 재시도 후에도 비면 오류 로그에 "SEO 설정 미반영" 명시 — "완료"로 보고 금지.

**[6h] 점수 확인 및 보정**
Rank Math 배지 숫자 확인. 목표 **78점 이상**.
미달 시 **지침서 5-3 + 오류표** 기준으로 REST API로 HTML 수정 → Ctrl+S → 재시도 1회.
(지침서 조회 실패 시에만 [부록 A] 사용.)
⚠️ 보정으로 HTML을 수정했으면 **[5-0] 1)~6) 검사를 다시 1회 돌린다.**

**[6i] 콘텐츠 재업로드 폴백** (에디터 본문이 비어 있을 때만)
POST `/wp-json/wp/v2/posts/{WP_POST_ID}` — `{"content": "<!-- wp:freeform -->\n{HTML_CONTENT}\n<!-- /wp:freeform -->"}`

### [6k] Notion SEO 점수 업데이트
메인 테이블 해당 행의 SEO 셀 `—` → 실제 점수.
⚠️ `<td>—</td>` + 카테고리 셀 같은 짧은 old_str은 다른 행과 중복된다. **제목 또는 한줄 요약 셀부터 포함해** 유일한 범위로 잡는다.

### [6l] draft 일자 기록 — 전 과정 성공 시에만

아래 중 하나라도 있었으면 draft 일자를 **공란으로 남긴다** (다음 실행이 [4d] 복구 로직으로 이어받는다):
- Chrome 로그인 실패
- Astra 설정 미반영 (재시도 후에도)
- Rank Math 키워드가 [6g] 새로고침 재검증에서 비어 있음 (재시도 후에도)
- **[6n] 구조 검증에서 🔴 항목이 남아 있음**
- **AdSense 로더 개수가 1이 아님 (STEP -1)**

성공했다면 메인 테이블 "draft 일자" 셀 → TODAY. SEO 점수 컬럼도 갱신.

---

### [6m] 들어오는 내부 링크 (지침서 6-3)

#### [6m-0] 사전 게이트 — 목적지가 `publish` 일 때만 삽입한다

```
GET /wp-json/wp/v2/posts?slug={신규슬러그}&status=any&_fields=id,slug,status
```
- `status == "publish"` → [6m-1]로 진행
- `status` 가 `draft` / `future` / `pending` → **삽입하지 않는다.** `[6m-Q]` 예약 큐에 적재하고 이번 회차는 건너뛴다

> 신규 글이 `future`인 동안 그 링크는 전부 404이며, 404가 사이트 전체 크롤에 누적된다.

#### [6m-Q] 인바운드 링크 예약 큐

- 큐 저장 위치: Notion 메인 목록 하단 실행 로그에 `⏳ 인바운드 대기: {신규슬러그} (발행예정 {날짜})` 한 줄로 남긴다
- **매 회차 STEP 2 직후** 큐를 훑어, 목적지가 `publish` 로 바뀐 항목을 [6m-1]부터 처리하고 큐에서 지운다
- 신규 후보가 0건인 날에도 이 큐는 처리한다

#### [6m-1] 삽입 대상 글 선정

주제가 인접한 **기존 발행(`publish`) 글 2개**를 고른다. **내부 링크를 이미 받고 있는 글 우선** — 고아 글에서 걸면 무효.

1. `GET /wp-json/wp/v2/posts?slug={기존슬러그}&status=any&_fields=id,status` → id·status 확인 (`publish` 아니면 대상에서 제외)
2. `GET /wp-json/wp/v2/posts/{id}?context=edit&_fields=content` → `content.raw` 확보
3. 이미 신규 슬러그가 들어 있으면 건너뜀(중복 방지)

⚠️ **슬러그 실재 확인**: koreaplug.com은 존재하지 않는 슬러그에도 HTTP 200 + "Page Not Found"(소프트404)를 반환한다. 상태코드로 판단하지 말고 **REST 조회 결과(id 존재 + status) 또는 title 문자열**로 확인한다.

#### [6m-2] ⛔ 삽입 위치 결정 — 래퍼 내부 판정 필수

`content.raw` 를 `C` 라 할 때:

```
① 래퍼 시작 W 를 찾는다
   W = C 에서 max-width 를 가진 첫 <div> 의 시작 인덱스
   (없으면 삽입 중단 → 오류 로그 '구조-래퍼없음', 발행은 유지)

② 래퍼를 닫는 </div> 위치 E 를 찾는다
   - Gutenberg 문서면: '<!-- /wp:html -->' 바로 앞의 마지막 </div>
   - 아니면: W 이후로 스캔하며 div 깊이가 처음 0이 되는 </div>

③ 삽입 지점 P 를 정한다
   - Related reading 섹션이 [W, E] 구간 안에 이미 있으면
       → 그 섹션 <ul> 의 </ul> 직전
   - 구간 안에 없으면
       → E 직전(래퍼 닫는 </div> 바로 앞)에 섹션을 신설한다:
         \n<p style="margin-top:36px;"><strong>Related reading</strong></p>\n<ul>\n{li}\n</ul>

④ ⛔ 검증 — 삽입 전 반드시 통과해야 한다
   depth = (C[W:P] 의 '<div' 개수) − (C[W:P] 의 '</div>' 개수)
   depth >= 1 이어야 한다. 0 이하면 P 가 래퍼 밖이므로 삽입하지 말고 ②부터 다시 계산한다
```

- ⛔ **`lastIndexOf('</ul>')` 를 삽입 기준으로 쓰지 않는다.** `content.raw` 의 마지막 `</ul>` 은 본문 래퍼가 닫힌 뒤에 있는 경우가 많다
- ⛔ **`content.raw` 의 끝에 append 하지 않는다.** 끝은 언제나 래퍼 밖이다
- 래퍼 밖은 `max-width`·`margin:auto` 가 적용되지 않아 그 블록만 전체 폭 왼쪽 끝에 렌더링된다

#### [6m-3] 삽입 + 검증

1. `P` 에 `<li><a href="/{신규슬러그}/">{신규 SEO_TITLE}</a></li>` 삽입 (섹션 신설이면 위 ③의 블록째 삽입)
2. `<ul>`/`<li>`/`<div>` 여닫이 개수 검증
3. POST 저장
4. **저장 후 재조회해 [부록 B] 판정식 ①(칼럼 이탈)을 1회 돌린다.** 실패하면 저장 직전 원본으로 되돌리고 오류 로그 기록
5. 실패 시 오류 로그만 남기고 발행은 유지(반려 아님)

#### [6m-R] 기존 글 구조 복구

[6m-1] 대상 글이 **이미 래퍼 밖에 Related reading 을 갖고 있으면**, 링크를 추가하기 전에 먼저 그 블록을 래퍼 안으로 옮긴다.

```
1. 래퍼 밖 블록 B 를 잘라낸다 (<p>…Related reading…</p> + 뒤따르는 <ul>…</ul>)
2. B 를 [6m-2] ③의 E 직전에 다시 삽입한다
3. 태그 개폐 균형 + [부록 B] ① 재검증
4. POST 저장 → 라이브 재조회로 확인
5. 실행 로그에 '구조 복구 {슬러그}' 기록
```

- ⛔ **복구 전 `content.raw` 원본을 파일 또는 로그에 남긴다.** 되돌릴 수 없는 편집을 백업 없이 하지 않는다
- 한 회차에 복구하는 글 수는 **최대 5편**으로 제한한다. 나머지는 다음 회차로 이월하고 STEP 7에 잔여 건수를 적는다

---

### [6n] 배포 후 구조 검증 (STEP 6 마지막, 필수)

이번 회차에 만들거나 수정한 **모든 글**에 대해 `GET /wp-json/wp/v2/posts/{id}?context=edit&_fields=content` 로 `content.raw` 를 받아 아래 9종을 검사한다. 판정식 원문은 [부록 B].

| # | 검사 | 판정 | 실패 시 |
|---|---|---|---|
| 1 | 칼럼 이탈 — 래퍼 밖 콘텐츠 | 🔴 | `[6m-R]` 복구 후 재검사. draft 일자 공란 |
| 2 | 금지 블록 (`wp:post-content` 등) | 🔴 | 제거 후 재검사. 판단 불가 시 반려 로그 |
| 3 | `div`/`table`/`ul`/`figure` 개폐 균형 | 🔴 | 오류 로그 + draft 일자 공란 |
| 4 | 미치환 플레이스홀더 | 🔴 | 오류 로그 + draft 일자 공란 |
| 5 | 본문 `<h1>` 정확히 1개 | 🔴 | 중복 본문 의심 → 2번 검사 재확인 |
| 6 | 내부링크 목적지가 전부 `publish` | 🟡 | 해당 링크 제거 + `[6m-Q]` 큐 적재 |
| 7 | 내부링크 절대경로 0건 | 🟡 | 상대경로로 치환 |
| 8 | 4열 이상 표에 `overflow-x` 래퍼 | 🟡 | 래퍼 추가 |
| 9 | 본문 `<img>` 전부 HTTP 200 | 🟡 | 오류 로그(이미지 루틴 이관) |

- 🔴 가 하나라도 남으면 **draft 일자를 기록하지 않는다**([6l]). 다음 실행이 `[4d]` 로 이어받는다
- 🟡 는 자동 수정 후 로그에만 남기고 진행한다
- 검사 결과는 STEP 7 알림에 `구조검증 {통과}/{전체}` 형태로 요약한다

---

## STEP 7 — 완료 알림 출력 (200자 이내, 이전 단계 성공 여부와 무관하게 반드시 실행)

- 신규 포스트 있음: `KoreaPlug 발행완료 ✅ draft {N}개 | 관문반려 {R}건(로그 기록) | 인바운드링크 {L}건 | 구조검증 {P}/{T} | AdSense {n}개 | SEO평균 {점수}점 | 오류 {E}개 ({TODAY_KST})`
- 신규 포스트 없음: `KoreaPlug 자동 체크 완료 — 신규 글 없음 | 인바운드 큐 {Q}건 처리 | 구조복구 {F}편 ({TODAY_KST})`
- [4d]에서 미완성 draft를 복구했으면 함께 기록: `KoreaPlug 미완성 draft {M}개 복구완료 (SEO/이미지/구조) | ({TODAY_KST})`

⚠️ STEP 0 결과를 한 줄로 함께 기록한다 — 조회 실패([0-5]) / 캐시 사고([0-3]에서 조항 확인) / **조항 자동 신설([0-4], 조항번호 + 전문)** / 진짜 상충. **캐시 사고를 상충으로 쓰지 않는다.**
⚠️ 추가 보고 항목: `[6m-Q]` 인바운드 대기 잔여 건수 / `[6m-R]` 구조 복구 편수와 이월 잔여 / `[6n]` 🔴 미해소 슬러그 목록 / **헤더 영역을 건드린 회차면 AdSense 로더 개수(STEP -1)**.
⚠️ Notion 메인 페이지 하단에 이번 회차 실행 로그를 append한다 (신규 draft·1급 자료·관문 결과·인바운드 링크·구조검증·오류·다음 실행 시각).

---

## 🚨 오류 처리

| 상황 | 조치 |
|---|---|
| GitHub 지침서 조회 실패 | [0-5] 저장소 루트 1회 → Chrome 1회 → 실패 시 오류 로그 + [부록 A] 폴백으로 계속 진행 (STOP 아님, 조항 자기보완 금지) |
| 조항이 지침서에 안 보임 | [0-3] 3단 검증(캐시버스터 → Chrome → 확정). 찾으면 그 기준 사용하고 **캐시 사고**로 기록(상충 아님) |
| 3단 검증 후에도 조항 결번 | [0-4] 조항을 직접 작성해 로컬 `KoreaPlug-Draft.md` 에 추가 → 즉시 적용해 배포 계속 → STEP 7·Notion에 전문 기록. 커밋·푸시는 사용자 |
| 지침서 개정 이력이 루틴이 아는 버전보다 낮음 | 캐시 사본 의심 — 새 `?cb=` 로 재조회 + Chrome 재확인. 캐시로 확인되면 상충 보고 금지 |
| pw.txt 접근 실패 | 폴더 미연결이면 정상. Chrome 세션 nonce(STEP 3 ②)로 전환 |
| **WP 세션 만료(reauth)** | ⛔ **로그인 버튼을 클릭하지 않는다**(STEP 3 ③). Basic Auth가 살아 있으면 STEP 5까지 진행하고 Rank Math만 미완으로 남긴 뒤 draft 일자 공란. 둘 다 죽었으면 오류 로그 후 STEP 7 |
| Chrome 미연결 | Basic Auth로 STEP 5·6b·6m·6n 은 계속 수행. Rank Math 구간만 건너뛰고 draft 일자 공란 유지 |
| WordPress API 실패 | 로그 기록 후 다음 포스트 진행 |
| Notion 페이지 없음 | 로그 기록 후 다음 포스트 진행 |
| 관문 불통과 | 반려 로그 행 추가 + draft 일자 공란 + 다음 포스트 진행 |
| 캡처 실패/어색 | 지침서 5-4B 기준으로 region 재지정해 1회 재캡처. 실패 시 관문 ① 불충족 → 반려 |
| 이미지 URL 404 | [4e] 재시도 1회, 실패 시 플레이스홀더 유지 + 오류 로그 |
| Rank Math 78점 미달 | 지침서 5-3/오류표 기준 수정 후 재시도 1회. 수정했으면 [5-0] 재검사 |
| SEO 설정이 새로고침 후 사라짐 | JS dispatch 금지 — UI 클릭([6d]~[6f]) + [6g] 새로고침 재검증 필수 |
| Astra 설정 미반영 | [6b] REST meta 재지정 1회 → 그래도 안 되면 명시 기록, draft 일자 공란 |
| **[6n] 🔴 항목 발생** | 해당 항목 수정 후 재검사 1회. 남으면 draft 일자 공란 + STEP 7에 슬러그 명시. **"완료"로 보고 금지** |
| **인바운드 목적지가 미발행** | 삽입하지 않고 `[6m-Q]` 큐 적재. 오류가 아니라 정상 동작이다 |
| **구조 복구 5편 초과** | 이번 회차 5편만 처리하고 잔여는 이월. STEP 7에 잔여 건수 기록 |
| **AdSense 로더가 0개** | 🔴 즉시 WPCode 스니펫 999를 활성화하고 재검증. draft 일자 공란 + STEP 7 명시 |
| **AdSense 로더가 2개 이상** | 추가된 쪽을 찾아 제거. **먼저 남길 쪽을 확인한 뒤 지운다** — 0개가 되는 순간을 만들지 않는다 |
| **WPCode 저장이 반영되지 않음** | [부록 C] 참조 — 저장 버튼 프로그램 클릭은 조용히 실패한다. 페이지를 새로 로드해 값을 다시 읽어 확인할 것 |

---

## [부록 A] 인라인 폴백 기준 (STEP 0 조회 실패 시에만 사용)

**관문(지침서 5-4 대체)**
1. 1급 원본 자료 최소 1개 — 직접 조작한 공개 화면 캡처 / 직접 센 수치 / 1차 기록. 비교표·공식 수치 재정리는 불인정
2. 하지 않은 일의 1인칭 서술 0건. (실제 수행한 작업의 1인칭은 허용)
3. 모든 `<img>` 가 koreaplug.com 자체 업로드 또는 images.unsplash.com. 타 사이트 핫링크 0건

**캡처(지침서 5-4B 대체)**
- 결과·표·조문 영역만 크롭, 헤더·스크롤바·커서·팝업 배제
- 파일명 `evidence-{SLUG}-{n}.webp`, `class="evidence-capture"` figure + figcaption 필수
- 삽입 위치는 해당 문단·표 바로 아래 (**래퍼 안** — [부록 B] ① 확인)

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

---

## [부록 B] 구조 판정식 ([5-0]·[6m-2]·[6n] 공통)

입력은 언제나 `content.raw`(문자열 `C`). 렌더된 HTML이 아니라 **원본**으로 판정한다.

**① 칼럼 이탈 (🔴)**
```
Gutenberg 문서면:
  tail = C 를 마지막 '<!-- /wp:html -->' 로 자른 뒷부분
  tail 에서 HTML 주석을 제거하고 공백을 턴 첫 요소가
    - <div ...>이고 그 여는 태그에 margin:0 auto / margin:auto 가 있으면 → 통과
    - 그 외(<p>, <ul>, <h2>, 중앙정렬 아닌 <div>)면 → 🔴 이탈
삽입 지점 판정용:
  depth(W, P) = C[W:P] 의 '<div' 수 − '</div>' 수    // W = 래퍼 시작
  depth >= 1 이어야 래퍼 안이다
```

**② H1 개수 (🔴)**
```
len(regex_findall(r'<h1\b', C)) == 1
```
2 이상이면 본문 중복을 의심하고 ③을 확인한다.

**③ 금지 블록 (🔴)**
```
'<!-- wp:post-content' not in C
'<!-- wp:template-part' not in C
'<!-- wp:query' not in C
```

**④ 태그 개폐 균형 (🔴)**
```
for tag in ['div','table','ul','figure']:
    count('<'+tag+'\b') == count('</'+tag+'>')
```

**⑤ 미치환 플레이스홀더 (🔴)** — [5-0] 3) 목록과 동일

**⑥ 내부링크 목적지 상태 (🟡)**
```
for slug in regex_findall(r'href="(?:https?://koreaplug\.com)?/([a-z0-9\-]+)/?"', C):
    GET /wp-json/wp/v2/posts?slug={slug}&status=any&_fields=status
    status == 'publish' 이어야 한다
```
빈 응답(=존재하지 않는 슬러그)은 🔴로 올린다.

**⑦ 절대경로 내부링크 (🟡)**
```
regex_findall(r'href="https?://koreaplug\.com/[a-z0-9\-]+/?"', C) == []
```

**⑧ 표 가로 넘침 (🟡)**
```
각 <table> 의 최대 열 수 = max(행별 <th|td> 개수)
열 수 >= 4 이면 상위에 overflow-x 컨테이너가 있어야 한다
```

**⑨ 이미지 생존 (🟡)**
```
각 <img src> 에 HEAD 요청 → 200
```

> ⚠️ 판정식은 **원본 문자열 기준**이다. 렌더된 페이지로 판정하면 플러그인이 주입한 마크업(EZ TOC·저자 박스 등)이 섞여 오탐이 난다. `<!-- TABLE OF CONTENTS -->` 주석은 EZ TOC가 목차를 따로 생성하므로 **결함이 아니고**, CSS 배경 히어로를 쓰는 글은 `<img>` 가 0개인 것이 정상이다.

---

## [부록 C] 사이트 상태 상수 및 도구 함정 (2026-09-04 실측)

**테마·플러그인**

| 항목 | 값 |
|---|---|
| 활성 테마 | **Astra 4.13.4** (자식 테마 없음). GeneratePress는 설치돼 있으나 **비활성** |
| 활성 플러그인 | 14개 (Breeze · Object Cache Pro · Rank Math SEO · WPCode Lite · UpdraftPlus · 간편한 목차 · 단순 작성자 상자 · WP Headers And Footers 등) |
| 캐시 스택 | **Breeze**(페이지) + **Object Cache Pro**(Redis 객체 캐시). 대시보드 위젯의 `Flush Cache` 로 비운다 |
| 오디오 | **Compact WP Audio Player 비활성화됨.** 오디오 글은 네이티브 `<audio>` 태그를 쓰고, WPCode 스니펫 `1550` "KP Audio Click Handler"(사이트 전체 바닥글·JS)가 클릭 핸들러를 담당한다. 이 스니펫 최상단에 `if (!document.querySelector('audio')) return;` 가드가 있어 오디오 없는 페이지에서는 즉시 종료한다 — **가드를 제거하지 않는다** |
| 성능 (참고) | PSI 모바일 61 / 데스크톱 97. 병목은 `<head>` 127KB 중 인라인 CSS 125KB. **CrUX 필드 데이터가 없어 현재 순위 요인이 아니다** — 이 루틴의 조치 대상이 아니며 기록만 한다 |

**⚠️ WPCode UI 저장 함정 — 반드시 검증한다**

WPCode의 저장 버튼(`업데이트` / `변경 사항 저장`)과 스니펫 목록의 상태 토글은 **ref 기반 프로그램 클릭이 조용히 실패하는 경우가 반복 확인됐다.** 응답도 오류도 없이 저장되지 않는다.

1. CodeMirror 값을 JS로 바꾼 뒤에는 **좌표 클릭**으로 버튼을 누른다
2. 누른 뒤 **성공 알림 문구**(`스니펫이 업데이트되었습니다` / `설정이 저장되었습니다`)를 스크린샷으로 확인한다
3. 그래도 **페이지를 새로 로드해 값을 다시 읽어** 반영 여부를 확인한다 — 알림만으로 신뢰하지 않는다
4. 미저장 상태에서 navigate 하면 "Leave site?" 다이얼로그로 이동이 차단된다. 이것이 **미저장 신호**다

**⚠️ 소프트404**

koreaplug.com은 존재하지 않는 슬러그에도 **HTTP 200 + "Page Not Found"** 를 반환한다. 링크 검증을 상태코드로 하지 말고 REST 조회(`id` 존재 + `status`)로 한다.

**⚠️ URL 조립**

경로를 문자열로 조합할 때 이중 슬래시(`//`)를 만들지 않는다. `https://koreaplug.com//?nc=` 는 301을 반환하고, `-L` 없는 curl은 빈 본문을 받아 검증 결과를 오판하게 만든다.
