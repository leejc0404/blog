[루틴 : KoreaPlug-Writer — v4 (웹 전용, 지침서 GitHub 이관)]
*예약된 트리거 시간이 되면 해당 일자에 먼저 루틴이 실행되었더라도 무조건 다시 진행한다.
날짜: 실행 시점의 실제 KST 날짜를 사용한다 (이 프롬프트에 적힌 고정 날짜가 있어도 무시).

⚠️ 실행 환경: Claude Code on the web — **Chrome MCP 없음.**
자동완성·트렌드·커뮤니티 수집은 WebFetch/Bash(예산 미소모)로 시도한다. 차단 여부 판정은 STEP 0에서 세션당 1회 수행하며, 이후 모든 STEP은 그 결과(WEBFETCH_STATUS)를 그대로 사용한다(재판정 금지). 403/차단이 확인되면 즉시 WebSearch로 대체한다 — 이는 정상 동작이며 오류·경고·사용자 알림 대상이 아니다.

⚠️ 알려진 취약 소스는 1회만 시도한다 (v1.20): Reddit(curl 기반 JSON 수집)은 데이터센터 IP 차단으로 실패 확률이 높다. 실패 시 재시도 없이 다음 소스로 진행한다 (엔진 B-2, STEP4-A 공통 적용).

⚠️ 역할 분담: 이 루틴은 **운영 절차(언제·무엇을·몇 회)**만 정의한다. 키워드 전략·글 방향·품질 기준의 단일 기준(SSOT)은 **GitHub 지침서**다 — 이 루틴과 지침서가 상충하면 지침서를 따르고, 상충 발견 시 STEP 8 리포트에 기록해 사용자에게 알린다.

🎯 타겟 독자: **한국에 관심 있고, 여행 오고, 한국을 좋아하는 외국인** (K-콘텐츠 시청자 · 여행 계획자 · 방문 중 여행자). 모든 주제 판단은 "이 외국인이 영어로 검색할까?"가 기준이다 (Foreigner Test).

⚠️ WebSearch 예산 (v1.20 — 하루 5회는 Claude 플랫폼 전체 한도이며 0and1life·KoreaPlug 두 블로그가 공유한다):
이 루틴은 글당 최대 **2회**로 자체 상한을 둔다 (WEBFETCH_STATUS 정상/차단과 무관하게 동일 — 두 블로그 합산 최대 4회, 나머지 1회는 여유분).

우선순위 (예산은 이 순서로만 쓴다):
1순위 — STEP 4-B 공백실측(경쟁 비교) 1회: 반드시 확보. WebFetch로 대체 불가능한 유일한 단계이자 주제 채택을 최종 결정하는 가장 중요한 단계.
2순위 — STEP 4-B에서 1순위 후보가 포화 판정일 때, 숏리스트 2순위 후보 비교용 1회.

STEP 2(브레인스토밍)와 STEP 4-A(수요검증)는 WebSearch를 쓰지 않는다 — 구글 자동완성 API WebFetch(`hl=en`, 예산 미소모)로 우선 시도하고, 막혀 있으면 Reddit search.json(무료, 1회만 시도) 또는 발행 이력·엔진 C·모델 지식 기반 대체 신호로 판단한다. 이건 검증 생략이 아니라 무료 증거로 검증한 결과이며, WebSearch로 보완하지 않는다.

후보 탈락 시 새 주제를 즉흥적으로 발명하지 말 것 — STEP 3에서 확정한 숏리스트/예비 리스트 순위로만 이동. STOP은 STEP 3·4-A에서 채택 가능한 후보가 완전히 0개가 됐을 때만 발생한다.

## STEP 0 — 트랙 판정 + 네트워크 상태 판정 (최우선, 둘 다 세션당 1회)
① 트랙: KST 오늘 날짜의 '일' 숫자: 홀수 → 트랙 S(숏테일 선점형) / 짝수 → 트랙 L(롱테일 공백형)
② WEBFETCH_STATUS: 구글 자동완성 API(`hl=en`) 1회 조회 → 정상/차단 확정. STEP 1~8 전체가 이 값을 그대로 사용한다(재판정 금지). 단, 이는 '조직 네트워크 차단' 여부 판정이며 개별 사이트 자체 실패(Reddit 등)와는 별개다 — WEBFETCH_STATUS=정상이어도 특정 소스가 개별 실패할 수 있으며, 이 경우 전체를 차단으로 재판정하지 않고 해당 소스만 건너뛴다.

## STEP 1 — Read Reference Materials from GitHub + Notion (검색 없이 먼저 실행)
아래 두 자료를 동시에 읽는다:
- 지침서: KoreaPlug Writer 지침 (GitHub 버전 — 반드시 준수):
  https://raw.githubusercontent.com/leejc0404/blog/main/KoreaPlug-Writer.md
  → WebFetch로 조회한다 (Notion MCP가 아님에 유의). 404/403 등으로 조회 실패 시:
    1. `main` 브랜치가 아닐 수 있으므로 저장소 루트(`https://github.com/leejc0404/blog`)를 1회 더 확인한다.
    2. 그래도 실패하면 세션 네트워크 정책상 GitHub 접근 자체가 막힌 것인지, 파일이 없거나 비공개 저장소인지 구분할 수 없는 상태이므로 **추측으로 지침 내용을 생성하지 않는다** — ⚠️ 경고 로그를 남기고 STOP, STEP 8 리포트에 원인과 함께 즉시 사용자에게 알린다 (STEP 3·4-A 후보 0개 STOP과 동급 처리).
- 발행 목록 (전체 글 현황, Notion 유지): https://www.notion.so/33cbfe4a2ae181b9a743cb7c194dea7f
→ 기존 제목 전체 + 포커스 키워드 + 현재 최고 번호 MAX_NUM 확인
→ 지침서 1-6 승자 패턴(잘 되는 것/안 되는 것) 확인 — STEP 2 브레인스토밍의 핵심 재료
- 키워드 백로그 (Notion, 2026-07-26 신설): https://www.notion.so/3a9bfe4a2ae1818f911bf852981d5018
→ 상태='대기' 항목 전체 확인 — STEP 2 엔진 D의 입력
- 최신 주간 GSC 리포트 (Notion, 페이지 ID 398bfe4a-2ae1-8150-93c4-fb98977c64bf): "## 리포트 (최신순)" 맨 위 섹션의 특이사항·다음 조치 제안 확인 — 후보 우선순위에 반영 (예: 특정 클러스터 후속 우선 제안이 있으면 그 클러스터 후보를 상위 배치)

## STEP 2 — Candidate Brainstorm (v1.20 3중 발굴 엔진 — 후보 10~15개 생성, WebSearch 0회 원칙 — 항상, 예외 없음)
**[짝수일 · 트랙 L]**
지침서 1-6 승자 패턴("외국인이 궁금해하지만 전용 영어 글이 없는 한국 특유 문화·시스템") + 기존 A등급 글 파생 + 발행 이력 회피 + 엔진 A 시드 마이닝(아래)으로 3~5단어 질문형 영어 롱테일 후보 10~15개 생성.
WebFetch 차단 시: 엔진 A 시드 마이닝을 생략하고 지침서 승자 패턴 + 발행 이력만으로 브레인스토밍한다 (수요 확인은 STEP 4-A로 이관 — 검증 자체는 절대 생략하지 않는다).

**[홀수일 · 트랙 S] 아래 3개 엔진을 모두 실행 — 우선 WebFetch, 예산 미소모. WebFetch 차단 시: 엔진 A는 엔진 C·발행 이력 기반 대체모드로 전환(WebSearch 사용 안 함 — STEP4-B 예산 보호, v1.20), 엔진 B는 생략. 엔진당 최소 3개, 합계 10~15개 후보.**

**엔진 D — 키워드 백로그 (2026-07-26 신설 — 트랙 공통 최우선, 예산 미소모)**
STEP 1에서 읽은 백로그의 '대기' 항목을 후보군 맨 앞에 배치한다.
- 출처=GSC쿼리 항목은 구글이 이미 이 사이트를 노출시키는 실측 쿼리이므로 **STEP 4-A 수요 검증 통과로 간주**한다. 단 STEP 3(중복 대조·Foreigner Test·'한국 자체' 테스트)과 STEP 4-B(공백 실측)는 동일하게 적용.
- 그 외 출처(TrendsRising/PAA)는 일반 후보와 동일하게 4-A를 거친다.
- 백로그 항목이 최종 채택되면 STEP 7 완료 후 백로그 해당 행의 상태를 '채택 #XX'로, 필터·검증에서 탈락하면 '탈락(사유)'로 갱신한다 (re-fetch 후 old_str 구성).
- 백로그가 비어 있거나 전부 부적합이면 아래 엔진 A~C로 정상 진행 (백로그는 추가 후보군이지 대체가 아님 — 합산 10~15개 목표는 동일).

**엔진 A — 자동완성 시드 마이닝 (수요 직접 수확)**
구글 자동완성 API를 요일별 시드로 8회 이상 조회해 외국인이 '지금' 검색 중인 질문을 직접 수확:
`https://suggestqueries.google.com/complete/search?client=firefox&hl=en&q={시드}`
요일 무관 상시 시드 (v1.20 — 매일 포함): `what's trending in korea` — 그날 지정 카테고리 밖에서 터진 트렌드를 놓치지 않기 위한 보완 시드.
요일별 시드 — 월: `why do koreans`/`korean etiquette` · 화: `is it rude in korea`/`can you in korea` · 수: `how to in korea`/`korea travel tips` · 목: `what does mean in korean`/`korean culture shock` · 금: `do koreans`/`korea vs` · 토: `korean food how`/`where in seoul` · 일: `moving to korea`/`dating in korea`
각 시드에 단어 1개 덧붙인 변형 조회 허용. 수확 문구 중 발행 이력에 없는 신선한 질문형을 후보화 (시의성 조합은 S, 에버그린 조합은 L 예비로 보관).
(WebFetch 차단 시: 엔진 A는 실시간 조회를 하지 않고 위 대체모드로 진행 — v1.20)

**엔진 B — 이슈 소스 스캔 (아래 소스를 이 순서로 스캔하고 종료, 지침서 0-1 — WebFetch 차단 시 전체 생략):**
1. **Google Trends RSS**: `https://trends.google.com/trending/rss?geo=US` → 한국 관련 급상승 검색어만 필터
2. **Reddit Top(week) JSON** (알려진 취약 소스 — 1회만 시도, 실패 시 재시도 없이 다음 소스로): r/koreatravel, r/Living_in_Korea, r/korea, r/kpop, r/KDRAMA
   — Bash `curl -A "Mozilla/5.0" "https://www.reddit.com/r/{sub}/top/.json?t=week&limit=25"`
   — upvote 100+ 또는 댓글 50+ 질문형 스레드만 후보화
3. **넷플릭스 Tudum Top10** WebFetch (`https://www.netflix.com/tudum/top10`) + **세부 주제 마이닝(필수)**: 작품 제목 자체가 아니라 작품 속 음식·장소·소품·관습을 위키피디아/`reddit.com/r/KDRAMA` 열람으로 마이닝해 세부 각도로 전환
4. **Soompi·allkpop 헤드라인** WebFetch — 'goes viral', 'fans react', 'trending' 류 기사 = SNS 바이럴 대체 프록시
   ⚠️ **(v10.14) 작품·시즌·배우 뉴스 '그 자체'는 후보 금지** — 반드시 그 이슈 속 **한국 요소**(음식·장소·관습·호칭·시스템)로 전환한 세부 각도만 후보화 (예: 드라마 시즌2 루머 ❌ → 극중 등장한 궁중 다과가 실제 무엇인지 ⭕)
5. **영어 매체 헤드라인** (Korea Herald, Korea JoongAng Daily, The Korea Times, Yonhap 영문판) WebFetch — 비자·K-ETA·교통·축제·티켓팅·음식 유행 등 외국인 직접 영향 이슈만

**엔진 C — 시즌·이벤트 캘린더 (예측형 선점 — 내장 지식 기반, WebFetch 차단과 무관하게 항상 실행)**
검색은 이벤트 2~3주 전부터 상승 — 오늘 기준 2~4주 내 다가오는 것을 선점: 벚꽃(3~4월) · 장마/폭염 대비(6~8월) · 추석 연휴 영업/교통(9~10월) · 단풍/등산(10~11월) · 김장/겨울축제(11~12월) · 설날(1~2월) · 비자/K-ETA 시행일 · 대형 콘서트/페스티벌 티켓팅. 이벤트 헤드 + 외국인 실용 각도(예약 방법·준비물·운영 시간)로 조합 후 엔진 A로 수요 확인.

→ 3개 엔진 합산 후보 10~15개 수집 (출처 엔진을 로그에 표기).
→ 후보가 빈약하면 그날은 트랙 L 로직(무검색)으로 대체하고 로그에 "S 후보 없음 → L 대체" 기록.
후보 비교 우선순위: ① 수요 증거 가능성 ② Foreigner Test 적합도 ③ 실용성.
광고단가(CPC)는 점수 축이 아니며 동점 시 타이브레이커로만 사용.

## STEP 3 — Duplicate Check + Foreigner Test & Shortlist 확정 (검색 이전, 최우선 필터, v1.20)
STEP 2 후보 전체에 대해 검색 없이 세 필터를 적용한다:
① 중복 대조 (v1.21 — 각도 기반 재정의): 발행 목록과 비교해 핵심 키워드 2단어 이상이 겹치는 후보를 1차로 추린 뒤, 그중 같은 대상·같은 질문·같은 목적(각도)을 다루는 경우만 최종 제거한다 — 단어만 겹치고 각도가 다르면 중복이 아니다. STEP4-B GAP 판정과 동일 기준.
② Foreigner Test (지침서 0-2): 3개 문항 모두 Yes가 아니면 제거 (트랙 S·L 공통)
③ (v10.14) '한국 자체' 테스트: 주제가 한국의 문화·장소·음식·시스템에 관한 것인가? 작품·시즌·배우 뉴스 그 자체면 제거 — 한국 요소로 전환된 각도만 통과

- 통과 후보 0개 → STOP: ⚠️ 경고 로그 + 사용자 알림 (재브레인스토밍 금지, 그날 종료)
- 통과 후보 있음 → 우선순위(수요 증거 가능성 → Foreigner Test 적합도 → 내부 링크 연결성) 순 정렬, **상위 2~3개를 최종 숏리스트로 확정**하고 나머지는 예비 리스트로 보관 (v1.20 — STEP 4-B가 비교·선정 방식으로 바뀌면서 비교 대상이 필요해짐)

## STEP 4 — Web Validation + Gap Analysis (WebSearch는 여기 4-B에서만, v1.20)

**[4-A] 수요 검증 — WebSearch를 쓰지 않는다 (v1.20, 필수 관문)**
숏리스트 1순위부터 순서대로 검증:
1. 구글 자동완성 API WebFetch → 영어 키워드 조합이 실제 노출/논의되는가? + 서브키워드 후보 2~4개 수집
2. 노출 없으면 대체 증거: `https://www.reddit.com/search.json?q={영어 키워드}&t=year` (알려진 취약 소스 — 1회만 시도) → 최근 1년 내 동일 질문 3건 이상, 또는 Trends 신호
→ 어느 쪽도 없으면 해당 후보 탈락 → 숏리스트/예비 리스트 다음 순위로 이동해 4-A 재시작 (무료, 몇 번이든 반복 가능).
4-A를 통과한 후보가 2개 모일 때까지(또는 리스트 전체 소진까지) 반복한다.
→ 리스트 전체를 다 써도 4-A 통과 후보가 0개면 STOP: ⚠️ 경고 로그 + 사용자 알림 (STEP3의 0개 상황과 동급).
검증 생략 후 진행 절대 금지 — 단, 검증 수단은 항상 무료(WebFetch/Bash/대체 신호)이며 WebSearch를 쓰지 않는다.

**[4-B] 공백 실측 — 4-A 통과 후보 중 경쟁이 가장 적은 1개를 고르는 선정 절차 (v1.20)**
쿼리: `"{FOCUS_KEYWORD}" -site:koreaplug.com`
1. 4-A 통과 후보 1순위로 검색 1회 실행.
2. 공백 판정: 구글 1페이지에 전용 영어 정리글 3개 이상(트랙 S) / 대형 여행블로그·공식기관 도배(트랙 L) → 포화.
3. 통과(미포화) → 그대로 채택, 종료 (예산 1회만 소모). 같은 검색 결과에서 블로그/가이드형 상위 2개 URL 확보 (Reddit·TripAdvisor·포럼 제외 — 정리글만. 추가 검색 금지).
4. 포화 → 4-A 통과 후보 2순위로 검색 1회 더 실행. 두 결과를 비교해 경쟁이 상대적으로 더 적은 쪽을 채택한다 (둘 다 포화라도 반드시 하나는 채택 — 완벽한 블루오션을 요구하지 않는다, v1.20).
→ 이 절차는 항상 최대 2회 안에 승자를 정하고 끝난다. 4-A 통과 후보가 1개뿐이면 비교 없이 그 후보로 검색 1회만 실행하고 결과를 GAP 재료로 활용한다 (탈락시키지 않음).

**[4-C] WebFetch — 상위 2개 URL 읽기 (차단 시: 4-B 검색 결과의 제목·스니펫으로 경쟁글 구조를 파악)**
H2/H3 헤딩 전체 / 도입부 접근 각도 / 수치·출처·경험 서술 유무

**[4-D] GAP_REPORT 생성**
✅ 경쟁글 공통 커버: [항목] → STEP 5에서 기본 포함
⭐ 경쟁글이 빠뜨린 각도: [1~2개] → STEP 5 H2로 반드시 반영 (없으면 발행 금지)
🚫 경쟁글과 완전 동일한 H2 구성 → 그대로 쓰지 말 것
⚠️ 정리글 없이 Reddit/포럼만 있는 경우 → ⭐ "전용 정리글 자체가 없음 — 실측/경험 중심 구조로 작성" 후 계속 진행
⚠️ 4-B에서 포화 후보를 그대로 채택한 경우(비교 후에도 경쟁 존재) → ⭐ "경쟁 존재 — 차별화 각도를 평소보다 강하게 반영, 개인 경험/실측 중심으로 승부" 후 계속 진행 (v1.20)

## STEP 5 — Write the Blog Post (스킬 2종 필수 적용 — 지침서 2-6)
**[5-0] Skill `create-viral-content` 호출 — 구조·훅 단계 (초안 작성 전)**
- SEO Title·H1: 제목 후보 10개 이상 생성 → 호기심/구체성/감정 3축 스코어링(각 0~3, 합 7점 이상만 채택)
- INTRO 첫 문장: Hook Architecture(Prediction+Stakes / Before-After Compression / 문제 직격 중 택1)
- 클로저: engagement bait 금지, 독자가 지금 할 행동 중심
- 정제 패스 최소 3개: Skeptic → Scroller → Editor

**[5-1] 본문 작성 — 지침서를 STEP 1에서 이미 읽었으므로 각 Phase를 직접 참조하여 실행:**
- 키워드 전략 → [Phase 1-0 → 1-4]: 트랙별 규칙(S=2단어 이하 / L=3~5단어 질문형), 서브키워드는 4-A 수집분 기반 2~4개 확정. AI 임의 조합 절대 금지.
- 대표 이미지 → [Phase 1-5]: Unsplash 고유 ID 탐색 후 URL 삽입.
- 기본 메타 정보 → [Phase 2-1]: 표 형식으로 Slug, SEO Title, Meta Description, Focus Keyword, Sub Keywords 작성.
- HTML 본문 → [Phase 2-3]: 필수 템플릿 구조 준수. TOC는 `<!-- TABLE OF CONTENTS -->` 플레이스홀더 유지.
- 단어수·밀도·링크 → [Phase 2-5]: 1,500~2,000단어, 밀도 0.5~0.8%, 외부 링크 포함, 내부 링크 포함.
- 테마 컬러 → [Phase 7]: 카테고리별 헥사코드 적용.
- GAP_REPORT ⭐ 각도를 H2 1개에 반드시 반영.

**[5-2] Skill `avoid-ai-writing` 호출 — 최종 패스 (HTML 완성 직후, Notion 업로드 전)**
- voice profile: casual~warm, 구어체(bar test) 유지 — 단 **1인칭(I/My)은 실제 수행한 행위에만** 사용한다 (v10.17, 작성 가이드 2-5 문체 규칙). 겪지 않은 일화를 문체 장치로 지어내지 않는다
- 균일 문장 길이·기계적 전환어(Furthermore/Moreover)·과잉 열정 표현·engagement bait 제거
- 수치·고유명사·링크·HTML 구조는 보존하고 문체만 교정

**[5-3] 교정 후 [Phase 5-3] Focus Keyword 배치 체크리스트 + [Phase 5-5] AEO·GEO 체크리스트 교차 검증.**

## STEP 6 — Create Notion Page
⚠️ parent는 반드시 tool call의 최상위 파라미터로 지정 (pages[] 배열 내부에 넣으면 오류).
[Phase 7] 참조 → 글 카테고리에 맞는 Notion Page ID 하위에 새 페이지 생성.
제목: Blog #XX — {post title} (XX = 현재 최고 번호 + 1)
2개 섹션 (섹션3 배포 JS 생성 금지 — wordpress_draft가 REST API로 직접 배포):
[섹션 1]: [Phase 3-2] 표 구조 생성 + 데이터 입력. draft 일자는 반드시 공란.
[섹션 2]: 완성된 HTML 전체를 ```html 코드 블록으로 삽입.

## STEP 7 — Update the Published Posts List
Page: https://www.notion.so/33cbfe4a2ae181b9a743cb7c194dea7f
① 헤더 카운트 업데이트
old_str: "전체 N개 글 현황 (YYYY-MM-DD 기준)"
new_str: "전체 N+1개 글 현황 ({today} 기준)"
② 표에 새 행 추가
⚠️ 실행 전 페이지 re-fetch 필수 — 마지막 행 실제 셀 값 확인 후 old_str 구성.
⚠️ old_str은 `<td>` 태그 포함 전체 행 그대로 복사 (bare text 불가).
업데이트 후 재fetch로 #XX 행 추가 여부 검증 (성공 응답만으로 신뢰 금지).
new_str: old_str + 아래 새 행:
`<tr><td>{XX}</td><td>{Post Title}</td><td>{한줄 요약}</td><td>—</td><td>{카테고리이모지+이름}</td><td>{아웃링크번호}</td><td>—</td><td>{작성일자}</td><td></td></tr>`
⚠️ 마지막 열(draft 일자) 공란 유지 — wordpress_draft 루틴이 WP 배포 시 자동 기재
⚠️ SEO 점수 열 "—" 유지
⚠️ 카테고리: 🍜 Food / 🚌 Travel / 🎭 Culture / 🏠 Lifestyle
--
✅ 자동 발행 실행: {today_kst}
신규 draft: #{XX} {Post Title} (Notion 등록 완료, WP 배포 대기)
SEO 개선: 없음 | 오류: 없음
다음 실행: {tomorrow} 07:00 KST

## STEP 8 — Report
✅ KoreaPlug Daily Automation — {today_kst} 완료
🔍 주제 탐색: 브레인스토밍 {M}개 / 중복·Foreigner Test 통과 {K}개 / 숏리스트 {J}개 / WebFetch 상태: {정상 또는 차단} / WebSearch 총 {N}회 (한도 2) / 트랙: {S 또는 L} / 수요 증거: {자동완성 API·Reddit JSON·Trends RSS·엔진C·모델지식 중 확인된 것}
🎯 스킬 적용: create-viral-content (제목 스코어 {X}/9, 정제 패스 {n}개) / avoid-ai-writing (최종 패스 완료)
📝 선택 주제: [주제명] / 제외 후보: [중복·Foreigner Test 탈락 vs 수요검증 탈락 vs 4-B 비교탈락 구분하여 기록]
📂 위치: [카테고리명] — Blog Posts
🔗 Notion URL: [생성된 페이지 URL]
📋 목록 업데이트: 헤더 #{XX} + 표 행 + 로그 추가 완료
💡 한줄 요약: [핵심 내용]
📤 HTML 작성 완료 — wordpress_draft 루틴이 다음 실행 시 자동 배포합니다.
🪝 훅 점검: 직전 10개 제목 중 이번 제목과 동일 훅 사용 {n}회 (규칙상 2회 이상이면 다른 훅으로 교체 — 교체했으면 명시. 예: "The Real Reason" 남용 재발 방지)
📐 주제 유형: {문화 퀴크 / 여행 실용 / K-콘텐츠 파생 / 거주 행정} — 거주 행정이면 최근 7일 내 행정 주제 발행 수 함께 기록 (주 1회 한도)
📦 백로그: 이번 실행에서 검토 {건수} / 채택 {0 또는 1} / 상태 갱신 완료 여부
⚠️ (해당 시) STEP 1 GitHub 지침서 조회 실패/지침-루틴 상충 등 SSOT 관련 이슈 기록.

## ⚠️ 전제 조건
| 항목 | 조건 |
|---|---|
| 실행 환경 | Claude Code on the web — Chrome MCP 없음. WebFetch/Bash 가능 시 수집 기본 수단, 불가 시 WebSearch 자동 대체(정상 동작). Reddit은 알려진 취약 소스로 1회만 시도(v1.20) |
| GitHub 접근 | 지침서 저장소(`leejc0404/blog`, 파일 `KoreaPlug-Writer.md`)에 대한 WebFetch 읽기 접근 필요. 저장소가 비공개이거나 세션 네트워크 정책으로 GitHub 자체가 차단된 경우 STEP 1에서 STOP하고 사용자에게 알린다 (지침 내용을 추측으로 대체하지 않음) |
| Notion 권한 | MCP 커넥터가 4개 카테고리 페이지 + 발행 목록 페이지 편집 권한 보유 (지침서는 더 이상 Notion에서 읽지 않음) |
| WebSearch 한도 | 글당 최대 2회, STEP 4-B 전용 (STEP 1~4-A는 WebSearch 미사용). 두 블로그 합산 최대 4회/일, 실제 플랫폼 한도(5회) 내. 예산 소진 시에도 STOP 아님 — 4-B는 숏리스트 내 비교로 항상 승자를 정함. 진짜 STOP은 STEP3·4-A에서 채택 가능한 후보가 0일 때, 또는 STEP1 GitHub 지침서 조회 자체가 실패했을 때뿐 |
| 스킬 | create-viral-content(STEP 5-0) + avoid-ai-writing(STEP 5-2) 필수 적용 |
| 카테고리 색상 | Phase 7 참조 (Culture=purple / Lifestyle=#16a34a / Food=red / Travel=yellow) |
| 중복 기준 | 기존 게시물 제목과 포커스 키워드 2단어 이상 겹침 시 중복 처리 (STEP 3에서 웹서칭 이전에 선행 적용) |
