# Schd_KoreaPlug-Revenue — KoreaPlug 수익·유입 루틴 (Cowork 예약 작업 `7. KoreaPlug 수익·유입`)

*v1.0 · 2026-10-10 신설 — `Schd_KoreaPlug-GSCCTR`(7. KoreaPlug 구글 CTR 개선)을 대체하고, `쇼츠) KoreaPlug 대본 2편 만들기 (주간)` 작업을 흡수한다.*
*매일 06:30 KST 실행 · **07:50 마감**(사용자 PC가 08:00 전후 꺼진다) · 요일마다 한 가지 일만 깊게 한다.*
*원본 문서: `C:\Users\win\Documents\Claude\blog\Schd_KoreaPlug-Revenue.md` (이 본문과 같다. 고칠 때는 문서와 예약 본문을 함께 바꾼다)*

날짜: 실행 시점의 실제 KST 날짜와 요일을 쓴다. 이 프롬프트에 적힌 고정 날짜는 무시한다.

## 왜 이 루틴인가 (2026-10-10 사용자 확정)

- 클릭률(CTR) 개선 루틴은 2026-09-24~10-10 동안 29편을 고쳤지만, 확실히 좋아진 글은 2편(주당 클릭 +17)뿐이었다. 같은 기간 추석 글 몇 편이 28일 클릭 416회를 냈다. 이 사이트의 병목은 클릭률이 아니라 **노출과 수익 구조**다.
- 현재 수익은 0원이다. 애드센스는 2026-10-05에 2차 반려됐다(사유: "가치가 별로 없는 콘텐츠"). 아마존 제휴는 아직 시작하지 않았다. 쇼츠 자동화는 2026-08-10 이후 멈춰 있다.
- 그래서 이 루틴은 세 가지를 순서대로 키운다. **① 애드센스 승인 → ② 아마존 제휴 준비 → ③ 유튜브 채널.** 유튜브는 블로그 유입 통로이면서 아마존 인플루언서 프로그램의 심사 근거가 된다.

## 요일별 일

| 요일 (KST) | 모듈 | 한 줄 |
|---|---|---|
| 월·목 | **A. 애드센스 재신청 준비** | 진단(2026-10-05)의 배치 A~G를 승인함 방식으로 하나씩 처리한다 |
| 화·금 | **B. 아마존 준비** | 클릭이 나는 글에서 "물건이 필요한 순간"을 찾아 상품 자리 목록을 쌓는다. 가입 전에는 링크를 넣지 않는다 |
| 수·토 | **C. 유튜브(쇼츠)** | 멈춘 쇼츠 공정을 점검·복구하고, 블로그 글 1편을 쇼츠 대본으로 만들어 대기열에 넣는다 |
| 일 | **D. 주간 수익 보고** | 애드센스·아마존·유튜브·외부 유입을 표 하나로 보고한다 |

사용자가 그날 다른 모듈을 지시하면(예: "오늘은 C") 그 모듈을 한다. 수동으로 다시 실행해도 `state.json` 의 그날 완료 표시가 있으면 이어서 하거나 건너뛴다.

---

## ⛔ 절대 규칙 (모든 STEP 에 우선)

1. **삭제 0건.** 글·미디어·리비전·파일·예약 작업·유튜브 영상을 지우지 않는다. 진단에 "삭제"로 적힌 항목도 이 루틴에서는 noindex 까지만 하고, 삭제는 사용자에게 넘긴다.
2. **게시·공개는 사용자가 한다.** 글의 발행 상태(`status`)를 공개로 바꾸지 않는다. 유튜브는 PC 공정이 **비공개**로만 올리고, 공개 전환·고정 댓글·썸네일 업로드는 사용자가 한다.
3. **승인함(`koreaplug-revenue\승인.md`)에서 `[x]` 로 표시된 항목만 실행한다.** 표시가 없으면 제안만 하고 끝낸다.
4. **애드센스 광고 코드를 건드리지 않는다.** WPCode 스니펫 `999`, ads.txt, 헤더 영역은 읽기만 한다. 상세 규칙은 `Schd_KoreaPlug-Draft.md` STEP -1 을 따른다.
5. **변경 금지:** 슬러그(URL), Focus Keyword 첫 항목, 카테고리, 발행일, 대표 이미지. 기존 1급 자료·캡처·표·이미지·내부 링크는 지우지 않는다(위치 이동은 가능).
6. **다른 루틴과 겹치지 않는다.** REST 응답의 `modified` 가 최근 14일 안인데 이 루틴의 기록(`koreaplug-revenue\log.md`)에 없으면 Writer·사용자가 고친 글이다. 그 회차에는 손대지 않고 보고에 적는다. `revenue_0and1life\`(0and1Life 수익 루틴 전용 폴더)는 읽지도 쓰지도 않는다.
7. **계정 만들기·로그인·결제·자격증명 입력을 하지 않는다.** 아마존 제휴 가입, 애드센스 재검토 요청 버튼, 유튜브 채널 설정 저장은 사용자가 한다. `pw.txt` 값은 출력하지 않는다.
8. **git commit·push 를 하지 않는다.** 사용자가 직접 한다.
9. **구글 API(`*.googleapis.com`)는 호출하지 않는다.** 이 환경에서 403 이다(2026-09-24 실측). 서치콘솔·GA4·유튜브 스튜디오는 로그인된 크롬 화면으로만 읽는다.

⚠️ [무인 실행] 사람이 없는 시간에 실행된다. 승인이 필요한 도구 호출은 그것 없이는 진행할 수 없음을 확인한 뒤에만 한다. 승인 창이 응답 없이 닫히면 재시도하지 않고 보고에 적는다.

⚠️ [시간] 06:00 네이버 CTR 루틴·06:40 0and1Life 수익 루틴이 같은 크롬을 쓴다. 이 루틴은 **자기 탭 그룹의 탭만** 쓰고 끝나면 닫는다. **07:50 KST 가 되면 하던 일을 멈추고** 상태를 `state.json` 에 남긴 뒤 STEP 9(보고)로 간다. 다음 회차가 이어서 한다.

⚠️ [작업 공간 대체] `device_bash` 가 `Workspace unavailable` 이면 재시도하지 말고, `device_stage_files` 로 필요한 파일을 클라우드로 가져와 클라우드 `Bash` 에서 실행한 뒤, `device_commit_files`(`expectedMtimeMs` 지정)로 되돌려 쓴다. koreaplug.com REST 는 클라우드에서도 접근된다.

---

## 실행 자산

| 무엇 | 위치 | 비고 |
|---|---|---|
| 작업 폴더 | `C:\Users\win\Documents\Claude\koreaplug-revenue\` | 이 루틴이 쓰는 모든 기록. ⛔ `revenue_0and1life\`(0and1Life 수익 루틴 전용)는 읽지도 쓰지도 않는다 |
| 진행 상태 | `koreaplug-revenue\state.json` | 회차·모듈별 진행, 승인 항목 처리 이력, 체크리스트 |
| 승인함 | `koreaplug-revenue\승인.md` | 루틴이 제안을 적고, 사용자가 `[x]` 로 승인한다 |
| 작업 기록 | `koreaplug-revenue\log.md` | 최신이 위. 무엇을 바꿨는지, 전후 값 |
| 백업 | `koreaplug-revenue\backups\` | 글을 바꾸기 전 REST `context=edit` 응답 원본 |
| 애드센스 | `koreaplug-revenue\adsense\checklist.md` | 재신청 체크리스트와 진행률 |
| 아마존 | `koreaplug-revenue\amazon\placements.csv` · `koreaplug-revenue\amazon\config.json` | 상품 자리 목록 · 제휴 태그(가입 후 사용자가 기입) |
| 유튜브 | `koreaplug-revenue\youtube\health-{날짜}.md` · `koreaplug-revenue\youtube\채널제안.md` | 공정 점검 결과 · 채널 기본기 제안 |
| 주간 보고 | `koreaplug-revenue\report-{날짜}.md` | 일요일 산출물. 대화에도 첨부한다 |
| 진단 원본 | `C:\Users\win\Documents\Claude\koreaplug_audit_2026-10-05\` | `koreaplug_진단_개선안_2026-10-05.md`(배치 A~G) · `content_audit.json`(글 173편별 `action`·`dup_cluster`·`value_score`) |
| 쇼츠 공정 | `C:\Users\win\Documents\Claude\shorts\` | `대본만들기.md`(SSOT) · `제작표준.md` · `자동화-구조.md` · `job.template.json` · `episodes.csv` · `queue\` · `queue\_done\` · `queue\_failed\` · `broll\` · `bgm\` · `pipeline.log` · `pipeline-마지막실행.txt` · `audit_history.csv` |
| 글 점검 도구 | `C:\Users\win\Documents\Claude\gsc-ctr\rm_check.py` · `gsc-ctr\work\pubcheck.py` | Rank Math 근사 점검 · 공개 페이지(구글봇) 점검 — 옛 CTR 루틴 자산을 그대로 쓴다 |
| 자격증명 | `C:\Users\win\Documents\Claude\pw.txt` | `KOREAPLUG_WP_USER` · `KOREAPLUG_WP_APP_PASSWORD` — 값 출력 금지 |

설정값(사용자만 수정):
```
DEADLINE_KST         = 07:50
A_PROPOSE_PER_RUN    = 5      # 애드센스 모듈이 한 회차에 새로 제안하는 항목 수
A_EXECUTE_PER_RUN    = 10     # 승인된 항목을 한 회차에 실행하는 최대 수
B_PROPOSE_PER_RUN    = 5      # 아마존 모듈이 한 회차에 새로 찾는 상품 자리 수
AMAZON_READY_SLOTS   = 15     # 상품 자리가 이 수 이상 쌓이면 "가입할 때" 판정의 첫 조건
AMAZON_READY_CLICKS  = 1500   # 블로그 28일 클릭이 이 이상이거나
AMAZON_READY_SHORTS  = 10     # 공개된 쇼츠가 이 편수 이상이면 "가입할 때" 알림
C_SCRIPTS_PER_RUN    = 1      # 유튜브 모듈 회차당 대본 수(수·토 → 주 2편)
```

---

## STEP 0 — 시작 (매 회차 공통)

1) `TODAY`(KST, YYYY-MM-DD)와 요일, 지금 시각을 기록한다. 07:50 이 지났으면 STEP 9 만 한다.
2) 폴더 확인:
```bash
C=$HOME/mnt/Claude; R=$C/koreaplug-revenue
ls $C/pw.txt $C/shorts/대본만들기.md $C/koreaplug_audit_2026-10-05/content_audit.json >/dev/null && echo OK
mkdir -p $R/backups $R/adsense $R/amazon $R/youtube
[ -f $R/state.json ] || echo '{"runs":{},"approvals":{},"checklist":{},"amazon":{},"youtube":{}}' > $R/state.json
[ -f $R/log.md ] || printf '# KoreaPlug 수익·유입 기록 (최신이 위)\n' > $R/log.md
```
   - `No folders are connected` 오류면 `device_request_folder_access { paths: ["C:\\Users\\win\\Documents\\Claude"] }` 를 **1회만** 하고, 실패하면 STEP 9 로 가서 `⛔ PC 폴더 미연결` 을 보고한다. **조용히 성공으로 끝내지 않는다.**
   - `Workspace unavailable` 이면 상단 [작업 공간 대체] 경로로 간다.
   - bash 는 호출마다 새 셸이다. 위의 `C=…; R=…` 줄을 이후 호출마다 맨 앞에 다시 넣는다.
3) 자격증명 확인(값은 출력하지 않는다):
```bash
cd $HOME/mnt/Claude
get(){ grep "^$1=" pw.txt | head -1 | cut -d'=' -f2- | tr -d '\r\n' | sed 's/^\xEF\xBB\xBF//; s/^ *//; s/ *$//'; }
U=$(get KOREAPLUG_WP_USER); P=$(get KOREAPLUG_WP_APP_PASSWORD)
curl -s -o /dev/null -w "WP %{http_code}\n" -u "$U:$P" "https://koreaplug.com/wp-json/wp/v2/users/me?context=edit"
```
   200 이 아니면 글을 바꾸는 단계만 건너뛰고(제안·점검·보고는 진행) 보고에 적는다.
4) 승인함 읽기 — `koreaplug-revenue\승인.md` 에서 `[x]` 이면서 `state.json.approvals` 에 `done` 이 없는 항목을 모은다(`APPROVED`). **그날 모듈의 승인 항목만** 실행한다(A 항목은 월·목, B 항목은 화·금, C 항목은 수·토). 일요일에는 실행하지 않고 개수만 센다.
5) 요일로 모듈을 정한다: 월·목 → STEP 1(A) · 화·금 → STEP 3(B) · 수·토 → STEP 5(C) · 일 → STEP 7(D). 그 STEP 을 마치면 STEP 9 로 간다.

---

## STEP 1 — A. 애드센스 재신청 준비 (월·목)

### 1-1. 승인된 항목 실행 (최대 `A_EXECUTE_PER_RUN`건)

`APPROVED` 의 A 항목을 위에서부터 처리한다. 항목마다:

1. **백업** — `GET /wp-json/wp/v2/posts?slug={slug}&context=edit&_fields=id,slug,status,modified,meta,content` 응답을 `koreaplug-revenue\backups\{slug}-{TODAY}.json` 에 저장한다. 실패하면 그 항목은 건너뛴다.
2. **외부 수정 확인** — 절대 규칙 6. 걸리면 건너뛰고 보고한다.
3. **종류별 실행**

| 종류 | 루틴이 하는 일 (REST) | 사용자가 하는 일 |
|---|---|---|
| `noindex` | `meta.rank_math_robots` 를 `["noindex","follow"]` 로 쓴다. 재조회해서 값이 바뀌었는지, 공개 페이지 `<meta name="robots">` 에 `noindex` 가 보이는지 확인한다. 메타가 REST 로 써지지 않으면(키 없음·403) 바꾸지 않고 "사용자 작업"으로 넘긴다 | (REST 불가일 때) 글 편집 → Rank Math → 고급 → No Index |
| `통합` | 대표 글에 흡수할 내용이 있으면 대표 글 본문에 섹션(H2)을 추가한다. 흡수되는 글의 클릭 있는 H2 제목을 그대로 쓴다. 그다음 흡수되는 글을 `noindex` 처리한다. **301 은 루틴이 등록하지 않는다** | Rank Math → 리디렉션 → `구 슬러그 → 대표 슬러그` 301 등록(루틴이 보고에 정확한 쌍을 적는다) |
| `보강` | 진단 `content_audit.json` 의 `val_parts` 가 낮은 항목(수치·출처·한글 원문·1인칭 확인)을 1차 출처로 확인한 사실로만 채운다. 근거 없는 경험담·인용은 지운다. 분량 ±40% 안에서 고친다 | — |
| `템플릿 정리` | 진단 배치 E 의 1~7을 그 글에 적용한다: "Last updated \| N min read" 줄, Core Fact 블록, "Where This Guide Breaks Down / Quick Answers / Key points" H2, 반박형 오프너, Focus Keyword 15회 이상 반복, 낚시형 부제, 60자 넘는 SEO 제목 | — |
| `내부링크 제거` | 미발행 글을 가리키는 링크의 `<a>` 만 풀고 앵커 글자는 남긴다 | — |
| `사이트 설정` | 하지 않는다(배치 A·B 의 플러그인·WPCode·리디렉션 설정) | 보고에 적힌 화면·버튼대로 사용자가 한다 |

4. **검증** — 본문을 바꾼 항목은 `python3 gsc-ctr/rm_check.py` 로 수정 전·후를 비교해 통과 수가 줄면 백업으로 되돌린다. `python3 gsc-ctr/work/pubcheck.py` 로 공개 페이지를 구글봇 관점에서 확인한다(200·canonical·H1 1개·JSON-LD 파싱). 이상이 있으면 즉시 백업으로 되돌린다.
5. **기록** — `state.json.approvals.{id} = {done: TODAY, result, before, after}`, `log.md` 맨 위에 한 줄. `승인.md` 의 그 줄 끝에 ` → 완료 {TODAY}` 를 붙인다(`[x]` 는 그대로 둔다).

### 1-2. 새 제안 (최대 `A_PROPOSE_PER_RUN`건)

1. `content_audit.json` 과 진단 개선안 §3 을 읽어, 아직 `승인.md` 에 없는 항목을 배치 순서대로 고른다. 순서: **배치 D(약한 글 noindex) → 배치 C(중복 통합, 클러스터 단위) → 배치 F(미발행 조정) → 배치 E(템플릿 정리, 클릭 있는 글부터)**.
2. 고르기 전에 지금 상태를 다시 확인한다. 진단 이후 바뀐 글(이미 정의형으로 끝낸 글, Writer가 고친 글, 이미 noindex 인 글)은 제안을 바꾸거나 뺀다. 최근 28일 클릭이 있는 글을 noindex 로 제안하지 않는다(통합으로 바꾼다).
3. `승인.md` 의 `## A. 애드센스` 아래에 한 줄씩 추가한다:
```
- [ ] A-{YYYYMMDD}-{nn} | {종류} | {slug}{ → 대표 slug} | 근거: {28일 노출·클릭, value_score, 중복 유사도, 진단 배치} | 사용자 작업: {있으면 한 줄}
```
4. 배치 A·B·G 의 사이트 설정 항목은 `승인.md` 가 아니라 `adsense\checklist.md` 의 "사용자 작업" 표에 정확한 화면 경로와 함께 적는다.

### 1-3. 재신청 체크리스트 갱신

`adsense\checklist.md` 를 다시 계산해 쓴다. 숫자는 REST·공개 페이지로 직접 센다.

| 항목 | 재는 법 | 목표 |
|---|---|---|
| 0클릭 글 비율 | 서치콘솔 28일 페이지 표(STEP 7-1 방식, 월요일만 새로 읽고 목요일은 직전 값) | 진단 54% → 낮아지는 추세 |
| 중복 클러스터 남은 글 | `content_audit.json` 의 클러스터 중 아직 공개·index 인 흡수 대상 수 | 0 |
| 약한 글(배치 D) 처리 | noindex 완료 수 / 대상 수 | 전부 |
| 템플릿 지문 | 공개 글 중 "Last updated \|" · "Quick Answers" · "Key points" 문자열이 있는 글 수 | 0 |
| 미발행 글 선링크 | 공개 글 본문에서 `status≠publish` 글을 가리키는 링크 수 | 0 |
| 필수 페이지 | about-us · contact · privacy-policy 가 200 | 3/3 |
| 광고 코드 | 홈·최신 글 3편에서 `pagead/js/adsbygoogle.js` 개수 | 페이지당 정확히 1 |
| 홈 문구 | 홈의 글 수 표기가 실제 공개 글 수와 같은가 | 일치 |
| 사용자 작업 | 배치 A·B 설정(피드 링크 제거, 이모지 끄기, 301·410, bbp 역할) 완료 여부 — 사용자가 표에 `[x]` | 전부 |

모든 항목이 목표에 닿으면 보고 맨 위에 **"애드센스 재검토 요청 가능 — 버튼은 사용자가 누릅니다"** 를 적는다. 다음 검토 가능일(진단 기준 10/12 이후)도 함께 적는다.

---

## STEP 3 — B. 아마존 준비 (화·금)

### 3-1. 승인된 항목 실행

- `amazon\config.json` 의 `amazon_tag` 가 **비어 있으면 링크를 넣지 않는다.** 승인된 B 항목은 `state.json` 에 "가입 대기"로만 표시한다.
- `amazon_tag` 가 있으면 승인된 자리마다:
  1. 백업 → 그 글의 지정 위치(H2 아래 첫 문단 뒤)에 상품 블록을 넣는다. 링크는 검색 링크 형식 `https://www.amazon.com/s?k={검색어}&tag={amazon_tag}` 를 쓰고 `rel="sponsored nofollow noopener"` 를 붙인다. **가격·별점·재고를 본문에 적지 않는다**(아마존 정책상 실시간이 아닌 가격 표기 금지).
  2. 그 글에 고지 문구가 없으면 첫 상품 블록 바로 위에 한 줄 넣는다: `As an Amazon Associate, KoreaPlug earns from qualifying purchases.`
  3. rm_check·pubcheck 로 검증하고, 이상이 있으면 되돌린다. 기록은 STEP 1-1 과 같다.

### 3-2. 상품 자리 찾기 (최대 `B_PROPOSE_PER_RUN`곳)

1. 클릭이 나는 글부터 본다: 최근 서치콘솔 28일 표(없으면 `koreaplug-revenue\state.json` 의 마지막 값)에서 클릭 상위 글 중 `placements.csv` 에 아직 없는 글.
2. 글 본문(REST)을 읽고 **독자가 그 순간 실제로 물건이 필요한 문장**을 찾는다. 예: 전압·플러그(→ Type C/F 어댑터), 하루 종일 지도·번역 사용(→ 보조배터리), 겨울 산행(→ 아이젠·핫팩), 찜질방·여행 세면(→ 여행용 파우치), K-뷰티 쇼핑 글(→ 그 제품군). **억지로 끼우지 않는다** — 글이 상품을 필요로 하지 않으면 그 글은 "자리 없음"으로 기록한다.
3. `amazon\placements.csv` 에 행을 추가한다(헤더: `id,slug,h2,moment,product_type,amazon_query,shorts_slug,status,added`). `status` 는 `후보`. 같은 상품을 다룰 쇼츠가 있거나 만들 예정이면 `shorts_slug` 에 적는다.
4. `승인.md` 의 `## B. 아마존` 아래에 `- [ ] B-{YYYYMMDD}-{nn} | {slug} | {h2} | {product_type} | 검색어 "{amazon_query}"` 로 추가한다.
5. 아마존 사이트를 긁지 않는다. 상품 종류와 검색어만 정한다.

### 3-3. 가입 시점 판정

아래를 계산해 `state.json.amazon.ready` 에 쓴다:
- 조건 ① `placements.csv` 의 `후보`+`승인` 자리 ≥ `AMAZON_READY_SLOTS`
- 조건 ② 블로그 28일 클릭 ≥ `AMAZON_READY_CLICKS` **또는** 공개된 쇼츠 ≥ `AMAZON_READY_SHORTS`

둘 다 참이 되는 첫 회차에 보고 맨 위에 **"아마존 제휴 가입할 때"** 를 적는다. 가입 순서(사용자 몫)도 함께 적는다: 아마존 어소시에이트(미국) 가입 → 사이트 `koreaplug.com` 과 유튜브 채널 등록 → 발급된 태그를 `koreaplug-revenue\amazon\config.json` 의 `amazon_tag` 에 입력. 가입 후 정해진 기간 안에 첫 판매가 있어야 계정이 유지되므로 **가입은 자리와 유입이 준비된 뒤에** 한다. 가입 조건·기간은 그때 공식 안내에서 다시 확인해 보고에 적는다.

---

## STEP 5 — C. 유튜브(쇼츠) (수·토)

흡수 전 작업: `쇼츠) KoreaPlug 대본 2편 만들기 (주간)` (2026-10-10 일시정지). 그 작업은 PC 폴더가 연결되지 않은 채 매주 "성공"으로 끝나 대기열이 비어 있었다. 이 모듈은 **만드는 일과 확인하는 일을 같이 한다.**

### 5-1. 공정 점검 (매 회차 먼저)

```bash
S=$HOME/mnt/Claude/shorts
cat $S/pipeline-마지막실행.txt; tail -40 $S/pipeline.log
ls -la $S/queue $S/queue/_done $S/queue/_failed; tail -5 $S/episodes.csv; tail -5 $S/audit_history.csv
```
`koreaplug-revenue\youtube\health-{TODAY}.md` 에 적는다:
- 마지막 실행 시각, 대기열에 남은 대본 수, 최근 실패 사유(`pipeline.log` 의 "고쳐야 할 것" 줄), 지금까지 올라간 영상 수(`episodes.csv` 의 `youtube_id` 가 있는 행).
- **대기열에 대본이 있는데 마지막 실행이 3일 넘게 지났으면** `🔴 쇼츠 공정이 돌지 않음` 으로 보고한다. 원인 후보: PC 가 새벽에 꺼져 있음, 윈도우 작업 스케줄러 작업 비활성, `token.json` 만료. 루틴은 작업 스케줄러를 바꾸지 않는다 — 확인할 화면을 사용자에게 적는다.
- **실패가 대본 쪽 문제면 고친다.** `제작표준.md` 10장(고치는 절차)에 있는 대본 수준 수정(효과음 지정, 장면 길이, 끝 여백)만 한다. 고친 대본은 새 이름(`job.{slug}_fix{n}.json`)으로 `queue\` 에 넣는다. `_failed\` 원본은 그대로 둔다. 코드(`*.py`)는 고치지 않고, 고쳐야 하면 보고한다.

### 5-2. 대본 만들기 (회차당 `C_SCRIPTS_PER_RUN`편)

1. `device_stage_files` 로 `대본만들기.md` · `제작표준.md` · `FLOW-B-roll-프롬프트팩.md` · `job.template.json` · `episodes.csv` 를 가져와 **전부 읽는다.** `대본만들기.md` 가 SSOT 다 — 이 프롬프트와 다르면 그 문서를 따르고 보고에 적는다.
2. `device_list_dir` 로 `broll\` 클립 목록과 `bgm\` 음악 파일명을 확인한다. 대본에는 실제로 있는 파일명만 쓴다(`hfz` 로 시작하는 파일은 지난 편 전용이라 쓰지 않는다).
3. **주제는 블로그에서 고른다.** 서치콘솔 28일 클릭이 있는 글 중 `queue\` · `queue\_done\` · `episodes.csv` 에 없는 글을 `대본만들기.md` 1장 기준(세 가지 관문)으로 검증한다. 웹 검색으로 (a) 외국인이 실제로 검색하는지 (b) 영어 자료가 부실한지 확인하고, 한국 공공데이터·지자체·국내 기사에서 영어권에 없는 사실을 최소 2개 찾는다. 숫자는 반드시 출처를 확인한다. `placements.csv` 에 상품 자리가 있는 글이면 우선한다.
4. `job.{slug}.json` 을 만든다. `blog_url` 은 그 글 주소. `description` 끝에 블로그 링크를 둔다. `amazon\config.json` 의 `amazon_tag` 가 있고 그 글의 상품 자리가 `승인` 이면 설명란에 상품 줄과 고지 문구를 넣는다. 태그가 없으면 상품 줄을 넣지 않는다.
5. `대본만들기.md` 5장 자가 점검을 하나씩 확인하고 `json.loads` 로 문법을 검증한다.
6. (선택) `대본만들기.md` 7장대로 정보 카드·한글 읽기 HyperFrames 클립을 편당 최대 2개 만든다. 통과한 클립은 `device_commit_files` 로 `shorts\broll\` 에 **먼저** 넣고, 그 장면 첫 컷에 파일명과 `"seek": 0.0` 을 쓴다. 실패하면 일반 클립을 쓴다.
7. `SendUserFile` 로 대본을 보낸 뒤 `device_commit_files` 로 `shorts\queue\` 에 넣는다.
8. **영상 본편을 렌더하거나 업로드하지 않는다.** PC 의 `pipeline.py` 가 한다(예외: 6의 HF B-roll 클립).

### 5-3. 채널 기본기 (토요일만, 한 달에 한 번 갱신)

`koreaplug-revenue\youtube\채널제안.md` 가 없거나 30일이 지났으면 새로 쓴다: 채널 이름·핸들 후보, 소개문(영문, 블로그 링크 포함), 배너 문구, 재생목록 3~4개(블로그 카테고리와 맞춤), 쇼츠 설명란 공통 꼬리말, 고정 댓글 틀, 공개 시간 권장. **반영은 사용자가 한다.** 유튜브 스튜디오 설정을 루틴이 저장하지 않는다.

---

## STEP 7 — D. 주간 수익 보고 (일)

### 7-1. 데이터 읽기 (크롬 — 자기 탭 그룹)

1. **서치콘솔 28일 페이지 표** — `https://search.google.com/search-console/performance/search-analytics?resource_id=https%3A%2F%2Fkoreaplug.com%2F&breakdown=page&metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION&start_date={LATEST−27}&end_date={LATEST}` (LATEST = TODAY−2일, 날짜는 YYYYMMDD). 7초 대기 후 `javascript_tool` 로 표를 읽어 900자씩 나눠 받는다. 반환 문자열에는 `.replace(/[=&?]/g,' ')` 를 붙인다(쿼리 문자열 차단 회피). 사이트 총 클릭·노출·CTR 과 글별 클릭을 `state.json.gsc.{TODAY}` 에 저장한다. 로그인 화면이면 `GSC 읽기 실패` 로 적고 다음으로 간다.
2. **GA4 유입 경로** — KoreaPlug 속성(계정 a393066616 · 속성 p535142552)의 트래픽 획득 보고서(세션 소스/매체, 최근 7일)를 연다. `google / organic` 을 뺀 상위 소스(youtube.com, reddit, bing, direct 등)의 세션을 적는다. 화면 주소는 GA4 왼쪽 메뉴 `보고서 → 획득 → 트래픽 획득` 에서 날짜를 최근 7일로 맞춰 얻는다. 열리지 않으면 `GA4 미확인`.
3. **유튜브** — `episodes.csv` 의 `youtube_id` 가 있는 영상과 `studio.youtube.com` 의 콘텐츠 목록(읽기만)에서 공개 여부·조회수·구독자 수를 읽는다. 로그인 화면이면 `유튜브 미확인`. 아무것도 누르지 않는다.
4. 탭을 모두 닫는다.

### 7-2. `koreaplug-revenue\report-{TODAY}.md` 쓰기

```
# KoreaPlug 수익·유입 주간 보고 {TODAY}

## 한 줄 요약
{이번 주 가장 중요한 변화 한 문장}

## 수익 현황
| 수익원 | 상태 | 이번 주 변화 | 다음 단계 |
|---|---|---|---|
| 애드센스 | 미승인 · 체크리스트 {n}/{m} | {처리한 항목 수} | {재검토 요청 가능 여부} |
| 아마존 | 가입 전 · 상품 자리 {n}/{AMAZON_READY_SLOTS} | {새 자리 수} | {가입할 때 여부} |
| 유튜브 | 영상 {n}편(공개 {n}) · 구독 {n} | {새 대본·업로드 수} | {공정 상태} |

## 유입
| 지표 | 지난주 | 이번 주 |
|---|---|---|
| 서치콘솔 28일 클릭 / 노출 / CTR | | |
| GA4 구글 외 유입 세션(7일) — 소스별 | | |

## 사용자 할 일
{승인함에 기다리는 항목 수(A·B·C), 사이트 설정 작업, 비공개 쇼츠 공개 전환, 아마존 가입 등 — 화면 경로까지}

## 이번 주 실행 기록
{log.md 에서 이번 주 줄}
```
지난주 값은 직전 `report-*.md` 에서 읽는다. 없으면 `–`.

---

## STEP 9 — 보고 (모든 회차, 앞 단계 성공 여부와 무관하게 반드시)

1. `state.json.runs.{TODAY} = {module, started, ended, done:[…], pending:[…], errors:[…]}` 를 쓴다.
2. 일요일이면 `report-{TODAY}.md` 를 `device_stage_files` 로 가져와 `SendUserFile`(status: proactive)로 보낸다.
3. **PushNotification** 1회. `<routine_summary>` 안에 쓴다. 첫 문장이 휴대폰 배너가 된다.
```
KoreaPlug 수익·유입 {TODAY}({요일}) — {모듈}: {가장 중요한 결과 한 문장}
- 실행: {승인 항목 n건 처리 · 새 제안 n건 · 대본 n편 등}
- 승인 기다리는 것: A {n} · B {n} · C {n} (revenue\승인.md)
- 사용자 할 일: {있으면 화면 경로까지, 없으면 "없음"}
- 확인 필요: {오류·미확인·외부 수정 감지·마감 중단, 없으면 "없음"}
```
   - **알림을 생략하는 경우:** 그날 실행한 것도, 새 제안도, 오류도 없고 일요일도 아니면 알림을 보내지 않는다.
   - **반드시 알림을 보내는 경우:** PC 미연결, WP 인증 실패, 쇼츠 공정 정지(🔴), "애드센스 재검토 요청 가능", "아마존 제휴 가입할 때".
4. 마지막 응답에도 같은 내용을 한글로 쓴다. 전문 용어 대신 쉬운 말을 쓰고, 글은 사람이 알아볼 이름 뒤에 괄호로 슬러그를 붙인다.

---

## 승인함 형식 (`koreaplug-revenue\승인.md`)

```
# KoreaPlug 수익·유입 승인함
사용 법: 실행해도 되는 줄의 [ ] 를 [x] 로 바꾸세요. 해당 요일 회차에 실행하고 줄 끝에 "→ 완료 날짜"를 붙입니다.
거절하려면 줄 맨 앞에 ~~ 를 붙이세요(루틴이 다시 제안하지 않습니다).

## A. 애드센스 (월·목 실행)
## B. 아마존 (화·금 실행)
## C. 유튜브 (수·토 실행)
```
- 루틴은 줄을 지우지 않는다. 사용자가 쓴 표시(`[x]`, `~~`)를 바꾸지 않는다.
- 같은 slug·같은 종류의 줄이 이미 있으면 다시 제안하지 않는다.

---

## 오류 처리

| 상황 | 처리 |
|---|---|
| PC 폴더 미연결 | `device_request_folder_access` 1회 → 실패면 아무것도 쓰지 않고 STEP 9, 알림 필수 |
| `Workspace unavailable` | [작업 공간 대체] 경로 |
| WP 인증 실패 | 글을 바꾸는 단계만 건너뜀. 제안·점검·보고는 진행 |
| `rank_math_robots` 를 REST 로 못 씀 | 바꾸지 않고 "사용자 작업"으로 넘김(화면 경로 기재) |
| 글 수정 후 rm_check 통과 수 감소·공개 페이지 이상 | 즉시 백업으로 되돌리고 기록 |
| 외부 수정 감지(14일 안 `modified`) | 그 회차 건너뜀, 보고 |
| 서치콘솔·GA4·유튜브 스튜디오 로그인 화면 | 해당 지표만 `미확인`. 로그인 버튼을 누르지 않는다 |
| 크롬 탭이 45초 응답 없음 | 그 탭을 닫고 새 탭에서 1회 재시도, 다시 실패면 `미확인` |
| 쇼츠 공정 3일 넘게 정지 | `🔴 쇼츠 공정 정지` 알림, 확인할 화면 기재 |
| 07:50 도달 | 하던 일을 멈추고 `state.json` 에 남긴 뒤 STEP 9 |
| 진단·지침 문서와 이 프롬프트가 다름 | 쇼츠는 `대본만들기.md`, 초안·광고 규칙은 `Schd_KoreaPlug-Draft.md` 를 따르고 보고에 적는다 |

## 전제조건 (사용자 몫)

| 항목 | 상태 |
|---|---|
| Cowork 예약 `7. KoreaPlug 수익·유입` (06:30 KST, 폴더 `Documents\Claude`·`Documents\Claude\blog`, 사용자 PC 필요) | 2026-10-10 기존 7번(구글 CTR 개선) 이름·본문 교체 |
| `쇼츠) KoreaPlug 대본 2편 만들기 (주간)` | 2026-10-10 일시정지(삭제 안 함) |
| 윈도우 작업 스케줄러의 `pipeline.py` 새벽 실행 · `shorts\token.json` 유효 | 사용자 확인 필요 — 2026-08-10 이후 실행 기록 없음 |
| 크롬 로그인: 서치콘솔·GA4·유튜브 스튜디오 | 유지 |
| 아마존 어소시에이트 가입 · `koreaplug-revenue\amazon\config.json` 의 `amazon_tag` | 루틴이 "가입할 때"를 알린 뒤 사용자가 |
| 애드센스 재검토 요청 | 체크리스트가 다 채워진 뒤 사용자가 |
| 문서 `blog\Schd_KoreaPlug-Revenue.md` GitHub 커밋 | 사용자가 직접 |
