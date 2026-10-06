[루틴 : KoreaPlug-Writer — v10.5 · 2026-10-06]

> **v10.5 변경 (지침서 v13.5 대응)**: 4-B의 (라) 판정을 GAP 질문 기준으로 옮김(헤드 기본 답만으로 탈락 금지 · 도구 요약문 불사용) · 위키백과만 나오면 1회 재검색 · 순서를 4-B(가·나·다) → 4-C 경쟁글 H2 → 4-D GAP 확정 → (라) 판정으로 정렬

> **v10.4 변경 (지침서 v13.4 대응)**: 수량 상한 전부 폐지 — 주간 상한(STEP 0-A 2-b) · 심사 중 모드(2-c) · 업그레이드 주 3회(STEP 0 ③) · 제도 주 1편(STEP 0 ④·STEP 3 ⑤) · 시즌 7일 간격. 남긴 가드는 같은 날 중복 실행 방지(0-A ①·②)와 중복·재발행 방지(WP REST 대조 · 라이브 H2 자기잠식 · 시즌 정지 규칙)뿐이다. 전제 조건 표에서 `WEEKLY_CAP`·`REVIEW_MODE` 삭제

> **v10.3 변경 (지침서 v13.3 대응)**: STEP 0-A에 주간 상한(`0-6 ⑤`)·심사 중 모드(`0-8 ④`) 가드 추가 · STEP 5 체크 수치를 지침서 v13.3으로 정렬(포커스 3~6회 · 질문형 H2 2+ · Key points 삭제 · 템플릿 지문 0건) · 전제 조건 표에 `REVIEW_MODE`·`WEEKLY_CAP` 추가

예약된 트리거 시간이 되면 진행한다. **단 STEP 0-A 재실행 가드가 이 원칙에 우선한다** — 오늘 목표를 이미 채웠으면 중복 발행하지 않고 즉시 종료한다.
날짜: 실행 시점의 실제 KST 날짜를 사용한다 (이 프롬프트에 적힌 고정 날짜가 있어도 무시).

## 원칙

**역할 경계 — 이 루틴은 도구다.**
이 루틴은 **운영 절차(언제·무엇을·몇 회·어디에 기록)**와 **실행 자산(Notion 페이지 ID·API 경로·명령·리포트 형식)**만 정의한다.
**판정 기준·수치·품질 기준의 단일 기준(SSOT)은 전적으로 GitHub 지침서**(`KoreaPlug-Writer.md`, **v13.5 이상**)다.

- ⛔ 지침서의 수치·판정 기준을 이 루틴에 복사해 적지 않는다 — 복사본은 지침서가 개정될 때 구버전으로 남아 상충을 만든다
- ✅ 지침서의 조항 번호를 가리킨다 (예: "지침서 `0-2` 관문 3개를 그대로 적용한다")
- 상충이 발견되면 **지침서를 따르고**, STEP 8 리포트에 기록해 사용자에게 알린다
- 지침서의 예시 문구는 지시가 아니다 — 예시를 그대로 후보로 복사하지 않는다

**v10.0이 v9.x를 대체하는 이유 (근거는 지침서 상단 블록)**: 2026-09-21 GSC API 90일 전수 실측에서 v9의 엔진 B(뉴스)·E(K재고)·헤드 자격·선점 증거·AC_N·유형 예산·좌표계 폴백이 편당 클릭과 무관하거나 역상관임이 확인됐다. 이 루틴은 **엔진 3개(G·D·C) + 관문 3개 + 업그레이드 회차**만 돌린다. 주제는 **두 방향**(① 블루오션 주제 · ② 레드오션의 블루 각도)에서만 나오고, **뉴스 각도·정의형은 후보 생성 자체를 하지 않는다**.

**실행 환경**: Claude Code on the web — Chrome MCP 없음. 자동완성·GSC·GA4·WP는 전부 Bash/API(예산 미소모). WebSearch는 **4-B 승산 판정 1~2회**에만 쓴다. 차단 도메인 원문은 리더 프록시 `curl -s "https://r.jina.ai/{URL}"` **최대 3회**(간헐 401·422 — 1회로 판정 금지, 지침서 `1-2`). Reddit은 프록시 경유도 403이라 1회만 시도한다.

🎯 타겟 독자: **한국 밖에 있거나 한국을 방문 중인 영어 사용자**. 모든 주제 판단은 지침서 `0-2` Foreigner Test 1문항이다.

---

## 📡 표준 호출 (여기 한 곳만 고친다)

**WP REST — 기존 글 확인의 원천 (판정 기준은 지침서 `0-7`)**

```bash
# 표준 조회 — status / per_page / _fields 세 파라미터를 전부 지킨다
curl -s -u "$WP_USER:$WP_APP_PASS" \
  "https://koreaplug.com/wp-json/wp/v2/posts?search={핵심어}&status=any&per_page=100&_fields=id,slug,status,title"

# 절단 확인 — 반환 건수가 per_page와 같을 때
curl -s -u "$WP_USER:$WP_APP_PASS" -D- -o /dev/null \
  "https://koreaplug.com/wp-json/wp/v2/posts?search={핵심어}&status=any&per_page=1&_fields=id" | grep -i x-wp-total

# 인증 실측 — 200이면 성공
curl -s -u "$WP_USER:$WP_APP_PASS" "https://koreaplug.com/wp-json/wp/v2/users/me?_fields=id,name,slug"

# 라이브 H2 대조 (자기잠식 선확인) — 슬러그는 REST 결과 그대로, 추측 금지
curl -s -u "$WP_USER:$WP_APP_PASS" "https://koreaplug.com/wp-json/wp/v2/posts?slug={slug}&status=any&_fields=id,status,content" \
  | python3 -c "import sys,json,re;c=json.load(sys.stdin)[0]['content']['rendered'];[print('-',re.sub('<[^>]+>','',h).strip()[:90]) for h in re.findall(r'<h2[^>]*>(.*?)</h2>',c,re.S)]"

# Rank Math 메타 읽기/쓰기 (업그레이드 회차) — context=edit 필수
curl -s -u "$WP_USER:$WP_APP_PASS" "https://koreaplug.com/wp-json/wp/v2/posts/{id}?context=edit&_fields=id,title,meta,content"
curl -s -u "$WP_USER:$WP_APP_PASS" -X POST -H "Content-Type: application/json" --data-binary @patch.json \
  "https://koreaplug.com/wp-json/wp/v2/posts/{id}?context=edit&_fields=id,modified,title,meta"
#  patch.json = {"title":..,"content":<raw>,"meta":{"rank_math_title":..,"rank_math_description":..,"rank_math_focus_keyword":"kw1,kw2,..."}}

# 내부 링크 공개 여부 검증 (STEP 5-4 · 4-U 필수) — 본문 HTML의 모든 상대경로 링크를 추출해 status 재조회
for s in $(grep -oE 'href="/[^"#?]+/"' post.html | sed -E 's#href="/([^"]+)/"#\1#' | sort -u); do
  st=$(curl -s -u "$WP_USER:$WP_APP_PASS" "https://koreaplug.com/wp-json/wp/v2/posts?slug=$s&status=any&_fields=id,status" \
       | python3 -c "import sys,json;d=json.load(sys.stdin);print(d[0]['status'] if d else 'NONE')")
  echo "$s $st"; [ "$st" = "publish" ] || echo "  ⛔ 교체 필요: $s ($st)"
done
```

- ⚠️ `per_page=100` 고정 · `_fields` 생략 금지 · `status=any` 필수 — 위반 시의 결과는 지침서 `0-7`
- ⚠️ 인증 호출은 Bash/curl 전용. `status=any`가 HTTP 400이면 인증 실패 → `status` 빼고 발행분만 조회하고 STEP 8에 기록. **STOP 사유 아님**
- ⚠️ 소프트404: 존재하지 않는 슬러그도 HTTP 200. 실존은 REST 결과(id + status)로만 판정
- ⛔ **내부 링크는 `status=publish`(공개) 글만** — `future`(예약)·`pending`(검토 대기)·`draft`·`private`는 공개 전까지 404. `status=any` 검색 결과에 섞여 나오므로 `status` 열로 걸러 고른다 (지침서 `2-5`)
- ⚠️ REST가 간헐적으로 HTML(WAF 챌린지)을 돌려준다 — JSON 파싱 실패 시 5초 후 `-A "Mozilla/5.0"`으로 1회 재시도

**GSC · GA4 — 데이터 SSOT (규격은 지침서 `0-9`)**

```bash
# 키: 환경변수 GSC_SA_JSON(JSON 원문) 또는 GSC_SA_JSON_PATH. 둘 다 없으면 Drive MCP로
#     'koreaplug-shorts-*.json' 검색 → download_file_content → base64 -d → 세션 임시 폴더에 저장 후 GSC_SA_JSON_PATH 지정
python3 tools/gsc_pull.py --site https://koreaplug.com/ --days 90 --out out/gsc
#  → out/gsc/koreaplug.com/{오늘}/ : daily.csv · pages_28d.csv · queries_28d.csv · query_page_28d.csv · country_28d.csv · device_28d.csv · summary.md
#  엔진 G 입력 = query_page_90d.csv · engine_g_candidates.csv (노출≥50·순위 5~30·비정의형 1차 필터 적용본)
```

- 키 파일은 **세션 임시 폴더에만** 두고 저장소에 커밋하지 않는다
- 수집 실패(키 없음·API 403)는 **엔진 G 생략 사유일 뿐 STOP 사유가 아니다** — D·C로 진행하고 STEP 8에 원인을 적는다

**구글 자동완성** (예산 미소모): `https://suggestqueries.google.com/complete/search?client=firefox&hl=en&q={시드}` — 반환 배열 `[1]`이 변형, `[3].google:suggestsubtypes`는 참고용

---

## STEP 0-A — 재실행 가드 (최우선 — 지침서 조회보다도 먼저)

1. **발행 목록**(https://www.notion.so/33cbfe4a2ae181b9a743cb7c194dea7f) **하나만** 조회한다
2. **지침서 `0-6 ①`** 적용: 현황표에서 작성일자 = 오늘(KST)인 행 개수(`TODAY_COUNT`, `[U/업그레이드]` 행 포함)를 `DAILY_TARGET`(전제 조건 표, 미지정 시 1)과 비교
   - `TODAY_COUNT >= DAILY_TARGET` → **즉시 종료.** 아래 한 줄만 출력:
     `⏭️ KoreaPlug — {today_kst} 목표 달성 ({TODAY_COUNT}/{DAILY_TARGET}건, 최신 #{XX}). 트리거 no-op 종료.`
   - 미달 → 3으로
3. **`0-6 ②` 부분 완료 확인**: 4개 카테고리 페이지에 `Blog #{MAX_NUM+1}` 초안이 오늘 생성돼 있는가?
   - **있음** → 새 글을 쓰지 않는다. **STEP 7만 이어서 수행**하고 종료 (표 행 값은 초안의 [섹션 1]에서 그대로, 헤더·로그 중복 갱신 금지, STEP 8은 `🔁 재실행 가드: STEP 7 이어받기`로 축약)
   - **없음** → STEP 0으로
4. **`0-6 ④` 미달 감지**: 최근 작성일자와 오늘 사이의 미달 날짜를 세어 STEP 8에 보고

## STEP 0 — 데이터 수집 · 시즌 창 · 인증 (세션당 1회)

① **GSC·GA4 수집**: 📡 블록대로 `tools/gsc_pull.py --days 90`. `summary.md` 상단(7일·28일 클릭 변화, 상승·하락 상위)을 읽어 STEP 8 🗄️ 줄에 옮긴다. `GSC_STATUS = 정상/실패`.

② **시즌 창 판정**: 지침서 `0-4` 캘린더에서 오늘이 포함된 창 + 시행일 확정 제도 + 날짜 확정 일회성 이벤트를 확인해 `SEASON_WINDOW = 열림/닫힘`, 열림이면 이벤트명·D-day. **정지 규칙은 발행 목록 현황표(편수·발행일) + GSC daily(직전 2편 7일 클릭)로 판정**한다. 음력·수능 날짜는 매년 실제 날짜 확인 — 불가 시 그 이벤트는 이번 회차 제외.

③ **WP 인증 실측** + `WP_TOTAL`(`?status=any&per_page=1`의 `x-wp-total`, publish/future/draft 각각) → STEP 8.

⑥ **자동완성 1회 조회**로 `WEBFETCH_STATUS = 정상/차단` 확정 (이후 재판정 금지).

## STEP 1 — 참조 자료 읽기 (검색 없이)

- **지침서**: `https://raw.githubusercontent.com/leejc0404/blog/main/KoreaPlug-Writer.md?cb={epoch_ms}` — WebFetch가 인용을 거부하면 `curl`로 원문. 404/403이면 저장소 루트 1회 재확인 후 실패 시 **STOP** (추측으로 지침 생성 금지)
  → **버전 확인**: 상단이 **`v13.5` 이상**이고 `0-0 두 방향·두 금지` · `0-1 엔진 G·D·C` · `0-2 관문 3개` · `0-3 채점 3축` · `0-5 업그레이드 회차` · `0-9 GSC·GA4 규격` · `1-1 승산 판정 (가)~(라)` · `1-2 경쟁글 H2 대조` 가 있는가? 없으면 구버전 — STEP 8에 SSOT 이슈로 기록하고 사용자에게 알린다
  → 읽을 조항: `0-0` / `0-1` / `0-2` / `0-3` / `0-4` / `0-5` / `0-7` / `0-8` / `1-0`~`1-3` / `2-1`~`2-3` / `2-5` / `2-6`
- **발행 목록** (https://www.notion.so/33cbfe4a2ae181b9a743cb7c194dea7f): `MAX_NUM` · 이벤트별 편수·발행일 · 최근 7일 `[U/업그레이드]`·`[제도]` 행 수. ⚠️ 중복 대조에는 쓰지 않는다(WP REST가 원천) · 행 수 ≠ 자산 수
- **키워드 백로그** (https://www.notion.so/3a9bfe4a2ae1818f911bf852981d5018): 상태 '대기' 항목 — 엔진 D의 입력으로 합류(같은 관문 적용). '업그레이드 대기' 항목은 엔진 G (a) 후보로 합류
- **발행 반려 로그** (https://www.notion.so/3adbfe4a2ae18167880ecbe3c73b90cc): 최근 7일 행. 같은 사유 코드 2회 이상 반복 유형은 이번 회차 제외. '조달 주체=사용자' 미해결 3건 이상이면 루틴 조달 가능 주제만
- **최신 주간 GSC 리포트** (398bfe4a-2ae1-8150-93c4-fb98977c64bf): "## 리포트 (최신순)" 맨 위의 다음 조치만 확인
- ⛔ **K-콘텐츠 재고 캐시·커버리지 좌표계는 읽지 않는다** (v10.0 폐지 — 참고용으로만 남아 있다)

## STEP 2 — 후보 발굴 (엔진 3개 전부, WebSearch 0회)

**순서**: `SEASON_WINDOW=열림` → **C → G → D** / 닫힘 → **G → D → C**. 세 엔진 모두 실행한다 — 하나라도 건너뛴 채 "후보 없음"을 선언하면 규칙 위반이다.

**엔진 G — GSC 쿼리 갭** (지침서 `0-1 G`)
1. `engine_g_candidates.csv`(수집기가 노출 ≥ 50 · 순위 5~30 · 비정의형으로 1차 필터한 것)를 페이지별로 묶는다. 결정형 여부는 지침서 `0-2 ①`로 다시 본다
2. 각 쿼리를 📡 WP REST `?search=`로 대조 — 그 쿼리(또는 의미상 같은 문구)가 **제목·H1·첫 H2·메타**에 있는 페이지가 있으면 후보에서 제외
3. 남은 쿼리마다 걸린 페이지의 **라이브 H2**를 읽고 판정:
   - 본문이 이미 답을 갖고 있다 → 노출 100+ 는 **(a) 업그레이드 후보** , 50~99는 백로그 '업그레이드 대기'로 적재
   - 답이 없거나 각도가 다르다 → **(b) 신규 후보** (그 쿼리가 포커스 키워드)
4. 정의형 제로클릭 페이지(`-meaning` · `why-do-koreans-` · `-explained` 계열)에 걸린 쿼리는 (a) 대상이 아니다
5. 출력 형식: `쿼리 | 노출 | 순위 | 걸린 페이지 | (a)/(b)` — 상위 10개까지

**엔진 D — 결정 쿼리 군집** (지침서 `0-1 D`)
1. 지침서 `0-1 D` **요일별 `{x}` 군**에서 시드 틀을 조합해 **최소 8개** 자동완성 조회 (오늘 요일 = KST)
2. 지침서 `0-1 D` 후보 조건(변형 6+ 이고 reddit·tourist 변형 有 또는 만석)을 통과한 시드만 후보화. 변형 문구 그대로 기록
3. 백로그 '대기' 항목을 여기에 합류시킨다(출처가 GSC쿼리인 항목은 수요 증거 5로 간주)
4. Reddit `search.json?q={키워드}&t=year`는 1회만 시도, 실패 시 건너뜀
5. 출력: `키워드(verbatim) | 시드 | 변형 수 | reddit 변형 유무`

**엔진 C — 시즌·날짜 이벤트** (지침서 `0-1 C` · `0-4`)
1. STEP 0 ②에서 정지되지 않은 이벤트만 + **공식 공지 4곳 제목 스캔**(지침서 `0-1 C`: AREX · 인천공항 · Korail · 서울시 영문 — 리더 프록시 각 3회, 제목만, 날짜+행동 변경만 후보화)
2. 이벤트마다 `0-4` 실행 수식 축에서 각도 2~3개 → 자동완성 실존 문구 또는 확정 사실 용어로 키워드 조합
3. 📡 WP REST `search={이벤트명}` + 라이브 H2로 **같은 이벤트 기존 글의 실행 수식을 제외**
4. 출력: `키워드 | 이벤트 | D-day | n편째 | 직전 2편 7일 클릭`

→ 합산 후보 **8~15개**. 각 후보에 방향(①/②/시즌)과 엔진을 표기한다.
→ 세 엔진 모두 0개면 STOP: ⚠️ 경고 + 사용자 알림. **즉흥 발명·재브레인스토밍 금지.**

## STEP 3 — 관문 3개 + 채점 → 숏리스트 (검색 이전)

후보 전체에 순서대로 적용한다. 판정 기준은 전부 지침서 `0-2`·`0-3`·`0-7`·`0-8`.

① **두 금지** (`0-0`): 뉴스 각도 · 정의형 → 제거
② **WP REST 중복 대조 + 라이브 H2 자기잠식** (`0-7` · `1-3`): 같은 각도 기존 글이 있으면 제거 — 단 엔진 G (a) 조건에 맞으면 **업그레이드로 재분류**
③ **Foreigner Test 1문항** (`0-2`)
④ **클릭 필연성** (`0-2 ①`): 답이 한 문장이면 제거
⑤ **채점** (`0-3`): 수요 증거 · 클릭 필연성 · 승산(잠정 — 4-B 전에는 (다) 미실측이므로 수요·필연성 두 축만) — 어느 축이든 1점이면 제거

출력 표: `순위 | 키워드 | 방향 | 엔진 | 수요 증거(숫자) | 클릭 필연성 /5 | 잠정 합계 | (a)업그레이드/(b)신규`
→ 상위 2~3개 숏리스트, 나머지 예비. **엔진 G (a) 업그레이드 후보가 숏리스트 1위이면 STEP 4-U로**, 아니면 STEP 4로.

## STEP 4 — 승산 판정 + 경쟁글 H2 대조 (WebSearch 1~2회)

**[4-B] 승산 판정** — 숏리스트 1순위로 `"{키워드}" -site:koreaplug.com` 1회. 지침서 `1-1` 표대로 **(가)·(나)·(다)·(라) 네 값을 숫자로** 읽는다.
- 결과가 위키백과·백과사전뿐이면 **검색 이상** → 따옴표 없이 `{키워드} guide`로 1회 재검색(지침서 `1-1`)
- (다) 0건 → 탈락 → 2순위로 1회 더. 둘 다 탈락이면 예비 리스트 → 그래도 없으면 STOP
- ⚠️ (라)는 여기서 판정하지 않는다 — 4-D에서 GAP 질문을 확정한 뒤 판정한다. 검색 도구의 AI 요약문은 근거로 쓰지 않는다
- 통과 → 같은 결과에서 블로그/가이드형 URL 2~3개 확보 (추가 검색 금지)
- 승산 점수를 채점표에 반영해 최종 합계 확정

**[4-C] 경쟁글 H2 대조** — 지침서 `1-2`: WebFetch → 실패 시 리더 프록시 **3회**. H2/H3 전부·발행일·수치 유무 기록. 3회 전부 실패 시에만 스니펫으로 대체하고 STEP 8에 기록.

**[4-D] GAP 질문 확정** — 경쟁글이 답하지 않는 검색자 질문 **1개 = 첫 H2**. 없으면 발행 금지 → 차순위.

**[4-E] (라) 판정** — 지침서 `1-1` (라): 상위 결과 제목·URL과 4-C에서 읽은 경쟁글 H2가 **4-D의 GAP 질문**에 이미 정면으로 답하면 `완결` → 탈락 → 차순위. 헤드 질문의 기본 답만 있으면 `부분` → 통과.

## STEP 4-U — 업그레이드 회차 (엔진 G (a) 채택 시 — STEP 5·6 대신)

지침서 `0-5` 수정 범위 안에서만 고친다. **지어내지 않는다** — 본문에 없는 사실이 필요하면 (b) 신규로 돌린다.

1. 📡 `context=edit`로 `title` · `content.raw` · `rank_math_*` 3종을 읽어 **세션 파일에 백업**(before)
2. 새 값 작성: 제목·H1(`2-2` 규칙, ≤60자, 대상 쿼리 선두) · `rank_math_description`(130~155자, 대상 쿼리 선두) · `rank_math_focus_keyword`(대상 쿼리 + 서브 3~4개, 쉼표 구분 공백 없음) · 첫 H2를 대상 쿼리의 질문형으로 + 직답 첫 문장 · 인트로 첫 문장 · AEO 3줄 박스(`2-3`) · 필요 시 표 열 1개 또는 문단 1개(출처 있는 것만) · 관련글 링크를 인접 글(REST `status=publish`만 — 예약·대기·임시 금지)로
3. 자가검사: `<h1>` 1개 · 태그 개폐 균형 · 플레이스홀더 0 · 4열+ 표 래퍼 · 대상 쿼리 출현 4회 이상 · 📡 내부 링크 공개 여부 검증 전부 `publish`
4. 📡 PATCH → 응답의 `title`·`meta` 확인 → 라이브 `<title>`·`<meta description>`·첫 H2를 `curl`로 재확인
5. STEP 7로 (Notion 카테고리 페이지 생성 없음)

## STEP 5 — 본문 작성 (스킬 2종 필수 — 지침서 `2-6`)

**[5-0] Skill `create-viral-content` — 구조·훅 단계 (초안 작성 전)**
- SEO Title·H1: 후보 10개 이상 → 검색어 일치/구체성/사실성 3축 스코어링(각 0~3, 합 7+ 채택, 지침서 `2-6 ①`). 직전 10개 제목과 동일 훅 2회+면 교체 · 직전 10편 중 콜론형 3편이면 콜론 없는 후보만 · 호기심 갭 금지어(`2-2`) 0
- INTRO 첫 문장: Hook Architecture(Prediction+Stakes / Before-After Compression / 문제 직격 중 택1) + 첫 100~150단어 안에 직답
- 클로저: engagement bait 금지, 독자가 지금 할 행동 중심
- 정제 패스 최소 3개: Skeptic → Scroller → Editor

**[5-1] 본문 작성 — 지침서 각 Phase 직접 참조**
- 키워드·서브키워드 → `1-0` (자동완성·GSC 실존 문구만, AI 임의 조합 금지)
- 대표 이미지 → `1-5` (**숫자-해시 전체 ID**, `curl` 200 확인, WP REST `?search={ID}` 0건 확인)
- 기본 메타 → `2-1`: **방향 · 엔진 · 수요 증거 · 승산 판정 · 클릭 필연성 · GAP 질문 · 배포 우선 · 1급 자료 조달 계획** 행 필수 — 전부 숫자·실측값
- HTML → `2-3` 필수 템플릿 + 구조 규칙 전부(본문 래퍼 · 금지 블록 없음 · 태그 개폐 균형 · 플레이스홀더 0 · `<h1>` 1개 · 4열+ 표 래퍼 · TOC 플레이스홀더 2개 · AEO 3줄 박스(라벨 없음) · FAQ 마크업 · **상황 질문형 H2 2개 이상, 같은 문형 반복 금지** · 히어로 메타 줄 없음 · 사이트 공통 H2 없음)
- **첫 H2 = STEP 4-D의 GAP 질문**, 첫 문장 20~30단어 직답
- 단어수·밀도·링크 → `2-5` / 테마 컬러 → Phase 7
- ⛔ **내부 링크 = 공개(`status=publish`) 글만.** 예약(`future`)·대기(`pending`)·임시(`draft`)·비공개(`private`) 글은 곧 공개될 예정이어도 걸지 않는다 — 공개 글이 없으면 인접 주제의 공개 글로 대체
- 시즌·날짜 이벤트 추가 요건: SEO Title 연도 / INTRO D-day / (나) 날짜×항목 매트릭스 / slug 연도 미포함 / 배포 우선 `당일`
- 방향 ② 추가 요건: (나) = 경쟁글이 흩어 놓은 사실을 처음 한 표로 통합한 결정표 (출처·확인일 병기)

**[5-2] Skill `avoid-ai-writing` — 최종 패스 (HTML 완성 직후, Notion 업로드 전)**
- voice profile: casual~warm, 구어체 — 1인칭은 실제 수행한 행위에만
- 균일 문장 길이·기계적 전환어·과잉 열정·engagement bait 제거. 수치·고유명사·링크·HTML 구조 보존

**[5-3] 문체 지문 대조 — 구조 항목만 (지침서 `2-6 ③`)**
짧은 문장 우위 + 길이 혼합 / 기계적 전환어 0 / 실용 정보 선배치 / 단점·한계 최소 한 단락 / 마무리는 행동 지시 / `*Key points` 꼬리 없음 / 반박형 오프너 없음

**[5-4] 지침서 `5-3` + `5-5` 체크리스트 교차 검증 — 기계적으로 카운트**
단어수(1,500~2,000) · 포커스 키워드 **3~6회**(정확일치 강제 삽입 0) · 외부 링크 2+(위키 단독 금지) · 내부 링크 1+ · 사진·캡처 1장 · 구조 규칙 6종 · 첫 H2 = GAP 질문 · 상황 질문형 H2 2+ · **지침서 `5-3` 마지막 항목(v13.3 템플릿 지문 0건)**
→ **📡 내부 링크 공개 여부 검증**을 실행해 모든 링크가 `publish`인지 확인한다. 하나라도 `future`·`pending`·`draft`·`private`·`NONE`이면 **교체 후 재검증** — 통과 전에는 STEP 6(Notion 업로드)으로 넘어가지 않는다

## STEP 6 — Notion 페이지 생성

⚠️ parent는 반드시 tool call의 최상위 파라미터로 지정 (pages[] 배열 내부 금지).
지침서 Phase 7 매핑 → 카테고리 Notion Page ID 하위에 생성. 제목: `Blog #XX — {post title}` (XX = MAX_NUM + 1)
- [섹션 1]: 지침서 `2-1` 표 그대로 + 값. **Draft 일자 공란.** 방향 · 엔진 · 수요 증거 · 승산 판정 · 클릭 필연성 · GAP 질문 · 배포 우선 · 1급 자료 조달 계획 행 필수 — 숫자로
- [섹션 2]: 완성 HTML 전체를 ```html 코드 블록으로

## STEP 7 — 발행 목록 갱신

Page: https://www.notion.so/33cbfe4a2ae181b9a743cb7c194dea7f

① **헤더 카운트**: `"전체 N개 글 현황 (YYYY-MM-DD 기준)"` → `N+1` · `{today}` (업그레이드 회차는 N 유지, 날짜만 갱신)

② **표에 새 행 추가**
- 실행 전 페이지 re-fetch 필수 — 마지막 행의 실제 셀 값으로 old_str 구성 (`<td>` 포함, 고유한 꼬리 부분이면 충분)
- 갱신 후 re-fetch로 행 추가 검증
- **신규**: `<tr><td>{XX}</td><td>{Post Title}</td><td>{한줄 요약}</td><td>—</td><td>{카테고리이모지+이름}</td><td>{아웃링크 #}</td><td>—</td><td>{작성일자}</td><td></td></tr>`
- **업그레이드**: `<tr><td>U-{원글#}</td><td>{새 제목}</td><td>[U/업그레이드] 원 #{n} · 대상 쿼리 `{쿼리}` · 기준선 28일 노출 {n} 클릭 {n} 순위 {n} · 바꾼 항목 {나열} · 판정일 {today+14}</td><td>—</td><td>{카테고리}</td><td>—</td><td>—</td><td>{작성일자}</td><td>{작성일자}</td></tr>`
- **한줄 요약 앞 태그**: `[①블루오션]` / `[②블루각도]` / `[시즌]` / `[제도]` / `[U/업그레이드]` 중 하나 + 엔진 `(G|D|C)` — v9의 `[S/…]`·`[유형/…]` 태그는 쓰지 않는다

③ **백로그 갱신**: 엔진 D 채택 시 해당 행 '채택 #XX' / 탈락 시 '탈락(사유)'

④ **로그 블록 추가** (최신이 위):
```
✅ 자동 발행 실행: {today_kst}
신규 draft: #{XX} {Post Title} (Notion 등록 완료, WP {배포 우선값} 대기)   ← 또는 →   업그레이드: U-{n} {새 제목} (WP {id} REST 반영 완료)
SEO 개선: 없음 | 오류: 없음
```

## STEP 8 — Report (한글 · 표 · 중요한 것만)

✅ KoreaPlug Daily — {today_kst}

| 항목 | 값 |
|---|---|
| 🔁 재실행 가드 | 오늘 {TODAY_COUNT}/{DAILY_TARGET} → {진행·이어받기·no-op} / 미달 회차 {없음·날짜} |
| 🗄️ 데이터 | GSC {정상·실패} · 7일 클릭 {n}({±}) · 28일 클릭 {n}({±}) · 클릭 상승·하락 상위 각 3편 / WP 인증 {정상·실패} · `WP_TOTAL` {n} (publish·future·draft) · 절단 {없음·검색어} |
| 🗓️ 시즌 창 | {열림(이벤트 D-n, n편째, 직전 2편 7일 클릭) · 닫힘} / 정지 이벤트 {목록} |
| ⚙️ 엔진 | G {후보 n · (a) n · (b) n · 대기 적재 n} / D {요일군 · 시드 n · 후보 n} / C {캘린더 후보 n · 공지 스캔 4곳 결과 n} — 생략 엔진과 사유 |
| 🔍 관문 | 두 금지 제거 {n} / 중복·자기잠식 제거 {n} (재분류 업그레이드 {n}) / FT 제거 {n} / 클릭 필연성 제거 {n} / 숏리스트 {n} |
| 🎯 승산 판정 | `{키워드}` 동일 {n} / 인접 {有·無} / 블로그·포럼 {n} / AIO {완결·부분·무} → {①·②·탈락} · 탈락 후보와 값 |
| 📝 채택 | {키워드} · 방향 {①·②·시즌} · 엔진 {G·D·C} · 수요 {n} · 필연성 {n}/5 · 승산 {n}/5 = {n}/15 · **GAP 질문(첫 H2)**: {문장} |
| 📄 본문 | {n}단어 · 포커스 {n}회 · H2 {n}(상황 질문형 {n}) · 외부 {n} · 내부 {n}(전부 publish 재조회 확인 · 교체 {n}건) · 구조 자가검사 {통과·항목} |
| 📚 1급 자료 | 조달처 {나열} · 프록시 사용 {n} · 3회 실패 {n} |
| 📂 위치 | {카테고리} · Notion URL {URL} (업그레이드는 WP id·라이브 확인 결과) |
| 📋 갱신 | 헤더 · 표 행 · 로그 · 백로그 {완료 항목} |
| ⚠️ 이슈 | 지침서 버전·상충 / GSC 실패 원인 / 인증 실패 / STOP 사유 (해당 시) |

## ⚠️ 전제 조건

| 항목 | 조건 |
|---|---|
| 실행 환경 | Claude Code on the web — Chrome MCP 없음. Bash/API 기본. WebSearch는 4-B에만 |
| 지침서 버전 | **v13.5 이상** (`0-0`~`0-9` · `1-0`~`1-6` 구조, 수량 상한 폐지). 미충족 시 STEP 8에 SSOT 이슈 + 사용자 알림 |
| GSC·GA4 | 서비스 계정 `analytics-koreaplug@koreaplug-shorts.iam.gserviceaccount.com` — GSC 두 속성 전체 권한 · GA4 `WP_분석` 계정 뷰어. 키: `GSC_SA_JSON` 환경변수(권장) 또는 Drive `koreaplug-shorts-*.json`. 수집기 `tools/gsc_pull.py`(저장소). 실패 시 엔진 G만 생략 |
| WP REST | `$WP_USER` · `$WP_APP_PASS`. Rank Math 메타 3종은 REST 읽기·쓰기 가능(WPCode 4183). 업그레이드 회차는 PATCH 전 백업 필수 |
| 리더 프록시 | `https://r.jina.ai/{URL}` 최대 3회 (간헐 401·422). Reddit은 경유 불가 |
| DAILY_TARGET | 기본 1. 업그레이드 회차도 1건으로 인정. 같은 날 중복 실행 방지용이며 주간·유형별 상한은 없다(지침서 v13.4) |
| 재시도 예약 | 매일, 본 트리거와 동일 프롬프트. 등록은 사용자 몫 |
| Notion 권한 | 4개 카테고리 페이지 + 발행 목록 + 백로그 + 반려 로그 편집 권한 (캐시·좌표계는 더 이상 쓰지 않음) |
| 품질 관문 (불변) | 두 금지 / WP REST 규격·절단 확인 / 라이브 H2 자기잠식 / 관문 3개 / 채점 1점 축 탈락 / 승산 4값 숫자 기록 / 첫 H2 = GAP 질문 / EEAT (가)·(나) / 구조 규칙 6종 / 내부 링크는 공개(publish) 글만 / 스킬 2종 / 업그레이드는 수정 범위 안에서만·지어내지 않음 |

[결과물] 간단하게 표로 정리할 것. 모든 것은 한글로 얘기하고, 중요한 부분이 아닌 것은 생략한다.
