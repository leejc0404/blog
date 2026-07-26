# ✏️ KoreaPlug Writer 지침 (Claude Code koreaplug-writer용)

## 📌 이 문서의 용도

`koreaplug-writer` (Claude Code 루틴)이 매일 실행 시 읽는 **작성 전용 지침**입니다.

- **포함**: Phase 0(트렌드 스캔) → Phase 1(키워드, 하이브리드) → Phase 2(HTML) → Phase 3(Notion, 2섹션) → Phase 5-1/5-3(SEO 자가검수) → Phase 7(카테고리 매핑)
- **제외**: Phase 5-2(TOC 스크립트), 5-4/5-5(업로드 후 보정), Phase 6(완료 처리), 오류표 → 📋 KoreaPlug Draft 지침 참조
- **Phase 번호 안내**: Phase 4·5-2·6과 2-4는 삭제·이관되어 **의도적으로 비어 있음**(오타 아님). 현재 유효 순서: Phase 0 → 1 → 2(2-1·2-2·2-3·2-5) → 3 → 5-1 → 5-3 → 7
- **v10.15 변경(3중 발굴 엔진 도입 — 주제 발굴량 대폭 확대, 2026-07-21)**: 필터링은 완성됐으나 정작 '넣을 재료'가 부족해 S 후보 전멸이 발생하는 날이 많음을 확인. 발굴을 ① 엔진 A: 자동완성 시드 마이닝(요일별 로테이션, 수요 직접 수확) ② 엔진 B: 이슈 소스 스캔(기존 0-1) ③ 엔진 C: 시즌·이벤트 캘린더(예측형 선점)의 3중 구조로 재편하고, 후보 목표를 10~15개로 상향 (0-1 하단 참조)
- **v10.14 변경('한국 자체' 테스트 신설, 2026-07-21 — 실전 테스트 피드백)**: 테스트 실행에서 K-드라마 '시즌2 루머' 같은 **작품 뉴스 자체**가 채택되는 문제 확인 — 이는 '한국'에 대한 글이 아니며 Soompi/IMDb가 이미 점령한 팬 뉴스 영역이다. 작품·시즌·배우·입대 뉴스 그 자체는 자동 탈락으로 명문화하고, 반드시 작품 속 한국 요소(음식·장소·관습·호칭)로 전환한 세부 각도만 후보 자격 부여(0-2·1-3에 체크 항목 추가)
- **v10.13 변경(웹 전용 전환 + 검색 예산 글당 2회 + 바이럴·휴먼라이징 스킬 통합, 2026-07-21)**: ① Chrome MCP 전면 제거 — 루틴이 Claude Code on the web에서 실행되므로 자동완성·트렌드 수집은 전부 WebFetch/Bash(구글 자동완성 공개 API·Google Trends RSS·Reddit JSON·정적 페이지 열람)로 일원화, 기존 '대체(v10.10)' 수단이 이제 기본 수단 ② **WebSearch 예산을 글당 최대 2회로 축소** — 수요 검증(1-T·1-3)은 자동완성 API WebFetch(예산 미소모)로 수행하고, WebSearch는 공백 실측·경쟁글 수집 1회(+예외적 S 탐색 또는 승계 후보 재검증 1회)에만 투입 ③ 트랙 S 트렌드 스캔을 WebFetch 전용 소스 체인(0-1)으로 재정의·강화 ④ **Phase 2-6 신설 — create-viral-content·avoid-ai-writing 스킬 통합**: 제목 스코어링·훅 아키텍처·정제 패스와 AI 티 제거 최종 패스를 발행 전 필수화
- **v10.12 변경(넷플릭스 세부 주제 마이닝 + SNS 대체 프록시, 2026-07-21 — 트랙 S 전용)**: 트랙 S는 '신문'류 소스(항목4 한국발 브릿지)보다 넷플릭스·SNS처럼 실시간으로 더 트렌디한 소스가 적합하다는 판단 하에, 항목3 핫플랫폼 스캔을 심화: ① 넷플릭스는 Top10 작품 제목을 그대로 주제로 삼지 않고, 작품 속 외국인이 궁금해할 구체 요소(음식·장소·관습 등)를 위키피디아/Reddit r/KDRAMA로 마이닝해 세부 각도로 전환 ② 인스타·X·유튜브는 직접 스크래핑이 안 되므로 포기하지 않고 Soompi·allkpop 헤드라인(정적 WebFetch) + Reddit r/kpop·r/KDRAMA(항목2)를 SNS 바이럴의 대체 프록시로 명시. 항목4(영어 뉴스 브릿지, v10.11)는 계속 최후순위 유지.
- **v10.11 변경(한국발 브릿지 우선순위 재조정, 2026-07-21 — 트랙 S 전용)**: 이 블로그는 외국인 독자 대상이므로 0-1 항목 4 '한국발 → 글로벌 브릿지'의 우선순위를 재조정: 외국인이 직접 읽는 영어 매체(Korea Herald, Korea JoongAng Daily, The Korea Times, Yonhap 영문판)를 1순위로 승격하고, 한국어 전용인 네이버 뉴스랭킹은 외국인 검색과 무관한 국내 뉴스 소스이므로 최후 보조 지표(선행 지표 확인용)로만 강등. 영어 매체만으로도 신호가 충분하면 네이버는 건너뛰고 바로 1-T 검증으로 진행.

---

## Phase 0: 트렌드 스캔 (v10.4 신규 — 매 실행 시 최우선)

> **(v10.17 변경) 발행 빈도 상한 폐지**: 주간 발행 횟수 게이트(구 v10.16, 주 3회 제한)는 사용자 지시로 삭제됨(2026-07-23) — 발행 draft/publish 여부는 더 이상 요일별 누적 발행 건수로 제한하지 않는다.

**(v10.5 홀짝 트랙제) 오늘의 트랙 결정 — 매 실행의 첫 단계**

**판정 기준**: KST 기준 오늘 날짜의 '일(day)' 숫자가 **홀수(1,3,5,…,31)면 트랙 S**, **짝수(2,4,6,…,30)면 트랙 L**. 예: 7월 13일→S, 7월 14일→L, 8월 31일→S(연속 홀수 허용).

| 구분 | 트랙 S — 숏테일 선점형 (홀수일) | 트랙 L — 롱테일 공백형 (짝수일) |
|---|---|---|
| 키워드 형태 | 2단어 이하 영어 헤드 키워드 — 해외에서 막 뜨기 시작한 한국 이슈 | 3~5단어 질문형 영어 롱테일 (예: What are the Korean greetings?) |
| 대표 소스 | 핫플랫폼 4종(넷플릭스·유튜브·인스타그램·X)에서 외국인이 한국에 반응 중인 이슈 — 넷플릭스 글로벌 Top 10·신작 K-콘텐츠(작품 속 음식·장소 포함), 유튜브 급상승·영어권 리액션, 인스타 릴스·해시태그 급증, X 영어권 바이럴 + K-pop 이슈, 비자·K-ETA 제도 변경 | Reddit, 인스타그램, X 등 Top(month/year) 반복 질문, 자동완성 마이닝, GSC 승자 패턴 파생 |
| 자격 조건 | 72시간 내 발생 + Trends Rising/자동완성 형성 초기 + 구글 1페이지 전용 영어 정리글 3개 미만 + Foreigner Test 통과 | 자동완성 실존 문구(Chrome MCP 불가 시 대체 수요 증거 필수 — 1-3 참조) + 1페이지 공백 실측 통과 + 에버그린 + Foreigner Test(0-2) 통과 |
| 실행 경로 | Phase 0 스캔 → 1-T 수요 검증 | Phase 0 트렌드 스캔은 건너뛰되 0-2 Foreigner Test는 필수 적용 → 1-0/1-1 롱테일 로직 |
| 금지 | 이미 자리잡은 대형 관광 키워드(street food, gwangjang market 등 — 승자 패턴 '안 되는 것') | 자동완성에 없는 인위적 조합 |
| 글 성격 | 시의성 명시 + 컨텍스트 2~3문장 + '지금 할 일' 행동 중심 (속도 우선) | 구체 답·표·FAQ 포함 에버그린 (깊이 우선) |
| 적합 후보 없을 때 | 그날은 트랙 L로 대체 + 로그에 "S 후보 없음 → L 대체" 기록 | 공백 실측 통과 후보 나올 때까지 재탐색 |

- **홀수일 → 트랙 S (숏테일 선점형)**: Phase 0 트렌드 스캔을 실행하고, 1-T 수요 검증을 통과한 **48시간 내 신규 이슈 숏테일(2단어 이하)**만 채택한다. 이미 자리잡은 대형 키워드(예: 그록, 가상자산 세금)는 트렌드처럼 보여도 금지. 통과 후보가 없으면 그날은 트랙 L로 대체하고 로그에 기록한다.
- **짝수일 → 트랙 L (롱테일 공백형)**: Phase 0을 건너뛰고 1-1 로직으로 **3~5단어 질문형·계산형 롱테일**을 발굴한다. 콘텐츠 공백 실측(1-3) 통과 필수.
- 舊 트랙 T=S, 트랙 E=L로 흡수한다.

> ⚠️ 이 블로그의 "핫함"은 한국 국내 기준이 아니라 **영어권 독자 기준**이다. 한국에서 아무리 화제여도 외국인이 영어로 검색하지 않으면 탈락, 반대로 한국에선 평범해도 해외에서 급상승이면 채택.

### 0-1. 트렌드 소스 (v10.13 — WebFetch 기본, 아래 4개만, 목적 없는 SNS 브라우징 금지)

> **(v10.13) 실행 환경**: 이 루틴은 Claude Code on the web에서 실행되며 **Chrome MCP는 없다**. 아래 각 항목의 '대체(v10.10)' 방법이 대체가 아니라 **기본 수단**이다 — 전부 WebFetch/Bash 기반, WebSearch 예산 미소모. 자동완성은 구글 공개 API `https://suggestqueries.google.com/complete/search?client=firefox&hl=en&q={키워드}`를 WebFetch로 조회한다(역시 미소모). 0-1 소스 체인 전체(프록시 포함)를 모두 스캔해도 후보가 없을 때만 탐색용 WebSearch 1회를 허용하며, 이 경우 남은 검증 예산은 1회뿐이다(**글당 총 2회 한도**).

1. **해외발 수요 (1순위)** — 구글 트렌드: `https://trends.google.com/trends/explore?date=now%207-d&geo=US&q=korea` 및 `q=korean` → **Related queries의 Rising/Breakout 항목**만 후보로 수집 (가장 강력한 신호)
   - *대체 (v10.10)*: Related queries는 JS 렌더링 전용이라 정적 fetch로 재현 불가 — 대신 Google Trends 공개 RSS `https://trends.google.com/trending/rss?geo=US`를 WebFetch로 읽어 한국 관련 급상승 검색어만 필터링 (신호는 더 거칠지만 예산 미소모)

2. **해외발 질문 (2순위)** — Reddit Hot/Top(week): r/koreatravel, r/Living_in_Korea, r/korea, r/kpop, r/KDRAMA — 최근 7일 내 upvote 100+ 또는 댓글 50+ 질문형 스레드
   - *대체 (v10.10)*: Bash `curl -A "Mozilla/5.0" "https://www.reddit.com/r/{subreddit}/top/.json?t=week&limit=25"`로 직접 조회해 ups·num_comments·created_utc를 파싱 (예산 미소모). 403/차단 시 WebFetch로 동일 URL 1회 재시도 → 그래도 실패하면 이 소스는 건너뛰고 나머지 소스로 진행 (전체 실패 시에만 대체 수요 증거 규칙 적용)

3. **핫플랫폼 스캔 (v10.6 확대 — 트랙 S의 핵심 소스)** — 외국인이 실제 몰려 있는 4대 플랫폼에서 '지금 한국에 반응 중인 것'을 직접 확인: ① 넷플릭스 글로벌 Top 10(`https://www.netflix.com/tudum/top10`)의 한국 작품 + 작품 속 음식·장소·문화 요소 ② 유튜브 — 글로벌/미국 급상승 탭의 한국 관련 영상, K-콘텐츠 영어권 리액션·쇼츠 반복 포맷 ③ 인스타그램 — 한국 여행·음식 릴스/해시태그 급증 ④ X — 영어권에서 바이럴 중인 한국 관련 포스트(리포스트·인용 수치 확인) + Soompi/allkpop 헤드라인 보조. ⚠️ 플랫폼에서 본 것은 어디까지나 '후보' — 채택은 반드시 1-T 구글 수요 검증 통과 후 (목적 없는 피드 브라우징 금지 원칙 유지: 위 4개 지점을 정해진 순서로 스캔하고 종료)
   - *대체 (v10.10)*: 넷플릭스 Top10은 WebFetch로 `https://www.netflix.com/tudum/top10/` 직접 열람 가능(예산 미소모)
   - *넷플릭스 세부 주제 마이닝 (v10.12 신설, 필수)*: Top10에서 확인한 한국 작품 '제목 자체'를 곧바로 주제로 삼지 않는다. WebFetch로 해당 작품의 위키피디아/팬덤 위키 또는 `site:reddit.com/r/KDRAMA [작품명]` 결과를 열람해, 외국인이 작중 등장한 구체 요소(음식·장소·소품·호칭·관습·대사)에 대해 실제로 무엇을 궁금해하는지 세부 각도를 추출한다 — 예: 넷플릭스 신작 '동궁' → 주제는 '동궁' 자체가 아니라 '극중 등장한 궁중 다과가 실제로 무엇인지'. 이렇게 뽑은 세부 후보에도 1-T 검증을 동일하게 적용
   - *SNS(인스타·X·유튜브) 대체 프록시 (v10.12 신설)*: 인스타그램·X·유튜브 급상승은 로그인 필요 SPA라 직접 스크래핑이 불가하지만, 포기하지 않고 아래 두 프록시로 대체한다 — ① Soompi(`soompi.com`)·allkpop(`allkpop.com`) 최신 헤드라인을 WebFetch로 확인해 'goes viral', 'fans react', 'trending' 류 표현이 붙은 기사를 SNS 바이럴의 대체 신호로 채택(이 매체들은 SNS 바이럴을 실시간 취재해 정적 기사로 발행함) ② 항목2의 Reddit r/kpop·r/KDRAMA 스캔 자체가 SNS에서 이미 화제된 콘텐츠를 유저들이 재게시·토론하는 경우가 많아 SNS 신호의 보조 프록시를 겸함 — 두 프록시 모두 예산 미소모

4. **한국발 → 글로벌 브릿지 (v10.11 재조정 — 영어 매체 1순위, 네이버 최후)** — **1순위**: Korea Herald, Korea JoongAng Daily, The Korea Times, Yonhap News Agency(영문판) 등 외국인이 실제로 읽는 영어 매체의 헤드라인·랭킹 중 **외국인에게 직접 영향이 있는 것만** (비자·K-ETA 제도 변경, 교통·공항, 축제, 입장료·티켓팅, 음식 유행) — 이 매체들은 처음부터 외국인 독자를 대상으로 쓰여있어 1-T 영어 검증과 정합성이 높다. **2순위(최후 보조, 단독 채택 근거 불가)**: 네이버 뉴스랭킹은 한국어 국내 독자용이라 외국인 검색 수요와 무관한 화제가 대부분이어서, 위 영어 매체에서 신호가 없거나 약할 때만 '한국 국내에서 1~7일 내 영어권으로 번질 수도 있는 이슈'를 예측하는 선행지표로만 참고하고, 반드시 1-T 영어 검증(구글 자동완성·Reddit)을 통과해야만 채택
   - *대체 (v10.10/11)*: 영어 매체는 WebFetch로 해당 사이트 헤드라인·랭킹 페이지를 직접 열람(예산 미소모, 1순위). 네이버는 동일하게 WebFetch 가능하나 보조용으로만 참고하고 단독 근거로 후보를 채택하지 않는다

### 0-2. 후보 추출 규칙 + Foreigner Test (이상한 주제 차단기)

- 후보 10~15개 추출 (v10.15 — 엔진 A/B/C 각각 최소 3개씩), 최근 48시간(최대 7일) 이슈 우선, 현황표 중복 확인
- **Foreigner Test — 세 질문에 모두 Yes여야 후보 유지**:
  1. 한국을 잘 모르는 외국인이 이걸 영어로 검색하는 **구체적 상황**이 그려지는가? — 유효 상황은 **여행 계획·여행 중 마주친 신기한 경험·K-콘텐츠(드라마/예능/K-pop) 시청 직후**로 한정 (v10.6). ⚠️ '한국 거주 중 행정 문제'(쓰레기 배출·세금·계약·보험 갱신 등 정착 행정)는 기본 탈락 — 예외 채택은 **주 1회 이하** + 수요 증거(자동완성 실존 또는 Reddit 반복 질문 3건 이상) 확보 시에만
  2. Food & Drink / Korean Culture / Travel & Transport / Lifestyle & Living 중 하나에 자연스럽게 속하는가?
  3. 승자 패턴(1-6)과 교차하는가 — **외국인이 여행·콘텐츠 시청 중 직접 마주치고 '신기하다'고 느낄** 한국 특유 문화·시스템이면서 전용 영어 글이 없는 영역인가? (예: 엘리베이터 취소 버튼, 찜질방 문신 규칙, 소개팅·회식 문화 ⭕ / 거주자만 겪는 행정 절차 ❌) (대형 관광 키워드성 트렌드는 신생 사이트가 못 이김)
- **자동 탈락(예외 없음)**: 한국 국내 정치, 해외 인지도 없는 연예인 스캔들·사건사고, 한국어로만 도는 밈/유행어, 외국인 접점 없는 국내 제도 이슈, **(v10.14) K-콘텐츠 '작품 자체' 뉴스** — 시즌 갱신·캐스팅·배우 입대·제작 루머 등 (팬 뉴스는 Soompi·IMDb·Tudum이 점령 + '한국'에 대한 글이 아님. 작품 속 한국 요소로 전환한 경우에만 후보 자격)

### 0-3. 트랙 분기

- 후보 중 1개라도 1-T 수요 검증 통과 → **트랙 T** 진행 (여럿이면 구글 수요 신호가 가장 강한 것)
- 전부 탈락 → 그날은 **트랙 L**(1-1 롱테일 공백 로직)로 대체하고 로그에 "S 후보 없음 → L 대체" 기록. **짝수일은 스캔 결과와 무관하게 트랙 L 고정**
- 기본 정보 표(2-1) 맨 아래에 `Track` 행 추가: `S (숏테일 선점)` 또는 `L (롱테일 공백)` 기록 (참고용 — Draft 루틴은 이 행 무시)

---

## Phase 1: 키워드 리서치 & 검증 (하이브리드)

### 1-T. 트렌드 수요 검증 (트랙 S 전용 — 홀수일, 가장 중요)

> 원칙: "한국에서 핫하다"는 사실만으로는 채택 불가. **영어권 실검색 수요의 증거를 구글 → Reddit 순으로 직접 확인**한 후에만 채택한다. (0and1life의 네이버 우선과 달리, 이 블로그는 구글이 1순위)

**[STEP T1] 구글 수요 검증 (1순위, 필수 관문)**

1. 이슈를 외국인이 실제로 칠 법한 **영어 질문 문장**으로 변환 (예: 콘서트 결제 이슈 → `interpark foreign card`)
2. WebFetch → `https://suggestqueries.google.com/complete/search?client=firefox&hl=en&q={영어 키워드}` (구글 자동완성 공개 API, 예산 미소모) → **자동완성에 해당 조합이 실제 노출되는가?** → 노출 없으면 영어권 수요 없음 = 탈락 (이 한 줄이 이상한 주제를 걸러내는 최종 안전망)
3. 자동완성에서 서브키워드 후보 2~4개 수집
4. 구글 1페이지 확인은 별도 검색 없이 **공백 실측 WebSearch(루틴 4-B, 글당 1회)와 겸용**한다: 뉴스 기사·Reddit 스레드만 있고 전용 정리 글(블로그/가이드)이 없으면 최적 기회

**[STEP T2] Reddit 보조 검증 (2순위)**

1. WebFetch/Bash로 `https://www.reddit.com/search.json?q={영어 키워드}&sort=new&t=week` 조회 → 최근 7일 내 질문 스레드 존재 확인 (예산 미소모)
2. 답변이 파편적이거나 댓글로만 흩어져 있으면 → 정리 글 수요 확인 (승산 높음)

**[STEP T3] 채택 기준 (모두 충족 시 채택)**

- 구글 자동완성 또는 관련검색어에 영어 키워드 조합 노출 (**필수**)
- Foreigner Test(0-2) 3개 문항 모두 Yes
- 검색 의도가 정보형(how/why/can/rules/cost 등)일 것 — 단순 뉴스 소비형이면 탈락
- 구글 1페이지에 전용 영어 정리 글 3개 미만
- ⚠️ 트랙 S에서는 **월 검색량 조건(500~5,000) 미적용** — 신규 이슈는 검색량 데이터 누적 전이므로 자동완성 노출 + Trends Rising이 수요 증거를 대신한다

**[트랙 S 작성 규칙] (Phase 2에 추가 적용)**

- SEO Title에 시의성 요소 포함: 연도(2026), "New Rules", "Just Changed" 등 (단, 이슈가 지나도 검색될 주제면 연도만)
- 외국인 독자는 한국 맥락을 전혀 모른다고 가정 — 첫 100단어 내에 무슨 일이 있었는지/왜 지금 중요한지 2~3문장 컨텍스트 필수
- 팩트 출처(공식 발표·영문 언론) 외부 링크 필수
- **뉴스 요약 금지**: 외국인이 지금 무엇을 해야 하는가(예약 방법, 우회로, 준비물, 비용) 중심으로 구성 — 영문 뉴스와의 차별화가 곧 상위노출 포인트

### 1-0. 🎯 핵심키워드 → 서브키워드 → 제목 전략 (트랙 공통 — 필수 선행)

> **목적**: 꾸준히 검색되지만 경쟁이 낮은 롱테일 핵심키워드를 중심으로, 연관 서브키워드를 파생시켜 제목과 포커스키워드를 구성한다.

**[STEP 1] 핵심키워드(Core Long-tail Keyword) 선정**

- 트렌디한 주제나 꾸준히 검색되는 주제에서 가장 핵심이 되는 롱테일 키워드 하나를 선정한다.
- 이 핵심키워드는 검색량은 충분하지만 해당 키워드를 제목에 직접 포함한 영어 게시물이 적은 형태여야 한다.
- 단어 수 (v10.5 트랙별): **트랙 S = 2단어 이하** 신규 이슈 헤드 (예: 넷플릭스 신작 제목, 새 제도명) / **트랙 L = 3~5단어** 질문형 롱테일 (예: `jjimjilbang tattoo rules`)
- 예: `korean age system`, `korean couple outfits`, `korea travel sim`

**[STEP 2] WebFetch로 Google 자동완성 수집 (v10.13 — 예산 미소모)**

- WebFetch → `https://suggestqueries.google.com/complete/search?client=firefox&hl=en&q=CORE_KEYWORD` (구글 자동완성 공개 API)
- 반환된 자동완성 목록 최대 10개 수집 + 필요 시 파생 쿼리(how/cost/rules 접미)로 1~2회 추가 조회 (모두 WebFetch, 예산 미소모)
- AI 임의 조합 절대 금지 — API가 실제로 반환하는 표현만 사용

**[STEP 3] 서브키워드 2~4개 확정**

- 자동완성/연관검색어 중 트랜잭션 키워드 포함 항목 우선 (best, how to, cost, guide, tips)
- 핵심키워드와 겹치지 않는 고유 표현 선택
- Focus Keyword: 핵심키워드 그대로 (2~3단어)
- Sub Keywords: 서브키워드 **4개 권장** (최소 2개), " / " 구분자로 기록 — 구글 자동완성·연관검색어에 실제 노출되는 것만, 부족하면 있는 만큼만 기록하고 AI 임의 조합으로 채우지 말 것

### 1-1. 황금 키워드의 조건 (트랙 E 전용 — 폴백 시에만 적용)

- 월 검색량 500~5,000 (너무 크면 경쟁 과다, 너무 작으면 트래픽 없음)
- 영어 게시물 10개 미만 (Google 1페이지 검색 결과 기준)
- 트랜잭션 키워드 포함: best / how to / cost / guide / tips / where to
- 한국 특화 표현: in Korea / korean / Seoul / Busan 등

### 1-2. 리서치 소스 (트랙 E 전용 — v10.4 개정)

- Reddit: r/koreatravel, r/Living_in_Korea, r/korea — **Top(month/year)** 질문형 스레드 (꾸준히 반복되는 고민 = 에버그린 수요)
- 구글 자동완성 마이닝: 기존 A등급 글 키워드에 how/why/can/rules/cost를 붙여 파생 롱테일 발굴
- GSC 승자 패턴(1-6) 파생: A등급 글과 같은 계열의 '한국 특유 문화·시스템' 후속 주제
- ❌ **v10.4 삭제**: X(트위터) 트윗 훑기, 네이버 실시간 검색어 단독 참조 — 목적 없는 SNS 브라우징은 수요 근거 없는 '이상한 주제' 채택의 주원인. 트렌드 탐색은 Phase 0의 4개 소스로만 수행하고, 모든 채택은 1-T 검증을 거친다

### 1-3. 키워드 검증 체크리스트 (v10.4 트랙별 분리)

**공통**

- [ ] **(v10.13) 검색 이전 중복 대조 + Foreigner Test — 최우선 관문**: 발행 목록(기존 제목 전체 + 포커스 키워드) 중복 대조와 Foreigner Test(0-2)를 모든 검증보다 먼저 끝냈는가? 수요 검증은 자동완성 API WebFetch(예산 미소모)로 하고, WebSearch는 통과 후보 중 **최종 1개의 공백 실측·경쟁글 수집 1회에만** 투입했는가? **글당 WebSearch 총 2회 한도**(예외적 S 탐색 1회 또는 승계 후보 재검증 1회 포함)를 지켰는가? 탈락 시 새 주제를 즉흥 발명하지 않고 기존 비중복 리스트의 다음 순위로만 이동했는가? (자동완성 API·RSS·Reddit JSON 등 WebFetch는 예산 미소모)
- [ ] (v10.5) 트랙별 단어 수 규칙에 맞는가? (S=2단어 이하 / L=3~5단어 질문형)
- [ ] 구글 자동완성으로 직접 수집했는가? (AI 조합 금지)
- [ ] 기존 발행 목록과 중복되지 않는가?
- [ ] 포괄 키워드가 아닌 구체적 질문형 롱테일인가? (예: `jjimjilbang guide` ❌ → `jjimjilbang tattoo rules` ⭕)
- [ ] **(v10.4) 서브키워드 인텐트 일치**: 서브키워드의 검색 의도가 글의 목적과 일치하는가? how-to 글에 lookup형 키워드(number, search, check, status) 혼입 금지 (사례: korea business registration 글에 `registration number/search` 서브키워드 혼입 → 제거, 2026-07-09)
- [ ] **(v10.4) YMYL 주제 규칙**: 비자·연금·세금·보험·은행 주제는 정부·공식기관이 1페이지를 점령한 헤드 키워드를 피하고, 1인칭 문제해결형 각도(catch-22, 실패 경험, 실제 순서)로 차별화 + 타이틀에 타겟 청중(for Foreigners/Freelancers) 명시 + 공식 출처 외부링크 필수

**트랙 S (숏테일 선점 — 홀수일)**

- [ ] 최근 48시간(최대 7일) 이내 이슈인가?
- [ ] 구글 자동완성/관련검색어에 영어 키워드가 실제 노출되는가? (필수)
- [ ] Foreigner Test(0-2) 3개 문항 모두 Yes인가?
- [ ] 검색 의도가 정보형(how/why/can/rules/cost)인가?
- [ ] 구글 1페이지에 전용 영어 정리 글이 부족한가? (Reddit/뉴스만 있으면 승산 높음)

**트랙 L (롱테일 공백 — 짝수일)**

- [ ] **(v10.13) 수요 실증 — 필수 관문**: 구글 자동완성 API(WebFetch, 예산 미소모)에 해당 문구가 실제 노출되는가? 노출이 없으면 대체 증거(Reddit search.json 최근 1년 내 동일 질문 3건 이상 또는 Google Trends RSS 신호 — 모두 WebFetch)로 확인 — 어느 쪽도 없으면 후보 탈락 ('아무도 안 찾는 공백'은 기회가 아님. 사례: korea bulky waste sticker, 2026-07-14)
- [ ] **(v10.6) Foreigner Test(0-2) 3개 문항 모두 Yes인가?** (트랙 L도 필수)
- [ ] 영어 게시물 10개 미만인가? (Google 1페이지 기준)
- [ ] 트랜잭션 키워드가 포함되어 있는가?
- [ ] Google 1페이지 상위가 대형 여행블로그·공식기관·대형 매체로 도배되어 있지 않은가? (Reddit/Tripadvisor 포럼 질문글이 상위면 전용 글이 없다는 뜻 = 승산 높음)

### 1-4. Focus Keyword 형식

- **Focus Keyword**: 핵심키워드 원문 그대로 (예: `korean age system`)
- **Sub Keywords**: 서브키워드 " / " 구분 (예: `korean age calculator / age in korea / how old am i in korea`)
- ⚠️ Notion 기본 정보 표에 기록된 값을 Cowork wordpress_draft가 그대로 복사함. 재검색·재조합 금지.

### 1-5. 히어로 이미지 조달 및 WordPress 업로드 규칙

- Unsplash에서 Korea 관련 고화질 이미지 선택
- URL 형식: `https://images.unsplash.com/photo-{ID}?w=1200&q=80`
- 각 글마다 고유 ID 사용 (중복 금지)
- HTML `<img>` 태그에 직접 삽입 (Gutenberg wp:image 블록 금지)
- alt text: Focus Keyword 포함, 60자 이내 영문

### 1-6. 발행 후 GSC 성과 피드백 루프 (v10.3 추가, 2026-07-08)

> **목적**: 키워드 검증은 발행 전 1회로 끝나지 않는다. Search Console 실데이터로 전체 글을 재분류하고 조치한다. (Search Console → 실적 → 3개월 → 페이지 탭: 클릭/노출/CTR/게재순위)
> ✅ (2026-07-26 확인) 실제 실행 주기는 **매주** — Cowork "SEO 주간 점검" 작업이 koreaplug.com·0and1life.com 두 블로그를 함께 점검해 각 GSC 리포트 페이지에 기록한다. 실행 절차는 → `GSC-Weekly-Report-Routine.md` 참조. "매월 1일"은 옛 설계값이며 실제 실행 이력(2026-07-11, 07-19)과 맞지 않아 폐기.
> **실행·기록 (v10.4 명시)**: 이 루프는 일일 writer 루틴과 별개의 월간 작업이다. 결과는 📈 KoreaPlug GSC 월간 성과 리포트 페이지에 "YYYY-MM 리포트" 섹션으로 기록하고, 아래 승자 패턴 항목을 갱신한다.

**등급 분류 기준 및 조치**

- **A 승자** (클릭 ≥2): 내부링크 허브로 활용, 같은 계열 후속 글 파생. 건드리지 말 것
- **B CTR 결함** (노출 ≥50 & 순위 ≤13 & CTR <1.5%): 1페이지에 노출되는데 아무도 안 누르는 상태 → SEO 타이틀·메타를 질문형/구체 수치형으로 재작성. **최우선 조치 — 효과 가장 빠름**
- **C 순위 부족** (노출 ≥30 & 순위 13~30): 콘텐츠 보강(FAQ·표·최신 정보) + A등급 글에서 내부링크 추가
- **D 경쟁 과다** (순위 >30): 대형 키워드 포기, 롱테일로 Focus Keyword·타이틀 재타겟 (사례: `jjimjilbang-guide` 노출 0 → `jjimjilbang tattoo rules`로 재타겟, 2026-07-08)
- **E 무반응** (게시 60일+ & 노출 <10): Search Console URL 검사로 색인 확인 → 재타겟 또는 유사 글과 통합

**⚠️ GA4 지표 해석 주의**

- 트래픽이 적은 글의 이탈률·참여시간은 봇/AI 크롤러에 왜곡된다. 판별법: 소스 `(not set)` + 참여시간 0초 + 미국 데이터센터 지역(Iowa/Oregon/Virginia) = 봇
- 세션 30 미만 페이지의 행동 지표로 글 품질을 판단하지 말 것. 판단 기준은 GSC 노출·순위가 우선

**승자 패턴 (2026-07 GSC 분석 결과)**

- 잘 되는 것: 외국인이 궁금해하지만 전용 영어 글이 없는 한국 특유 문화·시스템 (sogeting, hoesik, PC방 음식, 무인라면, 머리스파, 약과)
- 안 되는 것: 대형 관광 키워드 (street food 순위 66, gwangjang market 52, tipping 34) — 신생 사이트는 못 이김

**사실 정확성 재검증**

- 추천 장소·가격은 발행 전 + 월 피드백 루프에서 폐업/변경 여부 확인 (사례: Dragon Hill Spa 폐업 상태로 1순위 추천 중이었음 → SPAREX 동대문으로 교체)

---

## Phase 2: HTML 콘텐츠 작성

### 2-1. 페이지 기본 정보 설정 (메타 정보 표)

글 작성 전 아래 표를 먼저 완성한다. Notion 서브페이지 섹션 1에 그대로 기재.

| 항목 | 형식 | 예시 |
|---|---|---|
| Focus Keyword | S: 2단어 이하 신규 이슈 헤드 / L: 3~5단어 질문형 | `korean age system` |
| Sub Keywords | 구글 자동완성 기반 2~4개, " / " 구분 | `korean age calculator / age in korea` |
| SEO Title | Title Case + `:` • 호기심 후크 | `Korean Age System: The Real Reason You're Older in Korea` |
| H1 | SEO Title과 반드시 동일 | (위와 동일) |
| Slug | Focus Keyword 하이픈 연결, 40자 이하 | `korean-age-system` |
| Meta Description | Focus Keyword로 시작 + 호기심 갭 카피, 130~155자 | `Korean age system explained — Why does the math completely fail...` |
| Theme Color | Culture=`#7e22ce` / Lifestyle=`#16a34a` / Food=`#dc2626` / Travel=`#ca8a04` | `#7e22ce` |
| Internal Link 1 | 관련 슬러그 (상대경로 `/slug/`) | `/tipping-in-korea/` |
| Internal Link 2 | 관련 슬러그 (상대경로 `/slug/`) | `/korean-hoesik-drinking-culture-boss/` |
| Wrapper ID | `k-[slug-첫단어]-report` | `k-age-report` |

> ⚠️ 내부 링크는 반드시 상대경로 (`/slug/`). 절대경로 `https://koreaplug.com/slug/`는 외부 링크로 인식되어 SEO 감점.

### 2-2. 제목 규칙 (v10.0 개정)

- Focus Keyword를 제목 앞쪽에 유지 (Title Case 변환)
- 콜론 뒤 부제는 "호기심 후크": Why / How / What / The Real Reason 등
- 직역 제도 용어 전면 금지: Civil Act / Age of Majority / Equipment 등 관공서식 표현 금지
- 미국인이 실제로 구글에 칠 만한 표현만 사용
- "직전 10개 제목 중 동일 훅 표현이 이미 2회 이상이면 해당 훅 사용 금지"
- **(v10.8) 연도·패턴 획일화 금지**: ① 연도(2026)는 최신성이 검색 의도에 중요한 경우(제도 변경·가격·티켓팅 등)에만 표기하고 에버그린 문화 주제에는 생략 ② 작성 전 최근 발행 글 10개 제목과 동일 훅·동일 구조 반복 여부 확인 — 반복되면 다른 훅(Why/How/The Real Reason 외에도 질문형·수치형·경험형)으로 교체 ③ 제목은 템플릿이 아니다 — 키워드별 검색 의도에 맞는 최적 문장을 개별 작성한다

### 2-3. HTML 구조 (필수 템플릿)

```html
<div id="WRAPPER_ID" style="max-width:820px;margin:0 auto;padding:0 16px 40px;box-sizing:border-box;font-family:'Georgia',serif;color:#1a1a1a;line-height:1.8;">

<!-- HERO IMAGE -->
<div style="position:relative;border-radius:16px;overflow:hidden;margin-bottom:32px;background-color:#fff !important;width:100%;aspect-ratio:16/9;min-height:260px;max-height:380px;">
  <img decoding="async" src="UNSPLASH_URL" alt="ALT_TEXT" style="width:100%;height:100%;object-fit:cover;display:block;">
  <div style="position:absolute;inset:0;background:linear-gradient(to bottom, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.8) 100%);z-index:1;">
    <div style="position:absolute;bottom:0;left:0;right:0;padding:clamp(16px, 4vw, 32px);z-index:2;box-sizing:border-box;">
      <h1 style="color:#ffffff !important;font-size:clamp(20px, 4.5vw, 32px);font-weight:800;line-height:1.25;margin:0 0 10px;text-shadow:0 2px 8px rgba(0,0,0,0.6);word-break:keep-all;">SEO_TITLE</h1>
      <p style="color:rgba(255,255,255,0.9) !important;font-size:14px;margin:0;">Last updated: MONTH YEAR &nbsp;|&nbsp; N min read</p>
    </div>
  </div>
</div>

  <!-- TABLE OF CONTENTS -->
  <!-- TABLE OF CONTENTS -->

  <!-- INTRO (100~150 words) -->
  <p>INTRO_PARAGRAPH</p>

  <!-- SECTION 1 -->
  <h2 style="font-size:1.5rem;font-weight:700;margin:40px 0 16px;color:#THEME_COLOR;">SECTION_TITLE</h2>
  <p>CONTENT</p>

  <!-- EXTERNAL LINK (최소 2개 필수) -->
  <p>According to <a href="EXTERNAL_URL" target="_blank" rel="noopener noreferrer">AUTHORITY_SOURCE</a>, ...</p>

  <!-- INTERNAL LINK -->
  <p>... <a href="/RELATED_SLUG/">related article</a> ...</p>

  <!-- FOOTER CTA -->
  <div style="background:#f8f8f8;border-left:4px solid #THEME_COLOR;padding:16px 20px;margin-top:40px;border-radius:0 8px 8px 0;">
    <p style="margin:0;font-size:0.95rem;">FOOTER_CTA_TEXT</p>
  </div>

</div>
```

**TOC 규칙**: `<!-- TABLE OF CONTENTS -->` 플레이스홀더 2개 연속 삽입. Gutenberg 편집기에서 rank-math/toc-block으로 자동 변환됨. `<h2>` 이상 태그는 TOC와 충돌하므로 HTML 내 `core/heading` 블록 절대 금지.

### 2-5. 콘텐츠 작성 규칙

- **분량**: 1,500~2,000 단어 (영어 단어 기준)
- **키워드 밀도**: Focus Keyword 0.5~0.8% (1,500단어 기준 7~12회)
- **외부 링크**: 권위 있는 소스 최소 2개 (Wikipedia, 정부기관, 주요 언론)
- **내부 링크**: 기존 KoreaPlug 글 최소 1개 (상대경로)
- **문체**: 1인칭 경험 주어 (I, My, When I first...) + 구어체 연결어
- **금지**: Furthermore / Moreover / In conclusion 등 기계적 전환어
- **(v10.16) 형식 로테이션**: 글 형식을 (a) 내러티브(1인칭 경험 서사) (b) 리스트/비교표 중심 (c) Q&A 중심 중 최소 3종으로 로테이션한다. 발행 목록 기준 직전 3개 글과 동일 형식이면 다른 형식으로 전환한다
- **[경쟁글 차별화 — 필수]** STEP 3.5 GAP_REPORT의 ⭐ 각도를 H2 섹션 1개에 반드시 반영. 이 H2가 이 글의 차별화 포인트다. GAP_REPORT ⭐ H2가 없는 글은 발행하지 않는다.
- **[EEAT 강제]** 아래 중 최소 1개 없으면 발행 금지: ① 공식 출처 수치·가격 (현재 기준, 출처 링크 포함) ② Reddit 실제 질문·댓글 직접 인용 (링크 포함) ③ GAP_REPORT ⭐ 각도에서만 나오는 구체 상황 묘사 또는 경험
- **(v10.16) 경험 서술 진위 규칙**: ③은 실제 있었던 일에만 1인칭(I, My)을 쓴다. 실제 겪지 않은 사건을 1인칭으로 지어내는 것은 금지 — 확인 안 된 사례는 "많은 외국인이 이런 상황을 겪는다" 식 3인칭 일반화 서술로 대체한다

### 2-6. 바이럴 훅 & 휴먼라이징 패스 (v10.13 신설 — 발행 전 필수 2단계)

> Cowork 스킬 2종을 매 글마다 순서대로 적용한다. 두 패스 모두 검색 예산과 무관하다. 독자는 한국을 처음 접하는 영어권 독자 — 'bar test'(친구에게 술자리에서 말하듯)가 문체 기준이다.

**① create-viral-content 스킬 — 구조·훅 단계 (초안 작성 시)**

- SEO Title·H1: 제목 후보 10개 이상 생성 후 호기심/구체성/감정 3축 스코어링(각 0~3점, 합 7점 이상만 채택). 2-2 중복 검사를 먼저 통과한 후보만 스코어링 대상으로 삼는다(중복 훅 후보는 10개 후보 생성 단계에서 배제)
- INTRO 첫 문장: Hook Architecture(Prediction+Stakes / Before-After Compression / 문제 직격 중 택1) 적용 — 첫 2초에 읽을 이유를 만든다
- 마무리: "Let me know in the comments" 류 engagement bait 금지, 독자가 지금 할 행동 중심 클로저
- 정제 패스 최소 3개 실행: Skeptic("새로운 게 뭐지?") → Scroller("첫 문장에서 멈추는가?") → Editor("20% 덜어내면?")

**② avoid-ai-writing 스킬 — 최종 패스 (HTML 완성 직후, Notion 업로드 전)**

- voice profile: casual~warm — 1인칭 경험 문체(2-5) 유지
- 균일한 문장 길이 깨기, 기계적 전환어(Furthermore/Moreover/In conclusion)·과잉 열정 표현(game-changer 류)·engagement bait 제거
- 수치·고유명사·링크·HTML 구조는 보존하고 문체만 교정. 교정 후 5-3·5-5 체크리스트 재확인

---

## Phase 3: Notion 페이지 등록

### 3-1. Notion 페이지 위치

Phase 7 카테고리-Notion Page ID 매핑 참조 → 해당 카테고리 페이지 하위에 생성

### 3-2. Notion 페이지 필수 구성 (2개 섹션) — v10.1 변경

**섹션 1: 기본 정보 표**

- 2-1의 메타 정보 표 구조 그대로 생성
- `Draft 일자` 항목은 반드시 공란 (wordpress_draft 루틴이 자동 기재)

**섹션 2: HTML 전체**

- `html` 코드 블록으로 완성된 HTML 전체 삽입

> ⚠️ `parent`는 반드시 tool call의 최상위 파라미터로 지정 (pages[] 배열 내부 금지)
> (舊 섹션 3 "배포 JavaScript"는 v10.1부터 생성하지 않음 — wordpress_draft가 REST API로 직접 배포)

---

## Phase 5-1: 목표 점수

- **목표**: Rank Math SEO 78점 이상 (81점 권장)
- Phase 5-2 TOC 스크립트 및 5-3 블록구조/820px 체크는 → 📋 KoreaPlug Draft 지침 참조

> (v10.1: 舊 "블록 구조: toc-block+freeform 고정" 문구 삭제 — 실제 배포는 wordpress_draft의 freeform 래퍼+REST API 방식이며 기존 문구는 실제와 불일치했음)

### 5-3. Focus Keyword 배치 체크리스트 (writer 자가검수)

아래 항목을 HTML 작성 완료 후 교차 검증:

- [ ] SEO Title 앞쪽에 Focus Keyword 포함 (Title Case)
- [ ] Meta Description 첫 문장에 Focus Keyword 포함
- [ ] H1이 SEO Title과 동일한가?
- [ ] 본문 첫 100단어 내 Focus Keyword 1회 이상 등장
- [ ] H2 섹션 중 1개 이상에 Focus Keyword 또는 서브키워드 포함
- [ ] 이미지 alt text에 Focus Keyword 포함
- [ ] (트랙 S만) 시의성 표기·이슈 컨텍스트 2~3문장·팩트 출처 외부 링크가 모두 포함되어 있는가?
- [ ] STEP 3.5 GAP_REPORT의 ⭐ 각도가 H2 섹션으로 반영되었는가?
- [ ] EEAT 강제 조건 (① 공식 수치+출처 링크 ② Reddit 인용+링크 ③ 경쟁글에 없는 구체 상황 묘사) 중 최소 1개가 포함되어 있는가?

---

## Phase 5-5: AEO·GEO 최적화 체크리스트 (v10.7 신설 — 트랙 S·L 공통)

> ⚠️ **이 6개 항목은 SEO가 아니라 AEO·GEO를 위한 가이드다.** AEO(Answer Engine Optimization)는 구글 AI 개요(AI Overviews)·답변엔진에 내 글이 **발췌(직답)**되기 위한 것, GEO(Generative Engine Optimization)는 ChatGPT·Gemini·Perplexity 등 생성형 AI 답변에 내 글이 **인용(출처)**되기 위한 것이다. 영어권 독자는 AI 검색 의존도가 높으므로 KoreaPlug는 이 체크리스트의 효과가 특히 크다. 모든 글은 Notion 업로드 전 아래 6개를 자가점검한다.

- [ ] **① [AEO] INTRO에 직답 포함**: 첫 100~150단어 INTRO 안에 질문에 대한 핵심 답 1~2문장(예: "Yes, you can — but...")을 반드시 포함 — AI가 발췌할 수 있는 요약이 글 초반에 있어야 한다
- [ ] **② [AEO] 질문형 H2 + 직답 첫 문장**: H2 중 2개 이상을 외국인이 실제 검색하는 질문 형태(Can/How/Why/Do I need...)로 쓰고, 바로 아래 첫 문장에서 20~30단어로 먼저 답한 뒤 설명을 이어간다
- [ ] **③ [AEO] FAQ 섹션 필수화**: 구글 People Also Ask·자동완성·Reddit 반복 질문과 일치하는 Q&A 3개 이상 포함
- [ ] **④ [GEO] 통계·수치 3개 이상 + 출처 병기**: 가격·운영시간·수치는 반드시 출처(공식 기관·영문 언론·실측)와 함께 — 통계는 AI 인용률을 약 30% 높인다
- [ ] **⑤ [GEO] 전문가·공식 인용 1개 이상**: 공식 발표·기관 문서·현지 전문가 발언을 인용 부호와 출처 링크로 명시 — 인용률 약 41% 상승 요인
- [ ] **⑥ [AEO·GEO 공통] 구조화 유지**: 비교표·리스트(Top N) 구조 포함, Rank Math에서 Article + FAQ 스키마 설정, Last updated(dateModified) 90일 이내 유지(오래된 글은 1-6 월간 루프에서 갱신)

---

## Phase 7: 카테고리 Notion Page ID 매핑

| 카테고리 | 이모지 | Notion Page ID | WP Category ID | Theme Color |
|---|---|---|---|---|
| Food & Drink | 🍜 | `33ebfe4a2ae18136b1a9df45458cb1be` | 3 | `#dc2626` |
| Korean Culture | 🎭 | `33ebfe4a2ae1815ba5e1d58b1bf9a44c` | 4 | `#7e22ce` |
| Travel & Transport | 🚌 | `34fbfe4a2ae18031b3fbcc874496498e` | 5 | `#ca8a04` |
| Lifestyle & Living | 🏠 | `33ebfe4a2ae18133a438ed9274c1dfb1` | 18 | `#16a34a` |

**루틴 실패 처리**

| 상황 | 조치 |
|---|---|
| 후보 주제 전체 중복 | 루틴 중단, ⚠️ 경고 기록 후 사용자 알림 |
| Notion MCP 오류 | 오류 내용 로그 기록 후 중단 |
| WebFetch/Bash 외부 호스트 접속 자체가 세션 네트워크 정책으로 전면 차단된 경우 | 오류로 취급하여 루틴을 중단하거나 사용자에게 알릴 필요 없음 — 해당 세션에서는 STEP 2·4-A의 자동완성·Reddit·Trends 수집을 **무료 대체 신호**(발행 이력·승자 패턴·시즌 캘린더·모델 지식)로 수행한다. **글당 WebSearch 2회 한도는 차단 여부와 무관하게 그대로 유지하며, 예산을 늘려 메우지 않는다** — 하루 5회는 KoreaPlug·0and1Life가 공유하는 플랫폼 전체 한도이므로 한쪽이 더 쓰면 다른 블로그가 공백 실측을 못 한다. 예산은 공백 실측·경쟁글 수집에 우선 배정한다 (매 실행마다 이 상황을 보고할 필요는 없음) |
