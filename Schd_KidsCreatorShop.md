[루틴 : 13. 키즈 크리에이터샵 컬렉션 — 네이버 크리에이터샵 「어차피 사 줄 거면」(cshop.naver.com/wishnote_) · 화·금 02:40 · 같은 날 02:00에 도는 12번(kidspick-weekly)이 끝나기를 기다렸다가 새 글의 1위 상품 등록 → 아이 나이·노는 상황별 컬렉션에 담기 · 맞는 컬렉션이 없으면 새 컬렉션 만들기]

2026-11-26 신설(사용자 지시 — 11번 루틴을 12번 kidspick용으로 옮김 · 컬렉션 6개 제목·글마다 1위만 등록은 사용자 선택) · 파일은 이름 그대로 덮어쓴다(버전 접미사 없음)

## 0. 이 루틴이 하는 일과 하지 않는 일

- **하는 일**
  - 12번이 화·금에 새로 임시저장한 글마다 그 글의 1위 상품을 키즈 크리에이터샵에 등록하고, 정해 둔 컬렉션에 담는다. 한 회차에 한 번에 처리한다.
  - **같은 날 02:00에 시작한 12번의 글은 반드시 포함한다.** 12번이 현황표 갱신(STEP 8)까지 끝낼 때까지 기다린 뒤 처리한다(STEP 0).
  - 기존 컬렉션 어디에도 맞지 않는 제품군이 나오면 **새 컬렉션을 만들어** 담는다(STEP 3·6). 크리에이터샵에는 비공개 기능이 없어 만드는 즉시 공개되므로, 제목은 STEP 3 규칙대로 신중하게 짓고 리포트로 알린다.
- **하지 않는 일**
  - 삭제: 상품 빼기·컬렉션 지우기·잘못 등록된 상품 정리 모두 하지 않는다. 필요하면 리포트에 적고 사용자에게 묻는다.
  - 기존 컬렉션 제목 바꾸기: 제목은 사용자 확정본이다.
  - 블로그 글 수정, git 커밋, 자격증명 출력.
  - **11번·9번의 파일과 큐**(`creator_shop\` · `naver_blog\` 전체)를 고치거나 그 큐에 작업을 넣는 것. 예외는 STEP 1의 키즈 큐 서버 켜기 요청(`naver_blog\tasks\run\{RUN}_kids_server.json`) 하나뿐 — 12번 STEP 0 ⑧과 같다.
- **상품을 고르는 원칙**: 글마다 1위 상품 1개(2026-11-26 사용자 선택). 1위가 쇼핑 커넥트에서 빠졌으면 같은 글의 다음 순위 상품. 이름이 비슷하다는 이유만으로 다른 상품을 등록하지 않는다(11번 2026-11-19 액정보호필름 사례). `match` 결과가 맞지 않으면 그 글은 건너뛰고 리포트에 적는다.

## 1. 경로와 도구

`CR` = 연결된 사용자 폴더의 `Documents\Claude` (PC 셸에서는 `$HOME/mnt/Claude` — `ls $HOME/mnt`로 확인한다). `KB` = `{CR}\kids_blog`.

| 무엇 | 위치 |
|---|---|
| 샵 정보·컬렉션 6개+·ID·제품군→컬렉션 표·담은 글 | `KB\creator_shop\state.json` |
| 이번 회차 계획 | `KB\creator_shop\runs\{RUN}\plan.json` |
| 도우미 스크립트 | `KB\scripts\kcshop.py` |
| 글 목록 | 12번이 임시저장한 큐 `KB\upload_queue\*\result.json`(`drafted`) · 게시 `KB\upload_posted\*\result.json` · 글별 분석 `KB\out\{폴더}\` |
| 화면 작업 실행 | kidspick 확장 `cshop.js`(wishnote_ 크롬 프로필) — `KB\tasks\pending\kcshop_{RUN}_*.json`을 1분마다 이름순으로 하나씩 실행 |
| 화면 작업 결과 | `KB\inbox\kcshop_{RUN}\` · 끝난 작업 `KB\tasks\done\` |
| 확장·서버 기록 | `KB\upload_logs\{오늘}.log` · `KB\upload_logs\heartbeat.txt` |
| 실행 기록 | `CR\control_tower\runs\YYYY-MM.jsonl` |

- 샵: `creatorShopId 1019624575833632` · `shopUrl wishnote_` · 스페이스 `1019624415918464`(12번 커넥트 채널과 같음) — `state.shop`이 기준이다.
- `RUN` = 실행 날짜 KST `YYYYMMDD`. 같은 날 다시 돌리면 `YYYYMMDDb`.
- 작업 파일 이름은 **영문·숫자·밑줄만**(`kcshop_{RUN}_…`) — 한글이 들어가면 확장이 작업을 못 찾고 멈춘다(12번 STEP 0 ⑨ a).
- **PC 셸이 있을 때**: `cd {KB} && PYTHONDONTWRITEBYTECODE=1 python3 scripts/kcshop.py {명령} {RUN}` (`timeout`을 붙일 때는 `export PYTHONDONTWRITEBYTECODE=1`을 먼저 한다)
- **PC 셸이 없을 때(브리지 모드)**: `KB\tasks\run\kcshop_{RUN}_{명령}.json` ← `{"script":"kcshop.py","args":["{명령}","{RUN}"],"timeout_sec":300}`를 `device_commit_files`로 넣고, `KB\tasks\run_done\`의 같은 이름 파일(stdout_tail)로 결과를 읽는다. `wait` 명령은 쓰지 않고, 클라우드에서 `sleep 60` 뒤 `device_list_dir`로 `KB\tasks\pending`에 `kcshop_{RUN}_` 파일이 남았는지 본다.
- **키즈 큐 서버(8766)·확장이 살아 있는지**: `heartbeat.txt` 시각이 3분 안이면 확장 연결, `upload_logs\{오늘}.log`에 10분 안의 기록이 있으면 서버가 산 것으로 본다.
  - 서버가 꺼져 있으면 `{CR}\naver_blog\tasks\run\{RUN}_kids_server.json` ← `{"script":"kids_server_start.py"}`(9번 서버가 키즈 서버를 켠다) → 60초 뒤 키즈 로그에 `서버 시작`이 생기면 계속.
  - 작업을 넣고 5분 안에 `pending`에서 사라지지 않으면 STEP 9로 가서 `⛔ 키즈 큐 서버·확장 응답 없음`을 알리고 끝낸다(넣은 작업 파일은 남겨 둔다 — 켜지면 이어서 처리된다).

## 2. 컬렉션 기준표 (2026-11-26 사용자 확정)

| 번호 | 제목 | 담는 기준(부모가 사는 상황) | 시즌 |
|---|---|---|---|
| 1 | 리뷰 2만 개로 고른 크리스마스 선물 | 시즌 달(11~12월)에는 **모든 새 글의 1위**를 함께 담는다(`season_all`) | 11~12월 |
| 2 | 유치원생이 오래 노는 집놀이 장난감 | 유아 4~7세 · 집 안에서 오래 노는 장난감(블록·역할놀이·인형) | 상시 |
| 3 | 혼자 만들며 머리 쓰는 놀이 | 조립·구조·과학·퍼즐 등 만들고 생각하는 교구형 놀이(나이 무관) | 상시 |
| 4 | 초등학생이 조르는 요즘 유행템 | 초등 8~10세 · 또래 사이 유행하는 수집·손놀이·캐릭터템 | 상시 |
| 5 | 주말에 가족이 함께 하는 놀이 | 보드게임·카드게임 등 부모와 같이 하는 놀이 | 상시 |
| 6 | 밖에서 신나게 타는 탈것 | 킥보드·자전거·인라인·썰매 등 바깥 탈것·활동 | 상시 |

- **기본 1개 + 겹쳐 담기**(`state.also`): 한 글의 1위는 2~6번 중 기본 1곳에 담고, 성격이 겹치면 한 곳 더 담는다(예: 자석블럭 → 2 + 3). 시즌 달에는 1번에도 자동으로 담긴다.
- 이미 아는 제품군은 `state.group_to_collection`을 그대로 쓴다. 처음 보는 제품군만 판단한다. 판단할 때 글의 `category`(`유아 4~7세`·`초등 8~10세`·`선물 시즌`)를 참고한다.
- 1번 제목의 '리뷰 2만 개'는 2026-11-26 첫 7편의 분석 리뷰 합계(20,001개)다. 글이 늘면 합계도 늘어나므로 제목은 그대로 둔다.
- 표에 없는 7번 이후 컬렉션(STEP 6에서 새로 만든 것)은 `state.collections`에 있다. 판단할 때 그것도 함께 본다.

## STEP 0. 같은 날 12번이 끝날 때까지 기다리기

이 루틴은 02:40에 시작하지만 12번(02:00 시작)은 보통 2~3시간이 걸린다. 같은 날 12번이 쓴 글을 빠뜨리지 않으려고 먼저 12번 상태를 본다.

1. `kcshop.py status12 {날짜 YYYYMMDD}` (RUN에 `b`가 붙어도 날짜만 넣는다)
   - `done`(12번 `run_state.step` 8 이상 = 현황표 갱신 끝) → STEP 1로.
   - `running` → 기다린다: 클라우드 Bash에서 `sleep 540`(9분) 뒤 다시 `status12`. 셸이 없으면 `device_stage_files`로 `KB\run_state.json`을 가져와 `run`·`step`을 직접 본다.
   - `not_started` → 03:20까지는 같은 방법으로 기다린다(예약 실행이 늦게 뜨는 경우). 03:20이 지나도 그대로면 12번이 오늘 안 돈 것으로 보고 STEP 1로 간다(리포트에 `⚠️ 오늘 12번 실행 없음`).
2. **마감 07:30 KST**(12번 마감과 같다): 07:30이 되어도 `done`이 아니면 기다림을 멈추고, 그때까지 임시저장된 글만 처리한다. 리포트에 `⚠️ 12번 {step} 단계에서 미완료 — 남은 글은 다음 회차에 담김`을 적는다(다음 회차가 `state.posts`에 없는 글을 자동으로 다시 잡는다).
3. 기다리는 동안에는 크리에이터샵 작업을 넣지 않는다(12번의 수집·업로드 작업과 확장을 나눠 쓰지 않도록).

## STEP 1. 새 글 찾기

먼저 1절의 서버·확장 확인을 한다. 그다음 `kcshop.py new {RUN}` → `plan.json`. `upload_queue`·`upload_posted`의 `result.json`이 `drafted`·`posted`·`draft_unknown`인 글 중 `state.posts`에 없는 글(out 폴더 기준)마다 1위부터 순위별 후보 상품·`category`·기본 컬렉션(`collection`)·겹쳐 담기(`also`)가 들어간다.
- 같은 글을 여러 번 다시 저장한 큐(`_v2`·`_v3` …)는 out 폴더 하나로 묶인다 — 한 글에 한 번만 담는다.
- 새 글이 0편이면 STEP 9(리포트 없이 기록만)로 간다.

## STEP 2. 쇼핑 커넥트 상품 이름 맞추기

1. `kcshop.py queue-links {RUN}` → 최근 발급 링크 목록 조회(읽기 전용, 100개까지) 작업이 들어간다.
2. `kcshop.py wait {RUN}`(끝날 때까지 반복) → `kcshop.py match {RUN}`
3. 출력에서 글마다 `picked_rank`와 상품명을 확인한다.
   - `picked_rank`가 비었으면(1~3위 모두 발급 링크 목록에 없음) 그 글은 건너뛴다.
   - `picked_rank`가 1이 아니면 리포트에 `1위 {상품} 쇼핑 커넥트에서 빠짐 → {n}위 등록`으로 적는다.
   - `plan.json`의 `match` 목록에서 `ok`가 false인 후보는 쓰지 않는다. 상품명을 눈으로 한 번 더 보고, 글의 제품군과 다른 물건(부품·필름·케이스·리필 등)이면 그 글의 `shop_name`을 지운다.

## STEP 3. 컬렉션 정하기 (처음 보는 제품군만)

`plan.json`에서 `collection`이 `null`인 글은 2번 기준표(+ `state.collections`의 새 컬렉션)로 판단해 번호를 넣는다(필요하면 `also`에 겹쳐 담을 번호 1개). 판단 기준은 "4~10세 아이를 둔 부모가 어떤 상황에서 이 물건을 찾는가"다.
- 맞는 컬렉션이 **없으면** `state.collections`에 새 항목 `{"no": {다음 번호}, "title": "{새 제목}", "collectionId": null, "criteria": "{담는 기준}", "posts": []}`을 추가하고, 그 글의 `collection`에 새 번호를 넣는다. 같은 회차에 같은 상황의 글이 여럿이면 같은 번호로 묶는다.
- **새 컬렉션 제목 규칙**
  - 상품 이름이 아니라 부모가 사는 상황이 보이게 쓴다(예: 기존 「유치원생이 오래 노는 집놀이 장난감」, 「밖에서 신나게 타는 탈것」).
  - 궁금해서 한 번 더 누르게 만드는 말을 쓰되, 근거 없는 효능·과장(최고·완벽·무조건·두뇌 발달 같은 효과 주장)은 쓰지 않는다. 숫자를 넣으면 실제 집계값만 쓴다.
  - 휴대폰 화면 3줄 안(대략 25자 이내). 오타·어색한 줄임말이 없는지 두 번 읽고 확인한다.
  - 기존 컬렉션과 겹치는 상황이면 새로 만들지 말고 기존 컬렉션에 담는다. 한 회차에 새 컬렉션은 **최대 2개**까지만 만든다(넘치면 가장 가까운 기존 컬렉션에 담고 리포트에 적는다).
- 새 컬렉션은 상품이 1개여도 만든다. 다음 회차부터 같은 제품군은 `group_to_collection`으로 자동 배정된다.

## STEP 4. 상품 등록

`kcshop.py queue-register {RUN}` → `wait` 반복. 결과 `inbox\kcshop_{RUN}\register_*.json`에서
- `missing`이 있으면 그 이름만 한 번 다시 넣는다(`queue-register`를 다시 부르지 말고 `kcshop_{RUN}_19_retry.json`을 만든다 — 형식은 `register` 작업과 같고 `out`은 `register_9.json`, `search_queries`는 **기호(+ [] ())를 뺀 앞 낱말 2~3개**, `match_tokens`에 상품명의 특징 낱말 2~3개). 2026-11-26 첫 회차에 '빌리네집 비누 크런치 + 말랑이…'가 긴 검색어로는 안 잡히고 '빌리네집 비누 크런치'로 잡혔다.
- `registered`에 우리가 고르지 않은 상품(액세서리 등)이 새로 생겼으면 **지우지 말고** 리포트에 `⚠️ 잘못 등록 의심: {상품명} — 삭제 승인 필요`로 적는다.

## STEP 5. 컬렉션 담기

`kcshop.py queue-add {RUN}` → `wait` 반복 → (새 컬렉션이 있으면 STEP 6을 먼저 끝내고) `kcshop.py apply {RUN}`.
- `apply` 출력의 `added`에서 컬렉션마다 `saved: true`와 `missing`이 비었는지 확인한다.
  - `missing`이 남은 컬렉션은 그 상품만 한 번 다시 넣는다: `kcshop_{RUN}_2{번호}_add.json` ← `{"type":"cshop","step":"collection_create","mode":"add","url":"https://cshop.naver.com/my/collections/{collectionId}","inbox":"kcshop_{RUN}","out":"add_{번호}.json","wait_ms":4500,"search_wait_ms":3500,"shop_id":"{creatorShopId}","collection_title":"{제목}","names":["{상품명 그대로}"],"queries":["{브랜드 등 앞 낱말 1~2개}"]}` (2026-11-26: 담기 창 검색도 '빌리네집' 한 낱말로 잡혔다). 다시 `apply` — 같은 회차를 여러 번 `apply`해도 결과가 합쳐져 같은 값이 나온다.
  - `saved`가 false면 그 컬렉션 작업만 한 번 다시 넣는다(같은 작업, 이름 끝에 `_r`).
- 컬렉션 하나는 최대 50개다. 45개를 넘으면 리포트에 `📦 {제목} 45개 넘음 — 나누기 제안`을 적는다.

## STEP 6. 새 컬렉션 만들기

STEP 3에서 `collectionId`가 `null`인 컬렉션을 추가했으면 이 회차에 바로 만든다. 순서는 STEP 4(등록)가 끝난 뒤다 — 등록된 상품만 컬렉션에 담을 수 있다.
1. `kcshop.py queue-new {RUN}` → `collectionId`가 없는 컬렉션마다 만들기 작업(`kcshop_{RUN}_3{9-번호}_new`)이 들어간다. 샵 화면은 최근 만든 컬렉션이 맨 위에 오므로 번호 큰 것부터 만든다.
2. `wait` 반복 → `inbox\kcshop_{RUN}\new_{번호}.json`에서 `saved: true`, `picked` 수를 확인한다. 빠진 상품은 STEP 5의 재시도 방식으로 담는다. `saved`가 false면 그 작업만 한 번 다시 넣는다(같은 내용, 이름 끝에 `_r`).
3. STEP 5의 `apply`를 이 STEP 뒤에 실행한다(`collectionId`를 채우고, 그 제품군을 `group_to_collection`에 등록한다).
4. 2번 기준표에는 직접 손대지 않는다. 새 컬렉션은 `state.collections`가 기준이다.

## STEP 7. 시즌 알림 (순서 변경은 하지 않는다)

실행 날짜 기준으로 해당하면 리포트에 한 줄 적는다. 컬렉션 순서 변경·제목 변경은 사용자가 직접 하거나 승인 후 별도로 한다.
- 12월 26일 이후: `🗓️ 크리스마스 끝 — 1번 크리스마스 선물을 아래로 내리거나 「설 선물」로 바꾸는 것 제안`(1번은 1월부터 `season_all`이 꺼져 새 상품이 자동으로 담기지 않는다)
- 4월 1일~5월 5일: `🗓️ 어린이날 선물 시즌 — 어린이날 선물 컬렉션 만들기 제안`
- 7월 1일~8월 15일: `🗓️ 여름방학 — 6번 탈것·물놀이 컬렉션을 위로 올리는 것 제안`

## STEP 8. 결과 확인

작업 파일 `kcshop_{RUN}_40_check.json` ← `{"type":"cshop","step":"probe","url":"https://cshop.naver.com/wishnote_","inbox":"kcshop_{RUN}","out":"check.json","wait_ms":3000,"fetch":["https://gw-brandconnect.naver.com/creator-shop/query/creator-shops/1019624575833632/collections?limit=20","https://gw-brandconnect.naver.com/creator-shop/query/creator-shops/1019624575833632/products?limit=20"]}` → `wait` 뒤 컬렉션별 `productCount`가 `state.collections[].posts` 수와 맞는지, 상품 `paging.total`이 `state.posts` 중 `shop_name`이 있는 글 수와 맞는지 본다(차이가 나면 이유를 확인해 리포트에 적는다). 루틴 상태는 실제로 컬렉션에 담겼는지로 판단한다 — 작업이 돌았다는 것만으로 성공이라고 하지 않는다.

## STEP 9. 리포트와 실행 기록

새 글이 1편 이상이었으면 PushNotification 1회:

```
🧸 13. 키즈 크리에이터샵 {KST 날짜} — 새 글 {n}편 → 등록 {n} · 담기 {n}
📦 {컬렉션 제목} +{n} ({총 n}개) …
⚠️ {건너뛴 글·대체 등록·잘못 등록 의심·재시도 — 없으면 줄 생략}
🆕 새 컬렉션: {제목} ({n}개) — 이번 회차에 만들어 공개됨 (없으면 줄 생략)
⏳ 12번 기다림: {done까지 걸린 시간 · 미완료면 단계} (바로 시작했으면 줄 생략)
🗓️ {시즌 알림 — 없으면 줄 생략}
```

어떤 경로로 끝나든 마지막에 실행 기록 한 줄을 덧붙인다(셸 모드는 아래 코드, 브리지 모드는 `device_stage_files` → 클라우드에서 한 줄 추가 → `device_commit_files`에 `expectedMtimeMs`). `result`: 성공(다 담음) · 부분(일부) · 건너뜀(새 글 없음) · 실패(서버·확장 응답 없음 등). `count` = 이번 회차에 컬렉션에 담은 상품 수(겹쳐 담기 포함).

```bash
python3 - <<'PY'
import json, os, datetime
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
root = os.path.expanduser("~/mnt/Claude/control_tower/runs")   # 연결 폴더 이름에 맞게
os.makedirs(root, exist_ok=True)
rec = {"routine": "13. 키즈 크리에이터샵 컬렉션", "file": "Schd_KidsCreatorShop.md",
       "date": now.strftime("%Y-%m-%d"), "start": "{시작 HH:MM}", "end": now.strftime("%H:%M"),
       "result": "{성공|부분|건너뜀|실패}", "count": 0, "summary": "{60자 이내 한 줄}", "warnings": []}
with open(os.path.join(root, now.strftime("%Y-%m") + ".jsonl"), "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
PY
```
