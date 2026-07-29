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

=== STEP 2-B: 색인 거부(F등급) 수집 — 2026-07-29 신설, 매주 필수 ===

배경: 기존 STEP 1·2는 **실적(클릭/노출)** 만 본다. 구글이 크롤링한 뒤 색인을 거부한 페이지는 노출이 0이라 실적 탭에 아예 나타나지 않아, 몇 달간 누적되어도 아무도 모른다. 2026-07-29 최초 실측에서 koreaplug 46건 / 0and1life 23건이 방치 상태로 발견되었다. 이 글들은 사이트 전체 평가를 끌어내려 애드센스 심사에 직접 영향을 준다.

실행 (두 사이트 각각):
- https://search.google.com/search-console/index?resource_id=<RESOURCE_ID> 접속
- "페이지 색인이 생성되지 않는 이유" 표에서 **`크롤링됨 - 현재 색인이 생성되지 않음`** 행을 클릭해 URL 목록 전체를 추출한다
- 함께 기록: `발견됨 - 현재 색인이 생성되지 않음`, `찾을 수 없음(404)`, `리디렉션이 포함된 페이지` 각 건수
- 색인됨 / 색인 안 됨 총계를 기준치와 비교해 증감 기록

판정·조치 (Writer 지침 1-6 F등급 참조):
- 신규로 F등급에 들어온 URL은 리포트에 **목록 전체**를 적는다 (건수만 적지 말 것 — 조치 대상을 특정할 수 없다)
- F등급 누적이 색인됨 대비 30%를 넘으면 **신규 발행을 중단하고 기존 글 정리를 우선**한다고 리포트에 명시한다
- 각 URL은 ① 원본 자료 추가 후 전면 재작성 ② 유사 글과 병합 ③ 삭제(410) 중 하나로 분류해 제안한다

=== STEP 3: 키워드 수확 → 백로그 기록 (2026-07-26 신설 — 전부 Chrome, WebSearch 미사용) ===

수확한 후보는 아래 두 백로그 페이지의 표에 행으로 추가한다 (상태=대기, 수확일=오늘):
- KoreaPlug 백로그: 페이지 ID 3a9bfe4a-2ae1-818f-911b-f852981d5018
- 0and1Life 백로그: 페이지 ID 3a9bfe4a-2ae1-81e0-8fc9-dc8e035388af

공통 규칙:
- 추가 전 중복 제거 2중: ① 백로그 기존 행과 대조 ② 각 블로그 발행 목록(KoreaPlug 33cbfe4a-2ae1-81b9-a743-cb7c194dea7f / 0and1Life EFFICIENCY 37cbfe4a-2ae1-819f-8664-ff3d38fffe56 + LIFESTYLE 37cbfe4a-2ae1-81b9-a9ce-d0b937edd344)의 제목·포커스 키워드와 대조 — 단어가 겹쳐도 각도가 다르면 중복 아님(각도 기준)
- 주당 신규 후보는 블로그당 5~10개면 충분 — 양보다 증거의 질
- 수확 전에 정리 먼저: 백로그의 '대기' 항목 중 수확일이 4주 이상 지난 것은 상태를 '만료'로 변경

[3-A] GSC 쿼리 수확 (두 블로그 각각 — 최우선 소스)
STEP 1·2에서 쓴 실적 화면의 breakdown을 페이지 → 검색어로 전환:
- KoreaPlug: https://search.google.com/search-console/performance/search-analytics?resource_id=https%3A%2F%2Fkoreaplug.com%2F&num_of_days=28&breakdown=query&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION
- 0and1Life: https://search.google.com/search-console/performance/search-analytics?resource_id=https%3A%2F%2F0and1life.com%2F&num_of_days=28&breakdown=query&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION
javascript_tool로 상위 30개 쿼리의 노출·클릭·순위를 추출한 뒤 선별:
- **노출 기준은 블로그별로 다르다** (⚠️ 수정 2026-07-27 — 舊 공통 기준 '노출 ≥10'은 사이트 규모를 무시해 0and1Life에서 0건을 냈다. 이 블로그는 사이트 전체 28일 노출이 33 수준이라 ≥10을 넘는 쿼리가 구조적으로 나올 수 없다):
  - **KoreaPlug**: 노출 ≥10 (사이트 전체 노출 4,000+ 규모)
  - **0and1Life**: 노출 ≥2. 그래도 후보가 3건 미만이면 **노출 상위 10개 쿼리 전체**로 검토 대상을 넓힌다
- 위 기준을 넘으면서 그 쿼리를 정면으로 다루는 전용 글이 없는 것 → 백로그 후보 (출처=GSC쿼리, 수요 증거="노출N·순위P")
- 순위 8~20 구간을 최우선 표기 — 전용 글 신설 시 1페이지 진입 확률이 가장 높은 구간
- 이미 전용 글이 있는 쿼리는 백로그가 아니라 주간 리포트 '다음 조치'(기존 글 개선 대상)에 기재.
  ⭐ **전용 글이 있는데도 순위가 50위 밖인 클러스터는 '최우선 개선 대상'으로 별도 명시**한다 (2026-07-27 신설) — 노출은 이미 있는데 회수를 못 하는 구간이라 신규 글보다 수익률이 높다. 실제 사례: '한국 나이' 클러스터 합산 노출 90인데 전용 글 #5가 있음에도 전부 50위 밖.

[3-B] 네이버 수확 (0and1Life 전용 — 이 블로그의 실제 유입 주전장)
① 네이버 데이터랩(https://datalab.naver.com)에서 승자 클러스터 시드(백로그·최신 리포트의 클러스터 칸 참조, 예: 프로포즈/스드메/결혼 비용)의 연관 급상승 확인
② naver.com 검색창에 승자 클러스터 시드 2~3개 입력 → 자동완성·연관검색어 수확 (실존 문구만, 임의 조합 금지)
→ 후보화 (출처=네이버AC 또는 데이터랩)

⚠️ **차단 시 처리 (2026-07-27 확인)**: datalab·search.naver가 브라우저 안전 정책으로 막히는 경우가 있다. 이때 **추측 후보를 만들지 말고** 3-B를 생략한 뒤, 백로그 페이지에 "3-B 네이버 차단 — 생략"만 기록한다.
이는 0and1Life의 공급 공백으로 남지 않는다 — **daily writer 루틴(STEP 7-B)이 매일 4-A 통과 낙선 후보를 백로그에 적재**하기 때문이다. writer 환경은 WebFetch로 네이버 자동완성 API에 접근할 수 있어(2026-07-26 #66 실행에서 교차 확인 성공) Chrome이 막혀도 네이버 근거 후보가 계속 들어온다. 즉 0and1Life의 주 공급원은 이 주간 루틴이 아니라 daily writer다.

[3-C] 구글 Rising + PAA (KoreaPlug 전용)
① https://trends.google.com/trends/explore?date=now%207-d&geo=US&q=korea 의 Related queries Rising/Breakout 수확 (JS 렌더링 페이지 — Chrome에서만 가능, writer 환경에선 불가한 소스)
② google.com에서 GSC 승자 쿼리 1~2개 검색 → People Also Ask 질문 수확
→ 후보화 (출처=TrendsRising 또는 PAA)

[3-D] 백로그 기록
각 후보를 해당 블로그 백로그 표 맨 아래에 행으로 추가:
| {다음 번호} | {키워드} | {출처} | {증거 요약} | {클러스터} | {순위 또는 —} | {오늘 YYYY-MM-DD} | 대기 |
⚠️ 표 갱신 전 페이지 re-fetch로 마지막 행 원문 확인 후 old_str 구성 (기존 Notion 갱신 규칙과 동일).
주간 리포트 본문 끝에 "이번 주 수확: N건 (GSC n / 네이버 n / Trends·PAA n) · 만료 처리 m건" 한 줄을 추가한다.

=== 결과 저장 (필수) ===

Notion MCP의 update-page(insert 또는 update_content)로 STEP 0의 두 페이지 "## 리포트 (최신순)" 제목 바로 아래에 "### YYYY-MM-DD 주간 리포트" 섹션을 추가하라 (최신이 위):

각 리포트 내용: 지표 변화표(STEP 0 기준치 대비 증감) + 특이사항(색인/인증 문제 등) + 다음 조치 제안 1~2줄.

주의: GA4 이탈률·참여시간 단독으로 판단하지 말 것(봇 왜곡). direct 트래픽은 본인+AI크롤러 포함이므로 무시. GA4 표는 로딩이 느리므로 navigate 후 wait 10초 뒤 추출. 접근 불가 시 그 사실을 Notion 리포트에 기록하고 중단.
