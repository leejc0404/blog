[루틴 : 14. 쇼핑 커넥트 실적 수집 — 9번 「먹어보고 따져본 리스트」(ironeye) · 12번 「어차피 사 줄 거면」(wishnote_) · 매일 01:47 · 브랜드 커넥트 '판매 실적' 화면의 전체 누적을 읽어 전날과의 차이로 일자별 클릭·판매를 쌓는다]

2026-11-28 신설(사용자 지시 — "크롬 판매 실적 화면을 열어 확인하는 것과 똑같이 매일 취합하면 판매 일자도 알 수 있다") · 파일은 이름 그대로 덮어쓴다(버전 접미사 없음)
2026-11-29 수정(사용자 지시 — "새 판매가 일어나도 알람은 주지 말자") · 판매 알림 폐지, 실패 알림만 유지

## 0. 하는 일과 하지 않는 일

- **하는 일**: 두 블로그의 판매 실적 화면을 하루 한 번 읽어 저장한다. 화면은 하루 한 번 전날까지 갱신되므로(`최근 업데이트`), 매일 읽어 앞 날과 비교하면 **어느 날 어떤 상품이 몇 개 팔렸고 클릭이 몇 번 늘었는지** 하루 단위로 남는다. 팔린 상품이 어느 글의 몇 위 상품인지도 붙인다.
- **하지 않는 일**: 화면에서 '전체 누적'·'조회하기' 말고는 아무 버튼도 누르지 않는다(엑셀 다운로드·정산 신청 등 금지). 글·상품·링크를 바꾸지 않는다. git 커밋, 삭제, 자격증명 출력 금지. **판매가 생겨도 알림을 보내지 않는다.**
- 결과를 쓰는 곳은 각 블로그의 `radar\` 뿐이다. 9번·12번 루틴은 이 파일들을 **읽기만** 한다(9번 STEP 0 ⑧ · 12번 STEP 0 ⑪).

## 1. 경로

`CR` = 연결 폴더 루트(PC 셸에서 `$HOME/mnt/Claude`). `NB` = `{CR}\naver_blog`, `KB` = `{CR}\kids_blog`.

| 블로그 | 스크립트 | 확장(작업함) | 결과 |
|---|---|---|---|
| 9번 ironeye | `NB\scripts\perf_dashboard.py` (스페이스 1001760143114976) | aipick-extension · `NB\tasks\pending` · 큐 서버 8765 | `NB\radar\실적_{RUN}.json` · `실적_누적_{갱신일}.json` · `실적_log.jsonl` · **`실적_일별.jsonl`** |
| 12번 wishnote_ | `KB\scripts\perf_dashboard.py` (사본 · 스페이스 1019624415918464) | kidspick-extension · `KB\tasks\pending` · 큐 서버 8766 | `KB\radar\` 같은 이름 |

- `RUN` = 실행 날짜 KST `YYYYMMDD`.
- `실적_일별.jsonl` 한 줄 = `{date: 화면 갱신일, from: 앞 갱신일, days, clicks: 늘어난 클릭, orders: 늘어난 주문, sales: [{name, store, units, revenue, direct, post, rank}]}`. `days`가 2 이상이면 그 기간 합이다(하루 이상 못 읽은 경우).

## STEP 1. 블로그마다 읽기 (9번 → 12번 순서)

PC 셸(`mcp__remote-devices__device_bash`)에서 블로그 폴더(`NB` 또는 `KB`)로 가서:

1. **확장 확인**: 9번은 `NB\upload_logs\{오늘}.log`에 10분 안의 기록, 12번은 `KB\upload_logs\heartbeat.txt` 시각이 3분 안이면 연결된 것이다.
   - 9번 서버가 꺼져 있으면 아무것도 하지 않고 9번은 `⛔ 서버 꺼짐`으로 기록한다(9번 서버는 사용자가 켠다).
   - 12번 서버가 꺼져 있으면 `NB\tasks\run\{RUN}_kids_server.json` ← `{"script":"kids_server_start.py"}`. 12번 확장이 3분 넘게 조용하면 `KB\tasks\run\{RUN}_kick.json` ← `{"script":"open_write_tab.py","args":["Profile 1"]}`(wishnote_ 프로필 크롬을 깨운다) 뒤 2분 기다린다.
2. `PYTHONDONTWRITEBYTECODE=1 python3 scripts/perf_dashboard.py queue {RUN}` → `tasks\pending\cshop_{RUN}_perf{HHMM}.json`이 들어간다.
3. 10초 간격으로 그 파일이 `pending`에서 사라질 때까지 기다린다(최대 5분). 안 사라지면 그 블로그는 `⛔ 확장 응답 없음`으로 기록하고 다음 블로그로 간다(작업 파일은 남겨 둔다 — 켜지면 처리된다. 다음 날 다시 읽으면 2일 합으로 남는다).
4. `PYTHONDONTWRITEBYTECODE=1 python3 scripts/perf_dashboard.py parse {RUN}` → 출력의 `💰`·`📅` 줄을 적어 둔다.
   - `⛔ 판매 실적 화면 글자가 없음`이면 로그인이 풀렸거나 화면이 바뀐 것이다 → 리포트에 적는다.
   - `(화면이 아직 … 그대로)`면 네이버가 아직 갱신하지 않은 것이다 — 정상, 기록만 한다.

PC 셸이 없으면(브리지 모드) 같은 명령을 각 블로그의 큐 서버 `tasks\run\{RUN}_perf_queue.json` ← `{"script":"perf_dashboard.py","args":["queue","{RUN}"]}` · `…_perf_parse.json` ← `{"script":"perf_dashboard.py","args":["parse","{RUN}"]}`로 넣고(`parse`는 `pending`이 빈 것을 `device_list_dir`로 확인한 뒤), `tasks\run_done\` 결과(stdout_tail)를 읽는다.

## STEP 2. 알림

- **새 판매가 있어도 알림을 보내지 않는다.** 판매 내역은 `실적_일별.jsonl`과 STEP 3 실행 기록(`count`·`summary`)에만 남긴다.
- 둘 다 정상이면 알림을 보내지 않는다(조용히 기록만).
- **실패할 때만** 알림 1회: 둘 다 실패했거나 같은 블로그가 3일 연속 실패하면 `⛔ 14. 실적 {날짜} — {블로그} 실적 화면을 못 읽음: {사유}`.

## STEP 3. 실행 기록 한 줄

`{CR}\control_tower\runs\YYYY-MM.jsonl`에 9번 루틴과 같은 형식으로 한 줄을 덧붙인다: `{"routine":"14. 쇼핑 커넥트 실적 수집","file":"Schd_ConnectPerf.md","date":…,"start":…,"end":…,"result":"성공|부분|실패","count":{새 판매 건수},"summary":"9번 클릭 +n 판매 +n · 12번 클릭 +n 판매 +n","warnings":[…]}`.
