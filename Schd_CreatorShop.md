[루틴 : 11. 크리에이터샵 컬렉션 — 네이버 크리에이터샵 「먹어보고 따져본 리스트」(cshop.naver.com/exdata) · 월·목 05:13 · 9번(aipick-weekly)이 쓴 새 글의 1위 상품 등록 → 소비자 상황별 컬렉션에 담기]

2026-11-19 신설 · 파일은 이름 그대로 덮어쓴다(버전 접미사 없음)

## 0. 이 루틴이 하는 일과 하지 않는 일

- **하는 일**: 9번이 월·목에 새로 쓴 글(현황표 새 행)마다 그 글의 1위 상품을 크리에이터샵에 등록하고, 정해 둔 컬렉션에 담는다. 한 회차에 한 번에 처리한다.
- **하지 않는 일**
  - 삭제: 상품 빼기·컬렉션 지우기·잘못 등록된 상품 정리 모두 하지 않는다. 필요하면 리포트에 적고 사용자에게 묻는다.
  - 새 컬렉션 바로 만들기: 크리에이터샵에는 비공개 기능이 없어 만들면 바로 공개된다. 그래서 **제안만** 하고, 사용자가 승인한 것만 다음 회차에 만든다(STEP 6).
  - 컬렉션 제목 바꾸기: 제목은 사용자 확정본이다.
  - 블로그 글 수정, git 커밋, 자격증명 출력.
- **상품을 고르는 원칙**: 글마다 1위 상품 1개. 1위가 쇼핑 커넥트에서 빠졌으면 같은 글의 다음 순위 상품. 이름이 비슷하다는 이유만으로 다른 상품을 등록하지 않는다(2026-11-19 액정보호필름이 잘못 등록된 사례). `match` 결과가 맞지 않으면 그 글은 건너뛰고 리포트에 적는다.

## 1. 경로와 도구

`CR` = 연결된 사용자 폴더의 `Documents\Claude` (PC 셸에서는 `$HOME/mnt/<연결 폴더>/Documents/Claude` 또는 `$HOME/mnt/Claude` — `ls $HOME/mnt`로 확인한다).

| 무엇 | 위치 |
|---|---|
| 상태(컬렉션 8개·ID·제품군→컬렉션 표·담은 글) | `CR\creator_shop\state.json` |
| 이번 회차 계획 | `CR\creator_shop\runs\{RUN}\plan.json` |
| 도우미 스크립트 | `CR\naver_blog\scripts\cshop_shop.py` |
| 글 목록 | `CR\naver_blog\현황표.md` · 글별 분석 `CR\naver_blog\out\{폴더}\` |
| 화면 작업 실행 | AIPick 업로더 확장 `cshop.js` — `CR\naver_blog\tasks\pending\cshop_{RUN}_*.json`을 1분마다 하나씩 실행 |
| 화면 작업 결과 | `CR\naver_blog\inbox\cshop_{RUN}\` · 끝난 작업 `CR\naver_blog\tasks\done\` |
| 실행 기록 | `CR\control_tower\runs\YYYY-MM.jsonl` |

- `RUN` = 실행 날짜 KST `YYYYMMDD`. 같은 날 다시 돌리면 `YYYYMMDDb`.
- **PC 셸이 있을 때**: `cd {CR}/naver_blog && PYTHONDONTWRITEBYTECODE=1 python3 scripts/cshop_shop.py {명령} {RUN}`
- **PC 셸이 없을 때(브리지 모드)**: `tasks\run\cshop_{RUN}_{명령}.json` ← `{"script":"cshop_shop.py","args":["{명령}","{RUN}"],"timeout_sec":300}`를 `device_commit_files`로 넣고, `tasks\run_done\`의 같은 이름 파일(stdout_tail)로 결과를 읽는다. `wait` 명령은 쓰지 않고, 클라우드에서 `sleep 60` 뒤 `device_list_dir`로 `tasks\pending`에 `cshop_{RUN}_` 파일이 남았는지 본다.
- 큐 서버·확장이 살아 있는지: `upload_logs\{오늘}.log`에 10분 안의 기록이 있으면 산 것으로 본다. 없으면 작업을 넣고 5분 안에 `pending`에서 사라지는지로 판단한다. 안 사라지면 STEP 9로 가서 `⛔ 큐 서버·확장 응답 없음`을 알리고 끝낸다(넣은 작업 파일은 남겨 둔다 — 켜지면 이어서 처리된다).

## 2. 컬렉션 기준표 (2026-11-19 사용자 확정)

| 번호 | 제목 | 담는 기준(소비자가 사는 상황) | 시즌 |
|---|---|---|---|
| 1 | 리뷰 2만 개가 고른 김장템 | 김장 재료·김장 도구·김치 보관 | 11~12월 |
| 2 | 외풍·한기 잡는 겨울 집 | 집 안 추위·외풍·난방·보온 침구 | 11~2월 |
| 3 | 출근길이 덜 추운 겨울 옷 | 출퇴근·외출용 방한 의류·신발·소품 | 11~2월 |
| 4 | 겨울 산행·캠핑 준비물 | 등산·트레킹·캠핑·야외 활동 | 상시(겨울 강조) |
| 5 | 매일 쓰는 주방 1위템 | 매일 쓰는 주방 가전·조리 도구 — **글의 1위 상품만** | 상시 |
| 6 | 기사님 안 불러도 되는 셀프 교체 | 혼자 설치·교체하는 집수리·욕실 설비 | 상시 |
| 7 | 부모님이 진짜 쓰는 효도템 | 부모님 건강·안마·운동·선물 | 상시(설·어버이날 강조) |
| 8 | 살림이 편해지는 생활템 | 위에 해당하지 않는 살림 편의·생활용품 | 상시 |

- **겹쳐 담기**(`state.also`): 부모님 선물 성격이 강하면 7번에도, 산행에도 쓰는 방한 의류면 4번에도 담는다(예: 방한화·전기방석 → 7, 발열조끼·경량패딩 → 4).
- 이미 아는 제품군은 `state.group_to_collection`을 그대로 쓴다. 처음 보는 제품군만 판단한다.

## STEP 1. 새 글 찾기

`cshop_shop.py new {RUN}` → `plan.json`. 현황표에 있지만 `state.posts`에 없는 글마다 1위부터 순위별 후보 상품과 기본 컬렉션(`collection`)이 들어간다.
- 새 글이 0편이면 STEP 9(리포트 없이 기록만)로 간다.
- `error: out 폴더 없음`인 글은 이번 회차에서 빼고 리포트에 적는다(다음 회차에 다시 시도된다).

## STEP 2. 쇼핑 커넥트 상품 이름 맞추기

1. `cshop_shop.py queue-links {RUN}` → 최근 발급 링크 목록 조회(읽기 전용) 작업이 들어간다.
2. `cshop_shop.py wait {RUN}`(끝날 때까지 반복) → `cshop_shop.py match {RUN}`
3. 출력에서 글마다 `picked_rank`와 상품명을 확인한다.
   - `picked_rank`가 비었으면(1~3위 모두 발급 링크 목록에 없음) 그 글은 건너뛴다.
   - `picked_rank`가 1이 아니면 리포트에 `1위 {상품} 쇼핑 커넥트에서 빠짐 → {n}위 등록`으로 적는다.
   - `plan.json`의 `match` 목록에서 `ok`가 false인 후보는 쓰지 않는다. 상품명을 눈으로 한 번 더 보고, 글의 제품군과 다른 물건(부품·필름·케이스 등)이면 그 글의 `shop_name`을 지운다.

## STEP 3. 컬렉션 정하기 (처음 보는 제품군만)

`plan.json`에서 `collection`이 `null`인 글은 2번 기준표로 판단해 번호를 넣는다(필요하면 `also`에 겹쳐 담을 번호도). 판단 기준은 "이 상품을 사는 40대 이상 소비자가 어떤 상황에서 찾는가"다.
- 맞는 컬렉션이 **없으면** `collection`을 `null`로 두고 `state.json`의 `pending_new_collections`에 `{"title":"{제목 후보}","reason":"{한 줄 이유}","posts":[{글 번호}],"approved":false}`를 추가한다. 그 상품은 등록만 하고 컬렉션에는 넣지 않는다. 제목 후보는 기존 제목처럼 소비자 상황이 드러나고 궁금해지는 말로 쓰고, 오타·어색한 줄임말이 없는지 확인한다.
- 같은 제안이 이미 있으면 `posts`에 글 번호만 더한다.

## STEP 4. 상품 등록

`cshop_shop.py queue-register {RUN}` → `wait` 반복. 결과 `inbox\cshop_{RUN}\register_*.json`에서
- `missing`이 있으면 같은 이름으로 한 번만 다시 넣는다(`queue-register`를 다시 부르지 말고 남은 이름만 담은 작업 파일을 `cshop_{RUN}_19_retry.json`으로 만든다 — 형식은 `register_0` 작업과 같다).
- `registered`에 우리가 고르지 않은 상품(액세서리 등)이 새로 생겼으면 **지우지 말고** 리포트에 `⚠️ 잘못 등록 의심: {상품명} — 삭제 승인 필요`로 적는다.

## STEP 5. 컬렉션 담기

`cshop_shop.py queue-add {RUN}` → `wait` 반복 → `cshop_shop.py apply {RUN}`.
- `apply` 출력의 `added`에서 컬렉션마다 `saved: true`와 담긴 수를 확인한다. `saved`가 false면 그 컬렉션 작업만 한 번 다시 넣는다(같은 작업 파일을 이름 끝에 `_r`을 붙여 다시 만든다).
- 5번(주방 1위템)에는 `picked_rank`가 1인 상품만 들어간다(스크립트가 거른다).
- 컬렉션 하나는 최대 50개다. 45개를 넘으면 리포트에 `📦 {제목} 45개 넘음 — 나누기 제안`을 적는다.

## STEP 6. 승인된 새 컬렉션 만들기

`state.json`의 `pending_new_collections` 중 `"approved": true`인 것만 처리한다(사용자가 대화에서 승인하면 그때 true로 바뀐다).
1. 작업 파일 `cshop_{RUN}_30_new.json` ← `{"type":"cshop","step":"collection_create","url":"https://cshop.naver.com/my/collections/new","inbox":"cshop_{RUN}","out":"new_{n}.json","wait_ms":4500,"shop_id":"1016348833664320","title":"{제목}","names":[{그 글들의 shop_name}]}`
2. `wait` 뒤 결과의 `collections` 목록에서 새 컬렉션의 `collectionId`를 찾아 `state.collections`에 `{"no": 기존 최대 번호+1, "title", "collectionId", "season": false, "posts": [...]}`로 추가하고, 그 글들의 `state.posts[].collections`와 `group_to_collection`도 고친다. 처리한 제안은 `pending_new_collections`에서 뺀다.

## STEP 7. 시즌 알림 (순서 변경은 하지 않는다)

실행 날짜 기준으로 해당하면 리포트에 한 줄 적는다. 컬렉션 순서 변경은 사용자가 직접 하거나 승인 후 별도로 한다.
- 12월 15일 이후: `🗓️ 김장 시즌 끝 — 1번 김장템을 아래로 내리는 것 제안`
- 1월 10일~2월 설 연휴 전: `🗓️ 설 선물 시즌 — 7번 효도템을 맨 위로 올리는 것 제안`
- 3월 1일 이후: `🗓️ 겨울 끝 — 2·3번을 아래로 내리는 것 제안`

## STEP 8. 결과 확인

작업 파일 `cshop_{RUN}_40_check.json` ← `{"type":"cshop","step":"probe","url":"https://cshop.naver.com/exdata","inbox":"cshop_{RUN}","out":"check.json","wait_ms":3000,"fetch":["https://gw-brandconnect.naver.com/creator-shop/query/creator-shops/1016348833664320/collections?limit=20"]}` → `wait` 뒤 컬렉션별 `productCount`가 `state.collections[].posts` 수와 맞는지 본다(겹쳐 담기·대체 상품 때문에 차이가 나면 이유를 확인해 리포트에 적는다). 루틴 상태는 실제로 컬렉션에 담겼는지로 판단한다 — 작업이 돌았다는 것만으로 성공이라고 하지 않는다.

## STEP 9. 리포트와 실행 기록

새 글이 1편 이상이었으면 PushNotification 1회:

```
🛍️ 11. 크리에이터샵 {KST 날짜} — 새 글 {n}편 → 등록 {n} · 담기 {n}
📦 {컬렉션 제목} +{n} ({총 n}개) …
⚠️ {건너뛴 글·대체 등록·잘못 등록 의심 — 없으면 줄 생략}
🆕 새 컬렉션 제안: {제목} — 승인하면 다음 회차에 만듭니다 (없으면 줄 생략)
🗓️ {시즌 알림 — 없으면 줄 생략}
```

어떤 경로로 끝나든 마지막에 실행 기록 한 줄을 덧붙인다(9번 루틴의 '실행 기록 한 줄'과 같은 방식 — 셸 모드는 아래 코드, 브리지 모드는 `device_stage_files` → 클라우드에서 한 줄 추가 → `device_commit_files`에 `expectedMtimeMs`). `result`: 성공(다 담음) · 부분(일부) · 건너뜀(새 글 없음) · 실패(서버·확장 응답 없음 등). `count` = 이번 회차에 컬렉션에 담은 상품 수.

```bash
python3 - <<'PY'
import json, os, datetime
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
root = os.path.expanduser("~/mnt/Claude/control_tower/runs")   # 연결 폴더 이름에 맞게
os.makedirs(root, exist_ok=True)
rec = {"routine": "11. 크리에이터샵 컬렉션", "file": "Schd_CreatorShop.md",
       "date": now.strftime("%Y-%m-%d"), "start": "{시작 HH:MM}", "end": now.strftime("%H:%M"),
       "result": "{성공|부분|건너뜀|실패}", "count": 0, "summary": "{60자 이내 한 줄}", "warnings": []}
with open(os.path.join(root, now.strftime("%Y-%m") + ".jsonl"), "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
PY
```
