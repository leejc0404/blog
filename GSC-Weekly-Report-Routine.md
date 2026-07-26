koreaplug.com과 0and1life.com 두 블로그의 SEO 상태를 주간 점검하고, 결과를 한국어로 정리해 Notion 리포트 페이지 2곳에 저장하라. 읽기 전용 분석 작업이며 WordPress/GA4/GSC의 설정이나 글은 수정하지 말 것 (예외: 아래 명시된 Notion 리포트 페이지 기록은 허용). GSC 로그인 계정: leejc0404@gmail.com.

=== 파트 1: koreaplug.com (영어 블로그, 구글 중심) ===

배경: 2026-07-08에 아래 5개 글의 SEO 타이틀/메타를 수정하고 재색인을 요청했다. 목표는 CTR·클릭 상승. 직전(7/11) 측정치가 최신 기준치다.

1. https://koreaplug.com/jjimjilbang-guide/ (재타겟 "jjimjilbang tattoo rules" / 7-11: 노출 4, 순위 9.0)
2. https://koreaplug.com/seoul-apartment-prices-explained/ (7-11: 노출 65, 클릭 0, 순위 10.4, 색인 복구됨)
3. https://koreaplug.com/korean-chamoe-melon-guide/ (7-11: 노출 62, 클릭 0, 순위 8.8)
4. https://koreaplug.com/korean-address-terms-etiquette/ (7-11: 노출 32, 클릭 0, 순위 13.5)
5. https://koreaplug.com/no-trash-cans-seoul/ (7-11: 클릭 1, 노출 14, CTR 7.1%, 순위 9.9)

실행:
- https://search.google.com/search-console/performance/search-analytics?resource_id=https%3A%2F%2Fkoreaplug.com%2F&num_of_days=28&breakdown=page&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION 접속
- javascript_tool로 테이블(table tr, 첫 셀 innerText에 슬러그 포함 여부로 매칭)에서 5개 글의 클릭/노출/CTR/순위 추출 + 상단 카드의 사이트 전체 합계 기록 (7-11 기준: 클릭 44/노출 1,870/CTR 2.4%/순위 15.4)

=== 파트 2: 0and1life.com (한국어 블로그, 네이버 중심) ===

주의: 7-11에 GSC 소유권 인증이 풀려 있어 재확인으로 복구한 이력이 있다. "이 속성에 액세스할 수 없습니다"가 뜨면 [소유권 확인] 버튼을 눌러 재검증하고(설정 변경 아님), 결과를 리포트에 기록하라.

실행:
- https://search.google.com/search-console/index?resource_id=https%3A%2F%2F0and1life.com%2F 에서 색인 페이지 수 확인 (7-11 기준: 28개, 보고서 기준일 6/30 — 7/9 사이트맵 재제출 효과 반영 여부 확인)
- https://search.google.com/search-console/performance/search-analytics?resource_id=https%3A%2F%2F0and1life.com%2F&num_of_days=28&breakdown=page&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION 에서 지표 추출 (7-11 기준: 클릭 3/노출 59)
- GA4 세션 소스: https://analytics.google.com/analytics/web/?hl=ko#/a393066616p540835629/reports/explorer?params=_u..nav%3Dmaui%26_r.explorerCard..seldim%3D%5B%22sessionSourceMedium%22%5D&r=lifecycle-traffic-acquisition-v2 에서 네이버 유입(m.search.naver.com referral + naver organic) 합계 (7-11 기준: 56세션, 참여율 75%)
- 네이버 상위 글: https://analytics.google.com/analytics/web/?hl=ko#/a393066616p540835629/reports/explorer?params=_u..nav%3Dmaui%26_r.explorerCard..seldim%3D%5B%22unifiedPagePathScreen%22,%22sessionSourceMedium%22%5D%26_r.explorerCard..rowsPerPage%3D50&r=all-pages-and-screens 에서 naver 포함 행 추출 (7-11 기준: propose-necklace 40, employee-welfare 12, ai-counseling 7, signiel-hotel 3)

=== 결과 저장 (필수) ===

Notion MCP의 update-page(insert 또는 update_content)로 아래 두 페이지의 "## 리포트 (최신순)" 제목 바로 아래에 "### YYYY-MM-DD 주간 리포트" 섹션을 추가하라 (최신이 위):

- KoreaPlug: 페이지 ID 398bfe4a-2ae1-8150-93c4-fb98977c64bf
- 0and1Life: 페이지 ID 398bfe4a-2ae1-81ba-9ec6-fdae2acd6b2d

각 리포트 내용: 지표 변화표(직전 기준치 대비 증감) + 특이사항(색인/인증 문제 등) + 다음 조치 제안 1~2줄.

주의: GA4 이탈률·참여시간 단독으로 판단하지 말 것(봇 왜곡). direct 트래픽은 본인+AI크롤러 포함이므로 무시. GA4 표는 로딩이 느리므로 navigate 후 wait 10초 뒤 추출. 접근 불가 시 그 사실을 Notion 리포트에 기록하고 중단.
