*예약된 트리거 시간이 되면 해당 일자에 먼저 루틴이 실행되더라도 무조건 다시 진행한다.

날짜: 실행 시점의 실제 KST 날짜를 사용한다 (이 프롬프트에 적힌 고정 날짜가 있어도 무시한다).

콘텐츠 작성·키워드 리서치는 Claude Code에서 완료됨.

이 태스크는 업로드·SEO 설정·Notion 업데이트만 수행한다.

⚠️ [변경 2026-07-26] SEO 보정 지침 출처를 Notion → GitHub로 전환.
- 舊: Notion 페이지 "0and1Life Draft v1.2" (app.notion.com, 이제 참조하지 않음)
- 新: GitHub `leejc0404/blog` 저장소의 `0and1Life-Draft.md` (Public 저장소 — 로그인·새 탭 불필요)
  https://raw.githubusercontent.com/leejc0404/blog/main/0and1Life-Draft.md
- STEP 6j(SEO 81점 미달 보정)에서 이 문서를 매번 `fetch()`로 실시간으로 불러와 그 안의 지침을 그대로 따른다. 내용을 캐시·고정하지 않는다 — 문서가 갱신되면 다음 실행부터 자동으로 최신 내용이 반영되어야 한다.
- fetch 실패(네트워크 차단·404 등)면 STEP 6j 안의 [폴백 체크리스트]를 사용하고 오류 로그에 "GitHub 지침 접근 실패 — 폴백 체크리스트 사용"이라고 기록한다.

STEP 0 — 지침서 전체 읽기 (최우선, 세션당 1회 — 2026-07-30 신설)

fetch → https://raw.githubusercontent.com/leejc0404/blog/main/0and1Life-Draft.md (STEP 6j와 동일 문서 — 여기서 한 번 읽어 세션 내 재사용한다)
목적: **SEO 점수와 무관하게** Phase 5-4의 ⛔ 발행 차단 관문(원본자료·가짜경험·이미지출처)을 [4f]에서 항상 판정하기 위함. 舊 구조는 81점 미달일 때만 6j에서 지침을 읽어, 점수가 높으면 관문 전체가 건너뛰어질 수 있었다.
fetch 실패 시: 오류 로그 기록 후 [4f]에 요약된 4개 항목만으로 관문을 판정한다 (폴백 — 관문 생략 금지).

STEP 1 — 날짜 확인 (KST)

오늘(TODAY), 어제(TODAY_MINUS_1) 날짜를 기록한다.

STEP 2 — Notion 후보 글 수집 → CANDIDATE_POSTS

두 페이지에서 "Draft일" 컬럼이 비어 있는(—) 행 수집:

EFFICIENCY: notion-fetch → https://app.notion.com/p/37cbfe4a2ae1819f8664ff3d38fffe56
나의이야기: notion-fetch → https://app.notion.com/p/37cbfe4a2ae181b9a9ced0b937edd344

각 행에서: #번호, 제목, 서브카테고리, SOURCE_PAGE (EFFICIENCY / LIFESTYLE)

두 페이지 합산 비어 있으면 → STEP 7로 건너뜀.

STEP 3 — WordPress 인증 정보 및 카테고리 ID (API 호출 없음)

인증: Basic Auth — leejcfo@gmail.com / {pw.txt 참조 — ONEANDZERO_WP_APP_PASSWORD}
(로컬 C:\Users\win\.claude\blog\pw.txt 의 ONEANDZERO_WP_APP_PASSWORD 값을 사용한다.)

⚠️ [폴백 — v1.28, 2026-08-01 수동 배포에서 검증] pw.txt를 읽을 수 없으면 즉시 중단하지 말고 **브라우저 nonce 인증**으로 전환한다 (Chrome은 어차피 STEP 6 필수 의존성이므로 새 의존성이 아니다):
1) Chrome으로 https://0and1life.com/wp-admin/index.php 접속 → `document.body.classList.contains('wp-admin')`으로 로그인 확인
2) javascript_tool로 nonce 발급:
   `const nonce = (await fetch('/wp-admin/admin-ajax.php?action=rest-nonce', {credentials:'same-origin'}).then(r=>r.text())).trim();`
3) 이후 [4c]/STEP 5/[6i]/[6m]의 모든 REST 호출을 Basic Auth 대신 wp-admin 탭의 javascript_tool에서 `credentials:'same-origin'` + `'X-WP-Nonce': nonce` 헤더로 수행한다 (Post 901 생성에 실사용된 방식).
4) Chrome까지 불가할 때만 오류 로그에 "pw.txt 접근 실패 + Chrome 미연결"을 기록하고 STEP 7로 건너뛴다.

서브카테고리 → WP Category ID:
💰 직장인 재태크 → 23
📊 업무에서 AI 활용법 → 18
⚙️ 실생활 AI 활용법 → 18
📈 핫한 AI 트랜드 → 18
💼 대기업 직장인 생활 → 29 (slug corporate-worker-life — 2026-07-26 WP 관리자 화면 대조로 확인)
⏱️ 시간·돈 절약 시스템 → 30 (slug time-money-saving — 2026-07-26 WP 관리자 화면 대조로 확인)
[1] 나의이야기 전체 → 1 (Uncategorized)

⚠️ (2026-07-26) 위 4개(재테크/업무AI/실생활AI/AI트렌드)가 전부 WP ID 18·23 두 개로 수렴하는 것은 정상이다 — Notion 표기상의 세부 서브카테고리와 실제 WP taxonomy는 1:1이 아니다. 반면 대기업 직장인 생활·시간돈 절약 시스템은 각각 독립된 WP 카테고리이므로 재테크/AI로 대체 배정하지 않는다 (舊 임시 배정 규칙 폐기).

매핑 없는 서브카테고리는 WP REST API로 카테고리 먼저 생성 후 ID 사용. 단, 생성 전 GET /wp-json/wp/v2/categories?search={이름} 으로 동일·유사 카테고리가 이미 존재하는지 먼저 확인한다 (신규 생성은 최후 수단).
Notion 서브페이지 "Category" 행에 "(WP 29)" 처럼 WP 카테고리 ID가 이미 명시된 경우 그 값을 그대로 사용 (신규 생성 불필요).

⚠️ 전체 슬러그 페이지네이션 수집 삭제 — 슬러그 중복 확인은 STEP 4에서 후보 글별 1회 직접 확인.

STEP 4 — Notion 서브페이지 콘텐츠 읽기 → 필드 추출

CANDIDATE_POSTS 각 포스트에 대해:

[4a] 서브페이지 URL 확인 (⚠️ 수정 2026-07-26 — 위치 의존 제거, KoreaPlug [4a]와 동일 방식)
① notion-search로 포스트 제목(`Blog #{번호}` 또는 제목 앞부분)을 검색 → 서브페이지 page_id·URL 확인.
② 검색 결과가 없을 때만 SOURCE_PAGE에 해당하는 현황표 페이지를 fetch해 자식 페이지 목록에서 찾는다:
- EFFICIENCY → https://app.notion.com/p/37cbfe4a2ae1819f8664ff3d38fffe56
- LIFESTYLE → https://app.notion.com/p/37cbfe4a2ae181b9a9ced0b937edd344
③ 둘 다 실패 → 오류 로그에 "서브페이지 없음 #{번호}" 기록 후 다음 포스트로 진행. **Draft일은 공란 유지** — 다음 실행에서 재시도한다.

⚠️ 舊 방식("메인 페이지 내 서브페이지 링크로 fetch")은 초안이 현황표 페이지의 직계 자식일 때만 동작했다. 위 방식은 초안이 현황표 바로 아래에 있든, 나중에 카테고리 방을 만들어 그 안으로 옮기든 **위치와 무관하게** 찾는다.

[4b] 필드 추출
"기본 정보" 표에서 추출:
SLUG / SEO_TITLE / META_DESCRIPTION / FOCUS_KEYWORD / SUB_KEYWORDS / HTML_CONTENT / WP_CAT_ID

⚠️ FOCUS_KEYWORD: Notion "Focus Keyword" 행 값 그대로 복사 (AI 재생성·수정 금지)
⚠️ SUB_KEYWORDS: Notion "Sub Keywords" 행 값 그대로 복사 → " / " 구분자를 ", " 로 변환

[4c] 슬러그 중복 확인 (1회 직접 확인)
GET https://0and1life.com/wp-json/wp/v2/posts?slug={SLUG}&status=any&_fields=id,slug
인증: STEP 3과 동일. status=any 필수.
응답이 비어있으면 → 중복 없음, 업로드 진행.
응답에 데이터 있으면 → "건너뜀"이 아니라 상태를 먼저 점검한다 (과거 실행이 STEP5까지만 하고 STEP6을 못 마친 채 남아있는 경우가 있음):
  1) 반환된 post id로 GET /wp-json/wp/v2/posts/{id}?context=edit 호출.
  2) Chrome으로 https://0and1life.com/wp-admin/post.php?post={id}&action=edit 열어 GeneratePress 3필드(sidebar/full-width/title-disable)와 Rank Math(getKeywords/getSerpDescription/getAnalysisScore)가 비어있는지 확인.
  3) 비어있으면 WP_POST_ID = {id} 로 설정하고 STEP 6부터 정상 진행 (STEP 5 업로드는 건너뜀).
  4) 이미 채워져 있으면 진짜 완료된 것이므로 Notion "Draft일"만 TODAY로 업데이트하고 다음 후보로 건너뜀.

[4d] 히어로 이미지 처리
서브페이지 HTML_CONTENT 내 첫 <img> Unsplash URL 확인.
없거나 Unsplash URL 아닌 경우 서브카테고리 맞는 키워드로 Unsplash에서 선택 후 WP Media 업로드.

[4e] FAQ 스키마(FAQ_SCHEMA_JSON) 추출 — GEO/AEO 보강

HTML_CONTENT 안의 "자주 묻는 질문" 섹션에서 아래 패턴으로 Q/A 쌍을 모두 추출한다:
정규식: <p><strong>Q\.\s*(.+?)<\/strong><br>(.+?)<\/p>  (dotall)

2쌍 이상 추출되면 FAQPage 스키마 JSON을 만든다:
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [ { "@type": "Question", "name": "{질문}", "acceptedAnswer": {"@type":"Answer","text":"{답변}"} }, ... ]
}
이 JSON을 FAQ_SCHEMA_JSON 변수로 보관 (STEP 5에서 본문에 삽입).
Q/A가 1쌍 이하면 FAQ_SCHEMA_JSON = null (건너뜀).

> ⚠️ 이 정규식은 Writer 가이드가 FAQ를 정확히 위 마크업으로 작성했을 때만 매치된다. 다른 형식(h3, dl 등)이면 조용히 FAQ_SCHEMA_JSON = null로 건너뛴다 — 오류는 아니지만 FAQ 스키마 삽입률이 낮아질 수 있다. 필요하면 0and1Life-Writer.md에 이 마크업을 명문화하는 것을 권장한다.

참고: Article/BlogPosting 스키마는 Rank Math가 기본 템플릿(new-9999, %seo_title%/%seo_description% 자동 매핑)으로 이미 자동 처리하므로 별도 조치 불필요.

[4f] 발행 차단 관문 판정 (Phase 5-4 ⛔ — 업로드 전 필수, 2026-07-30 신설)

HTML_CONTENT와 기본 정보 표를 대상으로 판정한다:
① 원본자료: 1급 원본 자료(직접 조작한 화면 캡처·실측 수치·실제 고지서 등) 최소 1개 — 계산표·통합표·공식 수치 재정리만 있으면 불통과. 단, 기본 정보 표에 "1급 자료 조달 계획: 루틴가능 {화면·경로}"가 명시돼 있으면 **로그인 없이 접근 가능한 공개 페이지에 한해** Chrome으로 그 화면을 직접 조작·캡처 → WP 미디어 업로드 → 본문 해당 위치에 삽입해 관문을 스스로 충족시킨다 (캡처 실행 주체는 브라우저가 있는 이 루틴 — 가이드 v1.26).

**캡처 품질·마크업 규칙 (v1.28 — "캡처가 어색하다" 피드백 반영, 2026-08-01):**
- 전체 화면·전체 페이지 캡처 금지. **결과·조문 영역만** `zoom`(region 지정)으로 잘라 찍는다 — 사이트 헤더·메뉴·배너가 프레임에 들어가면 실패.
- 캡처 프레임에 **스크롤바·마우스 커서·드래그 핸들·쿠키 배너·팝업 잔재**가 보이면 재캡처한다 (스크린샷 육안 검증 필수). 우측 스크롤바는 region 우측 경계를 콘텐츠 폭 기준 ~20px 안쪽으로 잡아 배제한다.
- 표·조문처럼 사각형으로 떨어지는 콘텐츠는 그 사각형에 딱 맞춰 자른다. 문장 중간·행 중간에서 잘리면 재캡처.
- 삽입 마크업 표준 (증빙은 '자료 카드'로 보이게 — 데코 이미지와 시각적으로 구분):
  `<figure class="evidence-capture" style="margin:26px 0; border:1px solid #e2e8f0; border-radius:12px; padding:10px; background:#fafafa;"><img style="width:100%;display:block;height:auto;border-radius:8px;" src="{URL}" alt="{Focus Keyword 포함 설명}" /><figcaption style="font-size:13px; color:#64748b; margin-top:8px;">{출처 기관 — 화면명 · Captured YYYY-MM-DD}</figcaption></figure>`
- 업로드 파일명: `evidence-{SLUG}-{n}.webp` — **Image 루틴이 증빙을 생성 이미지와 구분하는 근거이므로 반드시 이 규칙을 따른다** (class="evidence-capture"와 파일명 prefix 둘 다).
② 가짜경험: 하지 않은 일의 1인칭 서술·가공된 신상 문장 0건.
③ 이미지출처: 모든 <img>가 자체 업로드(0and1life.com) 또는 images.unsplash.com — gstatic·pstatic 등 타 사이트 핫링크 0건.

①~③ 중 하나라도 불통과 → 이 포스트는 STEP 5~6을 건너뛴다 (Draft일 공란 유지). 그리고 발행 반려 로그에 행 1개를 추가한다:
https://www.notion.so/3adbfe4a2ae1817994f0f901de5c8dec
행 형식: | {TODAY} | {SLUG} | {사유 코드} | {무엇을} | {어디에} | {왜} | {어떻게} | {루틴 또는 사용자} | 대기 |
⚠️ "1급 자료 없음"만 적는 보고는 무효 — 무엇을·어디에·왜·어떻게 4항목을 반드시 채운다 (지침 v1.25). 같은 슬러그의 '대기' 행이 이미 있으면 중복 추가하지 않는다. 기록 후 다음 후보로 진행.

STEP 5 — WordPress Draft 업로드 + Notion 메인 테이블 업데이트

[4c]에서 "비어있음(재개 필요)"으로 판정된 경우 이 STEP은 건너뛰고 STEP 6으로 바로 이동한다 (WP_POST_ID는 이미 설정됨).

날짜 치환 (v1.28): HTML_CONTENT 상단 메타 라인의 날짜 문자열(정규식 `\d{4}년 \d{1,2}월 \d{1,2}일` — **첫 번째 매치 1개만**)을 TODAY(KST)로 치환한다. 본문 속 다른 날짜(제도 시행일 등)는 건드리지 않는다.
근거: #64 에너지캐시백이 작성일 7/25 표기를 단 채 8/1에 발행됨 — 독자·구글 모두에게 신선도 신호 손실.

HTML_BODY 조립 (FAQ 스키마 삽입):
FAQ_SCHEMA_JSON이 null이 아니면 HTML_CONTENT의 마지막 `</div>` 바로 뒤에 아래를 삽입한다:
  \n<script type="application/ld+json">{FAQ_SCHEMA_JSON 문자열}</script>\n
(원본 HTML_CONTENT 구조·스타일은 절대 변경하지 않음 — 스키마 스크립트만 끝에 추가)

POST https://0and1life.com/wp-json/wp/v2/posts
인증: STEP 3과 동일 | Content-Type: application/json
{
  "title":      "{SEO_TITLE}",
  "content":    "<!-- wp:freeform -->\n{HTML_BODY}\n<!-- /wp:freeform -->",
  "status":     "draft",
  "slug":       "{SLUG}",
  "categories": [{WP_CAT_ID}]
}
응답에서 WP_POST_ID 기록.

[5a] Notion 메인 테이블·서브페이지 업데이트 (Post ID·상태만 — Draft일은 여기서 기록하지 않음)

notion-update-page / update_content

SOURCE_PAGE EFFICIENCY → page_id: 37cbfe4a-2ae1-819f-8664-ff3d38fffe56
SOURCE_PAGE LIFESTYLE  → page_id: 37cbfe4a-2ae1-81b9-a9ce-d0b937edd344

⚠️ page_id 하드코딩되어 있으므로 실행 전 재확인 불필요.

서브페이지 업데이트:
상태: 작성완료 → 배포완료 (Draft) (서브페이지에 "상태" 행이 없으면 새 행으로 추가)
WordPress Post ID: {WP_POST_ID} 기재 (없으면 새 행으로 추가)

⚠️ [수정 2026-07-26] "Draft일자"(서브페이지)와 메인 테이블의 "Draft일" 셀은 이 단계에서 기록하지 않는다 — STEP 6 전 과정이 성공했을 때만 [6l]에서 기록한다. 여기서 기록해버리면 STEP 6이 실패해도 다음 실행의 STEP 2가 이 글을 후보로 다시 집지 않아, [4c]의 재개 로직이 영원히 실행되지 못한다.

[5b] 슬러그 충돌 감지
실제 slug ≠ 요청 SLUG → 오류 로그 기록 후 건너뜀.

STEP 6 — 에디터에서 Rank Math SEO + GeneratePress 설정 (Claude in Chrome 필수)

🎨 테마: GeneratePress (Astra 설정 절대 사용 금지)

[6a] 브라우저 연결
list_connected_browsers → select_browser

[6b] 에디터 열기
navigate → https://0and1life.com/wp-admin/post.php?post={WP_POST_ID}&action=edit

⚠️ navigate 직후 get_page_text 호출 금지. wait 3초 후 아래 javascript_tool로만 로그인 확인.
document.body?.classList.contains('wp-admin') ? 'logged-in' : 'not-logged-in'
결과가 'not-logged-in'이면 오류 로그 기록 후 건너뜀.

[6c] GeneratePress 레이아웃 설정 (JavaScript)

const nativeSelectSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
const nativeCheckSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'checked').set;

const sidebarSel = document.getElementById('generate-sidebar-layout');
if (sidebarSel) { nativeSelectSetter.call(sidebarSel, 'no-sidebar'); sidebarSel.dispatchEvent(new Event('change', {bubbles: true})); }

const contentSel = document.getElementById('_generate-full-width-content');
if (contentSel) { nativeSelectSetter.call(contentSel, 'true'); contentSel.dispatchEvent(new Event('change', {bubbles: true})); }

const titleCb = document.getElementById('meta-generate-disable-headline');
if (titleCb && !titleCb.checked) { nativeCheckSetter.call(titleCb, true); titleCb.dispatchEvent(new Event('click', {bubbles: true})); }

console.log('✅ GeneratePress 설정 완료 (no-sidebar / full-width / title disabled)');

[6c-검증] GeneratePress 설정 반영 확인

편집기 상단의 "임시 글로 저장" 버튼을 직접 클릭해 저장한다 (Ctrl+S 단축키는 포커스 위치에 따라 브라우저 자체 저장 다이얼로그를 열거나 반영되지 않는 경우가 있었으므로 버튼 클릭을 우선한다. Ctrl+S를 쓸 경우 저장 후 "임시글 저장됨" 문구가 실제로 뜨는지 스크린샷으로 확인할 것). 저장 후 wait 3초 → 에디터 새로고침(navigate로 같은 URL 재방문) → javascript_tool 실행:

const sidebarOk = document.getElementById('generate-sidebar-layout')?.value === 'no-sidebar';
const contentOk = document.getElementById('_generate-full-width-content')?.value === 'true';
const titleOk = document.getElementById('meta-generate-disable-headline')?.checked === true;
JSON.stringify({sidebarOk, contentOk, titleOk});

셋 중 하나라도 false → [6c] 재시도 1회.
재시도 후에도 false → 오류 로그에 "GP 레이아웃 미반영" 명시 기록 (기존처럼 "완료"로 보고 금지).

콘텐츠는 STEP 5 REST API 업로드 시 이미 freeform 래퍼로 저장됨. 에디터 자동 로딩.
본문이 비어있는 경우에만 [6i] 폴백 실행.

[6d] Rank Math SEO 설정 (JavaScript)

⚠️ FOCUS_KEYWORD·SUB_KEYWORDS는 Notion 서브페이지 값 그대로 사용 (재검색·수정 금지)
⚠️ 반드시 updateSerpDescription / updateSerpTitle도 함께 호출할 것 (updateDescription/updateTitle만으로는 실제 라이브 페이지의 <meta name="description">이나 SEO 점수 분석에 반영되지 않음).

if (!wp.data.select('rank-math')) {
  await new Promise(r => setTimeout(r, 3000));
}
if (!wp.data.select('rank-math')) {
  throw new Error('rank-math store not available');
}

const rmDispatch = wp.data.dispatch('rank-math');
const allKeywords = ['FOCUS_KEYWORD', ...'SUB_KEYWORDS_CSV'.split(',').map(k => k.trim())].join(', ');
rmDispatch.updateKeywords(allKeywords);
console.log('✅ Keywords set (focus + sub):', allKeywords);

rmDispatch.updateTitle('SEO_TITLE');
rmDispatch.updateSerpTitle('SEO_TITLE');
rmDispatch.updateDescription('META_DESCRIPTION');
rmDispatch.updateSerpDescription('META_DESCRIPTION');
rmDispatch.updateSerpSlug('SLUG');
await new Promise(r => setTimeout(r, 1000));
console.log('✅ Rank Math SEO 설정 완료, score:', wp.data.select('rank-math').getAnalysisScore());

throw 발생 시 → [6e]~[6g] 클릭 방식 폴백.

[6e] Rank Math 패널 열기 (폴백)
상단 우측 Rank Math 점수 배지 클릭.

[6f] 포커스 키워드 + 서브키워드 입력 (폴백)
포커스 키워드 필드: FOCUS_KEYWORD 입력 후 Enter
Additional Keywords 필드: SUB_KEYWORDS_CSV 각 항목 입력 후 Enter

[6g] 스니펫 편집 (폴백)
"스니펫 편집" 버튼 클릭 → SEO_TITLE, META_DESCRIPTION 입력 → 창 닫기.

[6h] 저장
편집기 상단 "임시 글로 저장" 버튼 클릭 → "임시글 저장됨" 확인 후 3초 대기.
⚠️ 저장 후 반드시 에디터를 새로고침하고 GP 3필드·Rank Math 키워드·설명 값을 다시 읽어 실제로 저장되었는지 확인할 것 (한 번의 저장으로 반영 안 되는 경우가 있었음 — 반영 안 됐으면 [6c]/[6d] 재실행 후 저장 재시도).

[6i] 콘텐츠 재업로드 폴백 (에디터 본문 비어있을 때만 실행)
POST https://0and1life.com/wp-json/wp/v2/posts/{WP_POST_ID}
페이로드: {"content": "<!-- wp:freeform -->\n{HTML_BODY}\n<!-- /wp:freeform -->"}

[6j] SEO 점수 확인 및 보정 (⚠️ 보정 지침 출처: GitHub, Public 저장소)

에디터 새로고침 → wait 3초 → Rank Math 점수 확인.
목표: 81점 이상.

81점 이상이면 아래 절차를 건너뛰고 [6k]로 진행한다.

81점 미달 시, 아래 순서로 진행한다:

1) GitHub 지침 문서 로드
   지금 열려 있는 편집기 탭에서 그대로 javascript_tool로 실행한다 (Public 저장소이므로 로그인·새 탭 불필요, raw.githubusercontent.com은 CORS 허용):

   window._draftGuide = null;
   fetch('https://raw.githubusercontent.com/leejc0404/blog/main/0and1Life-Draft.md')
     .then(r => r.text())
     .then(t => { window._draftGuide = t; })
     .catch(e => { window._draftGuide = 'FETCH_FAILED: ' + e.message; });
   // 2~3초 대기 후 window._draftGuide?.length 확인 ('FETCH_FAILED'로 시작하면 실패)

   window._draftGuide 문자열에서 "Phase 5-2"(TOC 강제 인식 스크립트), "Phase 5-3"(블록 구조/820px/키워드 체크리스트), "🔧 자주 발생하는 오류 & 해결법" 표, "Cowork 원라이너" 섹션을 찾아 읽는다.
   fetch 실패(FETCH_FAILED 또는 길이 0) 시 → 오류 로그에 "GitHub 지침 접근 실패 — 폴백 체크리스트 사용" 기록 후 하단 [폴백 체크리스트]로 바로 진행.

2) 문서에 실린 TOC 강제 인식 스크립트를 편집기 탭에서 그대로 실행한다 (javascript_tool). 스크립트 내용은 문서를 그대로 따르되, 요지는 다음과 같다: window.rankMath.assessor.hasTOCPlugin을 true로 강제 설정 → core/freeform 블록 내용을 살짝 건드렸다가 원복해 재분석을 트리거 → savePost() 호출.
   ⚠️ 舊 스크립트 `wp.data.dispatch('rank-math').updateReduxState({hasTOCPlugin:true})`는 실제로 존재하지 않는 함수(TypeError 발생 확인됨)이므로 더 이상 사용하지 않는다. GitHub 문서의 스크립트로 완전히 대체한다.

3) 문서의 "Phase 5-3" 체크리스트를 점검한다. 특히:
   - Rank Math 포커스 키워드 필드에 FOCUS_KEYWORD + SUB_KEYWORDS 전부가 쉼표로 연결되어 입력되었는가? `wp.data.select('rank-math').getKeywords()` 결과에 쉼표로 구분된 항목이 2개 이상 있는지 확인 (1개뿐이면 [6d]의 updateKeywords를 재실행).
   - 모든 콘텐츠가 `max-width:820px; padding:0 16px 40px; box-sizing:border-box;` 래퍼 안에 있는가?
   - HTML 내 이미지가 plain `<img>` 태그로 삽입되어 있고 `<!-- wp:image -->` 마커가 없는가?
   - freeform 블록 외부에 별도 Gutenberg 이미지 블록(`alignwide`)이 없는가?

4) 아래 로컬 체크리스트(①~⑦)도 함께 점검 — GitHub 문서는 TOC/블록구조/키워드 항목을 보강할 뿐 이 체크리스트를 대체하지 않는다:
   ① FOCUS_KEYWORD가 첫 <p>(도입부 100자 이내)에 포함되어 있는가?
   ② FOCUS_KEYWORD가 <h2> 헤딩 1개 이상에 포함되어 있는가?
   ③ SEO_TITLE이 60자 이하이며 FOCUS_KEYWORD를 포함하는가?
   ④ META_DESCRIPTION이 150자 이하이며 FOCUS_KEYWORD를 포함하는가?
   ⑤ 내부 링크(0and1life.com)가 1개 이상 있는가?
   ⑥ <img> alt 속성에 FOCUS_KEYWORD 또는 연관어가 포함되어 있는가?
   ⑦ 본문 글자 수가 1,500자 이상인가?
   위 1)~4)에서 미충족 항목만 REST API로 HTML 수정 후 저장 버튼 클릭 → 재시도 1회.
   ⚠️ 슬러그(SLUG)는 영문 그대로 유지 (URL에 한글 FOCUS_KEYWORD가 없다는 경고는 구조적 사양이며 수정 대상 아님 — 슬러그 변경 금지).
   키워드 기계적 반복 삽입 금지.

[폴백 체크리스트] (GitHub 지침 접근이 실패했을 때만 사용)
- 위 4)의 ①~⑦ 체크리스트만 점검 후 REST API로 HTML 수정 → 저장 → 재시도 1회.
- TOC 관련 보정(1)~3))은 생략하고 오류 로그에 사유를 남긴다.

⛔ 절대 금지: core/heading 블록 추가 / getEditedPostContent() freeform 소스 사용 / 키워드 반복 삽입

[6k] Notion SEO 점수 업데이트
old_str: "<td>—</td>\n<td>{서브카테고리이모지+이름}</td>"
new_str: "<td>{SEO_FINAL_SCORE}</td>\n<td>{서브카테고리이모지+이름}</td>"

[6l] Draft일 기록 (STEP 6 전 과정이 성공했을 때만 실행)

⚠️ 6c-검증(GeneratePress 레이아웃 반영)과 6d(Rank Math 키워드·스니펫 설정)가 모두 성공했을 때만 실행한다. 아래 중 하나라도 있었으면 Draft일을 공란으로 남긴다 — 다음 실행이 이 글을 다시 후보로 잡아 [4c] 재개 로직으로 STEP 6부터 이어간다(슬러그 중복이 이미 있으므로 STEP 5는 자동으로 건너뛴다):
- Chrome 로그인 실패
- GP 레이아웃 미반영 (재시도 후에도)
- Rank Math 설정 throw 후 클릭 폴백([6e]~[6g])까지 실패

성공했다면:

서브페이지 업데이트: Draft일자 = TODAY

메인 테이블 "Draft일" 셀 — → TODAY 교체 (실행 전 현재 셀 원문을 재확인해 old_str을 그대로 구성할 것 — "—"가 아니라 빈 칸(<td></td>)일 수 있다):
old_str: "<td>{작성일 YYYY-MM-DD}</td>\n<td></td>\n</tr>" (원문 확인 후 사용)
new_str: "<td>{작성일 YYYY-MM-DD}</td>\n<td>{TODAY}</td>\n</tr>"
작성일 중복 시 서브카테고리 이모지+이름까지 old_str에 포함해 범위 확장 (같은 작성일 행이 여러 개일 수 있음).

[6m] 들어오는 내부 링크 추가 (가이드 v1.23 — STEP 6 성공 시 필수)

현황표에서 이번 글과 주제가 인접한 기존 발행 글 2개를 고른다 (내부 링크를 이미 받고 있는 글 우선 — 고아 글에서 걸면 무효).
각 글에 REST API로 신규 글 링크를 추가한다:
1) GET /wp-json/wp/v2/posts?slug={기존슬러그}&_fields=id → id 확인
2) GET /wp-json/wp/v2/posts/{id}?context=edit → content.raw 확보
3) content 끝의 "함께 읽으면 좋은 글" <ul>에 <li><a href="/{신규슬러그}/">{신규 제목}</a></li> 추가 (섹션이 없으면 <p><strong>함께 읽으면 좋은 글</strong></p>\n<ul>...</ul> 신설)
4) 저장 전 <ul>/<li> 여닫이 짝 검증 → POST로 저장. 실패 시 오류 로그만 남기고 발행 자체는 유지 (반려 아님).

[6n] 트랙 S 빠른 발행 알림 (v1.28 — 선점 시의성 보존)

⛔ **이 루틴의 권한은 draft 작성·수정까지다. 발행(publish)·예약발행(future) 상태 변경은 어떤 경우에도 하지 않는다 — 발행 결정은 항상 사용자 몫이다 (2026-08-01 사용자 지시).**

기본 정보 표의 Track 행이 "S"로 시작하는 글은 발행이 늦어지면 선점 의미가 사라지므로, **정보만** 정리해 사용자에게 알린다:
1) GET /wp-json/wp/v2/posts?status=future&per_page=20&_fields=id,date 로 현재 예약 발행 목록 확보 (읽기 전용)
2) 내일부터 하루씩 09:00 KST 슬롯을 훑어 비어 있는 첫 날짜를 찾는다
3) Notion 실행 로그와 STEP 7 완료 알림에 다음 형식으로 기재한다 (글 상태는 draft 그대로 유지):
   "⚡ 트랙 S 글 — 시의성 소재({헤드 요약}). 빠른 발행 권장, 현재 빈 슬롯: {날짜} 09:00 (예약은 사용자가 직접)"
트랙 L 글은 이 알림 없이 기존 수동 예약 흐름을 따른다.
근거: 트랙 S는 급상승 헤드 기반이라 작성→발행 지연이 2일을 넘으면 선점 의미가 소멸 (#71 우리사주: 코스피 폭등 당일 작성, 기존 큐 순서면 8/11 발행 — 10일 지연).

STEP 7 — 완료 알림 출력 (이전 단계의 성공 여부와 무관하게 반드시 실행)

신규 포스트 있음: "0and1Life 발행완료 ✅ draft {N}개 | 관문반려 {R}건(로그 기록) | 인바운드링크 {L}건 | SEO평균 {점수}점 | FAQ스키마 {F}건 | 오류 {E}개 ({TODAY_KST})"
신규 포스트 없음: "0and1Life 자동 체크 완료 — 신규 글 없음 ({TODAY_KST})"

🚨 오류 처리

상황 | 조치
WordPress API 실패 | 로그 기록 후 다음 포스트 진행
Notion 페이지 없음 | 로그 기록 후 다음 포스트 진행
pw.txt 접근 실패 | 브라우저 nonce 폴백(STEP 3 v1.28)으로 전환. Chrome도 불가하면 오류 로그 기록 후 STEP 7로 건너뜀 (전체 중단)
Chrome 로그인 실패 (WordPress) | GP/Rank Math 미설정 로그, 포스트 업로드 유지, Draft일 공란 유지(다음 실행에서 재시도)
GitHub 지침 페이지 fetch 실패 (네트워크 차단·404 등) | [폴백 체크리스트] 사용 + 오류 로그 기록, 포스트 업로드는 유지
Rank Math store 미등록 | 3초 대기 재시도 → 실패 시 클릭 폴백
Rank Math 81점 미달 | STEP 6j 절차대로 보정 후 재시도 1회, 그래도 미달이면 최종 점수 그대로 Notion에 기록, Draft일은 [6l] 조건대로 처리
슬러그 중복이지만 GP/RankMath 미설정 | STEP 6부터 재개 (건너뛰지 않음, [4c] 참고)
관문 반려 ([4f] 불통과) | 반려 로그 행 추가 + Draft일 공란 유지 + 다음 포스트 진행 (STEP 7 알림에 관문반려 건수 표기)
