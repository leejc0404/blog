*예약된 트리거 시간이 되면 해당 일자에 먼저 루틴이 실행되더라도 무조건 다시 진행한다.

날짜: 실행 시점의 실제 KST 날짜를 사용한다 (이 프롬프트에 적힌 고정 날짜가 있어도 무시).

⚠️ 역할 분담: 이 루틴은 운영 절차(언제·무엇을·몇 회)만 정의한다. 배포·SEO 품질 기준의 단일 기준(SSOT)은 GitHub 지침서다 — 이 루틴과 지침서가 상충하면 지침서를 따르고, 상충 발견 시 STEP 7 알림에 기록한다.

---

STEP 0 — 지침서 읽기 (GitHub, SSOT — 최우선 실행)

WebFetch → https://raw.githubusercontent.com/leejc0404/blog/main/KoreaPlug-Draft.md
(브라우저용 뷰 URL: https://github.com/leejc0404/blog/blob/main/KoreaPlug-Draft.md)

⚠️ Notion 지침 페이지(KoreaPlug-Draft v10.0)는 더 이상 참조하지 않는다. 지침은 위 GitHub 파일만을 SSOT로 삼는다.

조회 실패 시(404/403/네트워크 차단):
1. main 브랜치가 아닐 수 있으므로 저장소 루트(https://github.com/leejc0404/blog)를 1회 더 확인한다.
2. 그래도 실패하면 STOP하지 않는다 — 오류 로그에 "GitHub 지침서 조회 실패 → 인라인 폴백"을 기록하고, STEP 6j의 인라인 SEO 보정 체크리스트를 그대로 사용해 배포를 계속 진행한다.
⚠️ 어떤 경우에도 지침 내용을 추측으로 생성하지 않는다.

⚠️ (2026-07-30 신설) 지침서의 Phase 5-4 ⛔ 발행 차단 관문(원본자료·가짜경험·이미지출처)은 **SEO 점수와 무관하게** 아래 [4f]에서 항상 판정한다 — 관문은 보정 절차가 아니라 업로드 전제 조건이다.

STEP 1 — 날짜 확인 (KST)

오늘(TODAY), 어제(TODAY_MINUS_1) 날짜를 기록한다.

STEP 2 — Notion 후보 글 수집 → CANDIDATE_POSTS

notion-fetch로 메인 목록(https://www.notion.so/33cbfe4a2ae181b9a743cb7c194dea7f) 읽기.
"draft 일자" 컬럼이 비어 있는(—) 행 전체를 CANDIDATE_POSTS로 수집.
각 행에서: #번호, 제목, 카테고리

⚠️ [변경] 카테고리 4개 페이지 별도 fetch 삭제 — 서브페이지 URL은 STEP 4에서 notion-search로 직접 찾는다.

CANDIDATE_POSTS가 비어 있으면 → STEP 7로 건너뜀.

STEP 3 — WordPress 인증 정보 및 카테고리 ID (API 호출 없음)

인증: Basic Auth — leejcfo@gmail.com / {pw.txt 참조 — KOREAPLUG_WP_APP_PASSWORD}
(로컬 C:\Users\win\.claude\blog\pw.txt 의 KOREAPLUG_WP_APP_PASSWORD 값을 사용한다. 파일을 읽을 수 없으면 오류 로그에 "pw.txt 접근 실패"를 기록하고 STEP 7로 건너뛴다.)

카테고리 ID:
🍜 Food & Drink → 3
🎭 Korean Culture → 4
🚌 Travel & Transport → 5
🏠 Lifestyle & Living → 18

⚠️ [변경] 전체 슬러그 수집(페이지네이션) 삭제 — 슬러그 중복 확인은 STEP 4에서 후보 글별 1회 직접 확인.

STEP 4 — Notion 서브페이지 콘텐츠 읽기 → 필드 추출

CANDIDATE_POSTS 각 포스트에 대해:

[4a] 서브페이지 URL 확인 (⚠️ [변경] 카테고리 전체 페이지 fetch 금지)
notion-search로 포스트 제목 검색 → 서브페이지 page_id·URL 확인.
검색 결과 없을 경우에만 해당 카테고리 페이지 1개만 fetch:
- Food → https://www.notion.so/Food-Dining-Blog-Posts-33ebfe4a2ae18136b1a9df45458cb1be
- Travel → https://www.notion.so/Travel-Transport-Blog-Posts-34fbfe4a2ae18031b3fbcc874496498e
- Culture → https://www.notion.so/Culture-Society-Blog-Posts-33ebfe4a2ae1815ba5e1d58b1bf9a44c
- Lifestyle → https://www.notion.so/Lifestyle-Living-Blog-Posts-33ebfe4a2ae18133a438ed9274c1dfb1

[4b] 서브페이지 로드
notion-fetch로 서브페이지 URL 호출.

[4c] 필드 추출
"기본 정보" 표(섹션 1)에서 추출:
SLUG / SEO_TITLE / META_DESCRIPTION / FOCUS_KEYWORD / SUB_KEYWORDS / HTML_CONTENT / WP_CAT_ID

⚠️ FOCUS_KEYWORD: Notion "Focus Keyword" 행 값 그대로 복사 (2~3단어, AI 재생성 금지)
⚠️ SUB_KEYWORDS: Notion "Sub Keywords" 행 값 그대로 복사 → " / " 를 ", " 로 변환
— koreaplug-writer가 Google 자동완성으로 수집한 값. Cowork에서 재검색 금지.

[4d] 슬러그 중복 확인 + 미완성 draft 복구 (⚠️ 2026-07-24 변경 — blind skip 금지)

GET https://koreaplug.com/wp-json/wp/v2/posts?slug={SLUG}&status=any&_fields=id,slug
인증: STEP 3과 동일. status=any 필수.
응답이 비어있으면 → 중복 없음, 업로드 진행 (STEP 4e로).
응답에 데이터 있으면(기존 WP_POST_ID 확보) → 곧바로 건너뛰지 않고 아래를 확인한다:

  1) https://koreaplug.com/wp-admin/edit.php?post_status=draft&post_type=post 목록(또는 해당 post가 이미 publish/future 상태면 https://koreaplug.com/wp-admin/edit.php?post_status=all)에서 이 글의 "SEO 상세" 칼럼(SEO 점수·키워드)을 확인한다.
  2) 콘텐츠에 unsplash.com/pexels.com/pixabay.com/FEATURED_IMAGE 패턴이 남아 있는지 GET /wp-json/wp/v2/posts/{id}?_fields=content 로 확인한다.

  판단:
  - SEO 점수가 숫자로 채워져 있고(N/A 아님) 키워드도 설정돼 있으며, 이미지에 스톡/깨진 패턴이 없으면 → 정상 완료된 글로 판단, Notion "draft 일자"를 TODAY로 업데이트 후 건너뜀.
  - SEO 점수가 N/A이거나 키워드가 미설정이면 → 이전 실행에서 STEP 6이 누락된 미완성 draft로 판단. 이 WP_POST_ID를 그대로 사용해 STEP 6(Rank Math/Astra 설정)을 수행해 완성시킨다 (STEP 5 재업로드는 생략, WP_POST_ID는 이 기존 id 사용).
  - 이미지에 unsplash.com/pexels.com/pixabay.com/FEATURED_IMAGE 패턴이 남아 있으면 [4e] 이미지 처리도 함께 수행해 유효한 이미지로 교체한다 (Unsplash 검색 결과에서 얻은 photo ID가 반드시 `^[0-9]{10,13}-[0-9a-f]{12}$` 형식인지 확인 후 사용 — 이 형식이 아니면 그 ID는 폐기하고 검색 결과의 다른 이미지를 사용).
  - 위 복구 처리를 했으면 완료 후 Notion "draft 일자"·SEO 점수를 갱신한다.

⚠️ [수정 2026-07-26] 위 판단 로직이 실제로 작동하려면 "draft 일자"가 STEP 6 실패 시 계속 비어 있어야 한다. [5a]에서 draft 일자를 기록하지 않는 이유가 바로 이것이다 — [5a]와 [6l] 참조.

[4e] 히어로 이미지 처리 (Chrome 브라우저 필수)

[FEATURED_IMAGE_URL] 플레이스홀더 감지 시, 또는 HTML_CONTENT에 이미 unsplash.com/photo-{ID} 형태의 URL이 박혀 있지만 {ID}가 `^[0-9]{10,13}-[0-9a-f]{12}$` 형식이 아닌 경우(=깨진 URL, 예: 2026-07-24 danggeun-market-korea 사례):

1) alt에서 IMAGE_KEYWORD 추출 (없으면 FOCUS_KEYWORD 사용)
2) navigate → unsplash.com/s/photos/{IMAGE_KEYWORD}
3) javascript_tool로 img[src*="images.unsplash.com/photo-"] 전체를 수집해 photo ID 후보 목록을 뽑는다. 반드시 `^[0-9]{10,13}-[0-9a-f]{12}$` 정규식과 일치하는 ID만 후보로 채택한다 (Unsplash 공유링크의 짧은 슬러그 ID는 CDN에서 404가 나므로 사용 금지).
4) CDN URL 구성(`https://images.unsplash.com/photo-{ID}?w=1200&q=80`) → REST API로 content 내 기존 URL을 교체
5) 교체한 URL을 Chrome으로 실제 navigate해 404가 아닌지 1회 육안 확인(스크린샷)한다.

실패 시 → 오류 로그 기록, 포스트 업로드는 계속 진행

[4f] 발행 차단 관문 판정 (Phase 5-4 ⛔ — 업로드 전 필수, 2026-07-30 신설)

HTML_CONTENT와 기본 정보 표를 대상으로 판정한다:
① 원본자료: 1급 원본 자료(직접 조작한 화면 캡처·실측 수치·실제 영수증 등) 최소 1개 — 비교표·통합표·공식 수치 재정리만 있으면 불통과. 단, 기본 정보 표에 "1급 자료 조달 계획: 루틴가능 {화면·경로}"가 명시돼 있으면 **로그인 없이 접근 가능한 공개 페이지에 한해** Chrome으로 그 화면을 직접 조작·캡처 → WP 미디어 업로드 → 본문 해당 위치에 삽입해 관문을 스스로 충족시킨다 (캡처 실행 주체는 브라우저가 있는 이 루틴 — 지침서 v10.22).
② 가짜경험: 하지 않은 일의 1인칭(I/My) 서술·지어낸 개인 일화 0건 ("When I first…", "my group chat…" 류).
③ 이미지출처: 모든 <img>가 자체 업로드(koreaplug.com) 또는 images.unsplash.com — gstatic·pstatic 등 타 사이트 핫링크 0건.

①~③ 중 하나라도 불통과 → 이 포스트는 STEP 5~6을 건너뛴다 (draft 일자 공란 유지). 그리고 발행 반려 로그에 행 1개를 추가한다:
https://www.notion.so/3adbfe4a2ae18167880ecbe3c73b90cc
행 형식: | {TODAY} | {SLUG} | {사유 코드} | {무엇을} | {어디에} | {왜} | {어떻게} | {루틴 또는 사용자} | 대기 |
⚠️ "1급 자료 없음"만 적는 보고는 무효 — 무엇을·어디에·왜·어떻게 4항목을 반드시 채운다 (지침서 v10.21). 같은 슬러그의 '대기' 행이 이미 있으면 중복 추가하지 않는다. 기록 후 다음 후보로 진행.

STEP 5 — WordPress Draft 업로드 + Notion 메인 테이블 업데이트

(⚠️ [4d]에서 기존 WP_POST_ID로 복구 처리한 경우 이 STEP은 건너뛰고 STEP 6으로 직행)

POST https://koreaplug.com/wp-json/wp/v2/posts
인증: STEP 3과 동일 | Content-Type: application/json
{
  "title":      "{SEO_TITLE}",
  "content":    "<!-- wp:freeform -->\n{HTML_CONTENT}\n<!-- /wp:freeform -->",
  "status":     "draft",
  "slug":       "{SLUG}",
  "categories": [{WP_CAT_ID}]
}
응답에서 WP_POST_ID 기록.

[5a] Notion 메인 테이블·서브페이지 업데이트 (Post ID·상태만 — draft 일자는 여기서 기록하지 않음)

notion-update-page / update_content / page_id: 33cbfe4a-2ae1-81b9-a743-cb7c194dea7f

⚠️ [변경] 실행 전 notion-fetch 재확인 삭제 — page_id가 하드코딩되어 있으므로 재확인 불필요.

서브페이지 업데이트:
상태: 작성완료 → 배포완료 (Draft)
WordPress Post ID: {WP_POST_ID} 기재

⚠️ [수정 2026-07-26] "draft 일자"(메인 테이블 셀)는 이 단계에서 기록하지 않는다 — STEP 6 전 과정이 성공했을 때만 [6l]에서 기록한다. 여기서 기록해버리면 STEP 6이 실패해도 다음 실행의 STEP 2가 이 글을 후보로 다시 집지 않아, [4d]의 미완성 draft 복구 로직이 영원히 실행되지 못한다.

[5b] 슬러그 충돌 감지
실제 slug ≠ 요청 SLUG → 오류 로그 기록 후 해당 포스트 건너뜀.

STEP 6 — 에디터에서 Rank Math SEO + Astra 설정 (Claude in Chrome 필수)

[6a] 브라우저 연결 (⚠️ [변경] tabs_context_mcp 삭제)
list_connected_browsers → select_browser

[6b] 에디터 열기
navigate → https://koreaplug.com/wp-admin/post.php?post={WP_POST_ID}&action=edit

⚠️ [변경] navigate 직후 get_page_text 호출 금지. wait 3초 후 아래 javascript_tool로만 로그인 확인.
document.body?.classList.contains('wp-admin') ? 'logged-in' : 'not-logged-in'
결과가 'not-logged-in'이면 오류 로그 기록 후 건너뜀.

[6c] Astra 설정
사이드바 "Astra 설정" 패널:
컨테이너 레이아웃: Full Width
컨테이너 스타일: Unboxed
"배너 영역 비활성화" 토글 ON

[6c-검증] Astra 설정 반영 확인
javascript_tool 실행:
const m = wp.data.select('core/editor').getEditedPostAttribute('meta');
JSON.stringify({
  style: m['site-content-style'],
  banner: (m['ast-banner-title-visibility'] === 'disabled' || m['ast-main-header-display'] === 'disabled')
});
기대값: style === 'unboxed' && banner === true
불일치 시 → [6c] 재시도 1회 (패널 닫았다 다시 열고 클릭).
재시도 후에도 불일치 → 오류 로그에 "Astra 설정 미반영" 명시 기록 (기존처럼 "완료"로 보고 금지).

⚠️ [변경] 구 6d(블록 구조 설정 / HTML_CONTENT resetBlocks) 삭제.
콘텐츠는 STEP 5 REST API 업로드 시 이미 freeform 래퍼로 저장됨. 에디터가 자동 로딩.
콘텐츠가 비어있는 경우에만 [6i] 폴백 사용.

[6d] Rank Math SEO 설정 (⚠️ 2026-07-24 변경 — UI 클릭 방식이 기본, JS dispatch 사용 금지)

실측 결과 wp.data.dispatch('rank-math').updateKeywords()/updateSerpTitle()/updateSerpDescription()/updateSerpSlug()는 에러 없이 "성공"한 것처럼 보이지만 실제로는 postmeta에 저장되지 않고, 페이지를 새로고침하면 값이 사라진다 (2026-07-24, danggeun-market-korea 사례로 실측 확인: JS dispatch 후 Ctrl+S 저장까지 했는데도 새로고침하면 키워드가 빈 값이었음). 이 JS dispatch 방식은 이제 사용하지 않는다. 반드시 아래 [6e]~[6g] UI 클릭 방식만 사용한다.

⚠️ FOCUS_KEYWORD·SUB_KEYWORDS는 Notion 값 그대로 사용. Cowork에서 재검색·수정 금지.

[6e] Rank Math 패널 열기
상단 우측 Rank Math 점수 배지 클릭.

[6f] 포커스 키워드 + 서브키워드 입력
포커스 키워드 입력창 클릭 → FOCUS_KEYWORD 타이핑 → Enter
같은 입력창에 이어서 SUB_KEYWORDS를 하나씩 타이핑 → Enter (콤마로 구분된 항목 수만큼 반복, 보통 4개)

[6g] 스니펫 편집
"스니펫 편집" 버튼 클릭 → 타이틀 필드 클릭 → Ctrl+A → SEO_TITLE 타이핑
→ 설명 필드 클릭 → Ctrl+A → META_DESCRIPTION 타이핑
⚠️ Ctrl+A로 전체선택 후 타이핑해도 이전 텍스트의 첫 글자 하나가 남는 경우가 있었다(예: "aDanggeun market korea..."). 타이핑 직후 반드시 스크린샷으로 필드 내용을 육안 확인하고, 이상하면 필드 클릭 → Home → Delete로 잔여 글자를 지운다.
→ 창 닫기 (X 버튼)

[6g-검증] 저장 전 반영 확인
스크린샷으로 "기본 SEO" 체크리스트 항목이 대부분 초록색(✅)인지, 포커스 키워드·서브키워드 칩이 입력창에 표시되는지 확인한다. 비어 있으면 [6e]부터 재시도.

[6h] 저장 + 저장 검증 (⚠️ 2026-07-24 신규 추가)
Ctrl+S → "임시글 저장됨" 확인 후 3초 대기.
저장 직후 같은 편집 URL로 navigate(새로고침)하고 3초 대기 후 Rank Math 패널을 다시 열어 포커스 키워드 칩이 실제로 남아있는지 확인한다. 새로고침 후 키워드가 비어 있으면 저장이 반영되지 않은 것이므로 [6e]부터 재시도(최대 1회). 재시도 후에도 비어 있으면 오류 로그에 "SEO 설정 미반영" 명시 기록 — "완료"로 보고 금지.

[6i] 콘텐츠 재업로드 폴백 (에디터 본문 비어있을 때만 실행)
POST https://koreaplug.com/wp-json/wp/v2/posts/{WP_POST_ID}
페이로드: {"content": "<!-- wp:freeform -->\n{HTML_CONTENT}\n<!-- /wp:freeform -->"}

[6j] SEO 점수 확인 및 보정

에디터 새로고침 → wait 3초 → Rank Math 점수 확인 (상단 배지 숫자, 또는 draft 목록의 "SEO 상세" 칼럼).
목표: 78점 이상.

미달 시 아래 체크리스트 기준으로 REST API로 HTML 수정 → Ctrl+S → 재시도 1회:
─────────────────────────────────────────
SEO 보정 체크리스트
⚠️ [변경] 기준 출처 = STEP 0에서 읽은 GitHub 지침서(KoreaPlug-Draft.md). 지침서를 정상적으로 읽었다면 그 기준을 따르고, 아래 인라인 목록과 상충하면 지침서를 우선한다.
⚠️ STEP 0에서 지침서 조회에 실패한 경우에만 아래 인라인 목록을 폴백으로 사용한다. (Notion 지침 fetch는 하지 않는다.)

1) FOCUS_KEYWORD가 첫 <p>(도입부 100자 이내)에 포함되어 있는가?
2) FOCUS_KEYWORD가 <h2> 헤딩 1개 이상에 포함되어 있는가?
3) SEO_TITLE이 60자 이하이며 FOCUS_KEYWORD를 포함하는가?
4) META_DESCRIPTION이 150자 이하이며 FOCUS_KEYWORD를 포함하는가?
5) 내부 링크(koreaplug.com)가 1개 이상 있는가?
6) <img> alt 속성에 FOCUS_KEYWORD 또는 연관어가 포함되어 있는가?
7) 본문 글자 수가 1,500자 이상인가?
8) 목차가 없으면 본문 상단에 <div class="wp-block-rank-math-toc-block"></div> 추가.
위 미충족 항목만 수정. 키워드 기계적 반복 삽입 금지.
─────────────────────────────────────────
⛔ 절대 금지: core/heading 블록 추가 / getEditedPostContent() freeform 소스 사용 / 키워드 반복 삽입

[6k] Notion SEO 점수 업데이트
old_str: "<td>—</td>\n<td>{카테고리이모지+이름}</td>"
new_str: "<td>{SEO_FINAL_SCORE}</td>\n<td>{카테고리이모지+이름}</td>"

[6l] draft 일자 기록 (STEP 6 전 과정이 성공했을 때만 실행)

⚠️ 6c-검증(Astra 레이아웃 반영)과 [6h](Rank Math 키워드·스니펫 저장 검증)가 모두 성공했을 때만 실행한다. 아래 중 하나라도 있었으면 draft 일자를 공란으로 남긴다 — 다음 실행이 이 글을 다시 후보로 잡아 [4d] 복구 로직으로 STEP 6부터 이어간다(슬러그 중복이 이미 있으므로 STEP 5는 자동으로 건너뛴다):
- Chrome 로그인 실패
- Astra 설정 미반영 (재시도 후에도)
- Rank Math 설정이 [6h] 새로고침 재검증에서 비어 있음 (재시도 후에도)

성공했다면:

메인 테이블 "draft 일자" 셀 — → TODAY 교체:
old_str: "<td>{작성일자}</td>\n<td>—</td>\n</tr>" (실행 전 원문 재확인 후 그대로 사용 — "—"가 아니라 빈 칸일 수 있다)
new_str: "<td>{작성일자}</td>\n<td>{TODAY}</td>\n</tr>"
작성일자 중복 시 SEO_TITLE 포함으로 old_str 범위 확장.

[6m] 들어오는 내부 링크 추가 (지침서 v10.19 — STEP 6 성공 시 필수)

발행 목록(메인 테이블)에서 이번 글과 주제가 인접한 기존 발행 글 2개를 고른다 (내부 링크를 이미 받고 있는 글 우선 — 고아 글에서 걸면 무효).
각 글에 REST API로 신규 글 링크를 추가한다:
1) GET /wp-json/wp/v2/posts?slug={기존슬러그}&_fields=id → id 확인
2) GET /wp-json/wp/v2/posts/{id}?context=edit → content.raw 확보
3) content 끝의 "Related reading" <ul>에 <li><a href="/{신규슬러그}/">{신규 SEO_TITLE}</a></li> 추가 (섹션이 없으면 <p><strong>Related reading</strong></p>\n<ul>...</ul> 신설)
4) 저장 전 <ul>/<li> 여닫이 짝 검증 → POST로 저장. 실패 시 오류 로그만 남기고 발행 자체는 유지 (반려 아님).

STEP 7 — 완료 알림 출력 (200자 이내, 이전 단계의 성공 여부와 무관하게 반드시 실행)

신규 포스트 있음: "KoreaPlug 발행완료 ✅ draft {N}개 | 관문반려 {R}건(로그 기록) | 인바운드링크 {L}건 | SEO평균 {점수}점 | 오류 {E}개 ({TODAY_KST})"
신규 포스트 없음: "KoreaPlug 자동 체크 완료 — 신규 글 없음 ({TODAY_KST})"
[4d]에서 미완성 draft를 복구 완료 처리한 경우: "KoreaPlug 미완성 draft {M}개 복구완료 (SEO/이미지) | ({TODAY_KST})" 를 함께 기록.
⚠️ STEP 0에서 GitHub 지침서 조회에 실패했거나 지침서-루틴 상충을 발견한 경우 해당 사실을 한 줄로 함께 기록한다.

🚨 오류 처리

상황 | 조치
GitHub 지침서 조회 실패 | 저장소 루트 1회 재확인 → 실패 시 오류 로그 기록 + 인라인 체크리스트 폴백으로 계속 진행 (STOP 아님, 지침 추측 생성 금지)
WordPress API 실패 | 로그 기록 후 다음 포스트 진행
Notion 페이지 없음 | 로그 기록 후 다음 포스트 진행
pw.txt 접근 실패 | 오류 로그 기록 후 STEP 7로 건너뜀 (전체 중단)
Chrome 로그인 실패 | Astra/Rank Math 미설정 로그, 포스트 업로드 유지, draft 일자 공란 유지(다음 실행에서 재시도)
Rank Math 78점 미달 | 체크리스트 기준 수정 후 재시도 1회
이미지 처리 실패 | [4e] 4) 재시도 1회, 실패 시 플레이스홀더 유지 + 오류 로그 기록
관문 반려 ([4f] 불통과) | 반려 로그 행 추가 + draft 일자 공란 유지 + 다음 포스트 진행 (STEP 7 알림에 관문반려 건수 표기)
SEO 설정이 새로고침 후 사라짐 | [6d] 참조 — JS dispatch 금지, UI 클릭 방식([6e]~[6g])만 사용 + [6h]에서 새로고침 재검증 필수
