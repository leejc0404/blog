[루틴 : aipick-weekly — 네이버 블로그 ironeye 「먹어보고 따져본 리스트」 AI 리뷰분석 · **월·목 03:00** 실행 · 제품군 N개(월 4 · 목 3) → 수집 → 분석 → 글 N편 → 임시저장 업로드 → 사용자가 매일 1편 발행]

v2.6 · 2026-10-10 (업로드를 **임시저장 전용**으로 전환 · 발행된 글 재업로드·삭제 금지 · STEP 0 ⑤ 색인 점검 `idx_check.py` — 가이드 v2.6 3-7·5-3) · v2.5 · 2026-10-08 (STEP 10 네이버 클립용 세로 영상 — HyperFrames `review_bars` · 선택 · **STEP 9 리포트까지 끝난 뒤에만** · 업로드 큐와 무관 · 실패·시간 부족이면 건너뜀 · 가이드 v2.5 4-C) · v2.4.3 · 2026-10-08 ("추천" 금지 → 필수 아님으로 완화) · v2.4.2 · 2026-10-08 (2-C BT 조회어에서 "추천" 제거 — 가이드 3-1-⑦) · v2.4.1 · 2026-10-08 (STEP 2-S 검색광고 `naver_sa.py` 월간 검색량·연관키워드 → ④축 수치 · 가이드 v2.4.1) · v2.4 · 2026-10-08 (STEP 2-R 데이터랩 인기검색어 40·50·60대 `naver_rank.py` 1순위 · STEP 2-T 시기 트리거 WebSearch · 후보 절반 이상 ①에서 · 가이드 v2.4 Phase 0) · v2.3 · 2026-10-06 (월·목 03:00 2회 실행(PC가 08:00 전후 꺼짐 → 07:30 마감) · 월 4편/목 3편 · 공개 예정일 큐 이름 · SR40·TR40 관문 — 가이드 v2.3) · v2.2 · 2026-10-06 (석PD 카피 법칙 01 반영: 독자 우선 제목 검사 · 도입 3단 · 카드 Q+V1~V3 `cards_v22.py` · check.py 7항목 · 가이드 v2.2) · v2.1 · 2026-10-05 (1회전 실측 반영: SR 실측을 STEP 2 맨 앞으로 · 서버 실행기 `tasks\run` · 확장 자동 리로드 · 카드 7장·captions.json · 링크 카드 · 형식 A/B/C · 쿠팡 보류) · v2.0 2026-10-02 (단일 스케줄·순차 실행·3편/회) · v1.4 네이버 리뷰 · v1.3 확장 자동 수집 · v1.1 ironeye 통합 · 위치: `C:\Users\win\Documents\Claude\naver_blog\` (GitHub 미사용)

*월·목 03:00 트리거 1개(같은 프롬프트)가 아래 STEP 0~9를 **한 세션에서 순서대로** 끝낸다. ⏰ **마감 07:30 KST** — 사용자 PC가 08:00 전후 꺼지므로 07:30까지 못 끝낸 STEP은 `run_state.json`에 남기고 STEP 8·9(현황표·리포트)만 하고 종료한다(다음 회차 STEP 0이 이어서 처리). 대기 루프마다 현재 시각을 확인한다. **편수 N**: 실행 요일이 월요일이면 4, 목요일이면 3(그 밖의 요일에 수동 실행하면 3). **공개 예정일**: 월 회차 = 화·수·목·금, 목 회차 = 토·일·월 — 확정 순서(1→N)대로 배정하고 큐 폴더명·현황표에 적는다. 발행은 사용자가 매일 1편 수기로 한다(루틴은 임시저장까지만, 발행된 글 재업로드·삭제 금지). 중간에 끊기면 `run_state.json`을 보고 끊긴 STEP부터 이어서 한다(수동 재실행 또는 다음 주 회차가 먼저 처리).
날짜: 실행 시점의 실제 KST 날짜. `RUN = YYYYMMDD`(이번 회차 키).

⚠️ **역할 경계 — 이 루틴은 도구다.** 판정 기준·수치·품질 기준의 SSOT는 `AIPick-Writer.md`(이하 가이드)다. 이 루틴은 운영 절차와 실행 자산만 정의한다.
- ⛔ 가이드의 수치를 이 루틴에 복사하지 않는다. 조항 번호로만 참조한다.
- 상충이 발견되면 가이드를 따르고 STEP 9 리포트에 기록한다.

⚠️ **실행 환경**: Cowork 예약 작업 · **사용자 PC(C:\Users\win) 필요**. PC 셸: `mcp__remote-devices__device_bash`. 파이썬 `py -3.12`.
- 작업 폴더 `NB = C:\Users\win\Documents\Claude\naver_blog`
  - `tasks\run\` — 루틴이 쓰는 **스크립트 실행 요청**(JSON `{"script":"naver_sr.py","args":["{RUN}"]}`). PC 셸(VM)은 외부망·localhost가 없으므로 **큐 서버(server.py)가 10초마다 읽어 Windows에서 `py -3.12 scripts\{script}`로 실행**하고 결과를 `tasks\run_done\{같은 이름}.json`(status·stdout_tail)에 쓴다. 허용 스크립트: `scripts\*.py` 전부(`_`로 시작하는 파일 제외 — 서버가 파일 존재로 동적 판정) + `ping` + `restart`(서버 자기 재시작, 코드 변경 반영)
  - `tasks\pending\` — 루틴이 쓰는 수집 작업(JSON). **업로더 확장이 1분마다** 읽어 커넥트·네이버 스토어·쿠팡 페이지에서 실행하고 결과를 `inbox\`에 넣은 뒤 `tasks\done\`로 옮긴다
  - `inbox\{RUN}_{n}_{제품군}\` — 수집 결과(`connect.json` · `naver_*.json` · `coupang_*.json` · `links.json`) + 사용자 수기 `links.txt`
  - `out\{RUN}_{n}_{제품군}\` — 원고 패키지 (`clip\` — STEP 10 클립 영상, 선택 · 업로드 큐와 무관)
  - `upload_queue\{RUN}_{n}_{제품군}\` — 업로드 대기(확장이 이름순으로 5분 간격 **임시저장** — 발행은 사용자)
  - `radar\{RUN}.md` — 채점표 · `run_state.json` — 이번 회차 진행 상태 · `현황표.md` — 글·실행 로그 · `scripts\` — 분석·카드 스크립트
- 확장·서버 상태 확인: PC 셸에서는 localhost에 닿지 않으므로 **`upload_logs\{오늘}.log`의 최근 10분 내 기록**(서버 시작·/peek·/run 등)으로 살아 있는지 판단한다. 기록이 없으면 `tasks\run\{RUN}_ping.json`(`{"script":"ping"}`)을 써서 60초 안에 `run_done`이 생기는지로 확인. 서버가 꺼져 있으면 **STEP 2까지만 하고**(채점·작업 투입) 리포트에 `⛔ 큐 서버 꺼짐 — 수집 대기`를 적고 종료한다. 다음 회차가 `tasks\done`을 보고 이어간다.
- PC 미연결 → 아무것도 쓰지 않고 한 줄로 종료: `⏸️ PC 미연결 — 다음 실행에서 처리`.

⚠️ **자격증명**: `C:\Users\win\Documents\Claude\pw.txt`는 스크립트가 Windows에서 읽는다(루틴은 값을 보지 않는다). 값은 로그·리포트·파일에 출력 금지. SR: `NAVER_APIGW_KEY_ID/KEY`(API HUB) · 검색량: `NAVER_SA_CUSTOMER_ID/ACCESS_LICENSE/SECRET`(검색광고) · BT: 사이트 릴레이(`ONEANDZERO_WP_USER/APP_PASSWORD`, `X-O1-NKID/NKEY`). 없으면 해당 지표 `미관측`.

⛔ **금지**: 루틴이 직접 네이버·쿠팡에 접속하거나 글쓰기 화면을 조작하는 것(전부 확장이 한다). 기존 맛집 글·맛집 파이프라인 파일(`naver_blog\guides`, 맛집 `inbox`) 수정(가이드 A-5). inbox 원본 수정·삭제(복사본으로 작업).

🔢 **회차당 글 수 N = 월요일 4 · 목요일 3 · 그 외 요일(수동 실행) 3** (바꾸려면 이 줄만). 사용자가 공개 예정일 아침에 1편씩 수기로 공개한다(가이드 3-7).

---

📅 **예약 설정 (Cowork 예정된 작업 1개 — 이 컴퓨터 필요)**

| 이름 | 시각 (KST) | 반복 | 비고 |
|---|---|---|---|
| aipick-weekly | 월·목 03:00 (`CRON_TZ=Asia/Seoul 0 3 * * 1,4`) | 매주 2회 | 이 루틴 전체. 소요 2~3시간(월 4편은 ~3.5시간, 수집 대기 포함) · 07:30 마감 |

- 확장은 스케줄이 없다. 1분마다 `tasks\pending`·`upload_queue`를 보고 있을 때 실행한다. 월·목 03:00~07:30에 **PC·크롬·큐 서버가 켜져 있어야** 한다(사용자 PC는 새벽에만 켜져 있고 08:00 전후 꺼진다).
- 재실행: 끊긴 회차는 Cowork에서 작업을 **지금 실행**하면 `run_state.json` 기준으로 이어간다.

---

STEP 0 — 준비 · 재개 판정

① `TODAY_KST`·`RUN` 확정. `NB` 존재 확인(없으면 폴더 구조·`현황표.md` 생성).
② `run_state.json` 읽기: `{run, step, groups:[{n, name, inbox, status}], started_at}`. `run == RUN`이고 `step < 9`면 **재개** — 그 STEP부터. 아니면 새 회차로 `{run: RUN, step: 0}` 기록. (각 STEP 끝에 `step`을 갱신한다.)
③ **지난 회차 뒷정리**: `upload_queue\`에 결과 없는 폴더(지난주 미업로드)가 있으면 리포트에 적고 그대로 둔다(확장이 켜지면 올라간다). `upload_posted\*\result.json`을 읽어 현황표 상태를 갱신한다: `drafted` → `임시저장됨`, `draft_unknown` → `임시저장 확인 필요`, `failed`는 사유 요약. (구 방식 `posted`는 `비공개 업로드됨`+URL) 상품별 클릭·구매가 `radar\20261005_형식테스트.md`에 적혀 있으면 가이드 6-0 판정안을 리포트에 넣는다.
④ `tasks\done\`에 지난 회차 실패 작업이 있으면 리포트에 적는다(같은 작업 자동 재투입 금지, 연속 2회 실패면 "스니펫 선택자 점검 필요").
⑤ **색인 점검**(가이드 5-3): 현황표에서 상태 `공개`이고 공개 후 3일 이상 지난 글의 **제목 전체**를 `tasks\run\{RUN}_idx.json` ← `{"script":"idx_check.py","args":["{RUN}","{제목1}","{제목2}",…]}`로 조회한다(결과 `radar\{RUN}_idx.json`, 상위 30위 안 ironeye 글 여부). 30위 밖이면 리포트에 `⚠️ 검색 누락 의심: {제목}`을 적는다. **누락이어도 재업로드·삭제는 하지 않는다**(가이드 3-7). 실패면 `색인 미관측`.

STEP 1 — 가이드 읽기

- PC 셸로 `NB\AIPick-Writer.md`(반드시 준수) · `C:\Users\win\Documents\Claude\blog\0and1Life-Writer.md`의 **5-6 문체 지문**(가이드 3-5) · `현황표.md`(최근 8주 제품군 — 가이드 0-6 재탕 금지, 직전 10개 제목 — 가이드 3-1 훅 중복, 공개 글 목록 — 내부 링크 후보). 가이드를 못 읽으면 아무것도 쓰지 않고 종료.

STEP 2 — 주제 레이더: **지금 검색되는 것 먼저**(가이드 Phase 0 머리말 — 전체 공정에서 가장 중요한 단계, 시간을 아끼지 않는다)

2-R. **데이터랩 인기검색어 40·50·60대** (가이드 0-2 ①) — 가장 먼저
```
tasks\run\{RUN}_rank.json  ←  {"script":"naver_rank.py","args":["{RUN}","100"]}
→ radar\{RUN}_rank.json (분야별 TOP100 + 이전 7일 대비 신규·상승·유지·하락) · radar\{RUN}_rank.md (요약)
```
- 60초 간격 확인, 최대 5분. `rank.md`의 **🔥 신규·상승** 줄을 먼저 읽고, 6분야 TOP100에서 **40대 이상 제품군 단위 키워드**를 뽑는다(브랜드·모델명은 제품군으로 올리고 원 표기는 제목·태그 재료로 `radar\{RUN}.md`에 적어 둔다). 가이드 0-6 제외 제품군은 뺀다.
- 실패(`status: err`)면 리포트에 `⚠️ 인기검색어 미관측`을 적고 2-T·2-0으로 후보를 채운다(이 경우 ④축은 트리거로만 채점).

2-T. **시기 트리거** (가이드 0-2 ②) — WebSearch 2~3회
- "이번 주 날씨 전망 한파/첫눈/폭염/장마/황사" · "{이번 달} 기념일 행사" · 절기 — 오늘~14일 안에 걸리는 트리거를 `radar\{RUN}.md`에 출처 1개와 함께 적는다. 트리거에 맞는 제품군(예: 첫 한파 → 전기매트·발열내의·온수매트)은 후보에 넣고 0-5 ④축 가점.

2-0. 후보 확정 목록: **2-R 신규·상승·TOP100에서 절반 이상** + 2-T 트리거 제품군 + 보조(가이드 0-4 시즌 캘린더 피크 15~60일 · 현황표 실적 인접 · `radar\trend_cands.txt` 사용자 수기 — 있으면 반드시 포함). 후보는 N+5개 이상(월 9~12, 목 8~10). 후보마다 쇼핑 분야명과 출처(①신규/①상승/①TOP/②트리거/④보조)를 붙여 `radar\{RUN}_sr_cands.json`에 `[["등산스틱","스포츠/레저"], …]`로 쓴다(분야명→코드 표는 `scripts\naver_sr.py`의 `CID`).

2-S. **월간 검색량** (가이드 0-2 ①-S) — 후보 전부
```
tasks\run\{RUN}_sa.json  ←  {"script":"naver_sa.py","args":["{RUN}"]}      (인자 없으면 radar\{RUN}_sr_cands.json의 키워드를 쓴다)
→ radar\{RUN}_sa.json (키워드별 pc·mo·total·comp·related 10) · radar\{RUN}_sa.md
```
- 60초 간격 확인, 최대 5분(후보 12개 ≈ 15초). `total`(PC+모바일)을 채점표 ④축 기준값으로, `related`를 3-1-⑥ 제목·태그 재료로 `radar\{RUN}.md`에 적는다. 실패면 `검색량 미관측`으로 적고 ④는 2-R·2-T로만 채점(가이드 0-5).

2-A. **SR 실측** (가이드 0-3) — 검증 관문
```
tasks\run\{RUN}_sr.json  ←  {"script":"naver_sr.py","args":["{RUN}"]}
→ 서버가 실행 → tasks\run_done\{RUN}_sr.json (status ok) → 결과 radar\{RUN}_sr.json
```
- 60초 간격으로 `run_done` 확인, 최대 10분. 결과의 후보별 `SR`·`SR40`·`TR40`·`trend`(가이드 0-3). **SR-C, SR40 < 60%, trend=하락(시즌 피크 ≤14일 예외)은 여기서 탈락**, 통과 후보만 2-B 이후로. 세 값을 `radar\{RUN}.md` 채점표에 같이 적는다.
- 실패·미관측 후보만 2-B 폴백(`SR-추정(AC)`). 실측된 후보에는 시니어 신호 15% 관문을 적용하지 않는다(가이드 0-3).

2-B. 자동완성 — 실존 문구 · 시니어 조합 (태그·제목 재료, 가이드 3-8)
```
tasks\run\{RUN}_ac.json  ←  {"script":"naver_ac.py","args":["{RUN}","{키워드1}","{키워드2}",…]}
→ radar\{RUN}_ac.json   (추가 문구는 radar\{RUN}_ac_queries.txt → _ac2.json)
```
- 후보당 `{키워드}`와 `{키워드} 부모님`. 응답 문구를 변형하지 않는다.

2-C. 블로그 경쟁 문서 수 BT — 기록용 (관문 아님)
```
tasks\run\{RUN}_bt.json  ←  {"script":"naver_bt.py","args":["{RUN}","{키워드1}","{키워드1 연관 상위 1개}",…]}   ("추천" 접미는 필수 아님 — 검색량 큰 표기 우선, 가이드 3-1-⑦)
→ radar\{RUN}_bt.json   (사이트 릴레이 https://0and1life.com/wp-json/o1/v1/naver-check 경유)
```

STEP 3 — 채점 · 제품군 N개 확정(월 4 · 목 3) · 1차 수집 작업 투입

- 가이드 **0-5 채점표**로 **SR-A·B 후보만** 점수. ④ 지금 수요는 2-S 월간 검색량을 기준으로 2-R(신규/상승)·2-T(트리거)로 가점, compIdx 높음+BT 10만↑이면 감점(가이드 0-5) — **④ 0점은 채택 금지**. ③ 수수료율·② 객단가·⑤ 리뷰 충분성은 아직 `미확인`(가채택) — 아래 3-B에서 커넥트 결과로 확정한다.
- 3-A. **상위 후보 N+2개**에 대해 `connect_search` 작업을 쓴다(확정 N개를 뽑기 위해 여유 2개):
  ```json
  {"type":"connect_search","keyword":"{커넥트 검색어}","inbox":"{RUN}_{n}_{제품군}"}
  ```
  파일명 `tasks\pending\{RUN}_{n}_connect.json`. `run_state.groups`에 N+2개를 `status: connect_wait`로 기록.
- 3-B. **대기** — `tasks\done\{RUN}_{n}_connect.json`이 N+2개 생길 때까지 60초 간격으로 확인, 최대 20분. (PC 셸에서 `py -3.12 -c "import time; time.sleep(60)"` 반복.) 20분 안에 안 끝난 후보는 `미관측`으로 둔다.
- 3-C. `inbox\…\connect.json`으로 ③②⑤ 확정 → 가이드 0-5 합계 9점 이상 중 **상위 N개 확정**(동점 규칙은 가이드: TR40 우선). N개 미만이면 있는 만큼만(최소 1개). 0개면 리포트 후 종료. 확정 순서 1→N에 **공개 예정일**을 붙인다(월: 화·수·목·금 / 목: 토·일·월).
- 출력 `radar\{RUN}.md`(채점표·확정·탈락 사유). `run_state.step = 3`.

STEP 4 — 2차 수집 작업 투입 · 대기

- 확정 제품군마다 모델 3~5개 선정(수수료율 상위 + 가격대 분산 + `review_count` 상위)하고 작업 3개를 쓴다:
  ```json
  {"type":"naver_collect","products":[{"name":"{커넥트 모델명}","url":"{product_url}"}],"inbox":"{RUN}_{n}_{제품군}","max_products":5,"max_pages":60}
  {"type":"coupang_collect","query":"{브랜드+모델명 또는 제품군}","inbox":"{같은 폴더}","max_products":4,"max_pages":60}
  {"type":"connect_links","models":["{모델명}…"],"inbox":"{같은 폴더}"}
  ```
  파일명 `tasks\pending\{RUN}_{n}_{naver|coupang|links}.json`. N개 제품군이면 작업 3N개. 확장이 순서대로 실행한다(한 번에 하나).
- **쿠팡 보류(가이드 1-2)**: 확장 탭에서 쿠팡이 차단되므로 `coupang_collect`는 **투입하지 않는다**(해결 전까지). 제품군당 작업 2개(naver_collect·connect_links), N개 제품군 = 2N개(월 8 · 목 6). 사용자 수기 쿠팡 스니펫 결과가 `inbox\…\coupang_*.json`에 있으면 병합한다.
- `naver_collect`는 상품 JSON API(originProductNo 기반)로 모델당 최대 1,800개를 받는다. `connect_links`는 커넥트 상품 검색 → 카드의 '링크 복사' → 클립보드 훅으로 전용 URL을 잡는다(15/15 성공 실적).
- **대기** — 투입한 작업 전부 `tasks\done`에 생길 때까지 60초 간격 확인, 최대 **100분**(월 4편은 **110분**) — 단, 07:30 마감이 먼저 오면 그때 중단. 시간 초과 시 완료된 제품군만 다음 STEP으로, 나머지는 `run_state`에 `collect_timeout`으로 남기고 리포트에 적는다(다음 회차 STEP 0에서 이어서 처리).
- `max_pages 60` = 모델당 리뷰 최대 약 1,800개. 더 필요하면 이 숫자만 바꾼다(수집 시간이 비례해 늘어난다).
- `run_state.step = 4`.

STEP 5-0 — 입력 점검 (제품군마다)

- `inbox\{RUN}_{n}_{제품군}\`에서 `connect.json`, `naver_*.json`(`connect_name`으로 모델 확정), `coupang_*.json`, `links.json`을 읽는다. 모델별로 두 출처를 합치고(가이드 2-1b) 출처별 리뷰 수 기록.
- 리뷰 파일이 **모델 2개 미만**이면 그 제품군은 `skipped`(리포트에 "리뷰 수집 부족")로 넘어간다.
- 모델 매칭(가이드 1-2): `naver_*.json`의 `connect_name` ↔ `connect.items[].name`(쿠팡이 있으면 `product_name`도). 불일치 모델은 분석에는 쓰되 추천 3선·링크에서 제외. `models.json`(key·name·short·connect_pid·price_won·commission_pct·link·connect_rating·connect_reviews)과 `meta.json`(product_group·category·labels·analysis_date)을 `out\…\`에 만든다.
- 원본은 `out\…\data\`로 복사해서 쓴다.

STEP 5 — 분석 (가이드 Phase 2) — 제품군마다

- `scripts\analyze.py`가 없으면 가이드 2-1~2-6 규격대로 만든다. 입력: 모델별 파일. 출력: `analysis.json`(제품별 N·평점·저평점 비율·재구매 비율·시니어 신호 수·제외 수, 추천 3선, 표본 라벨 비율).
- 주제 라벨링(가이드 2-5): 스크립트가 층화 표본을 `sample_{모델}.jsonl`로 뽑으면, Claude가 제품군 라벨 목록을 먼저 정하고 그 목록으로만 분류해 `labels_{모델}.json`으로 저장 → 스크립트가 비율을 집계해 `analysis.json`에 합친다.
- 표본 하한(가이드 2-4)에 걸리면 해당 섹션 생략 플래그를 `analysis.json`에 남긴다.
- 실행 순서(PC 셸에서 python3로 직접 실행 가능 — 외부망 불필요): `analyze.py load/stats/sample out\{폴더}` → Claude 라벨링(`labels_{key}.json`·`labels_{key}_neg.json`, 글자 코드 매핑은 `_lab.py`) → `analyze.py final` → `analysis.json`. Windows에서 돌릴 때는 `tasks\run`으로.

STEP 6 — 카드 이미지 (가이드 Phase 4) — 제품군마다

- `scripts\cards.py`: `analysis.json`·`models.json`만 읽어 **카드 7장** PNG(card1_summary · card2_reasons · card3_parents · card4_method · card5_pick1 · card6_pick2 · card7_pick3)를 `out\…\cards\`에 저장. 한글 폰트는 Windows `malgun.ttf`(VM은 Noto Sans CJK).
- `scripts\thumb.py out\{폴더} "훅1" "훅2"` → `cards\card0_thumb.png`(가이드 Phase 4 ⓪). 훅은 제목에서 뽑은 3~6단어 2줄(형식별).
- `scripts\cards_v22.py out\{폴더}` → `cards\card_quote.png`(인용 박스 Q) + `card_pick1_vs.png`~`card_pick3_vs.png`(✗✓ 비교 V1~V3). 입력: `analysis.json`(최다 반복 표현) · `models.json`(spec) · `meta.json`의 `benefit`(슬롯별 ✓ 문장, 없으면 만족 1위 라벨에서 생성). 라벨 태그·형광펜·다크/베이지 교차는 스크립트가 자동 적용(가이드 Phase 4-③). `thumb.py`도 좌상단 라벨 태그를 넣는다.
- `scripts\captions.py out\{폴더}` → `captions.json`(카드별 `alt`·`label`, 카드②③ `caption` 한 줄, Q·V1~V3 포함, 참고 사진이 있으면 `source` — 가이드 Phase 4·3-3 ⑤).
- 생성 후 카드 12장을 Read로 직접 열어 글자 깨짐·잘림·숫자 일치·라벨 태그를 눈으로 확인한다.

STEP 7 — 원고 (가이드 Phase 3) — 제품군마다

- **형식 배정**(가이드 3-3c): 이번 회차 N편에 A·B·C를 1편씩, 4편째는 기본형(판정 전까지 A형). 현황표에서 직전 회차 같은 제품군의 형식을 보고 겹치지 않게 한다. B형은 외부 사실을 WebSearch로 확인하고 `facts_allow.json`에 숫자·출처 기록.
- 제목 후보 10개 → 가이드 3-1 규칙 통과분 중 create-viral-content 3축 스코어 최고안. 키워드 표기는 `radar\{RUN}_rank.json`·자동완성에 실제로 나온 그대로(가이드 3-1-⑤). **3-1-④ 검사**: 키워드 다음 구절이 `리뷰|분석|AI|비교|모델`로 시작하면 탈락(독자 상황·얻는 것이 먼저, 리뷰 수는 쉼표·괄호 뒤).
- 본문 맨 앞에 `[카드0 삽입: card0_thumb.png]`, 이어서 **도입 3단**(질문 훅 → "보통이라면" 대조 → 전환 한마디 + `[카드Q 삽입: card_quote.png]`) → 결론 문단 → 가이드 3-3 순서로 작성(링크 5 + `[링크카드 삽입: URL]` 3 + 추천 슬롯마다 `[카드V{n} 삽입: card_pick{n}_vs.png]` + 카드②③ 아래 `<p class="cap">` 설명줄 + 마무리 공감 1줄 + 마지막 줄 11pt 대가성 문구) → avoid-ai-writing → 0and1Life 5-6 문체 지문 대조(가이드 3-5 조정 ⑥ 고객 문장 우선 포함).
- 출력 파일(`out\{폴더}\`):
  - `제목.txt` · `태그.txt`(가이드 3-8) · `카테고리.txt`(가이드 A-5)
  - `원고.html` — 업로더 입력. 이미지 자리는 `[카드1 삽입: card1_summary.png]`, 링크 카드 자리는 `[링크카드 삽입: https://naver.me/…]`
  - `captions.json` — STEP 6 산출(alt·label·caption) · `facts_allow.json` — B형일 때
  - `원고.txt` — 같은 내용의 텍스트판
  - `점검.md` — STEP 7-B 결과
- 7-B. **품질·SEO·URL·구매전환 점검** — `python3 scripts\check.py out\{폴더} {핵심키워드} [--variant]`(B·C형은 `--variant`). 가이드 **Phase 5** 전 항목을 코드로 대조하고 `점검.md`·`원고.txt`를 쓴다. v2.2 추가 7항목: ① 제목 독자 우선(3-1-④) ② 도입 3단 순서(첫 3문단: `?` 포함 문장 → "보통" 포함 문장 → 벽돌색 전환 문장) ③ `[카드Q 삽입]` 1개 ④ `[카드V1~V3 삽입]` 3개 ⑤ 카드 PNG 12장 존재 ⑥ 대가성 문구 바로 위 문장이 공감 1줄(`!`·`?`·"하세요" 없음) ⑦ 리드 마그넷 문구 없음("댓글 남기면", "DM"). 판정은 가이드 5-4. 통과 전에는 큐에 넣지 않는다.

7-C. **업로드 큐 넣기** — 7-B 판정이 통과일 때만.
- 대상: `upload_queue\{RUN}_{n}_{제품군}_{공개예정일MMDD}\` (확장이 **이름순**으로 5분 간격 **임시저장** — 발행은 사용자가 예정일 아침에 임시저장함에서 수기로)
- `python3 scripts\make_post.py out\{폴더} upload_queue\{RUN}_{n}_{제품군}_{공개예정일MMDD}` — `post.json`: `title`·`category`(A-5 표기, 업로더가 기호 차이 무시·반영 검증)·`tags`·`visibility: draft`(기본값)·`blocks`(`html`(style_html.py로 가독성 스타일 적용 + `<table>`→세로 비교 목록 변환, 가이드 3-2) / `image`{file, alt, label} / `link`{url}). `[카드Q 삽입]`·`[카드V{n} 삽입]`도 `[카드N 삽입]`과 같은 image 블록으로 변환. 카드 PNG 12장을 같은 폴더로 복사하고, 임시저장에는 카테고리·태그가 들어가지 않으므로 `발행정보.txt`(제목·카테고리·태그 한 줄씩)를 같은 폴더와 `out\{폴더}\`에 쓴다. `--private`(비공개 발행)는 쓰지 않는다.
- 큐 폴더명은 **항상 새 이름**(확장이 처리한 폴더명을 기억한다). 재시도(`_v2` 접미사)는 **임시저장이 실패(`failed`)했을 때만**. 이미 발행된 글은 어떤 이유로도 다시 큐에 넣지 않는다(재업로드·삭제 금지 — 고칠 점은 리포트에 적고 사용자가 편집기에서 수정, 가이드 3-7). 잠가 둘 폴더는 `_`로 시작.
- 전용 링크는 `links.json`(확장 결과) → `links.txt`(사용자 수기) 순으로 치환. 자리표시(`[커넥트 링크:`)가 남은 원고는 큐에 넣지 않고 `out\`에만 둔다(다음 회차 STEP 0에서 `links.txt`가 생겼으면 치환 후 큐에 넣는다).
- 넣은 뒤 `post.json` 재검증: ① JSON 파싱 ② 이미지 전부 존재 ③ 제목·카테고리·태그 비어 있지 않음 ④ 자리표시 없음. 실패하면 `upload_queue\_hold\…`로 옮기고 사유 기록.

STEP 5~7은 **확정 제품군마다 반복**한다(①→…→N). 각 제품군이 끝날 때마다 `run_state.groups[n].status = queued|hold|skipped`로 갱신해 중간 재개가 가능하게 한다.

STEP 8 — 현황표 갱신

`현황표.md` 형식(첫 실행 때 생성):

```
# AIPick 현황표

## 글 목록
| # | 분석일 | 제품군 | 카테고리 | 제목 | 분석 리뷰 수 | 채점(SR40·TR40) | 형식 | 커넥트 링크 | 상태 | 공개 예정일 | 공개 URL | 클릭 | 구매 | 수수료 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 실행 로그
- 실행: YYYYMMDD(월|목) · 제품군 N · 큐 n편 · 소요 n분
```

- 새 행(편당 1행): 상태 = `큐 대기`, **공개 예정일** 열에 배정일(MM/DD 요일). 확장이 임시저장하면 다음 회차 STEP 0에서 `임시저장됨`으로 갱신. 사용자가 발행 후 `공개`와 공개 URL을 채운다(루틴은 상태를 `공개`로 바꾸지 않는다).
- 다음 실행부터, 상태 `공개`인 행의 URL 응답을 확인해 200이 아니면 리포트에 남긴다(가이드 5-3 마지막 항목).

STEP 9 — 리포트 (SendUserMessage로 전송 — 사용자가 없을 수 있다)

```
📝 AIPick 실행 — {TODAY_KST} ({월|목} 03:00 회차 · N={n}) · 소요 {n}분 · 재개 {여부}
🎯 채택 제품군(공개 예정일 순): ① {제품군} {점수}/15 · 출처 {①신규/①상승/①TOP/②트리거} · SR40 {n}% TR40 {n} → {MM/DD 요일} · ② … · ③ … (· ④ …)   (탈락: {제품군 — 사유} …)
🔎 주제 레이더: 인기검색어 {6분야 TOP100 · 신규 n · 상승 n} · 시기 트리거 {내용/없음} · 후보 {n}개(①에서 n) · 월간 검색량 {채택 제품군별 n}
📡 SR 실측: {후보 n개 중 통과 n · 탈락 n(SR-C n / SR40<60% n / 하락 n)} · 수집: connect {성공/실패} · 네이버 리뷰 {모델 n개·리뷰 합 n} · 쿠팡 {보류/수기 n} · 링크 발급 {n/n} — 대기 {m}분
🔢 분석: 제품군별 제품 수·리뷰 합(네이버+쿠팡)·시니어 신호 비율
🏷️ 글 N편(형식): A {제목1} / B {제목2} / C {제목3} (/ 기본형 {제목4})
✅ 점검: 정직·구매전환·SEO·URL — 편별 {통과/불통과(사유)}
📤 업로드 큐: {n}편 넣음 (확장이 5분 간격으로 임시저장 — 본문·카드·링크 카드 자동, 카테고리·태그는 `발행정보.txt` 보고 발행 때 입력) · 보류 {n}편(사유)
🔍 색인 점검: 공개 글 {n}편 중 제목 검색 30위 안 {n} · 누락 의심 {제목들/없음}
📊 공개 분석 글 누계: {n}편 (20편 초과 시 "블로그 주제 재검토 시점" — 가이드 A-5)
🙋 사용자 할 일: 임시저장 글 N편 확인 → 공개 예정일 아침(07~08시)에 임시저장함에서 1편씩 발행(카테고리·태그는 `발행정보.txt`, 가이드 3-7 공개 요령). 링크 미발급 모델 있으면 커넥트에서 발급 → links.txt. 2주·4주 뒤 통계·커넥트 수치를 형식테스트 표에 기입
⚠️ 상충·특이사항: {없음 / 내용}
```

---

⚠️ 전제조건

| 항목 | 조건 |
|---|---|
| 실행 위치 | 사용자 PC(C:\Users\win) 브리지 연결. 월·목 03:00~07:30에 PC·크롬·큐 서버가 켜져 있어야 한다(08:00 전후 PC 꺼짐) |
| 가이드 | 로컬 `naver_blog\AIPick-Writer.md` — GitHub 커밋 없음 |
| 네이버 API | SR: API HUB 키(`NAVER_APIGW_KEY_ID/KEY`) · BT: 사이트 릴레이 · 인기검색어: 데이터랩 공개 웹 엔드포인트(키 불필요) · 검색량: 검색광고 API(`NAVER_SA_CUSTOMER_ID/ACCESS_LICENSE/SECRET`). pw.txt는 Windows 스크립트만 읽는다. 없으면 `미관측` 기록 후 진행 |
| 서버 실행기 | `server.py`가 `tasks\run\`을 읽어 스크립트를 대신 실행(루틴 PC 셸은 외부망·localhost 없음). 확장은 코드 변경 시 `/version`으로 자동 리로드 · 서버 코드 변경은 `{"script":"restart"}` |
| 수집·업로드 | 전부 확장(1분 폴링). 루틴은 작업 파일을 쓰고 기다릴 뿐, 네이버·쿠팡에 접속하지 않는다 |
| 발행 | 확장은 임시저장까지. 매일 1편 발행은 사용자(공개 예정일 기준). 발행된 글의 재업로드·삭제 금지 |

STEP 10 — 클립 영상 (선택 · 가이드 4-C · **STEP 9 리포트를 보낸 뒤에만**)

본 작업(글·큐·현황표·리포트)이 모두 끝난 뒤에 하는 덤이다. 여기서 무엇이 실패해도 이번 회차 결과에는 영향이 없다.

- **조건**: 지금 시각이 **06:50 KST 이전**이고, `run_state.groups[n].status == queued` 인 제품군만. 06:50 이 지나면 이 STEP 전체를 건너뛴다(07:30 마감·08:00 PC 꺼짐 보호). 제품군당 렌더 제한 300초, 이 STEP 전체 25분.
- **어디서**: 렌더는 **클라우드 작업 공간 `Bash`** 에서 한다(PC 셸 VM 은 외부망이 없어 npm·GitHub 에 닿지 않는다). Bash 도구 `timeout` 은 **600000ms** 로 지정한다. PC 파일은 `device_stage_files` 로 가져오고 결과는 `device_commit_files` 로 보낸다.
- **순서** (제품군마다):
  ① `device_stage_files`: `NB\out\{폴더}\analysis.json` · `meta.json` · `models.json` → 스테이징된 클라우드 폴더를 `D` 로 둔다.
  ② 값 파일 + 렌더 — 가이드 4-C 규칙 그대로(숫자는 이 코드가 파일에서 직접 옮긴다). 아래 블록을 **들여쓰기 없이 그대로** 실행한다:

```bash
D="{스테이징된 클라우드 폴더}"
(test -d ~/hfkit || git clone -q --depth 1 https://github.com/leejc0404/blog ~/hfkit) && K=~/hfkit/tools/hf
python3 - "$D" <<'PY'
import json, sys
d = sys.argv[1]; a = json.load(open(d + "/analysis.json")); m = json.load(open(d + "/meta.json"))
P = {p["key"]: p for p in a["products"]}; rec = a["recommend"]; o = P[rec["overall"]]
if len(o.get("sat_top3") or []) < 3 or len(o.get("dis_top3") or []) < 3 or not all(k in rec for k in ("overall", "value", "gift")):
    sys.exit("SKIP 가이드 4-C — 만족·불만 TOP3 또는 추천 3선 부족")
v = {"group": m["product_group"], "n_text": f"{a['totals']['N']:,}개",
     "quote": m["quote"]["text"], "quote_hl": m["quote"].get("hl"), "quote_note": f"리뷰 {a['totals']['N']:,}개에서 가장 자주 반복된 표현",
     "product": o["short"], "pros": [{"label": x["label"], "pct": x["pct"]} for x in o["sat_top3"]],
     "cons": [{"label": x["label"], "pct": x["pct"]} for x in o["dis_top3"]],
     "picks": [{"role": r, "name": P[rec[k]]["short"]} for r, k in (("종합 1위", "overall"), ("가성비", "value"), ("부모님 선물용", "gift"))],
     "cta": "모델별 비교는 블로그 글에서", "sticker": "상품은 아래 쇼핑 스티커",
     "disclosure": "이 영상은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다."}
json.dump(v, open(d + "/clip_vars.json", "w"), ensure_ascii=False, indent=1)
PY
timeout 300 python3 $K/hf_render.py review_bars "$D/clip_vars.json" "$D/clip.mp4"; echo "exit=$?"
```

  ③ 종료코드 0 이면 프레임 3장(0초·9.8초·12초 — 첫 화면·만족/불만 막대 완성·추천 3선)을 `Read` 로 열어 숫자가 `analysis.json` 과 같은지, 글자 잘림·깨짐이 없는지 본다.
  ④ `clip.txt` 를 가이드 4-C 다섯 줄 형식으로 쓴다(제목은 그 글 제목의 키워드 그대로).
  ⑤ `device_commit_files` → `NB\out\{폴더}\clip\clip.mp4` · `clip.txt` · `clip_vars.json`. **`upload_queue\` 에는 아무것도 넣지 않는다.** 현황표·`run_state.step` 은 건드리지 않는다.
- **실패**(SKIP 출력·종료코드 2·시간 초과·③에서 걸림)는 그 제품군 클립만 건너뛴다. 같은 회차에 다시 시도하지 않는다.
- **끝나면 SendUserMessage 한 번**(만든 게 없어도): `🎞 클립(선택): {n}편 → out\…\clip\ (네이버 클립에 올리고 clip.txt 의 종합 1위 상품으로 쇼핑커넥트 스티커 연결) · 건너뜀 {n}편(사유)` — 06:50 이 지나 하지 않았으면 `🎞 클립: 시간 부족으로 생략`.
