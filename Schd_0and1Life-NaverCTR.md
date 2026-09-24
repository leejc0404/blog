# Schd_0and1Life-NaverCTR — 네이버 "노출 많고 CTR 낮은 글" 개선 루틴 (Cowork 예약 작업용)

*매일 06:30 KST 실행. 예약 시각이 되면 같은 날 이미 실행됐더라도 다시 진행한다(판정·잠금은 `state.json` 이 막아 주므로 같은 글을 두 번 고치지 않는다).

날짜: 실행 시점의 실제 KST 날짜를 쓴다. 이 프롬프트에 적힌 고정 날짜는 무시한다.

이 루틴이 하는 일:
1. 서치어드바이저 TOP30 CSV를 읽는다(크롬 확장 `C:\Users\win\Documents\Claude\naver-advisor-export` v1.2.0이 매일 06:00에 백그라운드 탭으로 자동 수집해 `다운로드\네이버_수집\naver_search_report_full_30_{KST 날짜}.csv` 로 저장). **날짜만 바뀐 같은 내용의 CSV는 새 데이터로 치지 않는다.**
2. **이미 고친 글의 효과를 매일 판정**한다 → 개선이면 유지, 개선이 없으면 재수정, 나빠졌으면 되돌림
3. **검색 수요를 실측**한다(2026-09-24 추가) → 네이버 검색광고 API(월간 검색수) + 검색어트렌드 API(최근 흐름)
4. 수요 기준으로 새 대상 1편을 고른다 → **검색이 많고 우리가 덜 가져가는 글부터**, 시기성 글(긴급)은 그날 바로 수정
5. 원인을 **노출 점유율(우리 노출 ÷ 월 검색수)**로 판정해 처방을 고른다 → 보이는데 안 눌리면 제목·메타·첫 문단, 순위가 낮아 안 보이면 본문 답 블록까지
6. 모든 수정은 버전(v1·v2·v3)으로 기록해 다음 날 같은 글을 다시 고치지 않는다
7. **CTR 개선은 글 전체 기준으로 한다**(2026-09-24 사용자 지시) — 제목을 바꾸면 그 때문에 어긋나는 곳(Focus Keyword·부제목·이미지 대체 텍스트·키워드 밀도)도 같이 맞춰 **Rank Math 점수를 수정 전 수준으로 유지**한다. 전부 뜯어고치지 않고, 어긋나는 곳만 최소로 고친다
8. **수정한 글은 반영 후 7일 동안 매일 일자별 노출·클릭·CTR 표로 모니터링**한다(`monitor/{slug}.md`, 매일 알림에 포함)

작업 폴더: `C:\Users\win\Documents\Claude\naver-ctr\` (blog 저장소 밖 — 데이터는 커밋되지 않는다)
- `ctr_engine.py` — 계산 엔진(수집·중복 판별·선정·수요 점수·잠금·효과 판정·기록). **판단이 필요 없는 계산은 전부 이 스크립트가 한다.** 루틴은 결과(JSON)를 읽고 문구 작성과 WP 반영만 한다
- `demand.py` — 수요 조회(검색광고 월간 검색수 + 검색어트렌드 흐름) → `demand/{날짜}.json`
- `naver_volume.py`·`naver_trend.py` — 수동 조회용(키워드 몇 개를 바로 확인할 때)
- `state.json` — 키워드→글 연결, 추가 키워드(`extra_kw`), 이벤트 날짜, 글별 버전 이력(잠금의 유일한 근거)
- `snapshots/{날짜}.json` — 날짜별 TOP30 · `demand/` — 날짜별 수요 · `backups/` — 수정 전 원본 · `monitor/{slug}.md` — 반영 후 7일 일자별 표 · `log.md` — 사람이 읽는 기록 · `inbox/` — 수동으로 넣은 CSV · `tests/` — 엔진 테스트
- 사이트 릴레이(WPCode): 스니펫 1692 `o1/v1/naver-check`(상위 글 조사) · 스니펫 1819 `o1/v1/naver-trend`·`o1/v1/naver-volume`(수요). 키는 사이트에 저장하지 않고 요청 헤더로만 보낸다

⚠️ [무인 실행 원칙 — 최우선]
사람이 없는 시간에 실행된다. 승인이 필요한 도구 호출은 "그것 없이는 진행할 수 없음을 실측으로 확인한 뒤"에만 한다. 승인 창이 응답 없이 닫히면 재시도하지 않고 오류로 기록한 뒤 STEP 10으로 간다.

⚠️ [시간 제한]
06:51에 `0and1life-auto-image-insert` 가 같은 Chrome에서 에디터를 연다. **06:48까지 끝낸다.** STEP 8에 들어가는 시각이 **06:45~08:00(KST) 사이**면 반영하지 않고 수정안만 `log.md` 에 남긴다(기록하지 않았으므로 다음 날 다시 1순위로 뽑힌다).
- 이 창(06:45~08:00) 밖이면 — 예약이 늦게 돌았거나 사용자가 "지금 실행"으로 돌린 경우 — 에디터 충돌이 없으므로 **그대로 반영한다**(2026-09-24: 15:17 실행을 시간 초과로 건너뛴 문제 수정).

⚠️ [에디터·REST 충돌 규약 — Schd_0and1Life-Draft.md [6m-0]과 같다]
에디터 탭이 열려 있는 동안에는 REST로 본문을 쓰지 않는다. 본문 REST 수정은 ① post.php 탭이 없는지 확인 → ② REST POST → ③ 8초 후 재조회 검증 순서를 지킨다.

⚠️ 삭제 금지: 글·리비전·파일·Notion 행을 삭제하지 않는다. 필요하면 STEP 10에 "삭제 필요 — 사용자 확인"으로만 남긴다.
⚠️ 변경 금지 항목: 글의 status(publish/draft/private)·**슬러그(URL)**·카테고리·발행일·H2 순서·FAQ 문구와 ld+json. 본문은 첫 문단·답 블록(STEP 7-5)·정합성 보정(STEP 7-6)만 고친다.
- Focus Keyword: 제목 맨 앞을 `focus_kw` 로 바꾸면 **원인과 관계없이** 1순위를 `focus_kw` 로 바꾸고, 기존 키워드는 지우지 않고 뒤로 보낸다(2026-09-24: 제목만 바꾸고 FK를 그대로 둬 Rank Math 81→40으로 떨어진 사고).
⚠️ git commit·push 하지 않는다 — 사용자가 직접 한다.
⛔ searchadvisor.naver.com · search.naver.com · datalab.naver.com 은 Claude in Chrome과 내장 브라우저 모두에서 "안전 제한"으로 막혀 있다(2026-09-24 실측). **열려고 시도하지 않는다.** 성과 데이터는 CSV로, 검색 수요는 사이트 릴레이 API로만 받는다.
⛔ openapi.naver.com · naverapihub.apigw.ntruss.com · api.searchad.naver.com 은 이 PC·클라우드에서 직접 연결되지 않는다(2026-09-24 실측). **반드시 사이트 릴레이를 거친다.**

---

## STEP 0 — 설정값 (사용자만 수정)

```
URGENT_MODE  = AUTO      # 시기성 긴급 글(이벤트 3~14일 남음): 그날 바로 반영
NORMAL_MODE  = AUTO      # 상시 글: SAMPLE = 수정안만 기록 / AUTO = 바로 반영 (2026-09-24 AUTO로 변경)
REEDIT_MODE  = AUTO      # 효과 판정이 "개선 없음"이면 재수정(반영했던 글만 대상)
NEW_PER_DAY  = 1         # 하루 새로 고치는 글 수(상위부터)
REEDIT_PER_DAY = 1       # 하루 재수정·되돌림 글 수
ANSWER_BLOCK = AUTO      # 원인 C(노출 점유율 15% 미만)일 때 본문 답 블록 추가: AUTO / OFF
```
판정 기준값(노출 하한 300, 목표 CTR, 긴급 창 14일, 효과 판정 노출·클릭 기준, 재수정 한도 3차, 노출 점유율 기준 30%·15%, 식은 글·되살림 기준 등)은 `ctr_engine.py` 상단 `CFG` 에 있다. 바꿀 때는 그 파일만 고치고 `python3 -m pytest -q tests` 로 확인한다.

---

## STEP 1 — 날짜와 폴더

1) TODAY(KST)를 기록한다.
   - 스냅샷 기준일: `state.json` 의 `baseline`(현재 2026-09-24)보다 앞선 스냅샷은 엔진이 읽지 않는다(09-23은 시험 수집분).
2) **실행 위치 정하기** — 아래 2-A가 되면 2-A, 안 되면 2-B. 둘 다 같은 결과를 낸다.
   - 2-A(PC 작업 공간): `device_bash`(=사용자 PC의 Cowork 작업 공간 셸) 또는 `/sessions/*/mnt` 마운트가 있으면 그대로 쓴다.
   - 2-B(클라우드 폴백 — 2026-09-24 추가): `device_bash` 가 "Workspace unavailable" 이거나 마운트가 없으면 **폴더 요청을 하지 말고** 바로 이 방식으로 간다.
     ① `device_stage_files` 로 아래 파일을 클라우드로 가져온다: `C:\Users\win\Documents\Claude\pw.txt`, `naver-ctr\` 의 `ctr_engine.py`·`demand.py`·`naver_volume.py`·`naver_trend.py`·`state.json`·`log.md`·`snapshots\*.json`·`demand\*.json`(최근 3일), `다운로드\네이버_수집\` 의 CSV 중 `state.json` 의 `processed_csv` 에 없는 것
     ② 클라우드에 같은 구조(`$CLAUDE_DIR/pw.txt`, `$W/…`)로 복사하고 이후 STEP을 그대로 실행한다(클라우드에서 0and1life.com 접속 가능 — 2026-09-24 실측).
     ③ 끝나기 전에 바뀐 파일(`state.json`·`log.md`·새 `snapshots/`·`demand/`·`backups/`·`monitor/`)을 `/mnt/user-data/outputs/naver-ctr/` 에 두고 `device_commit_files` 로 원래 경로에 돌려놓는다. `state.json`·`log.md` 는 stage 때 받은 `mtimeMs` 를 `expectedMtimeMs` 로 넣는다. **돌려놓지 못하면 잠금이 사라지므로 STEP 10에 반드시 기록한다.**
3) 2-A일 때 bash로 마운트를 찾는다. 폴더 요청(`request_cowork_directory`)은 하지 않는다.
```bash
CLAUDE_DIR=$(ls -d /sessions/*/mnt/Claude 2>/dev/null | head -1)      # pw.txt, naver-ctr
NAVER_IN=$(ls -d /sessions/*/mnt/네이버_수집 2>/dev/null | head -1)      # 다운로드\네이버_수집
W=$CLAUDE_DIR/naver-ctr
echo "claude=$CLAUDE_DIR naver_in=${NAVER_IN:-없음}"; ls $W/ctr_engine.py $W/demand.py
```
- CLAUDE_DIR이 없으면 2-B로 간다(폴더 요청 창은 무인 실행에서 응답이 없다).
- NAVER_IN이 없으면 2-B의 stage로 CSV만 가져온다. 그것도 안 되면 기존 inbox만 읽는다.
- ⚠️ bash는 매 호출이 새 셸이다. 위 세 줄(CLAUDE_DIR·NAVER_IN·W)을 이후 bash 호출마다 맨 앞에 다시 넣는다.

---

## STEP 2 — 자격증명 확인 (값은 절대 출력하지 않는다)

pw.txt는 BOM이 있고 앱 비밀번호에 공백이 있다. `set -a; . pw.txt` 로 읽지 않는다.
```bash
cd $CLAUDE_DIR
get(){ grep "^$1=" pw.txt | head -1 | cut -d'=' -f2- | tr -d '\r\n' | sed 's/^\xEF\xBB\xBF//; s/^ *//; s/ *$//'; }
U=$(get ONEANDZERO_WP_USER); P=$(get ONEANDZERO_WP_APP_PASSWORD); NKID=$(get NAVER_APIGW_KEY_ID); NKEY=$(get NAVER_APIGW_KEY)
SAC=$(get NAVER_SEARCHAD_CUSTOMER_ID); SAK=$(get NAVER_SEARCHAD_ACCESS_LICENSE); SAS=$(get NAVER_SEARCHAD_SECRET_KEY)
for k in U P NKID NKEY SAC SAK SAS; do [ -n "${!k}" ] && echo "$k=있음" || echo "$k=없음"; done
[[ "$SAC" =~ ^[0-9]+$ ]] || echo "SAC 형식 이상(숫자만이어야 함)"
curl -s -o /dev/null -w "WP %{http_code}\n" -u "$U:$P" "https://0and1life.com/wp-json/wp/v2/users/me?context=edit"
```
- U·P·NKID·NKEY 중 하나라도 "없음" → STEP 10에 `pw.txt에 {키 이름} 없음` 을 적고 종료.
- SAC·SAK·SAS 가 없거나 형식 이상 → **종료하지 않는다.** 검색광고(월간 검색수) 없이 검색어트렌드만으로 진행하고 STEP 10에 `검색광고 키 확인 필요` 기록.
- WP가 200이 아니면 → Schd_0and1Life-Draft.md [3-2] nonce 폴백. 그것도 실패하면 반영 단계만 건너뛰고(판정·수정안은 진행) STEP 10에 기록.
- 이후 REST·릴레이 호출마다 `get` 함수와 변수 줄을 같은 명령 안에 다시 넣는다.

---

## STEP 3 — CSV 읽기

```bash
cd $W && python3 ctr_engine.py ingest ${NAVER_IN:+"$NAVER_IN"}
```
- `inbox/` 와 `네이버_수집` 의 CSV 중 **처음 보는 파일만** `snapshots/{파일명의 날짜}.json` 으로 저장한다(이미 처리한 파일은 건너뛴다).
- CSV 형식: 확장 프로그램 "서치어드바이저 TOP30 내보내기" 출력(`--- 검색 키워드 TOP 30 ---` / `--- 검색 웹문서 TOP 30 ---` 두 표). 요약 행은 단위가 잘려 있어("7.4" = 7.4백) **쓰지 않는다.** 합계는 엔진이 TOP30에서 직접 계산한다.
- 결과에 `error` 가 있으면 STEP 10에 파일명과 함께 기록.

---

## STEP 4 — 오늘 계획 받기 (plan → 수요 조회 → plan 다시)

[4-0] 1차 계획
```bash
cd $W && python3 ctr_engine.py plan --today {TODAY} > /tmp/plan.json && cat /tmp/plan.json
```
출력 JSON에서 읽을 것:
| 키 | 뜻 |
|---|---|
| `stale_days` | 마지막 **새** 스냅샷이 며칠 전 것인지. **0이 정상**. 날짜만 바뀐 같은 CSV는 `duplicate_snapshots` 로 빠지고 새 데이터로 치지 않는다(2026-09-24 실측: 09-23·09-24 CSV가 완전히 같았다) |
| `duplicate_snapshots[]` | 앞날과 수치가 완전히 같은 스냅샷 날짜 → 서치어드바이저 갱신 지연 또는 확장 수집 이상 |
| `evaluations[]` | 반영한 글의 효과 판정. verdict = KEEP(개선) / HOLD(개선 후 보호 기간) / WAIT(데이터 대기) / REEDIT(개선 없음) / ROLLBACK(악화) / LIMIT(3차까지 개선 없음) / NO_DATA(TOP30 밖). 수요 파일이 있으면 `volume`·`share`(노출 점유율 %)·`momentum` 이 붙는다 |
| `reedit[]`, `rollback[]` | 오늘 재수정·되돌림할 글 |
| `queue[]` | 새 대상 후보(우선순위 정렬). `track`=urgent/normal, `days_left`, `lost_clicks`, `main_kw`. 수요 파일이 있으면 `volume`·`share`·`momentum`·`now_vs_peak`·`opp_clicks`(기회 클릭)·`cause_hint`·`cooling`·`focus_kw`·`e3_revived` 가 붙는다 |
| `excluded[]` | E3 내년용(이벤트 종료·2일 이내이고 검색도 식음) / E4 네이버 즉답(키워드 CTR 0.3% 미만) |
| `demand_targets[]` | 수요를 조회할 글과 키워드(대기열 상위 5 + E3 제외 글 + 판정 중인 글) |
| `need_kw[]` | 수요 조회 대상인데 연결 키워드가 없는 글 |
| `need_event_date[]` | 이벤트 날짜를 아직 모르는 글 |
| `unmapped_keywords[]` | 어느 글과 연결할지 모르는 키워드 |

**stale 처리**
- `stale_days` = 0 → 전부 진행.
- `stale_days` = 1~2 → **효과 판정·재수정·되돌림은 건너뛴다**(새 성과 데이터가 없다). **새 대상 1편은 진행한다**(선정은 최신 새 스냅샷 + 오늘 수요로 한다. 잠금 때문에 어제와 같은 글이 다시 뽑히지 않는다). STEP 10에 `CSV 갱신 없음 {n}일` 기록.
- `stale_days` ≥ 3 → 판정·수정 모두 건너뛰고 STEP 10에 `CSV 미수집 — 확장 팝업의 오류 메시지 확인(로그인 풀림·크롬 꺼짐)` 기록.

[4-1] `unmapped_keywords` 가 있으면: WP_CORPUS(`GET /wp-json/wp/v2/posts?status=publish&per_page=100&_fields=id,slug,title` 끝 페이지까지)의 제목·슬러그와 의미로 대조해 한 편을 고른다. 없으면 none.
```bash
python3 ctr_engine.py set-map "키워드" 슬러그        # 또는 none
```
[4-2] `need_event_date` 가 있으면: 그 글 본문(REST `content.rendered`)에서 독자 행동을 막는 날짜(납부·신청 마감, 사전예약 마감, 시행일, 출시일, 명절 당일)를 찾는다. 여러 개면 **아직 지나지 않은 가장 이른 마감**을 쓴다. 날짜가 없거나 상시 정보면 none. 추정하지 않는다.
```bash
python3 ctr_engine.py set-event 슬러그 2026-09-30   # 또는 none
```
- `e3_revived: true` 로 되살아난 글은 저장된 이벤트 날짜가 이미 지난 것이다. 본문에서 **아직 지나지 않은 다음 날짜**(예: 접수 중지 종료일·재개일)가 있으면 그 날짜로 다시 `set-event` 한다(2026-09-24: 추석 택배 글 9/19 → 본문의 '9/29까지 접수 중지'로 갱신). 없으면 그대로 둔다.
[4-3] `need_kw` 가 있으면: 그 글의 공개 페이지 `<title>` 에서 "—"·"," 앞의 핵심 구절(2~5어절)을 키워드로 1~2개 정한다. 본문 H2에 반복해서 나오는 지역명·제품명 조합이 있으면 1개 더(최대 3개). 지어내지 않는다.
```bash
python3 ctr_engine.py set-kw 슬러그 "키워드1,키워드2"
```
[4-4] 4-1~4-3에서 하나라도 설정했으면 `plan` 을 다시 실행해 `/tmp/plan.json` 을 갱신한다.

[4-5] 수요 조회 (2026-09-24 추가 — 이 단계가 선정·원인 판정의 근거다)
```bash
cd $W && python3 demand.py /tmp/plan.json {TODAY}
```
- 출력 `slugs` 에 글별 `volume`(월 검색수 합) · `momentum`(최근 7일 ÷ 이전 7일) · `now_vs_peak`(최근 3일 ÷ 90일 최고) 가 나온다. 결과는 `demand/{TODAY}.json`.
- `volume_ok=false` → 검색광고 실패(키·한도). `trend_ok=false` → 검색어트렌드 실패. 한 쪽만 실패하면 있는 값으로 계속하고 STEP 10에 기록.
- 종료코드 2(둘 다 실패) → 1회 재시도 → 그래도 실패면 **수요 없이** 1차 계획대로 진행(기존 `lost_clicks` 순서)하고 STEP 10에 `수요 조회 실패` 기록. STOP 아님.

[4-6] 최종 계획
```bash
cd $W && python3 ctr_engine.py plan --today {TODAY} > /tmp/plan.json && cat /tmp/plan.json
```
- 이제 `queue[]` 는 **긴급 → 식지 않은 글 → 기회 클릭 큰 순**으로 정렬되어 있다.
- `e3_revived: true` = 이벤트는 지났지만 검색이 살아 있어(최고치의 30% 이상, 월 1,000회 이상) 내년용에서 되살린 글. 상시 글로 다룬다.
- `cooling: true` = 최고치의 20% 미만이고 줄어드는 중 → 맨 뒤로 밀려 있다.
- 수치는 지식으로 추정해 적지 않는다. **API가 준 값만 쓴다.**

---

## STEP 5 — 오늘 할 일 정하기 (이 순서, 이 한도)

1. **되돌림** `rollback[]` — REEDIT_PER_DAY 한도 안에서 가장 먼저. 백업의 직전 버전 값(제목·메타·첫 문단·답 블록)으로 되돌리고 `status: "rollback"` 으로 기록. 되돌린 글은 다음 날 새 수정 후보로 돌아온다.
2. **재수정** `reedit[]` — REEDIT_MODE=AUTO면 남은 한도 안에서 1편. 긴급 트랙 글 우선. 단 그 글의 `momentum` 이 0.5 미만(검색 자체가 반 토막)이면 CTR 하락이 검색 감소 탓일 수 있으므로 재수정하지 않고 STEP 10에 `검색 감소로 판정 보류` 기록.
3. **LIMIT** 글 — 고치지 않는다. `python3 ctr_engine.py close 슬러그 "3차까지 개선 없음"` 로 30일 닫고, STEP 10에 "각도 재타겟 신규 글 후보"로 올린다.
4. **새 대상** `queue[]` 맨 위부터 NEW_PER_DAY 편.
   - `track=urgent` → URGENT_MODE(AUTO)로 **그날 바로 반영**
   - `track=normal` → NORMAL_MODE(AUTO)로 **그날 바로 반영**
   - 맨 위 글이 `cooling: true` 면(대기열 전부가 식은 경우) 새 수정은 하지 않고 STEP 10에 기록한다.
5. 할 일이 없으면 STEP 10으로.

⚠️ 같은 글이 되돌림·재수정·새 대상에 동시에 걸릴 수 없다(엔진이 잠금으로 막는다). 엔진 출력에 없는 글은 손대지 않는다.

---

## STEP 6 — 대표 키워드 정하기와 네이버 상위 글 조사

[6-1] 대표 키워드(`focus_kw`) — 데이터로 정한다
- 기본값은 엔진이 준 `focus_kw`(그 글 키워드 중 월 검색수 1위).
- `demand/{TODAY}.json` 의 그 글 `related[]` 에 **우리 본문이 이미 답하고 있는** 더 큰 키워드가 있으면 그것을 쓸 수 있다(예: 글이 17곳을 다루는데 검색은 '김해 추석 민생지원금' 월 11,360회에 몰림 → 김해가 대표). 본문이 답하지 않는 키워드는 고르지 않는다.
- 필요하면 `python3 naver_volume.py --related 20 "{후보}"` · `python3 naver_trend.py {90일 전} {어제} "A=…" "B=…"` 로 후보 2~3개를 같은 요청 안에서 비교한다(트렌드 값은 요청 안에서만 비교 가능한 상대값).

[6-2] 상위 글 조사 (사이트 릴레이) — `focus_kw` (+ 검색수 2위 키워드)로 `webkr`·`blog` 조회. 최대 4회, 0.5초 간격.
```bash
curl -s --max-time 20 -u "$U:$P" -H "X-O1-NKID: $NKID" -H "X-O1-NKEY: $NKEY" \
  -G "https://0and1life.com/wp-json/o1/v1/naver-check" \
  --data-urlencode "q={키워드}" -d "type=webkr" -d "display=10"
# 파라미터 이름은 q (query로 보내면 400). type=blog 로 한 번 더.
```
기록: WT/BT(total) · 상위10 제목·요약·도메인 · 우리 글 포함 여부와 순위 · 구성(개인 블로그·카페 n / 기관·카드사·언론 n) · **상위10이 공통으로 보여주는 답(날짜·금액·방법)과 빠진 정보**.
- 실패(401·5xx·타임아웃·HTML) → 1회 재시도 → 그래도 실패면 `네이버 경쟁도 미검증` 으로 두고 우리 글만 보고 진행. STOP 아님.

[6-3] 잘되는 글 벤치마크 (2026-09-24 추가 — 수정안 작성 전 필수)
6-2 결과 중 **기관·카드사 공식 페이지를 뺀 정보글 상위 3편**(webkr 우선, 부족하면 blog)을 벤치마크 대상으로 삼아 아래 표를 채운다.
| 항목 | 상위 3편에서 볼 것 | 우리 글에 적용 |
|---|---|---|
| 제목 틀 | 키워드 위치 · 숫자(금액·날짜·개수) · 형식(목록형 "n곳/n가지" · 마감형 "~까지" · 비교형 "~별 비교" · 질문형) · 연도 표기 | 우리 본문이 뒷받침하는 틀 1개를 고른다. 상위 제목 문장을 베끼지 않는다 |
| 첫 화면 답 | 요약(설명란)에 바로 보이는 답 — 날짜·금액·대상·방법 중 무엇 | 메타 설명·첫 문단에 같은 종류의 답을 **우리 수치로** 먼저 쓴다 |
| 본문 구성 | 표(○○별 비교)·체크리스트·FAQ 유무 | 우리에게 없는 구성은 `본문 보강 후보` 로 기록(7-5 답 블록 조건이면 답 블록으로, 아니면 STEP 10에 제안만) |
| 차별점 | 상위 글이 오래됐거나(작년 연도), 공식 근거가 없거나, 빠뜨린 정보 | 제목 뒷부분·메타에 우리만의 정보로 드러낸다 |
- 결과는 `note` 와 log.md에 `벤치마크: {상위 3편 제목 틀 요약} → 적용: {고른 틀} · 보강 후보: {…}` 한 줄로 남긴다.
- 상위 3편 제목·요약은 수정안 근거로만 쓰고, 문장·표를 그대로 옮기지 않는다.

---

## STEP 7 — 원인 분류와 수정안

[7-1] 우리 글 현재 값
- REST `GET /wp-json/wp/v2/posts/{id}?context=edit` → `content.raw`
- **도입 첫 문단 = `style` 속성이 없는 첫 `<p>`**. 맨 위의 `<p style=...>2026년 9월 1일 작성 · 읽는 시간…</p>` 는 메타 줄이므로 건드리지 않는다(2026-09-24 실측).
- 현재 SEO 제목·메타·Focus Keyword: STEP 8-3 에디터 ①에서 확인한다(REST에는 없다).
- **문서 노출 vs 키워드 노출**: 문서 노출에서 TOP30 연결 키워드 노출 합을 뺀 비율(롱테일 비중)을 기록한다. 롱테일이 크면 제목을 한 키워드로 너무 좁히지 않는다 — 단, 6-1 데이터가 한 키워드 쏠림을 보여주면 그 키워드를 앞에 둔다.

[7-2] 원인 분류 — **노출 점유율(`share`)이 1차 근거**, 상위10 조사가 2차 근거
| 분류 | 판단 근거 | 처방 |
|---|---|---|
| A 제목·메타 약함 | `share` ≥ 30% 이고 우리 글이 webkr 상위10 안 | 제목·메타·첫 문단 |
| B 검색의도 불일치 | `share` 15~30%, 또는 키워드가 묻는 것(날짜·금액·방법·목록)과 제목 앞부분 각도가 다름 | 제목 앞부분을 `focus_kw` 의도에 맞추고 첫 문단에서 답을 먼저 |
| C 순위·노출 영역 문제 | `share` < 15% (검색은 많은데 우리가 거의 안 보임) 또는 상위10을 기관·언론이 채움 | B 처방 + **본문 답 블록(7-5)** |
- A·B·C 모두 제목 앞을 `focus_kw` 로 바꾸면 **7-6 정합성 보정**을 함께 한다.
- 수요 조회가 실패해 `share` 가 없으면 기존 기준(상위10 안/밖)으로 분류하고 답 블록은 추가하지 않는다.
- `cause_hint = "KW부족"`(`kw_short: true`) = 글의 노출이 조회한 키워드의 월 검색수보다 많다 → 키워드가 실제 유입 검색어를 못 잡은 것이라 `share` 를 믿을 수 없다(2026-09-24 추가). `python3 naver_volume.py --related 20 "{focus_kw}"` 로 **본문이 답하는** 더 큰 키워드를 찾아 `set-kw` → 4-5·4-6을 다시 돌린 뒤 분류한다. 그래도 KW부족이면 상위10 조사로만 분류하고 답 블록은 넣지 않는다.

[7-3] 작성 규칙
- **SEO 제목**: `focus_kw` 원문을 맨 앞에 그대로. 25~45자. 본문에 있는 구체값(마감일·금액·수치) 1~2개. 시기성 글은 마감일을 제목에 넣는다(예: `10/30 마감`). 상위10 제목과 겹치지 않는 우리 글만의 정보를 드러낸다. 부정형 훅("~해도 0원")을 앞에 두지 않는다.
- **메타 설명**: 110~155자. 첫 문장에 `focus_kw` + 마감/핵심 답. `keywordInMetaDescription` 유지.
- **도입 첫 문단**: 첫 문장에 `<strong>{focus_kw}</strong>` 와 결론(날짜·금액·조건). 길이는 기존 ±30%. 문체(~요/~습니다 혼용)는 기존 글과 같게. 본문 뒤쪽 꼭지를 안내할 때는 실제 H2 순서를 확인하고 쓴다.
- ⛔ 금지: 본문·공식 출처에 없는 사실·수치 / 과장·낚시 / 키워드 반복 / 슬러그·기존 H2 변경 / 첫 문단·답 블록 외 본문 수정.

[7-4] 재수정(v2·v3) 규칙
- `state.json` 의 이전 버전(before/after)을 읽고, **이전 버전과 다른 각도**로 쓴다. 같은 문장 순서만 바꾸는 수정은 금지.
- v1이 A·B 처방이었다면 v2는 ① `focus_kw` 가 바뀌었는지(수요 1위가 옮겨갔는지) 먼저 보고 ② 상위10에서 클릭을 받는 제목 유형(목록형·마감형·계산형 중 우리 본문이 뒷받침하는 것)으로 바꾼다. 답 블록이 없고 `share` < 15%면 v2에서 추가한다.
- 재수정은 판정 결과(`ctr_before → ctr_after`, 반영 후 노출·클릭, `share` 변화)를 근거로 `note` 에 한 줄 적는다.

[7-5] 본문 답 블록 (원인 C · ANSWER_BLOCK=AUTO일 때만, 글당 1개)
- 목적: `focus_kw` 로 검색한 사람이 첫 화면에서 답을 찾게 한다(2026-09-24 김해 섹션과 같은 방식).
- 구성: 새 H2 1개(`{focus_kw} — {핵심 답을 한 줄로}`, 기존 H2 스타일 속성 그대로 복사) + 도입 `<p>` 1개(2~3문장) + 표 1개(4~8행: 대상·금액·기간·방법·수령·문의 중 해당 항목) + 출처 `<p style="font-size:13px; color:#6b7280;">` 1개(공식 페이지 링크 + 확인 날짜).
- 사실은 **공식 출처(지자체·기관·제조사 공지)**에서 WebFetch로 확인한 것만 쓴다. 확인 못 한 항목은 행을 만들지 않는다. 기존 본문과 숫자가 다르면 답 블록을 넣지 않고 STEP 10에 `본문 수치 불일치 — 확인 필요` 기록.
- 위치: `<!-- TABLE OF CONTENTS -->` 바로 뒤. 표시가 없으면 첫 H2 바로 앞.
- 이미 `focus_kw` 가 들어간 H2가 있으면 답 블록을 만들지 않는다(중복 금지).

[7-6] 정합성 보정 — Rank Math 점수 유지 (2026-09-24 추가 · 모든 수정에 필수)
- 목표: `score_after ≥ score_before − 2` 이고 70 이상. `score_before` 는 8-0에서 잰다.
- 제목·FK를 `focus_kw` 로 옮기면 아래를 **같은 반영 안에서** 맞춘다(본문에 이미 있으면 건너뛴다):
  | 항목 | Rank Math 검사 | 고치는 법(최소) |
  |---|---|---|
  | Focus Keyword | 제목·메타·첫 문단의 키워드 | 1순위 `focus_kw`, 기존 1순위는 2순위로(서브 키워드는 제목과 비슷한 표현 순으로 정렬) |
  | 부제목 | H2~H4에 포커스 키워드 | `focus_kw` 와 가장 가까운 **기존 H2 1개**의 앞부분에 `focus_kw` 를 넣는다. 뜻과 순서는 유지, 스타일 속성 그대로 |
  | 이미지 대체 텍스트 | 포커스 키워드가 든 alt | 근거 화면(공지 캡처 등) 이미지 **1개**의 alt 앞부분을 `focus_kw` 로 바꾼다 |
  | 키워드 밀도 | 낮음 경고 | 요약 상자·핵심 정리 제목 같은 라벨 1곳에 `focus_kw` 를 넣는다. 문장 억지 반복 금지 |
  | URL | 슬러그에 키워드 | 바꾸지 않는다(슬러그 변경 금지) — 원래 실패였으면 그대로 둔다 |
- 방법: 8-3 에디터에서 새 값으로 넣은 뒤 **저장하지 말고** Rank Math 패널의 실패 항목(`li.test-fail`·`li.test-warning`)과 점수를 먼저 확인 → 위 표대로 본문 보정안을 만든다 → 본문은 8-2(REST)로, SEO 값은 8-3으로 반영한다.
- 보정 1회 후에도 목표 미달이면 제목·메타·첫 문단·보정을 모두 백업 값으로 되돌리고 `Rank Math 유지 실패 — 원복` 기록(엔진 기록 안 함 → 다음 날 다른 각도로).

---

## STEP 8 — 반영 (URGENT·NORMAL 모두 AUTO)

[8-0] 수정 전 점수 재기 — 에디터를 열어 8-3 ① 값(제목·메타·FK)과 `score_before = s.getAnalysisScore()` 를 기록한다. 그다음 7-6 확인(새 제목·메타·FK를 넣고 저장하지 않은 채 실패 항목 확인)을 하고, 에디터 값을 원래대로 돌린 뒤 `window.onbeforeunload=null` 로 탭을 `https://0and1life.com/` 로 옮긴다.

[8-1] 백업 — `backups/{slug}-{TODAY}-v{n-1}.json` 에 REST `context=edit` 응답(title·content·modified)을 저장한다. 저장 실패면 반영하지 않는다.

[8-2] 본문 교체 (REST, 에디터 탭 없음)
1) Chrome MCP 탭 중 `post.php` 가 있으면 `https://0and1life.com/` 로 이동(about:blank는 이동 불가 — 2026-09-24 실측).
2) python으로 `content.raw` 의 **style 없는 첫 `<p>…</p>`** 하나만 새 문단으로 바꾸고, 7-6 보정(H2 1개·alt 1개·라벨 1곳 — 각각 정확히 1곳 일치를 assert)을 같이 적용하고, 답 블록이 있으면 7-5 위치에 넣어 `POST /wp-json/wp/v2/posts/{id}` `{"content": ...}`. 원래 문단에 기대한 문구가 있는지, 삽입 기준 표시가 정확히 1개인지 assert 후 교체한다.
3) 8초 후 재조회: `status=publish` 유지 · `<p` 개수 = 백업 + (답 블록의 `<p` 수, 보통 2) · `<h2` 개수 = 백업 + (답 블록이면 1) · 새 문장 포함 · 옛 문장 없음. 하나라도 어긋나면 백업 raw로 즉시 되돌리고 `본문 반영 실패 — 원복` 기록, 8-3은 건너뛴다.
   ⚠️ 기대 개수는 **추가한 태그 수를 코드로 세어서** 계산한다(2026-09-24: 기대값을 손으로 +3으로 잡아 정상 반영을 원복한 사고가 있었다).

[8-3] SEO 제목·메타·Focus Keyword (Claude in Chrome 에디터)
navigate `https://0and1life.com/wp-admin/post.php?post={id}&action=edit` 후:
```javascript
await new Promise(r=>setTimeout(r,3000));
if (!document.body?.classList.contains('wp-admin')) throw new Error('not-logged-in');
if (!wp.data.select('rank-math')) { await new Promise(r => setTimeout(r, 3000)); }
const s = wp.data.select('rank-math'), ed = wp.data.select('core/editor');
// ① 현재 값 확인 — before 로 기록, 에디터 본문에 8-2 새 문장이 들어왔는지 확인
({ title: s.getSerpTitle(), desc: s.getSerpDescription(), fk: s.getKeywords(),
   p: (ed.getEditedPostContent().match(/<p/g)||[]).length, dirty: ed.isEditedPostDirty() })
```
```javascript
// ② 반영 — savePost 는 한 번만. 제목 앞이 focus_kw 면 K는 필수(focus_kw 를 맨 앞, 기존 키워드는 중복 없이 뒤로)
const T='NEW_SEO_TITLE', M='NEW_META', K='focus_kw, 기존1, 기존2';
const rm = wp.data.dispatch('rank-math');
if (K) rm.updateKeywords(K);
rm.updateTitle(T); rm.updateSerpTitle(T); rm.updateDescription(M); rm.updateSerpDescription(M);
await new Promise(r=>setTimeout(r,1500));
await wp.data.dispatch('core/editor').savePost();
await new Promise(r=>setTimeout(r,4000));
({ dirty: wp.data.select('core/editor').isEditedPostDirty(), title: s.getSerpTitle(), desc: s.getSerpDescription(), fk: s.getKeywords(), score: s.getAnalysisScore?.() })
```
- ①에서 `p` 가 REST 개수와 다르거나 새 문장이 없으면 저장하지 않는다(에디터가 구버전을 들고 있음) → 새로고침 1회 후 재확인, 그래도 다르면 중단·기록.
- ⛔ 재분석 트리거를 돌리지 않는다(Draft 루틴 [6j]).
- 저장 후 탭을 `https://0and1life.com/` 로 옮긴다.

[8-4] 검증
- REST 재조회: `status=publish` · `<p`·`<h2` 개수 유지(8-2 기대값) · ld+json 유지. 줄었으면 백업 raw로 원복하고 `저장 중 태그 소실 — 원복` 기록.
- 공개 페이지 `?nc={epoch}` 로 `<title>`·`<meta name="description">`·`canonical`·(답 블록이면) 새 H2 문구 확인. 캐시로 다르면 `캐시 반영 대기` 로만 기록.
- Rank Math: `score_after ≥ score_before − 2` 이고 70 이상이어야 한다. 미달이면 7-6 마지막 줄대로 원복한다.

[8-5] 수정 후 전수검사 (2026-09-24 추가 — Schd_0and1Life-Draft.md [6h]·[6j]·[6m-0] 기준, 반영마다 필수)
수정은 **승인 없이 바로 반영**하되(2026-09-24 사용자 지시), 반영 직후 아래를 전부 확인한다. 하나라도 실패하면 백업 raw와 이전 SEO 값으로 원복하고 `전수검사 실패 — 원복: {항목}` 을 기록한다(엔진 기록 안 함).
| 구분 | 확인 | 기준 |
|---|---|---|
| 상태 | REST `status`·`slug`·canonical | publish 유지 · 슬러그·canonical 불변 |
| 구조 | `<p`·`<h2`·`<figure`·`<img`·`<table`·`<a `·`wp:freeform` 개수 | 백업 + 추가한 수(코드로 계산)와 정확히 같음 · freeform 마커 2개 |
| 태그 짝 | div·ul·ol·table·figure·blockquote·p·h2·strong·a 여닫이 수 | 모두 같음(`<ul[\s>]` 정규식으로 셀 것) |
| 스키마 | ld+json 개수와 JSON 파싱 | 개수 유지 · 전부 파싱 성공 |
| Rank Math | 글 목록 화면(`/wp-admin/edit.php?s=…`)의 **서버 저장 점수** · 패널 실패 항목 | 수정 전 −2 이내·70 이상 · 실패 항목은 `keywordInPermalink`·`hasContentAI`·`contentHasShortParagraphs`(조치 불가)만 남아야 함 |
| 공개 페이지 | `?nc={epoch}` 의 `<title>`·description·robots·H1·H2 목록·목차 | 새 제목·메타 반영 · index 유지 · H2 수·순서 유지 · 목차에 바뀐 H2 반영 |
| 리소스 | 본문 이미지(0and1life.com) HTTP · 내부 링크 | 전부 200 · 내부 링크 수 유지(외부 기관 링크는 클라우드에서 000일 수 있음 — `확인 불가`로만 기록) |
| 품질 | 첫 문단 길이(기존 ±30%) · 키워드 반복(같은 문단 2회 이상 금지) · 본문 글자수 | 기준 안 · 1,500자 이상 |
- 결과는 log.md에 `전수검사: 구조 OK · 태그 OK · 스키마 OK · RM {전}→{후} · 공개 OK · 이미지 n/n` 한 줄로 남긴다.

---

## STEP 9 — 기록

[9-1] 엔진에 기록 (잠금의 유일한 근거 — 반드시 실행)
```bash
cat > /tmp/v.json <<'J'
{"slug":"...","status":"applied|rollback","track":"urgent|normal","date":"{TODAY}",
 "keyword":"{focus_kw}","ctr_before":{판정 시점 CTR},"impr_before":{노출},"published":"{발행일}","cause":"A|B|C",
 "volume":{월 검색수},"share_before":{노출 점유율},"momentum":{흐름},"rank_math":{"before":{score_before},"after":{score_after}},
 "before":{"title":"...","desc":"...","fk":"...","first_p":"backups/{파일명}"},
 "after":{"title":"...","desc":"...","fk":"...","first_p":"...","answer_block":"{H2 문구 또는 없음}"},
 "summary":"수정 요약 한 줄(무엇을 어떤 검색어·결론형으로 바꿨는지)",
 "benchmark":"6-3 벤치마크 한 줄",
 "note":"수요 근거(월 검색수·점유율·흐름) + 상위10 구성 한 줄"}
J
cd $W && python3 ctr_engine.py record --file /tmp/v.json
```
- `snapshot` 은 비워 두면 **최신 새(중복 아닌) 스냅샷**이 들어간다. 효과 판정은 이 스냅샷 이후 증가분으로 계산된다.
- 반영에 실패해 원복했으면 기록하지 않는다(다음 날 다시 뽑힌다).

[9-2] 7일 모니터링 표 (2026-09-24 추가 — 매일 실행, 반영이 없는 날도)
```bash
cd $W && python3 ctr_engine.py monitor --today {TODAY}
```
- 반영 후 7일 안의 모든 글에 대해 `monitor/{slug}.md` 와 전체 요약표 `monitor/_summary.md` 를 새로 쓴다: 수정 요약 + 반영 전 기준 행(일평균 노출·CTR) + D+1~D+7 일별 노출·클릭·CTR과 **증감(기준 대비·전일 대비)** + 반영 후 합계.
- 발행 30일 이내 글은 정확, 그보다 오래된 글은 근사(표에 표시). 중복 CSV 날은 빈 날로 표시된다.
- 7일이 지나면 `monitor_done` 으로 닫히고 효과 판정(evaluate)으로 넘어간다.

[9-3] `log.md` 맨 위에 추가
```
## {TODAY} · {v1 반영 | v2 재수정 | 되돌림} · {slug}
- 선정: {긴급 D-n | 기회 클릭 n | 놓친 클릭 n(수요 없음)} / 노출 {n} · CTR {x}% (목표 {target}%)
- 수요: {focus_kw} 월 {n}회 · 노출 점유율 {x}% · 흐름 {momentum}(최고 대비 {now_vs_peak}) · 연관 상위 {kw n}
- 대표 키워드: {focus_kw} (선정 근거 한 줄) · TOP30 노출 {n} · CTR {x}%
- 네이버: WT {n} / BT {n} / 우리 글 webkr {순위|밖} / 상위10 {구성}
- 원인: {A|B|C} — {share 근거 + 상위10 근거}
| 항목 | 전 | 후 |
|---|---|---|
| SEO 제목 | … | … |
| 메타 설명 | … | … |
| Focus Keyword | … | … |
| 첫 문단 | (백업 파일) | … |
| 답 블록 | 없음 | {H2 문구 · 표 n행 · 출처} |
- 정합성 보정: FK {전→후} · H2 {전→후 또는 없음} · alt {전→후 또는 없음} · 라벨 {…}
- 검증: REST p {n}→{n} · h2 {n}→{n} · 공개 title {일치|캐시 대기} · Rank Math {수정 전}→{수정 후}
```

---

## STEP 10 — 완료 알림 (앞 단계 성공 여부와 무관하게 반드시 실행)

```
🔎 네이버 CTR 루틴 {TODAY}
- 데이터: {스냅샷 날짜} (stale {n}일{· 중복 CSV {날짜}}) · 목표 CTR {x}% · 수요 {조회됨 | 트렌드만 | 실패}
- 7일 트래킹 표: `monitor/_summary.md` 의 표를 **그대로** 붙인다(글 · 반영일 · 경과 · 수정 요약 · 반영 전 일노출·CTR · 최근일 노출(기준 대비 %) · 최근일 CTR(기준 대비 %p) · 반영 후 누적 노출·클릭·CTR(기준 대비 %p) · Rank Math 전→후). 노출은 수요에 흔들리므로 효과는 CTR 증감으로 먼저 판단한다
- 효과 판정: {slug v1 — KEEP CTR 0.83%→1.5% (반영 후 노출 +535 · 클릭 +8 · 점유율 12%→18%)} / {slug — WAIT 노출 335/400 · 클릭 3/5 · 1/4일} …
  ※ CTR과 함께 **반영 후 클릭 수와 노출 점유율**을 반드시 적는다(검색량 변화로 클릭이 늘거나 준 것과 구분하기 위해)
- 오늘 작업: {재수정·되돌림·새 반영} — {slug} — 원인 {A|B|C} — {focus_kw} 월 {n}회 · 점유율 {x}%
  제목: {전} → {후}{ · 답 블록 추가}
- 대기열 다음 3편: {slug(긴급 D-n | 기회 클릭 n | 식음)} …
- 제외: 내년용 {n} · 네이버 즉답 {n} · 되살림 {n}
- ⚠️ 조치 필요: {CSV 갱신 없음 · 검색광고 키 · 수요 조회 실패 · pw.txt · 로그인 · LIMIT 글 · 본문 수치 불일치 · 우리 글 없는 고수요 키워드}
```

---

## 효과 판정 규칙 (ctr_engine.py `evaluate`, 참고용 — 수치는 CFG)

- 반영 후 데이터 = **오늘(최신 새) 스냅샷 − 반영 당일 스냅샷**(노출·클릭 증가분). 서치어드바이저 조회 기간(WINDOW_DAYS=30) 안에 발행된 글은 정확하고, 그보다 오래된 글은 누적 CTR 비교로 근사한다(출력에 `method` 로 표시). 중복 스냅샷은 새 데이터로 치지 않는다.
- 판정 시점(2026-09-24 개정 — 노출 150에서는 클릭 1~2번 차이로 결과가 뒤집혀 운에 가까웠다):
  - 긴급 = 반영 후 **노출 +400 이상 그리고 클릭 +5 이상**. 4일이 지나면 쌓인 만큼으로 판정
  - 상시 = 반영 후 **노출 +800 이상 그리고 클릭 +8 이상**. 14일이 지나면 쌓인 만큼으로 판정
  - 판정 전에는 WAIT로 두고 `노출 n/기준 · 클릭 n/기준 · 경과일/기한` 을 보고한다
- KEEP: 반영 후 CTR ≥ max(이전×1.3, 이전+0.5%p) 또는 ≥ 목표 CTR → 14일 보호(HOLD), 그 뒤 목표 미달이면 다시 후보.
- REEDIT: 기준 미달 → 재수정(버전 +1). 3차(v3)까지 개선이 없으면 LIMIT → 30일 닫음. 단 `momentum` < 0.5면 재수정 보류(STEP 5-2).
- ROLLBACK: 반영 후 CTR < 이전×0.7 → 직전 값으로 되돌림(답 블록 포함).
- 이벤트가 지난 글(E3)은 더 고치지 않는다. **단 검색이 살아 있으면(`e3_revived`) 상시 글로 다룬다.**
- 참고 지표: `share`(노출 점유율)가 오르면 순위가 오른 것, CTR이 오르면 제목이 먹힌 것이다. 둘을 따로 보고한다.

## 색인 영향 메모

제목·메타·첫 문단(+원인 C일 때 답 블록 1개)만 바꾸고 **URL(슬러그)·canonical·기존 H2 구조는 유지**하므로 네이버·구글은 같은 문서의 갱신으로 처리한다(수정일 갱신 → 재수집). 오류가 되는 경우는 URL 변경, 본문 대량 교체, 짧은 간격의 반복 변경인데, 이 루틴은 URL을 바꾸지 않고, 답 블록은 글당 1개로 제한하며, 재수정 간격(긴급 노출 +400·클릭 +5 또는 4일, 상시 노출 +800·클릭 +8 또는 14일)과 3차 한도로 반복 변경을 막는다.

---

## 오류 처리 요약

| 상황 | 처리 |
|---|---|
| Claude 폴더 미연결 | 폴더 요청 없이 STEP 1 2-B(클라우드 폴백) → stage도 실패하면 STEP 10 |
| 네이버_수집 폴더 미연결 | 2-B의 stage로 CSV만 가져옴 → 실패해도 inbox만으로 진행 |
| 같은 내용 CSV(중복) | 새 데이터로 치지 않음 → stale 규칙(STEP 4-0) |
| 새 CSV 없음(stale 1~2) | 판정·재수정 건너뜀, 새 대상 1편은 진행 |
| 새 CSV 없음(stale ≥ 3) | 판정·수정 건너뜀, STEP 10에 `CSV 미수집` |
| pw.txt WP·NCP 키 누락 | 키 이름만 적고 종료(값 출력 금지) |
| 검색광고 키 누락·형식 이상·403 | 트렌드만으로 진행, STEP 10에 `검색광고 키 확인 필요` |
| 수요 조회 둘 다 실패 | 1회 재시도 → 수요 없이 기존 순서로 진행, 답 블록 안 넣음 |
| 릴레이(naver-check) 실패 | 1회 재시도 → `네이버 경쟁도 미검증` 으로 계속 |
| 06:45~08:00 사이에 STEP 8 도달 | 반영하지 않고 수정안만 log.md, 엔진 기록 안 함 |
| 08:00 이후 늦은 실행·수동 실행 | 에디터 충돌 없음 → 정상 반영 |
| device_bash "Workspace unavailable"·마운트 없음 | 폴더 요청 없이 STEP 1 2-B(클라우드 폴백) |
| 같은 날 같은 글을 다시 반영 | 엔진이 앞 버전을 SUPERSEDED로 표시 → 재수정 한도에 넣지 않음 |
| 본문 반영 후 불일치 | 백업 raw로 원복, 제목·메타 반영 안 함, 엔진 기록 안 함 |
| 에디터가 구버전 본문 보유 | 저장하지 않음 → 새로고침 1회 → 실패 시 중단·기록 |
| 저장 후 태그 소실 | 백업 raw로 원복, 기록 |
| 공식 출처 확인 실패 | 답 블록 없이 제목·메타·첫 문단만 반영 |
| Rank Math 점수 하락(수정 전 −2 초과 또는 70 미만) | 7-6 보정 1회 → 그래도 미달이면 전부 원복, 엔진 기록 안 함 |
| 서치어드바이저·네이버 검색·데이터랩 화면 접근 | 시도 금지(안전 제한 확인됨) |
| 네이버 API 직접 호출 | 시도 금지 — 사이트 릴레이만 사용 |
