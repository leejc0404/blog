koreaplug.com과 0and1life.com 두 블로그의 SEO 상태를 주간 점검하고, 결과를 한국어로 정리해 Notion 리포트 페이지 2곳에 저장하라. 읽기 전용 분석 작업이며 WordPress/GA4/GSC의 설정이나 글은 수정하지 말 것 (예외: 아래 명시된 Notion 리포트 페이지 기록은 허용). GSC 로그인 계정: leejc0404@gmail.com.

=== STEP 0: 직전 기준치 읽기 (필수 — 매번 이 STEP부터 시작) ===

⚠️ [수정 2026-07-26] 기준치를 프롬프트에 고정 텍스트로 넣지 않는다. 아래 두 페이지를 notion-fetch로 열어, 각 페이지의 "## 리포트 (최신순)" 아래 **가장 위에 있는(=가장 최근 날짜의) "### YYYY-MM-DD 주간 리포트"** 섹션을 그대로 이번 주 비교의 기준치로 삼는다.

- KoreaPlug: 페이지 ID 398bfe4a-2ae1-8150-93c4-fb98977c64bf
- 0and1Life: 페이지 ID 398bfe4a-2ae1-81ba-9ec6-fdae2acd6b2d

각 최신 섹션에서 추출할 값:
- KoreaPlug: 사이트 전체(클릭/노출/CTR/순위) + 추적 중인 개별 글 5개의 클릭/노출/CTR/순위
- 0and1Life: GSC(클릭/노출/CTR/순위) + 색인 페이지 수 + 네이버 유입 세션·참여율 + 네이버 상위 글 조회수

이 값을 STEP 1·2의 "직전 기준치"로 사용한다. **아래 STEP 1·2에 나오는 과거 수치(7-11 기준 등)는 이 루틴을 처음 설계할 때의 예시일 뿐이며, 실제 비교에는 절대 쓰지 않는다** — 항상 이 STEP 0에서 방금 읽은 최신 섹션의 수치를 쓴다.

=== STEP 1: koreaplug.com (영어 블로그, 구글 중심) ===

추적 대상 5개 글 (2026-07-08 SEO 타이틀/메타 수정 + 재색인 요청분 — 슬러그는 고정, 수치는 STEP 0에서 읽은 최신 기준치를 사용):

1. https://koreaplug.com/jjimjilbang-guide/ (재타겟 키워드 "jjimjilbang tattoo rules")
2. https://koreaplug.com/seoul-apartment-prices-explained/
3. https://koreaplug.com/korean-chamoe-melon-guide/
4. https://koreaplug.com/korean-address-terms-etiquette/
5. https://koreaplug.com/no-trash-cans-seoul/

실행:
- https://search.google.com/search-console/performance/search-analytics?resource_id=https%3A%2F%2Fkoreaplug.com%2F&num_of_days=28&breakdown=page&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION 접속
- javascript_tool로 테이블(table tr, 첫 셀 innerText에 슬러그 포함 여부로 매칭)에서 5개 글의 클릭/노출/CTR/순위 추출 + 상단 카드의 사이트 전체 합계 기록
- STEP 0에서 읽은 KoreaPlug 최신 기준치와 비교해 증감을 계산한다

=== STEP 2: 0and1life.com (한국어 블로그, 네이버 중심) ===

주의: 과거 GSC 소유권 인증이 풀린 이력이 있다(최초 발생 2026-07-11). "이 속성에 액세스할 수 없습니다"가 뜨면 [소유권 확인] 버튼을 눌러 재검증하고(설정 변경 아님), 결과를 리포트에 기록하라.

실행:
- https://search.google.com/search-console/index?resource_id=https%3A%2F%2F0and1life.com%2F 에서 색인 페이지 수 확인
- https://search.google.com/search-console/performance/search-analytics?resource_id=https%3A%2F%2F0and1life.com%2F&num_of_days=28&breakdown=page&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION 에서 지표 추출
- GA4 세션 소스: https://analytics.google.com/analytics/web/?hl=ko#/a393066616p540835629/reports/explorer?params=_u..nav%3Dmaui%26_r.explorerCard..seldim%3D%5B%22sessionSourceMedium%22%5D&r=lifecycle-traffic-acquisition-v2 에서 네이버 유입(m.search.naver.com referral + naver organic) 합계·참여율
- 네이버 상위 글: https://analytics.google.com/analytics/web/?hl=ko#/a393066616p540835629/reports/explorer?params=_u..nav%3Dmaui%26_r.explorerCard..seldim%3D%5B%22unifiedPagePathScreen%22,%22sessionSourceMedium%22%5D%26_r.explorerCard..rowsPerPage%3D50&r=all-pages-and-screens 에서 naver 포함 행 추출 (주요 추적 슬러그: propose-necklace-ring-bag-guide, employee-welfare-fund-loan, ai-counseling-guide-workers, signiel-hotel-proposal-guide — 이 외 새로 상위권에 진입한 글이 있으면 함께 기록)
- 위 모든 수치를 STEP 0에서 읽은 0and1Life 최신 기준치와 비교해 증감을 계산한다

=== 결과 저장 (필수) ===

Notion MCP의 update-page(insert 또는 update_content)로 STEP 0의 두 페이지 "## 리포트 (최신순)" 제목 바로 아래에 "### YYYY-MM-DD 주간 리포트" 섹션을 추가하라 (최신이 위):

각 리포트 내용: 지표 변화표(STEP 0 기준치 대비 증감) + 특이사항(색인/인증 문제 등) + 다음 조치 제안 1~2줄.

주의: GA4 이탈률·참여시간 단독으로 판단하지 말 것(봇 왜곡). direct 트래픽은 본인+AI크롤러 포함이므로 무시. GA4 표는 로딩이 느리므로 navigate 후 wait 10초 뒤 추출. 접근 불가 시 그 사실을 Notion 리포트에 기록하고 중단.
