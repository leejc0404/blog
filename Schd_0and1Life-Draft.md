# Schd_0and1Life-Draft — WordPress Draft 업로드 루틴 (Cowork 예약 작업용)

*예약된 트리거 시간이 되면 해당 일자에 먼저 루틴이 실행되었더라도 무조건 다시 진행한다.

날짜: 실행 시점의 실제 KST 날짜를 사용한다 (이 프롬프트에 적힌 고정 날짜가 있어도 무시한다).

콘텐츠 작성·키워드 리서치는 Claude Code에서 완료됨. 이 태스크는 업로드·SEO 설정·Notion 업데이트만 수행한다.

⚠️ [무인 실행 원칙 — 최우선]
이 루틴은 사람이 없는 새벽에 실행된다. **사용자 승인이 필요한 도구 호출을 불필요하게 하지 않는다.** 승인이 필요한 호출은 "그것 없이는 진행이 불가능함을 먼저 실측으로 확인한 뒤"에만 한다.

⚠️ [최우선 규약 — 저장 순서와 자동저장]
**에디터 탭이 열려 있는 동안에는 REST로 본문을 쓰지 않는다.**
draft는 Gutenberg 자동저장이 리비전이 아니라 **원본 글에 직접 기록**된다. 에디터 탭을 열어둔 채 REST로 본문을 덮어쓰면 에디터 메모리의 구버전이 REST 결과를 되덮어쓴다(`<p>` 대량 소실).
본문 REST 수정이 필요하면 반드시 **① 열린 에디터 탭의 dirty 해제 → ② 탭을 post.php 밖으로 이동 → ③ REST POST → ④ 8초 후 재조회 검증** 순서를 지킨다 ([6m-0] 참조).

⚠️ [SEO 보정 지침 출처] GitHub `leejc0404/blog` 저장소의 `0and1Life-Draft.md`
https://raw.githubusercontent.com/leejc0404/blog/main/0and1Life-Draft.md
STEP 0에서 매번 `web_fetch`로 실시간으로 불러와 세션 내 재사용한다. 캐시·고정하지 않는다.
⚠️ **조회 URL에는 반드시 `?cb={epoch_ms}` 를 붙인다.** 캐시된 구버전이 반환되면 실재하는 조항을 결번으로 오판한다.
fetch 실패면 이 프롬프트의 규칙만으로 진행하고 오류 로그에 "GitHub 지침 접근 실패 — 폴백 사용"이라고 기록한다.

⚠️ [조항 자기보완 규약 — 지침서 Phase 5-0]
조항이 안 보여도 **바로 "없다"고 판정하지 않는다.** ①새 `?cb=` 로 재조회 → ②Claude in Chrome 에서 `fetch(rawURL+'?cb='+Date.now())` → ③그래도 없으면 결번 확정. 어느 단계에서든 찾으면 그것이 진짜 지침서이고, 이 경우는 **상충이 아니라 캐시 사고**로 기록한다.
결번이 확정되면 **STOP하지 않고** 조항을 직접 작성해 `C:\Users\win\Documents\Claude\blog\0and1Life-Draft.md` 에 써 넣고(제목에 `(자동 신설 {TODAY}, 루틴 작성)` 표기, **추가만**, 삭제·번호변경 금지) 그 회차 판정 기준으로 즉시 적용해 draft 를 계속한다. 근거는 ⓐ이 프롬프트의 인라인 폴백([4f]·[6j]) → ⓑ`KoreaPlug-Draft.md` 대응 조항 → ⓒ최근 7일 반려·실행 로그 실측 **순서로만** 삼는다. **git commit·push 는 하지 않는다 — 사용자가 직접 한다.** 신설 사실과 **전문**을 STEP 7 알림과 Notion 로그에 남긴다.

⚠️ 이 프롬프트가 실행되는 유일한 원본이다. 다른 위치의 사본을 참조하지 않는다.

STEP 0 — 지침서 읽기 + 무결성 검증 (최우선, 세션당 1회)

[0-1] 조회 (캐시버스터 필수)
fetch → https://raw.githubusercontent.com/leejc0404/blog/main/0and1Life-Draft.md?cb={epoch_ms}
목적: ① Phase 5-1 저장 순서 규약 ② Phase 5-3-B 조치 가능 여부 판정표 ③ Phase 7 카테고리 배정 ④ Phase 5-4 ⛔ 발행 차단 관문 ⑤ Phase 5-0 무결성·자기보완 규약.
※ web_fetch 도구로 수행한다. bash curl 은 샌드박스 네트워크 제한으로 raw.githubusercontent.com 에 접근할 수 없다.
※ `?cb=` 를 빠뜨리지 않는다 — 캐시된 구버전이 반환되면 실재하는 조항을 결번으로 오판한다.

[0-2] 본문 자가검증 (지침서 5-0-A)
받은 문서에서 아래를 문자열로 확인하고 결과를 기록한다:
· `⛔ 발행 차단 관문` 포함 여부
· `Phase 5-1. 저장 순서 규약` / `Phase 5-3-B` / `Phase 7. 카테고리 배정` 포함 여부
· 문서 문자 수 / 최신 개정 이력 줄(`**v1.x (`)
다 정상이면 STEP 1로 진행.

[0-3] 조항이 안 보이면 — 3단 검증 (지침서 5-0-A)
1) 새 `?cb={epoch_ms}` 로 1회 재조회
2) Claude in Chrome 에서 `fetch(rawURL + '?cb=' + Date.now())` 로 재조회 (캐시 계층이 다르다)
3) 그래도 없으면 결번 확정
어느 단계에서든 찾으면 그것이 진짜 지침서다. 폴백으로 판정을 시작했더라도 되돌려 다시 판정한다.
⚠️ 이 경우는 상충이 아니다 — STEP 7에 "지침서 조회 캐시 사고 — {단계}에서 조항 확인"으로 기록한다.

[0-4] 결번 확정 시 — 조항 자기보완 후 계속 진행 (지침서 5-0-B)
STOP하지 않는다.
1) 조항 초안 작성. 근거는 ⓐ이 프롬프트 인라인 폴백([4f]·[6j]) → ⓑ`KoreaPlug-Draft.md` 대응 조항 → ⓒ최근 7일 반려·실행 로그 실측 순서로만. 근거 없는 창작 금지
2) `C:\Users\win\Documents\Claude\blog\0and1Life-Draft.md` 에 직접 써 넣는다. 제목에 `(자동 신설 {TODAY}, 루틴 작성)` 표기. 추가만 — 삭제·번호변경 금지
   · 폴더 미연결이면 [3-0] 절차대로 먼저 연결한다 (무인 승인 창 주의 — bash 탐색 먼저)
3) git commit·push 는 하지 않는다 (사용자가 직접)
4) 신설 조항을 그 회차 판정 기준으로 즉시 적용
5) STEP 7 알림과 Notion 로그에 `조항 자동 신설 {조항번호}` + 신설 조항 전문 기록

[0-5] 조회 자체가 실패할 때
저장소 루트 1회 → Chrome 1회 → 그래도 실패면 이 프롬프트 규칙만으로 진행 + "GitHub 지침 접근 실패 — 폴백 사용" 기록.
⚠️ 이 경우는 조항 자기보완을 하지 않는다 (문서를 못 읽은 것이지 결번이 아니다).

STEP 1 — 날짜 확인 (KST). 오늘(TODAY), 어제(TODAY_MINUS_1)를 기록한다.

STEP 2 — Notion 후보 글 수집 → CANDIDATE_POSTS
두 페이지에서 "Draft일" 컬럼이 비어 있는(— 또는 빈 칸) 행 수집:
EFFICIENCY: notion-fetch → https://app.notion.com/p/37cbfe4a2ae1819f8664ff3d38fffe56
나의이야기: notion-fetch → https://app.notion.com/p/37cbfe4a2ae181b9a9ced0b937edd344
각 행에서: #번호, 제목, 서브카테고리, SOURCE_PAGE. 둘 다 비어 있으면 STEP 7로 건너뜀.

STEP 3 — WordPress 인증 및 카테고리 ID

[3-0] 폴더 접근 확인 (조건부)
⛔ `request_cowork_directory` 를 무조건 호출하지 않는다. 무인 시간대에 승인 창이 뜨면 세션이 정지한다.
1) 먼저 bash로 읽기를 시도한다: `ls /sessions/*/mnt/Claude/pw.txt 2>/dev/null`
   경로가 나오면 → [3-1]로 바로 진행, `request_cowork_directory` 호출 금지. 세션명은 실행마다 다르므로 와일드카드로 찾고 실제 경로를 이후 단계에서 쓴다.
2) 1)이 실패했을 때만 `mcp__cowork__request_cowork_directory { path: "C:\Users\win\Documents\Claude" }` 1회. 승인 창이 응답 없이 닫히면(AbortError) 재시도하지 말고 [3-2]로 즉시 이동.
3) 이 단계에서는 승인이 필요한 호출을 다른 도구 호출과 같은 블록에 묶지 않는다.

[3-1] Basic Auth (우선 경로)
  cd {[3-0]에서 확인한 실제 경로}
  U=$(grep '^ONEANDZERO_WP_USER' pw.txt | cut -d'=' -f2- | tr -d ' \r\n')
  P=$(grep '^ONEANDZERO_WP_APP_PASSWORD' pw.txt | cut -d'=' -f2- | tr -d '\r\n' | sed 's/^ *//')
  curl -s -u "$U:$P" "https://0and1life.com/wp-json/wp/v2/users/me?context=edit"
200이면 이후 모든 REST 호출을 이 방식으로 수행한다.
⚠️ 비밀번호 값을 응답·로그·Notion에 절대 출력하지 않는다. bash 변수로만 다룬다.
※ 샌드박스 네트워크는 0and1life.com 만 열려 있다. unsplash·pexels·github raw는 curl 불가 — 브라우저 또는 web_fetch 경로를 쓴다.
⚠️ 파일 생성 후 곧바로 curl 업로드할 때는 `[ -f "$f" ] || continue` 로 존재를 확인한다 (빈 페이로드 덮어쓰기 방지).

[3-2] 브라우저 nonce 폴백 (Basic Auth 실패 시)
1) Chrome으로 https://0and1life.com/wp-admin/index.php → `document.body.classList.contains('wp-admin')` 로 로그인 확인
2) `const nonce = (await fetch('/wp-admin/admin-ajax.php?action=rest-nonce', {credentials:'same-origin'}).then(r=>r.text())).trim();`
3) 이후 REST 호출을 wp-admin 탭의 javascript_tool 에서 `credentials:'same-origin'` + `'X-WP-Nonce': nonce` 로 수행.

[3-3] 둘 다 실패 시
⛔ AI는 wp-login.php 로그인 폼을 대신 제출하지 않는다. 오류 로그에 사유와 사용자 조치 안내를 남기고 STEP 7로 건너뛴다. Draft일은 공란 유지.

[3-4] 서브카테고리 → WP Category ID
💰 직장인 재테크 / 재태크 → 23 (office-worker-finance)
💼 대기업 직장인 생활 → 29 (corporate-worker-life)
📐 생활 규정·계약 계산 → 30 (time-money-saving)
💍 Wedding → 27 (wedding)
🏠 Life · My Story / [1] 나의이야기 → 25 (daily-life)
🤖 AI 정보 (업무 AI · 실생활 AI · AI 트렌드) → 26 (ai-guide)
0. 테크와 효율 → 18 (레거시, 신규 배정 금지)

카테고리 판정이 애매하면 **더 좁은 쪽**으로 보낸다. 예: '웨딩홀 계약금 환불'은 웨딩(27)이 아니라 규정·계약 계산(30).
- 매핑 없는 서브카테고리는 생성 전에 `GET /wp-json/wp/v2/categories?search={이름}` 으로 유사 카테고리 존재를 먼저 확인한다 (신규 생성은 최후 수단).
- Notion 서브페이지 "Category" 행에 "(WP 29)" 처럼 ID가 명시돼 있으면 그 값을 그대로 사용한다.

STEP 4 — Notion 서브페이지 읽기 → 필드 추출

[4a] 서브페이지 URL 확인
① notion-search로 `Blog #{번호}` 또는 제목 앞부분 검색 → page_id 확인
② 실패 시에만 SOURCE_PAGE 현황표를 fetch해 자식 페이지 목록에서 찾는다
③ 둘 다 실패 → "서브페이지 없음 #{번호}" 기록 후 다음 포스트. Draft일 공란 유지.

[4b] 필드 추출 — "기본 정보" 표에서:
SLUG / SEO_TITLE / META_DESCRIPTION / FOCUS_KEYWORD / SUB_KEYWORDS / HTML_CONTENT / WP_CAT_ID
⚠️ FOCUS_KEYWORD는 Notion 값 그대로 (AI 재생성·수정 금지)
⚠️ SUB_KEYWORDS도 그대로 복사 → " / " 를 ", " 로 변환

[4c] 슬러그 중복 확인
GET /wp-json/wp/v2/posts?slug={SLUG}&status=any&_fields=id,slug
비어있으면 업로드 진행. 데이터가 있으면 "건너뜀"이 아니라 상태를 점검한다:
  1) GET /wp-json/wp/v2/posts/{id}?context=edit
  2) Chrome으로 에디터를 열어 GP 3필드와 Rank Math 값이 비어있는지 확인
  3) 비어있으면 WP_POST_ID = {id} 로 두고 STEP 6부터 진행 (STEP 5 건너뜀)
  4) 채워져 있으면 Notion Draft일만 TODAY로 갱신하고 다음 후보로

[4d] 히어로 이미지
첫 <img> 의 src가 `[FEATURED_IMAGE_URL]` 등 플레이스홀더면 그대로 두고 STEP 7에 "히어로 플레이스홀더 — 이미지 루틴 대기" 기재 (매일 06:51 `0and1life-auto-image-insert` 가 처리).
타 사이트 핫링크(gstatic·pstatic 등)면 [4f] 관문 ③ 위반이므로 반려. images.unsplash.com은 통과.

[4e] FAQ 스키마 추출
"자주 묻는 질문" 섹션에서 정규식 `<p><strong>Q\.\s*(.+?)<\/strong><br>(.+?)<\/p>` (dotall)로 Q/A 추출.
2쌍 이상이면 FAQPage 스키마 JSON 생성:
{ "@context":"https://schema.org", "@type":"FAQPage", "mainEntity":[ {"@type":"Question","name":"{질문}","acceptedAnswer":{"@type":"Answer","text":"{답변}"}} ] }
⚠️ **답변 텍스트는 첫 문장만 넣는다.** 전문을 넣으면 200어절을 넘고 Rank Math가 본문 문단으로 계산해 잡음이 된다. 스키마 유효성에는 영향 없다.
Q/A가 1쌍 이하면 null.

[4f] 발행 차단 관문 (⛔ 업로드 전 필수)

① 원본자료 — 1급 원본 자료(직접 조작한 화면 캡처·실측 수치) 최소 1개. 계산표·공식 수치 재정리만이면 불통과. 기본 정보 표에 "1급 자료 조달 계획: 루틴가능 {화면·경로}"가 있으면 **로그인 없이 접근 가능한 공개 페이지에 한해** Chrome으로 직접 조작·캡처 → WP 미디어 업로드 → 본문에 삽입해 스스로 충족시킨다.

⛔ **앱전용 화면 판정**: 이 루틴은 **브라우저만 조작**한다. 모바일 앱 안에서만 보이는 화면은 로그인 여부와 무관하게 캡처 불가다.
· **판정 질문: "이 자료가 웹 브라우저에서 보이는가?"** 아니오면 [4g]를 시도하지 말고 즉시 반려한다.
· **반려 전 1회 확인**: 같은 서비스의 **웹 버전·공식 페이지**가 있으면 그 화면으로 대체 가능한지 본다. 대체되면 `루틴가능`으로 전환해 [4g] 진행
· 반려 시 사유 코드 `1급-앱전용`, 조달 주체 `사용자`로 기록

캡처 대상 선정:
- ✅ 법령(法令) 조문은 캡처 가능 — `https://www.law.go.kr/법령/{법률명}/제{n}조` 는 `lawService` iframe에 HTML 인라인 렌더링된다. **1순위 경로.**
- ⛔ 행정규칙 별표는 캡처 불가 (HWP 첨부로만 제공). 조달 계획에 지정하지 않는다.
- ⛔ kca.go.kr·consumer.go.kr 기준 조문 페이지는 없거나 목록 리다이렉트. 대체 경로로 적지 않는다.

캡처 품질·마크업:
- 전체 화면·전체 페이지 캡처 금지. 결과·조문 영역만 잘라 찍는다.
- 스크롤바·커서·드래그 핸들·쿠키 배너·팝업 잔재·깨진 아이콘이 보이면 재캡처. 오버레이 구성 시 `ul, img, a.lsLink, button` 노드를 먼저 제거.
- ⚠️ 표준 우회로: 대상 블록을 복제해 `position:fixed;inset:0;background:#fff` 오버레이로 뷰포트를 채운 뒤 전체 스크린샷.
  · law.go.kr처럼 iframe 안에 내용이 있으면 **iframe 자체를 `position:fixed;inset:0;width:100vw;height:100vh`로 만들고 오버레이는 iframe 문서 안에 삽입**한다 (사이트 CSS를 살리기 위함).
  · 콘텐츠가 뷰포트보다 짧아 여백이 크면 래퍼에 `zoom` 을 걸고 폭을 `(뷰포트폭-패딩)/zoom` 으로 맞춘다. zoom은 1.4부터 0.05씩 올리며 높이가 목표를 넘지 않는 최대값을 고른다.
  · ⚠️ `resize_window` 는 이 환경에서 뷰포트에 반영되지 않는다(outerWidth/Height=0). 창 크기로 프레임을 맞추려 하지 말 것.
- 업로드 경로: 샌드박스에 스크린샷 파일이 없으므로 `mcp__claude-in-chrome__upload_image` 로 `/wp-admin/media-new.php?browser-uploader=1` 의 `#async-upload` 에 넣고 **'업로드' submit 버튼을 좌표 클릭**한다 (ref 클릭만으로는 전송되지 않는 사례 확인). 이후 `GET /wp-json/wp/v2/media?per_page=2` 로 id·source_url 확인.
- 파일명: `evidence-{SLUG}-{n}` — Image 루틴이 증빙과 생성 이미지를 구분하는 근거. webp 변환 불가 경로에서는 .jpg 허용하되 로그에 남긴다.
- 삽입 마크업:
  `<figure class="evidence-capture" style="margin:26px 0; border:1px solid #e2e8f0; border-radius:12px; padding:10px; background:#fafafa;"><img style="width:100%;display:block;height:auto;border-radius:8px;" src="{URL}" alt="{Focus Keyword 포함 설명}" /><figcaption style="font-size:13px; color:#64748b; margin-top:8px;">{출처 기관 — 화면명 · Captured YYYY-MM-DD}</figcaption></figure>`

② 가짜경험 — 하지 않은 일의 1인칭 서술·가공된 신상 0건.
⚠️ **도입 첫 문단을 특히 주의해 읽는다.** 주어가 생략된 완료형("PT 20회를 100만원에 끊었습니다. 5회 받고 환불을 요청했더니…")은 필자의 실경험으로 읽힌다. Writer가 "가짜경험 0건"이라 적어두었어도 본문을 직접 읽고 판정한다. 적발 시 반려하지 말고 "~라고 해보죠"·"~인 경우를 가정하면"으로 **최소 수정 후 통과**시키고 로그에 남긴다.
화자 프로필(사용자 확정): 미혼 · 2026-11-01 결혼 예정 · 예식장 계약 완료 · 스드메 상담 3곳 · **상견례 미완료** · **신혼집 입주 전** · **자녀 없음(육아휴직 경험 없음)** · 직장 10년차 이상 · AI는 Claude(Max)·Gemini(Pro)·ChatGPT·퍼플렉시티 실사용.

③ 이미지출처 — 모든 <img>가 자체 업로드(0and1life.com) 또는 images.unsplash.com 또는 [4d] 플레이스홀더. 타 사이트 핫링크 0건.

①~③ 중 하나라도 자체 해소 불가면 STEP 5~6을 건너뛴다 (Draft일 공란 유지). 그리고 발행 반려 로그에 행 추가:
https://www.notion.so/3adbfe4a2ae1817994f0f901de5c8dec
형식: | {TODAY} | {SLUG} | {사유 코드} | {무엇을} | {어디에} | {왜} | {어떻게} | {루틴 또는 사용자} | 대기 |
⚠️ "1급 자료 없음"만 적는 보고는 무효 — 4항목을 반드시 채운다. 같은 슬러그의 '대기' 행이 이미 있으면 중복 추가하지 않는다.

STEP 5 — WordPress Draft 업로드

[4c]에서 "비어있음(재개 필요)"이면 이 STEP을 건너뛰고 STEP 6으로 간다.

날짜 치환: HTML_CONTENT 상단 메타 라인의 `\d{4}년 \d{1,2}월 \d{1,2}일` **첫 번째 매치 1개만** TODAY로 치환한다. 본문 속 다른 날짜(제도 시행일 등)는 건드리지 않는다.

HTML_BODY 조립: FAQ_SCHEMA_JSON이 null이 아니면 HTML_CONTENT의 마지막 `</div>` 바로 뒤에 삽입:
  \n<script type="application/ld+json">{FAQ_SCHEMA_JSON}</script>\n
원본 구조·스타일은 절대 변경하지 않는다 (예외: [4f]② 가짜경험 최소 수정, [4f]① evidence figure 삽입).

POST /wp-json/wp/v2/posts
{ "title":"{SEO_TITLE}", "content":"<!-- wp:freeform -->\n{HTML_BODY}\n<!-- /wp:freeform -->", "status":"draft", "slug":"{SLUG}", "categories":[{WP_CAT_ID}] }
응답에서 WP_POST_ID 기록.

[5a] Notion 서브페이지 업데이트 (Post ID·상태만)
상태: 작성완료 → 배포완료 (Draft) · WordPress Post ID: {WP_POST_ID} (행이 없으면 새로 추가)
⚠️ Draft일자는 여기서 기록하지 않는다 — STEP 6 전 과정 성공 시 [6l]에서만 기록한다.

[5b] 슬러그 충돌: 실제 slug ≠ 요청 SLUG → 오류 로그 후 건너뜀.

STEP 6 — 에디터에서 Rank Math + GeneratePress 설정 (Claude in Chrome)
🎨 테마: GeneratePress (Astra 설정 절대 사용 금지)

[6a] list_connected_browsers → select_browser
[6b] navigate → https://0and1life.com/wp-admin/post.php?post={WP_POST_ID}&action=edit
⚠️ navigate 직후 get_page_text 금지. wait 3초 후 javascript_tool로만 확인:
`document.body?.classList.contains('wp-admin') ? 'logged-in' : 'not-logged-in'`
'not-logged-in'이면 [3-3]대로 오류 로그 후 건너뜀 (Draft일 공란 유지).

[6c] GeneratePress 레이아웃 (JavaScript)
const nativeSelectSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
const nativeCheckSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'checked').set;
const sidebarSel = document.getElementById('generate-sidebar-layout');
if (sidebarSel) { nativeSelectSetter.call(sidebarSel, 'no-sidebar'); sidebarSel.dispatchEvent(new Event('change', {bubbles: true})); }
const contentSel = document.getElementById('_generate-full-width-content');
if (contentSel) { nativeSelectSetter.call(contentSel, 'true'); contentSel.dispatchEvent(new Event('change', {bubbles: true})); }
const titleCb = document.getElementById('meta-generate-disable-headline');
if (titleCb && !titleCb.checked) { nativeCheckSetter.call(titleCb, true); titleCb.dispatchEvent(new Event('click', {bubbles: true})); }

⚠️ **이 단계에서 저장하지 않는다.** [6d]까지 마친 뒤 [6h]에서 한 번만 저장한다 (저장 횟수를 줄여야 `<p>` 소실 위험이 준다).

[6d] Rank Math SEO 설정 (JavaScript)
⚠️ FOCUS_KEYWORD·SUB_KEYWORDS는 Notion 값 그대로 (재검색·수정 금지)
⚠️ TOC 강제 인식을 **이 단계에서 미리** 넣는다. 이것만으로 TOC 항목은 통과한다.

if (!wp.data.select('rank-math')) { await new Promise(r => setTimeout(r, 3000)); }
if (!wp.data.select('rank-math')) { throw new Error('rank-math store not available'); }
const rm = wp.data.dispatch('rank-math');
const allKeywords = ['FOCUS_KEYWORD', ...'SUB_KEYWORDS_CSV'.split(',').map(k => k.trim())].join(', ');
rm.updateKeywords(allKeywords);
rm.updateTitle('SEO_TITLE'); rm.updateSerpTitle('SEO_TITLE');
rm.updateDescription('META_DESCRIPTION'); rm.updateSerpDescription('META_DESCRIPTION');
rm.updateSerpSlug('SLUG');
if (window.rankMath && window.rankMath.assessor) { window.rankMath.assessor.hasTOCPlugin = true; }
await new Promise(r => setTimeout(r, 1500));

throw 발생 시 → [6e]~[6g] 클릭 폴백.
[6e] 상단 우측 점수 배지 클릭으로 패널 열기
[6f] 포커스 키워드 + Additional Keywords 각 항목 입력 후 Enter
[6g] 스니펫 편집 → SEO_TITLE, META_DESCRIPTION 입력 후 닫기

[6h] 저장 (⭐ 이 STEP의 핵심)
`await wp.data.dispatch('core/editor').savePost()` 를 **한 번만** 호출 → 3초 대기.
⚠️ 이 저장 시점에 **서버(PHP)가 계산한 SEO 점수**가 메타에 기록된다. 서버 분석은 저장본(`<p>` 보존)을 보므로 클라이언트 분석보다 유리하다.

저장 후 에디터를 새로고침하고 검증한다:
- GP 3필드: `generate-sidebar-layout === 'no-sidebar'` · `_generate-full-width-content === 'true'` · `meta-generate-disable-headline === true`
- Rank Math: `getKeywords()` 에 쉼표 항목 2개 이상 · `getSerpDescription()` 길이 > 0
- 본문 무결성(REST): `<p>` 개수 · ld+json · evidence figure · `wp:freeform` 마커 2개
하나라도 false → [6c]/[6d] 재시도 1회. 그래도 false → 오류 로그에 명시 기록 ("GP 레이아웃 미반영" 등, "완료"로 보고 금지).

[6i] 콘텐츠 재업로드 폴백 (에디터 본문이 비어있을 때만)
POST /wp-json/wp/v2/posts/{WP_POST_ID} · {"content": "<!-- wp:freeform -->\n{HTML_BODY}\n<!-- /wp:freeform -->"}
⚠️ 실행 전 반드시 [6m-0] 탭 정리 절차를 먼저 거친다.

[6j] SEO 점수 확인 및 보정

에디터 새로고침 → wait 3초 → `wp.data.select('rank-math').getAnalysisScore()`. 목표 81점 이상이면 [6k]로.

**81점 미달 시 — 보정 전에 조치 가능 여부부터 판정한다.**

⛔ **재분석 트리거를 반사적으로 돌리지 말 것.** 클라이언트 분석은 `getEditedPostContent()` 를 쓰는데 이 값은 freeform 직렬화에서 `<p>`가 소실된 상태라 구조적으로 불리하다 — 트리거를 돌리면 낮은 클라이언트 점수가 높은 서버 점수를 덮어쓴다.

1) 패널을 열고 실패 항목을 뽑는다 (그룹이 접혀 있으면 6개만 렌더링된다 — 전부 펼친 뒤 읽을 것, 펼치면 20개):
const p = document.querySelector('.rank-math-sidebar-panel, .interface-complementary-area');
p.querySelectorAll('.rank-math-collapsible-title, .components-button[aria-expanded="false"]').forEach(b=>{try{b.click()}catch(e){}});
await new Promise(r=>setTimeout(r,1500));
JSON.stringify([...p.querySelectorAll('[class*="seo-check-"]')].filter(n=>/test-fail/.test(n.className)).map(n=>(n.className.match(/seo-check-([A-Za-z]+)/)||[])[1]));

2) 판정표
⛔ 조치 불가: `keywordInPermalink` (슬러그 영문 정책 — 변경 금지, 로그에 '사양' 기록) · `hasContentAI` (PRO 전용) · `contentHasShortParagraphs` (구조적, 아래 참조)
✅ 조치 가능: `keywordIn10Percent` (도입 첫 문단 100자 안에 Focus Keyword) · `keywordInSubheadings` (H2 1개 이상에 포함) · `keywordInMetaDescription` (메타 150자 이내 + 키워드) · `linksHasInternal` (`/slug/` 상대경로 1개 이상) · `lengthContent` (본문 1,500자 이상) · `contentHasAssets` (이미지 1개 이상)

⛔ **`contentHasShortParagraphs` 는 문단을 쪼개도 해소되지 않는다.**
Rank Math가 보는 `getEditedPostContent()` 에서 `<p>`가 소실돼 본문을 통짜 덩어리로 계산하기 때문이다. 저장본 raw가 정상이어도 실패한다.
→ 이 항목이 뜨면 **보정을 시도하지 말고** "freeform 직렬화 구조적 한계 — 조치 불가"로 기록하고 넘어간다.

3) **조치 가능 항목이 하나도 없으면 보정을 생략하고, 재분석 트리거도 돌리지 않고, 서버 저장 점수를 그대로 최종값으로 기록한다.**

4) 조치 가능 항목이 있을 때만: [6m-0] 탭 정리 → REST로 HTML 수정 → 에디터 재오픈 → 재분석 트리거(GitHub 지침 Phase 5-2) → 저장 → 검증. **재시도는 1회.** 키워드 기계적 반복 삽입 금지.

⛔ 절대 금지: core/heading 블록 추가 / 슬러그 한글화 / 키워드 반복 삽입

[6k] Notion SEO 점수 업데이트
현황표 해당 행의 SEO 셀을 최종 점수로 교체한다. old_str은 실행 전 re-fetch로 현재 셀 원문을 확인해 구성하고, 같은 값이 여러 행에 있으면 작성일까지 포함해 범위를 확장한다.

[6l] Draft일 기록 (STEP 6 전 과정 성공 시에만)
⚠️ 아래 중 하나라도 있었으면 공란으로 남긴다: Chrome 로그인 실패 / GP 레이아웃 미반영(재시도 후에도) / Rank Math 설정 throw 후 클릭 폴백까지 실패.
성공 시: 서브페이지 Draft일자 = TODAY · 메인 테이블 "Draft일" 셀 → TODAY (실행 전 현재 셀 원문을 재확인해 old_str 구성 — "—"가 아니라 빈 칸일 수 있다)

[6m-0] ⭐ 탭 정리 절차 (REST 본문 수정 전 필수)
1) 열려 있는 모든 post.php 탭에서 `wp.data.select('core/editor').isEditedPostDirty()` 확인
2) true면 `await wp.data.dispatch('core/editor').savePost()` 로 dirty 해제 (⚠️ navigate가 "Leave site?"로 막히면 억지로 뚫지 말고 이 방법을 쓴다)
3) 모든 에디터 탭을 `https://0and1life.com/wp-admin/upload.php` 로 이동
4) 그 다음에 REST POST 실행
5) **8초 대기 후** GET context=edit 으로 `<p>` 개수·길이·ld+json·evidence·freeform 마커를 검증
6) `<p>` 가 기대값보다 크게 작으면 자동저장에 덮인 것이다 → 1)부터 다시 한다

[6m] 들어오는 내부 링크 추가 (STEP 6 성공 시 필수)
현황표에서 주제가 인접한 기존 발행 글 2개를 고른다 (내부 링크를 이미 받고 있는 글 우선). 이번 글이 아웃바운드로 거는 두 글을 그대로 쓰면 상호 링크가 성립해 가장 안전하다.
1) GET /wp-json/wp/v2/posts?slug={기존슬러그}&_fields=id
2) GET /wp-json/wp/v2/posts/{id}?context=edit → content.raw
3) "함께 읽으면 좋은 글" <ul>에 `<li><a href="/{신규슬러그}/">{신규 제목}</a></li>` 추가 (섹션이 없으면 `<p><strong>함께 읽으면 좋은 글</strong></p>\n<ul>...</ul>` 신설)
4) 저장 전 여닫이 짝 검증 → POST. 실패 시 오류 로그만 남기고 발행은 유지.
   ⚠️ 짝 검증은 정규식 `<ul[\s>]` 로 센다 (`<ul style="...">` 때문에 단순 문자열 비교는 오탐)
   ⚠️ 전송 직전 `[ -f "$f" ]` 로 페이로드 파일 존재 확인
   ⚠️ 대상 글의 에디터 탭이 열려 있으면 [6m-0]을 먼저 거친다

[6n] 트랙 S 빠른 발행 알림
⛔ **이 루틴의 권한은 draft 작성·수정까지다. 발행(publish)·예약발행(future) 상태 변경은 어떤 경우에도 하지 않는다.**
Track 행이 "S"로 시작하는 글은 정보만 정리해 알린다:
1) GET /wp-json/wp/v2/posts?status=future&per_page=20&_fields=id,date (읽기 전용)
2) 내일부터 하루씩 09:00 KST 슬롯을 훑어 비어 있는 첫 날짜를 찾는다
3) STEP 7에 기재: "⚡ 트랙 S 글 — 시의성 소재({헤드 요약}). 빠른 발행 권장, 현재 빈 슬롯: {날짜} 09:00 (예약은 사용자가 직접)"
트랙 L 글은 이 알림 없이 기존 수동 예약 흐름을 따른다.

[6o] 카테고리 균형 점검 (보고 전용)
현황표에서 **최근 7일 발행분의 카테고리 분포**를 센다. 아래에 해당하면 STEP 7에 명시한다:
- 7일 창 상한 초과? — 💰 재테크 2 · 💼 대기업 2 · 📐 규정계산 2 · 💍 웨딩 2 · 🏠 Life 2 · 🤖 AI 1
  ⚠️ 이 한도는 `0and1Life-Writer.md` 1-3 R1의 **사본**이다. 두 값이 어긋나면 Writer 지침이 이긴다 — Writer 개정 시 이 줄도 같이 고친다.
- 직전 3건이 같은 카테고리? (3연속 금지 위반)
- 7일 창에 서로 다른 카테고리가 3개 미만?
- 7일 창에 `N-통과`가 2건 미만이거나 `N-구글전용`이 4건 이상? (R6 네이버 수요 하한 — 보고만)
⚠️ 이 루틴은 카테고리를 바꾸지 않는다 — **초과 사실을 보고만 한다.** 배정은 Writer 루틴의 책임이다. 조용히 넘어가지 말 것.

STEP 7 — 완료 알림 (이전 단계의 성공 여부와 무관하게 반드시 실행)

신규 있음: "0and1Life 발행완료 ✅ draft {N}개 | 관문반려 {R}건 | 인바운드링크 {L}건 | SEO {점수}점 | FAQ스키마 {F}건 | 오류 {E}개 ({TODAY_KST})"
⚠️ STEP 0 결과를 한 줄로 함께 기록한다 — 조회 실패([0-5]) / 캐시 사고([0-3]) / 조항 자동 신설([0-4], 조항번호 + 전문) / 진짜 상충. 캐시 사고를 상충으로 쓰지 않는다.
신규 없음: "0and1Life 자동 체크 완료 — 신규 글 없음 ({TODAY_KST})"

아래 해당 시 각각 한 줄 덧붙인다:
- [6o] 균형 위반 → "⚠️ 카테고리 균형 — {내용}"
- 히어로 플레이스홀더 → "히어로 플레이스홀더 — 이미지 루틴 대기"
- 조치 불가 항목만 남아 보정을 생략 → "SEO {n}점 — 실패 {항목들} 전부 조치 불가(구조적/PRO), 보정 생략"

🚨 오류 처리
WordPress API 실패 | 로그 기록 후 다음 포스트 진행
Notion 페이지 없음 | 로그 기록 후 다음 포스트 진행
pw.txt 접근 실패 | [3-0] 1) bash 탐색부터 재확인 → 실패 시에만 request_cowork_directory 1회 → 그래도 실패면 [3-2] nonce 폴백. 셋 다 불가하면 [3-3]대로 로그 후 STEP 7
승인 창 무응답(AbortError) | 같은 호출을 반복하지 않는다. 즉시 다음 폴백으로 이동하고 "무인 시간대 승인 대기 실패"로 기록
Chrome 로그인 실패 | GP/Rank Math 미설정 로그, 업로드는 유지, Draft일 공란 유지. 로그인 폼 대신 제출 금지
본문 `<p>` 대량 소실 발견 | 에디터 자동저장에 덮인 것 — [6m-0]으로 탭 정리 후 REST 재복원, 8초 후 재검증
navigate가 "Leave site?"로 막힘 | savePost() 1회로 dirty 해제 후 이동. 억지로 뚫지 말 것
GitHub 지침 fetch 실패 | [0-5] 저장소 루트 1회 → Chrome 1회 → 실패 시 이 프롬프트의 [4f]·[6j] 규칙만으로 진행 + 오류 로그 기록 (조항 자기보완 금지)
조항이 지침서에 안 보임 | [0-3] 3단 검증(캐시버스터 → Chrome → 확정). 찾으면 그 기준 사용하고 캐시 사고로 기록(상충 아님)
3단 검증 후에도 조항 결번 | [0-4] 조항을 직접 작성해 로컬 0and1Life-Draft.md 에 추가 → 즉시 적용해 배포 계속 → STEP 7·Notion에 전문 기록. 커밋·푸시는 사용자
지침서 개정 이력이 루틴이 아는 버전보다 낮음 | 캐시 사본 의심 — 새 ?cb= 로 재조회 + Chrome 재확인. 캐시로 확인되면 상충 보고 금지
Rank Math store 미등록 | 3초 대기 재시도 → 실패 시 클릭 폴백
SEO 81점 미달 | [6j] 판정표로 조치 가능 여부 먼저 확인. 조치 가능 항목이 없으면 보정·트리거 없이 서버 점수 그대로 기록
캡처 대상이 행정규칙 별표 | HTML 렌더링 불가 — 법령 조문으로 대체하고 경로 변경 사실 기록
슬러그 중복이지만 GP/RankMath 미설정 | STEP 6부터 재개 ([4c] 참고)
관문 반려 ([4f] 불통과) | 반려 로그 행 추가 + Draft일 공란 유지 + 다음 포스트 진행
