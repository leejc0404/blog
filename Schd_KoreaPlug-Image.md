# KoreaPlug 자동 이미지 삽입 태스크 (v5.5 — 세션 사전 점검 + 사건 설계 + 한국성 + 신체 결손 방지 + 반응형 전송 + Google Flow)

> 🔑 **v5.5 변경 (2026-08-25) — 이 루틴은 들어갈 수 없는 문 앞까지 20분을 걸어간 뒤에야 문이 잠긴 걸 알았다.**
> 2026-08-25 실행: STEP 1(Notion 조회) → STEP 2(분류) → STEP 3(본문 정독·프롬프트 4개 설계) → STEP 4(삽입 위치 계산)를 **전부 정상 완료**한 뒤, STEP 5에서 `labs.google` 접속 시 **Google 계정 선택(OAuth 동의) 화면**으로 리다이렉트됐다. 루틴 규정상 로그인·OAuth 동의는 대신 수행할 수 없으므로 그 자리에서 중단했고, **그때까지 만든 프롬프트 4개는 전부 버려졌다.**
> 문제는 두 겹이었다.
> - ① **점검 시점이 틀렸다.** 舊 STEP 1은 **WP 세션만** 점검했고 그것도 Notion fetch 이후였다. Flow 세션은 **점검 항목에 아예 없었다.** 두 세션 중 하나라도 죽으면 루틴은 100% 실패하는데, 확인은 각각 STEP 2와 STEP 5에서 **따로, 뒤늦게** 이뤄졌다.
> - ② **중단 시 산출물을 버렸다.** STEP 3의 프롬프트 설계는 이 루틴에서 가장 비싼 단계(본문 정독 + 3중 게이트 검증)인데, 중단 보고 양식에 이를 남기라는 조항이 없어 다음 실행이 **처음부터 다시** 해야 했다.
> → v5.5는 ① **STEP 0 「세션 사전 점검」을 신설**해 WP·Flow **두 세션을 Notion 조회보다 먼저, 한 번에** 확인하고 하나라도 죽어 있으면 즉시 종료한다 ② 舊 STEP 1의 WP 세션 조항을 STEP 0으로 흡수하고 **Flow 세션 만료 대응을 동일 형식으로 신설**한다 ③ **STEP 8에 「중단 보고」 양식**을 신설해, 어느 단계에서 멈췄든 **그때까지 확정된 산출물(대상 글·분류·프롬프트·삽입 위치)을 재사용 가능한 형태로** 남기게 한다.
> ⛔ **로그인·OAuth 동의는 어떤 경우에도 루틴이 대신하지 않는다.** 계정 선택 화면에 이미 계정이 떠 있어도 클릭하지 않는다 — 그 클릭은 OAuth 권한 부여이며 사용자 승인 사항이다.

> 🖼️ **v5.4 변경 (2026-08-19) — WordPress가 만들어 둔 축소 사본을 이 루틴이 단 한 번도 쓰지 않고 있었다.**
> 사용자 지적으로 확인: **WebP 변환과 크롭은 정상**이었지만(1226×768, 75~242KB), 본문 래퍼가 **788px**인데 전 기기가 **1226px full 파일**을 내려받고 있었다. WordPress는 업로드 시 `medium 300` · `medium_large 768` · `large 1024` WebP 사본을 **이미 만들어 두고 있었는데도** 전혀 쓰이지 않았다.
> 원인은 삽입 마크업이다. 舊 7-2는 `<img style src alt>` 4개 속성만 넣었고 **`srcset` 도 `wp-image-{ID}` 클래스도 없었다.** 클래스가 없으면 WordPress의 `wp_filter_content_tags()` 가 그 `<img>` 를 첨부파일과 매핑하지 못해 **srcset 자동 주입을 건너뛴다.** `width`/`height` 부재로 **CLS**가, `loading` 부재로 **본문 하단 이미지까지 즉시 로드**되는 문제도 함께 있었다.
> 실측(2026-08-19, #138·#139·#140 12장): full 합계 **1,836KB** → large **1,216KB(-34%)** → medium_large **792KB(-57%)**. 하단 3장은 `lazy` 로 초기 로드에서 아예 빠진다.
> → v5.4는 ① **7-2-0에서 `media_details` 를 조회해 `window._srcset` 구축**(필수) ② **`window._buildImg()` 반응형 빌더**로 삽입·스톡교체 마크업 통일(`srcset`·`sizes`·`width`·`height`·`loading`·`decoding`·`wp-image-{ID}`, 히어로만 `eager`+`fetchpriority`) ③ `_evGuard` 에 **`noSrcset`·`noWH`·`noLoad` 가드**(하나라도 0이 아니면 저장 금지) ④ **7.5에 `currentSrc` 실측 검증**을 추가한다.
> ⚠️ **원본 폭 1226은 줄이지 않는다.** dpr 2 기기는 788×2=1576px가 필요하므로 1226은 이미 상한에 가깝다. 해결책은 원본 축소가 아니라 **브라우저가 srcset에서 고르게 하는 것**이다.

> 🩻 **v5.3 변경 (2026-08-19) — 이 루틴은 사람의 머리를 지우는 문구를 권장 표현으로 싣고 있었다.**
> 2026-08-19 #139(Post 3461) 마지막 이미지에 **머리와 목이 통째로 없는 인물**이 생성됐고, 발행 전 사용자가 직접 발견했다. 원인은 프롬프트 실수가 아니라 **舊 3-3 ③ 384행이 `hands only, no faces visible` 을 권장 표현으로 명시**한 것이었다. `only` 는 생성 모델에게 "**열거된 것만 그리고 나머지는 지워라**"로 읽히므로, 손만 프레임에 들어오는 접사에서는 안전하지만 **몸통이 보이는 인물**에 붙이면 열거되지 않은 부위가 실제로 사라진다.
> 실측 대조: 문제 이미지는 `shoulders and one hand only, no face visible` → **머리 결손**. 같은 프롬프트의 나머지 후보 1장, 그리고 `only` 없이 `seen from behind` 만 쓴 #138 골목·#140 부산역 이미지는 **전부 정상**이었다. 문구가 유일한 변수였다.
> 부차 원인: 舊 5-3 채택 기준에 "왜곡된 손"은 있었지만 **결손 신체 항목이 없어** 판정에서 걸러지지 않았고, 7.5 육안 검증에도 해부 항목이 없었다.
> → v5.3은 ① **3-3 ③에 `X only` 금지 규칙과 「몸통이 보이는 인물」 표준 문형**을 신설 ② 표준 제외 세트에 **`no headless figures` 계열 추가** ③ **5-3에 해부 검사를 최우선 탈락 기준으로 신설** ④ **7.5에 프리뷰 재확인**을 추가해 **두 번 거르는 구조**로 만든다. 핵심 원리는 **"얼굴을 지워라(no face)"가 아니라 "얼굴을 돌려라(turned away)"** 로 지시하는 것이다.

> 🎯 **v5.2 변경 (2026-08-18) — 0and1Life v5.0/v5.1에서 역백포트한 2건.**
> ① **프롬프트 철학이 한 세대 뒤처져 있었다.** v4.1은 '어디에서 찍었는가'(한국성)를 고쳤지만 **'무슨 일이 벌어지는가'(사건)** 는 비어 있어, 규칙을 다 지켜도 *"한국이 배경인, 아무 일도 일어나지 않는 사진"* 이 나왔다. 2026-08-18 #137 채택본 4장의 한 문장이 **전부 "…가 있다"** 였다. → **STEP 3-2를 「장면 설계 원칙」으로 교체**하고(한 문장 테스트·훅 문장·물리량 번역·긴장 요소·시선 유도점·범용 은유 금지·3초 테스트), 기존 피사체 정확성은 3-2B, 한국성은 3-3으로 내렸다. **3-3B 자기비판 표**와 **3-3C 8항목 체크리스트**를 신설했다. 최종 통과 조건은 **사건 + 한국성 + 썸네일** 3중 게이트다.
> ② **다중 스톡 버그가 남아 있었다.** 舊 7-2.5는 스톡 태그 전부를 같은 히어로로 치환해, `[FEATURED_IMAGE_URL]` 이 2곳인 글에서 **같은 이미지를 본문에 두 번** 박았다 (0and1Life #88 Post 1160 실측). → **순차 교체**(첫 번째만 히어로, 나머지는 본문 이미지)로 바꾸고 `_evGuard` 에 **`dupImg` 가드**를 추가했다.
> 함께 정리: 5-4 제목이 "에디터 뷰에 띄운 상태에서 실행"인데 본문은 "에디터에 들어가지 않는다"였던 모순을 제거하고, 오해를 부르던 SPA 안전 문단을 **"그리드를 떠나지 않는다"**로 교체했다 (재진입 시 지연 로딩 20초+ 재발생).

> ⚡ **v4.2 변경 (2026-08-18) — 실행 시간을 25분에서 8~10분으로 줄인다.**
> 2026-08-18 #137 실행이 **약 130회 도구 호출 / 25분**이 걸렸다. 정작 이미지 생성 자체는 4장 × 20초 = **80초**면 되는 일이었고, 나머지는 전부 **직렬 대기와 왕복 낭비**였다. 원인 4개를 실측으로 확인하고 「⚡ 실행 효율 원칙」 절을 신설해 STEP 5·6에 반영했다.
> ① Flow는 **생성 중에도 다음 프롬프트를 받는다** → 4장 연속 제출 후 대기 1회 (실측: 4장 60초)
> ② `javascript_tool` 은 **최상위 `await` 반환을 지원한다** → `fire-and-read` 2회 호출 패턴 폐기
> ③ 그리드 썸네일이 **원본 1376×768을 그대로 갖고 있다** → 에디터 진입 없이 4장 일괄 캡처 (실측 439ms)
> ④ `browser_batch` 로 `click→type→click→wait→screenshot` 을 1회로 묶는다

> 🇰🇷 **v4.1 변경 (2026-08-18) — 이미지가 "어디에나 있을 법한" 문제를 고친다.**
> 2026-08-18 #137 실측: 생성한 4장 중 **3장이 한국 요소를 지우면 다른 나라 사진과 구분되지 않았다** (빈 지하철 통로, 스테인리스 좌석 위 정물, KTX 트레이). 사실적이지만 **아무 데도 아닌 곳**의 사진이었고, "한국이 궁금한 외국인"이라는 독자에게 아무 매력도 주지 못했다.
> 원인은 프롬프트 실력이 아니라 **루틴이 강제한 제외 조건**이었다. 舊 STEP 3-3은 `no people, no text` 를 기본값으로 못 박았는데, 이 두 줄이 ① 생활감·스케일·이야기를 지우고 ② **한글 간판이라는 가장 강력한 '한국' 신호**를 통째로 차단했다.
> → v4.1은 STEP 3-3을 **「한국성(Korean-ness) 원칙」**으로 전면 교체한다: **Nowhere 테스트**(한국 요소를 지우면 다른 나라 사진이 되는가) 필수 적용, **한국 지표 표 7개 영역**에서 이미지마다 2개 이상 물리적 묘사, **인물 정책 전환**(부분 인물 적극 허용, 3장 중 1장은 사람 흔적 필수), **텍스트 정책 전환**(아웃포커스 한글 간판 허용, 읽히는 문단만 금지). 프롬프트 예시 5종도 전부 다시 썼고, STEP 5-3 채택 기준·STEP 7.5 검증·STEP 8 보고에 한국성 게이트를 연결했다.

### 목적

Notion 글 현황 테이블에서 오늘 날짜에 작성된 WordPress 글을 찾아, **데코(생성) 이미지가 3장 미만인 글**에 **Google Flow(Nano Banana 2)** 로 생성한 이미지를 WebP 형식으로 삽입한다 — 단, **증빙+데코 합계가 5장을 넘지 않는 범위**에서만 (생성 수를 3→2→1장으로 자동 감축). 기존에 무관한 스톡(Unsplash 등) 이미지가 들어가 있으면 함께 교체한다.

> 🚀 **v4.0 변경 (2026-08-18) — 이미지 생성처를 gemini.google.com에서 Google Flow로 교체한다.**
> 2026-08-18 동일 프롬프트(지하철 좌석 위 밀폐 냉음료 vs 개봉 뜨거운 음식) 실측 비교:
>
> | 항목 | 舊 Gemini 웹 UI | **新 Google Flow (Nano Banana 2)** |
> |---|---|---|
> | 생성 속도 | 60~90초, **당일 2회는 3~4분 지연** | **약 20초에 2장** (진행률 % 실시간 표시) |
> | 1회 산출 | 1장 | **2장** (x2 설정, 0크레딧) |
> | 전송 안정성 | 첫 클릭 씹힘 **4회 중 2회** | 첫 클릭 **즉시 전송** |
> | 원본 해상도 | 1024×559 | **1376×768 (16:9)** |
> | 이미지 호스트 | `blob:` → 리로드 시 `lh3` **taint** | **`labs.google` 동일 출처** |
> | 워터마크 | 우하단 모서리, `cropBottom 150` | 상대좌표 **(0.925W, 0.875H) 고정**, `cropRight 150` |
> | 크롭 후 크기 | 984×409 (402k px) | **1226×768 (942k px, 2.34배)** |
> | 4장 총 소요 | 약 25분 | **약 3분** |
>
> 결정적 이점은 속도가 아니라 **구조적 안정성**이다. Flow는 이미지를 `labs.google` **동일 출처**로 서빙하므로 v3.4~v3.5를 괴롭힌 `SecurityError: canvas has been tainted` 가 **원천적으로 발생하지 않는다.** 이에 따라 舊 STEP 5의 blob 복구 절차(URL 릴레이·IMGTAB 탭·`location.href` 이동)는 **전부 삭제**했다. 또 x2로 2장을 받아 **좋은 쪽을 고르는 구조**라 舊 "수정 재시도 1회" 규정이 실제로 발동할 일이 거의 없다.

> ⚠️ v3 변경 (2026-08-01): Draft 루틴이 발행 관문용 **증빙 캡처**(`figure class="evidence-capture"`, 파일명 `evidence-*`)를 본문에 넣기 시작하면서, 총 이미지 수 기준(舊 imgCount ≥ 3 → skip)으로는 모든 글이 스킵되어 이 루틴이 돌지 않았다. 판정은 **데코 개수**로 하되, 글이 이미지로 과밀해지지 않도록 **총량 상한 5장**(증빙+데코, 히어로 교체는 총량 불변이라 제외)을 함께 둔다. 증빙 캡처는 어떤 단계에서도 교체·이동·삭제하지 않는다.

> ⚠️ v3.2 변경 (2026-08-04): 舊 정규식 분류기는 **v1.28 이전에 작성된 레거시 글의 증빙 캡처를 인식하지 못했다.** Draft 루틴이 `evidence-` 파일명·`evidence-capture` 클래스를 붙이기 시작한 것은 v1.28(2026-08-02)부터라, 그 이전 글의 증빙은 마커가 없어 **데코로 오분류**된다. 0and1Life에서 먼저 실측된 사례: #70 결혼식 보증인원(Post 894)은 공공 출처(price.go.kr) 조회 캡처 2장이 데코로 잡혀 deco=4 → genCount 0 → skip. 이미지가 필요한 글인데 루틴이 3일 내내 그냥 지나쳤다. KoreaPlug도 v1.28 이전 글은 동일한 구멍이 있으므로 같은 수정을 적용한다. STEP 2를 **DOM 기반 8단계 우선순위 분류기**로 교체하고, **미분류(unknown)가 있으면 skip 금지** 가드를 신설한다.

> ⚠️ v3.3 변경 (2026-08-08): STEP 6-1의 `window.open(url, '_blank')` 로 연 WP admin 탭이 **Chrome MCP 탭 그룹 밖에 생성돼** `tabs_context_mcp` 목록에 나타나지 않았고, 그 결과 6-2의 postMessage 리스너를 주입할 수 없어 업로드 경로 전체가 막혔다 (2026-08-08 #129 실측). 두 번째 인자 `'_blank'` 를 **제거**하면 탭이 그룹에 정상 등록된다.

> 🚨 v3.4 변경 (2026-08-12) — **지금까지 이 루틴은 매 실행마다 본문 원본을 조용히 훼손해 왔다.**
> 舊 코드는 모든 본문 fetch에서 `d.content.raw || d.content.rendered` 를 썼는데, WP REST는 **`context=edit` 를 붙이지 않으면 `content.raw` 를 아예 내려주지 않는다.** 즉 폴백이 항상 발동해 **렌더링된 HTML**(ez-toc 플러그인이 생성한 목차 마크업 + wpautop이 넣은 `<p>` 태그)을 읽었고, 거기에 이미지를 끼워 그대로 `post_content` 에 저장했다. 결과:
> - Gutenberg 블록 주석(`<!-- wp:rank-math/toc-block -->`, `<!-- wp:freeform -->`)이 **전부 소실**
> - 플러그인이 매번 생성해야 할 목차가 **정적 HTML로 본문에 박제** — 이후 헤딩을 고쳐도 목차가 따라가지 않는다
> - 2026-08-12 실측: #128(3301) ez-toc 59개 · #129(3341) 40개 · #130(3352) 50개 · #131(3363) 66개 — **이미 4편이 오염된 상태로 발행·예약됨**
> 또한 같은 날 #132(3376)에서 **content만 POST했는데 글 상태가 `draft` → `future`(예약발행)로 자동 전환**되는 사고가 났다. 글의 `post_date` 가 미래면 WP가 업데이트 시 스스로 예약 상태로 승격시킨다. 이는 루틴의 절대 금지사항(발행·예약 전환 금지)을 위반한다.
> → v3.4는 ① 모든 본문 fetch에 **`context=edit` 필수**, raw 없으면 **중단** ② 모든 저장 POST에 **원래 status 명시 동봉** ③ 저장 후 **raw 오염·상태 검증**을 신설한다. 아울러 삽입 위치를 헤딩 개수가 아닌 **문자 위치** 기준으로 잡는다(STEP 4).

---

### ⚡ 실행 효율 원칙 (v4.2 — 모든 STEP에 우선 적용)

> 🚨 **v4.2 개정 사유 (2026-08-18)**: 2026-08-18 #137 실행이 **약 130회 도구 호출 / 25분**이 걸렸다. 이미지 생성 자체는 4장 × 20초 = **80초**면 끝나는 일인데, 나머지 시간은 전부 **직렬 대기와 왕복 낭비**였다. 아래 4개 규칙으로 같은 작업이 **약 30회 호출 / 8~10분**으로 줄어든다. 실측 근거는 각 항목에 붙였다.

**① 이미지는 '전부 제출 → 한 번 대기 → 한 번에 캡처' 순서로 한다 (최대 효과)**

舊 방식은 `프롬프트1 → 90초 대기 → 검증 → 캡처 → 프롬프트2 → 90초 대기 → …` 로 **4번 직렬 대기**했다.
✅ **(2026-08-18 실측) Flow는 앞 이미지가 생성 중일 때 다음 프롬프트를 그대로 받는다.** 제출 직후 입력창이 비워지므로 곧바로 다음 것을 넣으면 된다. 4장이 **병렬로** 진행된다 (실측: 13%·13%·74%·74% 동시 진행 → 약 60초에 4장 완료).
→ **프롬프트 4개를 STEP 3에서 모두 완성한 뒤, STEP 5에서 연속 제출하고 대기는 1회만 한다.**

**② `browser_batch` 로 왕복을 묶는다**

`click → type → click → wait → screenshot` 은 **1회 호출**로 처리한다. 10초 `wait` 를 3번 반복해야 하면 그것도 한 배치에 넣는다. 舊 실행은 이 시퀀스를 매번 5회로 나눠 불렀다.

**③ `fire-and-read` 2회 호출 패턴을 폐기한다**

✅ **(2026-08-18 실측) `javascript_tool` 은 최상위 `await` 를 지원하고 마지막 표현식 값을 그대로 반환한다** (`await new Promise(...)` → 2.2초 뒤 값 반환 확인).
→ 舊 규칙이던 "async는 window 변수에 담고 다음 호출에서 읽는다"는 **더 이상 필요 없다.** `const d = await fetch(...).then(r=>r.json()); '요약문'` 형태로 **fetch와 검증을 한 호출에 합친다.** STEP 2·3·7에서만 호출이 절반으로 준다.
⚠️ 단, **window 변수 저장 자체는 계속 한다** — 뒤 단계에서 재사용해야 하기 때문이다. 없애는 것은 '읽기 위한 추가 호출'뿐이다.

**④ 캡처는 그리드에서 일괄로 한다 — 에디터 뷰에 들어가지 않는다**

✅ **(2026-08-18 실측) Flow 그리드 썸네일은 표시폭이 318px여도 `naturalWidth` 는 원본 1376×768 그대로다.** 따라서 에디터를 열 필요가 전혀 없다.
→ **4장을 한 번의 `javascript_tool` 호출로 캡처한다. 실측 439ms.** 舊 방식은 이미지마다 `클릭 → 스크린샷 → 캡처 → 확인 → 뒤로가기` 5회씩, 총 20회를 썼다.

**시간 예산 (이 4개를 지켰을 때)**

| 단계 | 舊 (2026-08-18 실측) | 新 목표 |
|---|---|---|
| **STEP 0 세션 점검 (v5.5)** | — (없었음) | **2~3회 / 30초** — 여기서 걸리면 총 3회로 종료 |
| STEP 1 Notion | 6회 호출 (오버플로+실패 grep 3회) | 2~3회 |
| STEP 2~4 판정·프롬프트·위치 | 약 20회 | 7~8회 |
| **STEP 5 생성·캡처** | **약 70회 / 25분** | **6~8회 / 2~3분** |
| STEP 6 업로드 | 약 12회 | 4회 |
| STEP 7~7.5 삽입·검증 | 약 20회 | 6~8회 |
| **합계** | **약 130회 / 25분+** | **약 30회 / 8~10분** |

---

### STEP 0: 세션 사전 점검 (v5.5 신설 — 다른 모든 것보다 먼저 한다)

> 🚨 **이 절이 STEP 1보다 앞에 있는 이유 (2026-08-25 실측)**: 이 루틴은 **WP 세션**과 **Flow 세션** 두 개에 전적으로 의존한다. 둘 중 하나라도 죽으면 결과물은 0이다. 그런데 舊 버전은 WP를 STEP 2에서, Flow를 STEP 5에서 **각각 뒤늦게** 만났다. 2026-08-25 실행은 Flow가 죽은 상태에서 STEP 1~4를 전부 수행한 뒤 STEP 5에서 중단됐고, **본문 정독과 프롬프트 4개 설계가 통째로 낭비**됐다. 실패할 실행은 **1분 안에** 실패시킨다.

⛔ **공통 원칙 — 루틴은 어떤 서비스에도 로그인하지 않는다.** 자격증명 입력, 인증 폼 제출, OAuth/SSO 동의, 계정 선택 화면 클릭은 **전부 금지**다. 자동완성이 채워져 있거나 계정이 이미 목록에 떠 있어도 클릭하지 않는다 — 그 클릭은 권한 부여 행위이며 사용자 승인 사항이다.

**0-1. 두 탭을 함께 연다 (`browser_batch` 1회).**

```
browser_batch([
  {navigate: 'https://koreaplug.com/wp-admin/media-new.php', tabId: WP},
  {navigate: 'https://labs.google/fx/ko/tools/flow/project/6a6af995-4d64-4bbb-8e97-4be7aa267e6d', tabId: FLOW},
  {computer: wait 10},
  {computer: wait 5},
  {computer: screenshot scale 0.45, tabId: FLOW}
])
```

**0-2. WP 세션 판정** — WP 탭에서 nonce 추출을 겸해 한 번에 확인한다.

```javascript
const s = Array.from(document.querySelectorAll('script:not([src])')).map(x => x.textContent).join('\n');
const m = s.match(/apiFetch\.createNonceMiddleware\(\s*["']([a-f0-9]+)["']/);
window._nonce = m ? m[1] : (window.wpApiSettings ? wpApiSettings.nonce : null);
'url:' + location.pathname + ' nonce:' + (window._nonce ? 'ok' : 'MISSING')
```

- ✅ 정상: `url:/wp-admin/media-new.php nonce:ok`
- ⛔ 만료: `wp-login.php?...&reauth=1` 로 리다이렉트됐거나 `nonce:MISSING`
- 만료 시 조치: 오류 로그에 **"WP 세션 만료 — 사용자 직접 로그인 필요"** 를 기록하고 **즉시 종료**한다. 이미지 생성·삽입은 일절 수행하지 않으며, 대상 글의 상태는 건드리지 않는다.
- 사용자 조치 안내: "Chrome에서 `https://koreaplug.com/wp-admin` 에 직접 로그인하고 '기억하기'를 체크해 주세요."

**0-3. Flow 세션 판정 (v5.5 신설)** — 스크린샷과 최종 URL 두 가지로 본다.

- ✅ 정상: 최종 URL이 `labs.google/fx/...` 를 유지하고, 화면에 **프롬프트 입력창과 생성물 그리드**가 보인다.
- ⛔ 만료: 최종 URL이 **`accounts.google.com/...signin...`** 계열로 바뀌었거나, 화면에 **"계정을 선택하세요"**·"Google 계정으로 로그인"·OAuth 동의 문구가 보인다.
- 만료 시 조치: 오류 로그에 **"Flow 세션 만료 — 사용자 직접 로그인 필요"** 를 기록하고 **즉시 종료**한다. 계정 목록에 `leejc0404@gmail.com` 이 떠 있어도 **클릭 금지**.
- 사용자 조치 안내: "Chrome에서 `https://labs.google/fx/ko/tools/flow` 에 `leejc0404@gmail.com` 으로 직접 로그인해 주세요."

**0-4. 판정 결과 처리**

| WP | Flow | 조치 |
|---|---|---|
| ✅ | ✅ | STEP 1로 진행 |
| ⛔ | ✅ | WP 만료 보고 후 종료 |
| ✅ | ⛔ | Flow 만료 보고 후 종료 |
| ⛔ | ⛔ | 둘 다 보고 후 종료 |

⛔ **하나라도 만료면 STEP 1(Notion 조회)로 진행하지 않는다.** Notion fetch는 9만 자 규모라 토큰만 태우고 결과를 못 쓴다.
ℹ️ 세션이 복구되면 **STEP 1의 2일 소급 규정**(오늘·어제)이 누락분을 자동으로 따라잡으므로, 하루 건너뛴 것은 다음 실행에서 회수된다.
ℹ️ 종료 전 **이 루틴이 연 탭은 모두 닫는다** (`tabs_close_mcp`).

---

### STEP 1: Notion에서 오늘 날짜 글 찾기

⚠️ **STEP 0을 통과하지 않았다면 이 단계를 시작하지 않는다.**

Notion MCP를 사용해 https://app.notion.com/p/33cbfe4a2ae181b9a743cb7c194dea7f 페이지를 fetch한다.

⚠️ **Notion 페이지가 커서 fetch 결과가 토큰 한도를 넘으면** 결과가 파일로 저장된다. 이때 전체를 다시 읽지 말고, 저장된 파일에 `grep`(최근 날짜 문자열) 또는 python 슬라이스로 **표 끝부분과 로그 tail만** 확인한다 (2026-08-18 실측: 72,436자 초과).

ℹ️ **(v4.0) `grep` 결과가 "Omitted long matching line"으로 막히면** 매치 창을 좁힌다. `.{0,300}날짜.{0,300}` 는 막히고 **`.{0,90}2026-08-18.{0,90}` 는 통과**한다 (2026-08-18 실측). 글 번호로 찾을 때는 `.{0,90}#13[5-8].{0,90}` 처럼 범위 패턴을 쓰면 최근 회차 로그가 한 번에 잡힌다.

(v3.1) **오늘 또는 어제 날짜**(YYYY-MM-DD)와 일치하는 **'draft 일자'** 또는 **'작성일자'** 행을 모두 찾는다. — 2일 소급 이유: 배포 루틴이 인증 문제 등으로 늦게 재실행되면 이 루틴이 도는 시점엔 글이 아직 WP에 없어 영영 누락된다 (2026-08-02 #122 실제 사례). 어제 글까지 봐야 다음 실행이 따라잡는다.
해당 행에서 **글 제목(영문)**, **카테고리**, **한줄 요약**을 추출한다.
대상이 여러 건이면 **오래된 날짜부터** 각각 STEP 2 판정을 거쳐, genCount>0 이거나 스톡 교체가 필요한 글만 순서대로 처리한다 (이미 충족된 글은 skip — 중복 삽입 방지는 STEP 2 판정이 보장).

오늘·어제 모두 대상 글이 없으면 "최근 2일 글 없음"을 출력하고 종료.

---

### STEP 2: WordPress에서 해당 글 확인

✅ **(v5.5) STEP 0-2에서 이미 `media-new.php` 탭과 `window._nonce` 를 확보했으므로 그 탭을 그대로 이어 쓴다.** 새 탭을 열거나 nonce를 다시 뽑지 않는다 — 재이동은 `window._nonce` 를 날린다.

⚠️ **(v3.4) `/wp-admin/` 대시보드는 간헐적으로 자체 리다이렉트를 일으켜 window 변수를 날린다** (2026-08-12 실측: `index.php` → `edit-comments.php`). 장시간 window 상태를 유지해야 하는 이 루틴은 **처음부터 `media-new.php` 에서 작업한다.**

⚠️ `media-new.php` 에는 `wpApiSettings` 가 정의되어 있지 않다. REST nonce를 먼저 확보해 `window._nonce` 에 담고, 이후 모든 fetch에서 이 값을 쓴다:

```javascript
const s = Array.from(document.querySelectorAll('script:not([src])')).map(x => x.textContent).join('\n');
const m = s.match(/apiFetch\.createNonceMiddleware\(\s*["']([a-f0-9]+)["']/);
window._nonce = m ? m[1] : (window.wpApiSettings ? wpApiSettings.nonce : null);
'url:' + location.pathname + ' nonce:' + (window._nonce ? 'ok' : 'MISSING')
```

⛔ **(v3.4) 본문을 읽는 모든 fetch에 `context=edit` 를 반드시 붙인다.** 붙이지 않으면 `content.raw` 가 응답에 없어 `|| content.rendered` 폴백이 발동하고, 이후 저장 단계에서 **렌더링된 HTML이 원본 본문을 덮어쓴다.**

`status=any` 와 `context=edit` 가 **둘 다** 필요하다.

```javascript
window._postData = null;
fetch('/wp-json/wp/v2/posts?search=TITLE_KEYWORD&per_page=5&status=any&context=edit&_fields=id,title,status,content,date,featured_media,slug', {
  headers: {'X-WP-Nonce': window._nonce}
}).then(r => r.json())
  .then(d => { window._postData = d; });
// 2~3초 대기 후 확인
```

ℹ️ Post ID를 이미 알고 있으면 `search=` 대신 `include[]=ID1&include[]=ID2` 로 여러 건을 한 번에 가져올 수 있다.

```javascript
// (v3.4 필수) raw 확보 검증 — raw가 없으면 여기서 중단한다
window._postData.map(p => p.id + ' | ' + p.status + ' | ' + p.date + ' | fm:' + p.featured_media + ' | ' + p.slug
  + ' | raw:' + (p.content && typeof p.content.raw === 'string' ? 'ok len' + p.content.raw.length : 'RAW-MISSING')).join('\n')
```

⛔ 하나라도 `RAW-MISSING` 이면 **더 진행하지 않는다.** nonce 권한 또는 `context=edit` 누락 문제이므로, 원인을 해결한 뒤 재실행한다. rendered 폴백으로 진행하는 것은 금지한다.

(v3.2) 분류는 정규식을 본문 전체에 훑는 방식이 아니라, **이미지 하나씩 DOM으로 열어 8단계 우선순위**로 판정한다. 판정 근거(`why`)를 이미지별로 남겨 오분류를 사후 추적할 수 있게 한다.

```javascript
window._cls = window._postData.map(p => {
  const html = p.content.raw;                 // (v3.4) rendered 폴백 제거 — raw만 사용
  const div = document.createElement('div'); div.innerHTML = html;

  const evClassRe = /evidence-capture/i;                                      // ① figure 클래스 (v1.28 표준)
  const evNameRe  = /^evidence-/i;                                            // ② 파일명 prefix (v1.28 표준)
  const stockRe   = /unsplash\.com|pexels\.com|pixabay\.com|FEATURED_IMAGE/i;  // ③ 스톡·플레이스홀더
  const genNameRe = /^(koreaplug|0and1life)-/i;                               // ④ 이 루틴이 만든 생성 이미지
  const evCapRe   = /Captured\s*\d{4}\s*[-.\/]\s*\d{1,2}\s*[-.\/]\s*\d{1,2}/i; // ⑤ figcaption 촬영일 (레거시)
  const evSrcRe   = /(go[-_.]kr|korea[-_.]kr|kosis|hometax|work24)/i;         // ⑥ 공공 출처 도메인 흔적 (레거시)
  const evAltRe   = /(캡처|캡쳐|스크린샷|Captured|Screenshot|조회한|조회 결과|확인한|고지서|명세서|모의계산)/i; // ⑦ alt 단서 (레거시)

  let evidence = 0, stock = 0, deco = 0;
  const detail = [], unknown = [];

  for (const img of Array.from(div.querySelectorAll('img'))) {
    const src  = img.getAttribute('src') || '';
    const base = (src.split('/').pop() || '').split('?')[0];
    const alt  = img.getAttribute('alt') || '';
    const fig  = img.closest('figure');
    const capEl = fig ? fig.querySelector('figcaption') : null;
    const cap  = capEl ? capEl.textContent : '';
    const cl   = fig ? (fig.getAttribute('class') || '') : '';

    let k, why;
    if      (evClassRe.test(cl))   { k = 'evidence'; why = 'figure.class'; }
    else if (evNameRe.test(base))  { k = 'evidence'; why = 'filename'; }
    else if (stockRe.test(src))    { k = 'stock';    why = 'stock'; }
    else if (genNameRe.test(base)) { k = 'deco';     why = 'gen-prefix'; }
    else if (evCapRe.test(cap))    { k = 'evidence'; why = 'figcaption'; }
    else if (evSrcRe.test(base))   { k = 'evidence'; why = 'public-src'; }
    else if (evAltRe.test(alt))    { k = 'evidence'; why = 'alt-cue'; }
    else                           { k = 'deco';     why = 'UNKNOWN'; unknown.push(base); }

    if (k === 'evidence') evidence++; else if (k === 'stock') stock++; else deco++;
    detail.push(base.slice(0, 44).replace(/[?&=]/g, '_') + ' => ' + k + ' [' + why + ']');
  }

  const genCount = deco >= 3 ? 0 : Math.max(0, Math.min(3 - deco, 5 - evidence - deco)); // 총량 상한 5장
  return {id: p.id, title: p.title.raw || p.title.rendered, status: p.status, date: p.date, fm: p.featured_media, slug: p.slug,
          evidence, stock, deco, genCount, hasStockImg: stock > 0, unknown, detail};
});
window._cls.map(c => c.id + ' st:' + c.status + ' fm:' + c.fm + ' ev:' + c.evidence + ' stk:' + c.stock + ' deco:' + c.deco + ' gen:' + c.genCount + ' unk:' + c.unknown.length).join('\n')
```

⚠️ (v3.3 / 2026-08-08 실측) `javascript_tool` 의 반환 문자열에 이미지 URL·쿼리스트링이 그대로 섞이면 **`[BLOCKED: Cookie/query string data]`** 로 출력 전체가 막힌다. 결과를 읽을 때는 한 번에 전부 찍지 말고 ⓐ 집계값만(`ev/st/deco/gen/unk`) 먼저, ⓑ `detail` 은 글 단위로 나눠서, ⓒ 파일명에서 `?&=` 를 치환하거나 공통 prefix를 축약해 출력한다. `.replace(/<img[^>]*>/g,'[IMG]')` 같은 치환도 **원본 문자열에 URL이 남아 있으면 소용없다** — 반드시 파일명만 잘라서 출력할 것.

ℹ️ **(v4.0) 본문 텍스트를 읽을 때도 같은 차단이 걸린다.** 본문에서 링크·이미지를 제거해도 `<a href>` 의 URL이 textContent에 남으면 막히므로, `https?:\/\/\S+` 를 공백으로 치환하고 `[?&=]` 를 제거한 뒤 출력한다 (2026-08-18 실측).

우선순위를 이 순서로 고정한 이유: 표준 마커(①②)가 있으면 그것이 가장 확실한 근거이므로 먼저 본다. 스톡(③)은 호스트로 확정된다. 이 루틴이 직접 만든 이미지(④)는 파일명 prefix로 확실히 데코이므로, 레거시 추정 규칙(⑤⑥⑦)이 이를 잘못 증빙으로 끌고 가지 않도록 **레거시 규칙보다 먼저** 판정한다. ⑤⑥⑦은 마커가 없는 옛 글에만 적용되는 폴백이다.

⛔ **(v3.2 신설) `unknown`이 비어 있지 않으면 genCount 값과 무관하게 즉시 skip하지 않는다.** `unknown`에 잡힌 이미지는 자동 판정이 실패한 것이다. 본문에서 해당 `<figure>`를 직접 열어 figcaption에 출처 기관·`Captured YYYY-MM-DD`가 있는지, 화면 캡처처럼 보이는지 눈으로 확인한 뒤 증빙/데코를 손으로 확정하고 **genCount를 다시 계산한 다음** 진행 여부를 정한다. 확인 결과는 STEP 8 보고에 이미지별로 남긴다.

> 이 가드가 필요한 이유 (2026-08-04 실측): 0and1Life #70(Post 894)은 증빙 2장이 데코로 오분류돼 genCount 0으로 계산됐고, 그 자리에서 종료되는 바람에 "애매하면 사람이 확인한다"는 아래 단계까지 **도달조차 하지 못했다.** 자동 분류가 틀렸다고 말할 기회 없이 skip된 것이 문제의 핵심이었다.

⛔ **(v3.4 신설) Notion에 대상 행이 있는데 WP 검색 결과가 0건이면 '미배포'로 판정하고 즉시 종료한다.** 배포 루틴이 아직 글을 올리지 못한 상태이므로 이미지 생성·업로드를 일절 수행하지 않는다 (2026-08-11 #132 실측: 배포 루틴이 샌드박스 VM 부팅 실패로 중단). 보고에 ① 미배포로 판정된 글 번호·제목·예상 slug ② WP 최신 수정 글의 날짜 ③ "배포 루틴 재실행 후 이 루틴을 다시 돌리면 자동으로 따라잡는다"는 안내를 남긴다.

- **genCount가 0이면 본문 삽입을 skip하고 종료** (단, `hasStockImg: true`면 스톡 이미지 교체만 수행 — 교체는 총량을 늘리지 않으므로 상한과 무관). `unknown`이 있으면 위 가드를 먼저 수행한 뒤 판단한다.
- genCount가 1~2장이면 그 수만큼만 생성·삽입한다. 우선순위: **이미지 1(도입 훅) → 이미지 3(결론 시각화) → 이미지 2(중반 클로즈업)** — 증빙 캡처가 이미 있는 글에서는 중반 클로즈업의 역할을 증빙이 대신한다.
- **증빙 캡처는 절대 건드리지 않는다**: 교체·이동·삭제 금지, 삽입 위치가 증빙 figure 내부에 떨어지면 직전 헤딩 바로 앞으로 옮긴다.
- `hasStockImg: true`면 **히어로 교체용 이미지 1장을 추가 생성**한다 (총 4장). 이 히어로 이미지는 STEP 7-2.5에서 기존 스톡 이미지의 src/alt를 교체하는 데 사용하고, 대표이미지로도 설정한다.
- **(v3.4) `status` 와 `date` 를 여기서 기록해 둔다.** STEP 7의 저장 POST에 원래 status를 동봉해야 상태 전환을 막을 수 있다.

```javascript
window._origStatus  = window._cls[0].status;   // 'draft' | 'future' | 'publish'
window._origDate    = window._cls[0].date;
window._curFeatured = window._cls[0].fm;
window._origStatus + ' / ' + window._origDate + ' / fm:' + window._curFeatured
```

---

### STEP 3: 글 본문 분석 및 이미지 프롬프트 생성

#### 3-1. 본문을 먼저 읽는다 (필수)

제목·한줄 요약만으로 프롬프트를 만들면 글과 어긋난 이미지가 나온다. **반드시 본문 raw content를 가져와 읽고** 프롬프트를 만든다 (이 fetch 결과는 STEP 4에서 재사용):

```javascript
window._rawContent = null;
fetch('/wp-json/wp/v2/posts/POST_ID?context=edit&_fields=content', {   // (v3.4) context=edit 필수
  headers: {'X-WP-Nonce': window._nonce}
}).then(r => r.json())
  .then(d => { window._rawContent = d.content.raw; });                  // (v3.4) rendered 폴백 금지
// 2~3초 대기 후 확인
```

```javascript
// (v3.4 필수) raw 건강 검진 — 블록 주석이 있고 ez-toc 흔적이 없어야 정상 원본이다
const c = window._rawContent;
'len:' + (c ? c.length : 'NULL')
 + ' blocks:' + ((c || '').match(/<!-- wp:/g) || []).length
 + ' ezToc:'  + ((c || '').match(/ez-toc/g) || []).length
 + ' pTags:'  + ((c || '').match(/<p>/g) || []).length
```

⛔ **`ezToc` 가 0이 아니거나 `blocks` 가 0이면 그 글의 `post_content` 는 이미 오염된 상태다.** 과거 실행이 rendered를 저장했다는 뜻이다. 이때는 삽입을 진행하지 말고, 먼저 **리비전에서 원본을 복구**한 뒤 진행한다:

```javascript
// 오염 복구 — 리비전 목록에서 blocks>0 · ezToc=0 인 가장 최근 리비전을 찾는다
window._revs = null;
fetch('/wp-json/wp/v2/posts/POST_ID/revisions?context=edit&per_page=20&_fields=id,modified,content', {
  headers: {'X-WP-Nonce': window._nonce}
}).then(r => r.json()).then(d => { window._revs = d; });
// 확인용 요약
// window._revs.map(x => { const c = x.content.raw || ''; return x.id + ' | ' + x.modified + ' | len' + c.length
//   + ' | wp:' + (c.match(/<!-- wp:/g)||[]).length + ' | ezToc' + (c.match(/ez-toc/g)||[]).length; }).join('\n')
// → 조건을 만족하는 리비전의 content.raw 를 window._rawContent 로 삼아 STEP 4로 진행한다
```

> 2026-08-12 #132(3376) 실측 복구 사례: 오염본 raw 20,592자(blocks 0 / ez-toc 66) → 리비전 3377의 원본 raw 15,422자(blocks 2 / ez-toc 0)를 기준으로 이미지를 다시 삽입해 16,278자(blocks 2 / ez-toc 0)로 정상화했다.
> **알려진 이월 과제**: #128(3301)·#129(3341)·#130(3352)·#131(3363)은 이미 오염된 채 발행·예약된 상태다. 이 루틴이 그 글을 다시 만질 일이 생기면 위 복구 절차를 먼저 적용하고, 그렇지 않다면 사용자 확인 후 별도로 정리한다.

본문에서 파악할 것:

- **핵심 피사체**: 글이 실제로 다루는 사물·기기·장소·음식이 무엇인가 (제목의 추상 키워드가 아니라 본문이 묘사하는 구체적 실물)
- 본문이 언급하는 **브랜드·형태·색·재질·사용 장면** (예: "black or silver rectangle with a numeric keypad", "Gateman, Samsung SDS" 같은 서술은 그대로 프롬프트 재료가 됨)
- 헤딩(h2/h3) 텍스트 — 각 이미지가 들어갈 위치 주변 섹션의 주제

#### 3-2. 장면 설계 원칙 (v5.0 — 최우선. 정확성보다도 먼저 통과해야 한다)

> 🎯 **v5.0 이식 사유 (2026-08-18)**: KoreaPlug은 v4.1에서 **'어디에서 찍었는가'(한국성)** 를 고쳤지만, **'무슨 일이 벌어지는가'(사건)** 는 여전히 비어 있었다. 그래서 v4.1 규칙을 지켜도 *"한국이 배경인, 아무 일도 일어나지 않는 사진"* 이 나온다. 0and1Life v5.0이 먼저 도달한 사건 설계 원칙을 이식하되, **한국성 원칙(3-3)은 그 위에 그대로 얹는다.** KoreaPlug의 이미지는 **사건 + 한국성**을 둘 다 통과해야 채택된다.

> 이 루틴의 이미지는 '글을 설명하는 삽화'가 아니라 **'글을 계속 읽게 만드는 장치'**다.
> 정확하기만 한 이미지는 실패다. **정확하면서 사건이 있는** 이미지만 채택한다.

**① 한 문장 테스트 (필수 · 프롬프트 작성 직후 스스로 물어본다)**
"이 이미지를 처음 보는 사람이 **지금 무슨 일이 벌어지는지** 한 문장으로 말할 수 있는가?"
- ❌ "빈 지하철 객실이 있다" · "좌석 위에 커피와 치킨 봉투가 놓여 있다" → **상태 서술 = 탈락**
- ✅ "치킨 봉투에서 김이 올라오는 순간 옆자리 승객이 고개를 돌린다" · "영수증 한 장이 개찰구에서 흘러내려 바닥까지 늘어져 있다" → **사건 서술 = 통과**
한 문장이 '있다/놓여 있다'로 끝나면 그 프롬프트는 버리고 다시 쓴다.

> 2026-08-18 #137 자기비판: 채택했던 4장의 한 문장이 전부 "…가 있다"였다. 한국성 이전에 **사건이 없었다.**

**② 본문에서 '훅 문장' 1개를 먼저 뽑는다 (필수 · 기록 대상)**
프롬프트를 쓰기 전에, 본문에서 외국인 독자가 가장 놀랄 문장 한 줄을 그대로 인용해 적어둔다. 그 문장 **한 줄만**을 그림으로 옮긴다. 이미지마다 훅 문장이 다르면 3장이 자동으로 달라진다.
> 예(#137): "No law bans eating. Article 34 lets staff stop you for smell."
> 예(#137): "The cost of eating on the subway is an audience, not a penalty."
훅 문장은 STEP 8 보고에 이미지별로 **반드시 남긴다.**

**③ 숫자를 사물의 물리량으로 번역한다 (문자로 쓰지 않는다)**
글의 핵심 수치는 화면에서 **눈으로 세지거나 비교되는 형태**여야 한다. 글자는 어차피 깨지므로 절대 쓰지 않는다.

| 본문 수치 | 번역 |
|---|---|
| 30배 차이 | 영수증 **길이** (손바닥 한 장 vs 바닥까지 늘어진 한 장) |
| 6,868원 vs 22만원 | 동전 몇 개 vs 지폐 다발 **부피** |
| 40분 소요 | 노선도 위 **정거장 점의 개수** |
| 670,000 views | 들어 올려진 **휴대폰 화면의 수** (한 대 vs 객실 가득) |
| 1/4만 해당 | 같은 물건 4개 중 **하나만 색·방향이 다름** |

**④ 긴장 요소를 최소 1개 넣는다 (정적 배치 금지)**
다음 중 하나 이상이 프롬프트에 명시돼야 한다 — 기울어짐 / 떨어지는 중 / 반쯤 열림·찢김 / 김이 막 오르는 / 한쪽만 켜짐 / 넘치기 직전 / 손이 막 놓거나 집는 순간 / 고개가 막 돌아가는 / 문이 닫히는 중.

**⑤ 시선 유도점은 1개만 둔다**
화면에서 가장 밝은 곳(또는 가장 채도가 높은 곳)이 **훅 문장의 주어와 일치**해야 한다. `the only bright accent in the frame is X` 처럼 못 박는다.

**⑥ 범용 은유 금지 목록 (글이 그 물건 자체를 다루지 않는 한 사용 금지)**
⛔ 모래시계 · 저울 · 전구 · 퍼즐 조각 · 체스말 · 화살표 그래픽 · 돼지저금통 · 악수 · 계산기와 안경 플랫레이 · 창밖 도시야경 단독 컷 · **텅 빈 지하철/거리/로비** · 정렬된 문구류 톱뷰 · 여권과 지도 플랫레이.
이 목록은 **어느 글에 붙여도 말이 되기 때문에** 금지한다. 어느 글에나 어울린다는 건 이 글의 이미지가 아니라는 뜻이다.

**⑦ 썸네일 3초 테스트**
완성된 이미지를 폭 320px로 줄였다고 상상한다. 그 크기에서 주제가 안 읽히면 피사체가 너무 작거나 배경이 복잡한 것이다 — 피사체를 화면의 **1/3 이상** 차지하게 다시 잡는다. **한국 지표(3-3)도 이 크기에서 읽혀야 한다.**

#### 3-2B. 피사체 정확성 원칙 (2순위 — 사건이 있어야 그다음이다)

> 사건 설계를 통과했더라도 핵심 피사체가 실물과 다르면 그 이미지는 실패다. 셋(사건·정확성·한국성)을 모두 만족해야 채택한다.

1. **한국 고유 형태를 가진 피사체는 실제 형태를 물리적으로 상세 묘사한다.** 한국의 가전·기기·시설·음식·소품은 서구식 일반형과 형태가 다른 경우가 많다. "Korean digital door lock"처럼 이름만 쓰면 생성 모델은 서구식 형태(둥근 도어노브 + 소형 사각 키패드)를 생성한다.
2. **형태를 정확히 모르면 웹 검색으로 실제 제품·장소 사진을 확인한 뒤** 프롬프트를 작성한다. 추측으로 쓰지 않는다.
3. **잘못 나오기 쉬운 형태를 명시적으로 배제한다.** 예: "absolutely no separate round doorknob", "no Western-style deadbolt".
4. **브랜드 스타일 참조는 허용, 로고는 배제.** 예: "(Gateman/Samsung SDS style)" + "no logos".

**정확성 묘사 예시 (Korean digital door lock):**

```
an authentic modern Korean digital door lock (Gateman/Samsung SDS style) — a tall vertical
rectangular brushed-silver metal panel mounted flush on the door, a touch-sensitive numeric
keypad glowing faintly blue in the upper section, a slim horizontal push-down lever handle
integrated into the lower section of the same panel, absolutely no separate round doorknob
```

이 원칙은 도어락에 한정되지 않는다. 밥솥·정수기·무인 키오스크·찜질방 시설·지하철 좌석·분리수거장 등 **글의 핵심 피사체가 무엇이든 동일하게 적용**한다.

**(v3.3 보강) 화면·디스플레이가 피사체인 글**: 한국 방송의 가림 처리는 서구식 가우시안 블러가 아니라 **각진 픽셀 블록(모자이크)**이다. `soft grey pixelated mosaic patch`, `the individual mosaic squares clearly larger and coarser than the surrounding picture detail` 처럼 **블록 형태와 거칠기를 명시**해야 의도한 결과가 나온다. 화면 안 장면까지 지정할 때는 `no readable text` 를 반드시 붙인다.

**(v3.4 보강) 거리·상가가 피사체인 글**: 한국 상가 거리는 ⓐ **주름진 금속 셔터**, ⓑ 그 위 **층층이 쌓인 간판 패널**, ⓒ **파란색으로 칠해진 버스전용차선**, ⓓ 원경의 **고층 아파트 단지**, ⓔ 전선이 얽힌 **전봇대**가 특징이다. 간판 글자는 깨져 나오므로 `the stacked signboard panels above them reduced to plain flat coloured rectangles` 처럼 **글자 없는 색면으로 지정**한다.

**(v4.0 보강) 지하철 내부가 피사체인 글**: 서울 지하철 객실은 ⓐ **브러시드 스테인리스 롱벤치 좌석**과 좌석 사이 **얇은 세로 칸막이 바**, ⓑ **파란색 삼각 손잡이**가 줄지어 달린 스트랩, ⓒ 세로 스테인리스 봉, ⓓ **노약자석 노란 표시**, ⓔ 차가운 백색 LED 천장등, ⓕ 짙게 틴팅된 창이 특징이다. 이 6가지를 나열하면 실제와 거의 일치하는 결과가 나온다 (2026-08-18 #137 실측, 2장 모두 통과).

#### 3-3. 한국성(Korean-ness) 원칙 — v4.1 전면 개정 (3순위 · KoreaPlug 고유. 0and1Life에는 없는 절이다)

> **적용 순서**: 3-2 사건 설계(무슨 일이 벌어지는가) → 3-2B 피사체 정확성(실물이 맞는가) → **3-3 한국성(한국임이 읽히는가)**. 앞 두 개를 통과해도 이 절에서 떨어지면 채택하지 않는다. KoreaPlug 독자는 "한국이 궁금한 외국인"이므로 이 절이 사이트의 정체성이다.

> 🚨 **v4.1 개정 사유 (2026-08-18)**: 舊 3-3은 "분위기·라이팅 원칙"이었고, `no people, no text` 를 기본 제외 조건으로 못 박고 있었다. 그 결과 **깨끗하고 텅 빈, 어디에나 있을 법한 이미지**가 양산됐다. 2026-08-18 #137 실측: 생성한 4장 중 **3장(빈 지하철 통로, 스테인리스 좌석 위 정물, KTX 트레이)은 한국 요소를 지우면 도쿄·타이베이·뉴욕 사진과 구분되지 않았다.** 사실적이지만 **아무 데도 아닌 곳(nowhere)** 의 사진이었다.
> KoreaPlug의 독자는 "한국이 궁금한 외국인"이다. 이들에게 필요한 건 **깔끔한 제품 사진이 아니라 "저기 가 보고 싶다"는 충동**이다. 따라서 v4.1은 제외 조건 두 개를 뒤집는다.

**① 원칙 0 — 'Nowhere 테스트' (모든 이미지에 필수 적용)**

프롬프트를 완성한 뒤 스스로 묻는다:

> **"이 장면에서 한국 고유 요소를 지우면, 다른 나라 사진이 되는가?"**
> 그렇다면 **실패다.** 프롬프트를 버리고 다시 쓴다.

빈 지하철 객실, 깨끗한 책상 위 노트북, 창밖 풍경이 흐른 기차 좌석, 흰 배경 위 음식 — 이런 구도는 이 테스트를 통과하지 못한다.

**② 한국 지표(Korea Markers) — 이미지마다 최소 2개 이상 명시적으로 넣는다**

아래는 외국인이 한눈에 "한국"으로 인식하는 시각 요소다. 글의 주제와 상관있는 것을 골라 **프롬프트 문장에 물리적으로 묘사**한다. 단순히 "Korean"이라는 형용사를 붙이는 것으로는 절대 대체되지 않는다.

| 영역 | 지표 (프롬프트에 쓸 물리 묘사) |
|---|---|
| 간판·거리 | 한 건물 외벽을 층층이 덮은 **간판 패널 더미**, 붉은 네온 십자가, 얽힌 전봇대 전선, **파란색으로 칠해진 버스전용차선**, 주름진 금속 셔터, 노란 안전 볼라드 |
| 식탁 | **납작한 은색 스테인리스 젓가락과 긴 숟가락**, 뚜껑 덮인 **은색 스테인리스 밥공기**, 작은 접시에 담긴 **반찬 여러 종**, 초록 소주병과 작은 소주잔, 테이블 매립형 가스버너, 가위로 자르는 고기 |
| 편의점·가게 | 삼각김밥 매대, **온장고**, 즉석 라면 조리기, 가게 앞 **플라스틱 스툴과 접이식 테이블**, 파라솔 |
| 대중교통 | **분홍색 임산부 배려석**, 경로석 표시, 스크린도어, 벽면 노선도, 파란 삼각 손잡이, 은색 롱벤치 |
| 주거 | 회색·베이지 **고층 아파트 단지**와 동 번호, 현관 **디지털 도어락**, 베란다 빨래건조대, 보일러 온돌 바닥, 신발 벗는 현관 단차 |
| 계절·자연 | 벚꽃 터널, 은행나무 노란 낙엽, 단풍 든 산비탈, 장마철 젖은 아스팔트, 한강 둔치 돗자리 |
| 전통 | 기와 처마 곡선, 창호지 문살, 단청, 돌담길, 한복 저고리 옷고름 |

**③ 인물 정책 — `no people` 기본값을 폐기한다 (v5.3 개정)**

사람이 없으면 스케일·생활감·이야기가 사라진다. 이제 기본값은 **"부분 인물 허용"** 이다.

- ✅ **적극 허용**: 손·팔·뒷모습·실루엣·군중의 흐름·움직임 블러로 흐른 행인, 우산 쓴 사람들의 무리
- ✅ 인물은 **행위 중**이어야 한다 — 가위로 고기를 자르는 손, 개찰구를 통과하는 뒷모습, 젓가락으로 반찬을 집는 손
- ⛔ **금지**: 카메라를 보고 웃는 정면 모델 컷, 스톡사진 느낌의 연출된 포즈, 알아볼 수 있는 특정 인물의 얼굴
- 3장 중 **최소 1장은 사람의 흔적(손·뒷모습·군중)이 들어가야 한다.** 4장 전부 무인 정물이면 실패다.

🚨 **`X only` 구문은 프레임 안에 그 부위밖에 없는 접사에서만 쓴다 (v5.3 신설 — 위반 시 신체 결손이 생긴다).**

`only` 는 생성 모델에게 "**열거된 것만 그리고 나머지는 지워라**"로 읽힌다. 손이 화면을 가득 채우는 매크로 컷에서는 의도대로 동작하지만, **몸통이 보이는 인물**에 붙이면 열거되지 않은 부위가 실제로 사라진다.

> 2026-08-19 #139 실측: `The person is seen from behind, shoulders and one hand only, no face visible` → **머리와 목이 통째로 없는 인물**이 생성돼 발행 전 사용자가 발견(Post 3461, media 3478 → 3486으로 교체). 같은 프롬프트의 나머지 1장은 정상이었고, `seen from behind` 만 쓴 #138 골목·#140 부산역 이미지도 전부 정상이었다. **문구가 유일한 변수였다.** 이 표현은 舊 384행이 권장 표현으로 명시하고 있었으므로, 원인은 지침서 자체였다.

**프레임 안에 몸통이 보이는 인물에는 반드시 아래 형식을 쓴다:**

```
a complete and anatomically correct adult figure seen from behind, the whole back of their head and hair clearly visible above the collar, neck and shoulders fully intact and connected, face simply turned away from the camera so it cannot be seen
```

핵심은 **"얼굴을 지워라"가 아니라 "얼굴을 돌려라"** 로 지시하는 것이다. 부재(no face)가 아니라 방향(turned away)으로 표현해야 모델이 부위를 삭제하지 않는다.

- ✅ **접사 전용 (손·발만 프레임에 있을 때)**: `hands only, no faces visible`
- ✅ **몸통이 보이는 인물**: `seen from behind, the back of the head clearly visible, face turned away from the camera`
- ✅ **군중**: `all seen from behind or in profile, motion blurred, faces not recognisable` — `only` 를 쓰지 않는다
- ⛔ **금지**: `shoulders and one hand only` · `torso only` · `upper body only` 처럼 **몸의 일부를 `only` 로 한정하는 모든 표현**

**④ 텍스트 정책 — `no text` 전면 금지를 해제한다**

**한글 간판은 외국인에게 가장 강력한 '한국' 신호**인데, 舊 규칙은 이것을 통째로 금지했다. 이제 구분해서 지정한다.

- ✅ **허용**: 원경·중경의 **간판 덩어리**, 초점 밖으로 흐려진 한글 네온, 형태로만 읽히는 글자 — `blurred Hangul neon signage in the background`, `stacked Korean signboards rendered as soft out-of-focus colour and letterform shapes`
- ⛔ **금지**: 화면 안 UI 텍스트, 문서·자막·안내문의 **읽히는 문단**, 브랜드 로고 — `no readable paragraphs, no UI text, no logos`
- 핵심 피사체 위에 **초점 맞은 글자를 올리지 않는다** (깨진 글자로 생성됨). 글자는 **배경·주변부·아웃포커스**에만 둔다.

**⑤ 그 위에 얹는 촬영 조건 (기존 유지)**

- **시간·날씨·빛** — 한국 특유의 빛을 명시. 예: "late afternoon cinematic side lighting", "rain-slicked asphalt reflecting colorful neon at night", "hazy blue hour over apartment towers"
- **카메라·렌즈** — 예: "shot on Leica M11 with 35mm f/1.4 lens", "Sony A7R V with 90mm macro lens"
- **구도·깊이감** — 예: "intense shallow depth of field", "low-angle dramatic perspective showing leading lines"
- **텍스처·디테일** — 예: "glistening condensation on a cold green soju bottle", "rising steam and fine texture of red chili oil"
- **제외 조건 (v5.3 표준 세트)** — `no readable paragraphs, no UI text, no logos, no watermark, no 3d render, no anime style, no posed model looking at camera, no generic stock photo look`
  **인물이 들어가는 컷에는 아래를 반드시 덧붙인다** — `complete natural human anatomy with no missing or cropped body parts, no headless figures, no floating clothing`
  ⚠️ 이 세트에 **`no people` 과 `no text` 는 들어 있지 않다.** 무인·무텍스트가 정말 필요한 정물 컷에서만 개별적으로 추가한다.

> 아래 예시는 모두 **한국 지표 2개 이상 + 사람의 흔적 또는 아웃포커스 한글**을 포함하도록 v4.1에서 다시 쓴 것이다. 舊 예시(무인·무텍스트 정물)는 Nowhere 테스트를 통과하지 못해 폐기했다.

**프롬프트 예시 (Food 카테고리) — 지표: 스테인리스 반상기 + 반찬 + 소주병 + 자르는 손**

```
A boiling stone pot of kimchi-jjigae still bubbling hard, set on a scratched stainless steel table inside a cramped Korean tavern. Around it, six small side dishes in shallow white saucers, a lidded silver stainless rice bowl, and flat silver metal chopsticks resting on a paper napkin. A cold green soju bottle sweating with condensation and two small shot glasses beside it. A pair of hands enters the frame from the right holding kitchen scissors, cutting a strip of pork belly directly in the pot, hands only, no faces visible. Warm late afternoon window light rakes across the broth surface, blurred Hangul signage glowing faintly through the window behind. Shot on Sony A7R V with 90mm macro lens, eye-level close-up, cinematic shallow depth of field, hyperrealistic food photography capturing rising steam and the fine texture of red chili oil, no readable paragraphs, no UI text, no logos, no watermark, no 3d render, no anime style, no posed model looking at camera
```

**프롬프트 예시 (Travel 카테고리) — 지표: 간판 더미 + 플라스틱 스툴 + 전선 + 행인 실루엣**

```
A narrow alleyway in Euljiro, Seoul at blue hour, both walls stacked from ground to roofline with dense layered Korean signboard panels glowing in red, yellow and green neon, the lettering soft and out of focus so it reads as colour and letterform shapes rather than words. Tangled overhead power lines cross the strip of sky. Blue and orange plastic stools and a folding table sit outside a tiny restaurant, a corrugated metal shutter half rolled down next door. Two silhouetted figures walk away from the camera deeper into the alley, seen from behind, slightly motion blurred. The ground is wet and mirrors the neon. Dramatic blue hour lighting with warm gold neon highlights, shot on Leica M11 with 35mm f/1.4 lens, low-angle perspective showing strong leading lines into the alley, crisp metallic and concrete textures, ultra realistic documentary street photography, no readable paragraphs, no UI text, no logos, no watermark, no 3d render, no anime style
```

**프롬프트 예시 (Culture 카테고리) — 지표: 창호지 문살 + 기와 처마 + 작업하는 손**

```
An extreme close-up of two hands folding a colourful silk Bojagi wrapping cloth on the polished dark wood floor of a quiet hanok room, hands only, no faces visible, fingers pressing a sharp crease into the fabric. Detailed silk texture with subtle satin sheen and traditional patchwork seams. Behind them, a sliding paper screen door with a fine wooden lattice grid filters warm morning sunlight into soft geometric patches across the floor, and through the open doorway the upward curve of a tiled roof eave is visible against a pale sky. Shot on Fujifilm X-T5 with 35mm lens, shallow depth of field focused on the fingertips and the knot, warm and quiet mood, no readable paragraphs, no UI text, no logos, no watermark, no 3d render, no anime style
```

**프롬프트 예시 (Lifecycle 카테고리) — 지표: 돌상 오브젝트 + 한복 옷고름 + 아이 손**

```
A low three-quarter view across an elaborate Korean doljanchi first-birthday table, foreground filled with neat towers of pastel rainbow rice cakes on brass plates, a wooden thread spool, a calligraphy brush and a brass bowl arranged in a row on a richly embroidered silk cloth. At the edge of the frame a small child's hand in a bright hanbok sleeve with a long silk ribbon tie reaches toward the brush, hand only, no face visible, slight motion blur on the reaching arm. Soft diffused daylight from a large window rakes across the silk texture. Shot on Canon EOS R5 with 50mm f/1.2 lens, crisp focus on the symbolic objects with soft bokeh behind, cheerful vibrant mood, no readable paragraphs, no UI text, no logos, no watermark, no 3d render, no anime style
```

**프롬프트 예시 (v4.1 신설 — 대중교통·생활 장면, #137류 주제의 올바른 처리)**

舊 #137은 "텅 빈 지하철 객실"을 그려 Nowhere 테스트에 걸렸다. 같은 주제를 이렇게 쓴다.

```
Interior of a crowded Seoul metro car in the evening, shot down the length of the aisle. Rows of silver stainless bench seats on both sides, a block of bright pink priority seats clearly visible on the left with a printed pregnant-woman pictogram above them, blue triangular hanging strap handles swaying in rows, a wall-mounted route map panel and a small advertising screen glowing above the door. Standing passengers fill the middle of the car, all seen from behind or in profile, several of them motion blurred, faces not visible. One seated passenger's hands hold a sealed convenience-store rice triangle in its plastic film. Cool white LED ceiling light mixed with the warm glow of the ad screen, dark tunnel rushing past the tinted windows. Shot on Sony A7R V with 35mm lens, eye-level documentary perspective, crisp metal and fabric textures, ultra realistic street photography, no readable paragraphs, no UI text, no logos, no watermark, no 3d render, no anime style, no posed model looking at camera
```

**프롬프트 예시 (기기·시설 피사체 — 피사체 정확성 + v4.1 한국성 보강):**

기기 접사는 Nowhere 테스트에 걸리기 가장 쉬운 유형이다. **주변부에 한국 주거 지표(복도 창밖 아파트 동, 현관 단차, 벗어 둔 신발)와 조작하는 손을 반드시 함께 넣는다.**

```
A close-to-medium shot of a beige steel apartment entrance door in a Seoul apartment corridor, fitted with an authentic modern Korean digital door lock (Gateman/Samsung SDS style) — a tall vertical rectangular brushed-silver metal panel mounted flush on the door, a touch-sensitive numeric keypad glowing faintly blue in the upper section, a slim horizontal push-down lever handle integrated into the lower section of the same panel, absolutely no separate round doorknob. A hand enters from the right and presses the keypad, hand only, no face visible. Through the corridor window behind, out-of-focus grey concrete apartment towers with painted building numbers rise against a hazy sky. A pair of shoes sits on the raised threshold at the base of the door. Soft afternoon light casting gentle shadows across the door, shot on Sony A7R V with 50mm f/1.8 lens, eye-level composition centered on the lock panel, crisp brushed metal and matte painted steel texture, no readable paragraphs, no UI text, no logos, no watermark, no 3d render, no anime style
```

**프롬프트 예시 (v3.3 — 두 상태 비교형 히어로):**

글의 핵심이 'A일 때와 B일 때가 다르다'인 경우, 히어로는 **두 상태를 한 프레임에 나란히** 넣으면 썸네일만으로 주제가 읽힌다.

```
A clean straight-on wide photograph of two screens side by side on a low table in a Korean apartment living room, the floor a warm honey-toned ondol laminate with a floor cushion beside the table. On the left, a flat-screen television shows a scene in which one object is covered by a coarse grey pixelated mosaic patch, the individual mosaic squares clearly larger than the surrounding picture detail. On the right, a tablet propped on a stand shows the exact same scene completely sharp with no mosaic at all. Identical framing and identical colours on both screens so the single difference is obvious at a glance. Through the sliding balcony door behind, out-of-focus grey apartment towers and a laundry drying rack are visible. Soft diffused daylight, shot on Canon EOS R5 with 50mm f/1.2 lens, symmetrical eye-level composition, crisp screen glass and matte surface textures, no readable paragraphs, no UI text, no logos, no watermark, no 3d render, no anime style
```

ℹ️ **(v4.1)** 舊 버전은 "bright modern living room"이라 어느 나라 거실인지 알 수 없었다. **온돌 바닥재·좌식 쿠션·베란다 빨래건조대·아파트 동** 네 가지를 넣어 장소를 못 박았다.

**프롬프트 예시 (v3.4 — 두 상태 비교형 히어로, 실사 풍경형):**

화면·소품이 아니라 **풍경 자체가 두 상태**인 글에서는, 하나의 실제 장면 안에 두 상태가 공존하는 구도를 찾으면 합성 느낌 없이 대비가 만들어진다.

```
A high aerial drone photograph of a wide Korean expressway just outside Seoul on a public holiday morning, showing two opposite traffic states in one single frame. The outbound carriageway on the right side is completely jammed bumper to bumper with hundreds of cars crawling in every lane, stretching unbroken all the way to the horizon. The inbound carriageway on the left side of the same central barrier is almost totally empty, with only two or three lone cars on wide open asphalt. Identical road width and identical lighting on both sides so the contrast is obvious at a glance, a low concrete median barrier and green roadside trees separating them, clusters of tall grey Korean apartment towers and forested hills in the hazy background, blue-painted bus-only lane markings running along the inside edge of the jammed carriageway, soft early-autumn morning light, shot on Sony A7R V with 70mm lens, high three-quarter aerial perspective looking down the length of the road, crisp asphalt and car roof textures, ultra realistic documentary aerial photography, no readable paragraphs, no UI text, no logos, no watermark, no 3d render, no anime style
```

ℹ️ **(v4.1)** 이 구도는 **아파트 단지 + 파란 버스전용차선**이라는 지표가 이미 들어 있어 Nowhere 테스트를 통과한다. 원경 항공 컷은 지표를 크게 잡아야 썸네일에서 살아남는다.

**프롬프트 예시 (v4.1 — 두 상태 비교형 히어로, 정물 대비형 / #137 개선판):**

두 상태를 **같은 평면 위 두 개의 사물**로 놓으면 썸네일에서 가장 잘 읽힌다. 다만 정물 대비형은 배경이 비어 Nowhere가 되기 쉬우므로, **배경에 한국 지표와 사람의 흔적을 반드시 깔아 준다.**

```
A straight-on wide photograph of the interior of a Seoul metro train car, centered on a silver stainless steel bench seat with slim vertical dividers, and exactly two items placed side by side on that seat. On the left, a tall sealed transparent plastic cup of iced coffee with a domed lid and heavy condensation running down the cup. On the right, an open brown paper takeout bag with hot fried chicken spilling out of the top and faint steam rising from it. Identical lighting and identical framing on both items so the contrast between sealed-and-cold and open-and-hot is obvious at a glance. Behind the seat, a block of bright pink priority seats with a printed pictogram above them, a wall-mounted route map panel, vertical stainless grab poles and a row of blue triangular hanging strap handles. Further down the car, two standing passengers seen from behind, slightly motion blurred, faces not visible. Cool white LED ceiling lighting, dark tunnel rushing past the tinted windows. Shot on Sony A7R V with 35mm lens, eye-level symmetrical composition, crisp metal, plastic and paper textures, ultra realistic documentary photography, no readable paragraphs, no UI text, no logos, no watermark, no 3d render, no anime style, no posed model looking at camera
```

ℹ️ **(v4.1)** 2026-08-18 채택본은 이 프롬프트의 舊 버전(`No people at all` + 텅 빈 객실)으로 만들어졌고, 결과물은 도쿄·타이베이 지하철과 구분되지 않았다. **분홍 임산부 배려석·노선도 패널·뒷모습 승객** 세 가지를 추가한 것이 이 개정판의 핵심이다.

**이미지 3장의 역할 분담 (v4.1 개정):**

- **이미지 1 (글 도입부)**: 글의 무대가 되는 **실제 한국 공간의 생활 장면** — 사람·간판·거리가 살아 있는 와이드 컷. 텅 빈 공간이 아니라 **쓰이고 있는 공간**을 그린다. 핵심 피사체는 이 안에도 정확한 형태로 들어가야 한다.
- **이미지 2 (글 중반)**: 핵심 소재의 클로즈업 — 음식 디테일, 문화 오브젝트, **행위 중인 손**. 한국 지표(스테인리스 식기·반찬·한복 소매 등)를 프레임 안에 반드시 포함한다.
- **이미지 3 (글 후반)**: 감성적 마무리 — 저녁빛, 계절감, 여운. **계절 지표(벚꽃·은행잎·단풍·장마)나 한강·아파트 스카이라인** 중 하나를 넣어 장소를 못 박는다.
- **(hasStockImg인 경우) 히어로 이미지**: 제목을 가장 직관적으로 시각화한 컷 — 썸네일에서 주제가 한눈에 읽히되, **한국 지표가 최소 2개 보여야 한다.** 썸네일 크기로 줄였을 때 "한국"이 안 읽히면 다시 만든다.

⚠️ **(v3.4) 히어로와 본문 이미지의 소재가 겹치지 않게 배분한다.** 히어로가 이미 A를 다뤘다면 본문 3장은 B·C·D를 맡는다. 같은 피사체가 두 번 나오면 글이 단조로워진다.

⚠️ **(v4.1) 4장의 '한국 지표'가 서로 달라야 한다.** 4장 모두 지하철 실내이거나 4장 모두 음식 접사면, 각각은 한국적이어도 글 전체는 단조롭다. 거리·실내·접사·계절 중 최소 3개 영역을 섞는다.

⚠️ **(v4.1) 3장 중 최소 1장에는 사람의 흔적(손·뒷모습·군중)이 들어가야 한다.** 전부 무인 정물이면 글이 박물관 도록처럼 보인다.

#### 3-3B. 나쁜 예 → 좋은 예 (2026-08-18 #137 실전 자기비판)

v4.1 한국성 규칙만으로는 부족했다는 증거다. 아래 4장은 전부 "정확하고 한국적이지만 아무 일도 일어나지 않는" 이미지였다.

| 이미지 | v4.0/v4.1 산출 (통과했지만 무난) | v5.0 재설계 (사건 + 한국성) |
|---|---|---|
| 히어로 | 스테인리스 좌석 위 아이스커피와 치킨 봉투가 **놓여 있음** — 상태 서술 | 치킨 봉투에서 **김이 막 피어오르는 순간**, 분홍 임산부 배려석에 앉은 승객이 **고개를 막 돌린다**(뒷모습). 유일한 밝은 지점은 김이 오르는 봉투 입구 |
| 이미지1 | 삼각김밥·바나나우유가 좌석에 **놓여 있음** | 손이 삼각김밥 포장 **탭을 뜯는 중**, 비닐이 반쯤 벌어지고 김이 서린 우유병이 옆에서 **미끄러지려 기울어져 있다** |
| 이미지2 | 텅 빈 심야 객실 통로 — **⑥ 범용 은유 위반(텅 빈 공간)** | 만원 객실, 승객 **여러 명이 동시에 휴대폰을 들어 한 방향을 향하고** 있다(전부 뒷모습). "벌금이 아니라 시선"을 그대로 시각화 |
| 이미지3 | KTX 트레이에 도시락이 **놓여 있음** | 트레이 위 도시락 뚜껑이 **막 열리며 김이 오르고**, 창밖 논이 흐르는 가운데 젓가락을 **집으려는 손**이 프레임에 들어온다 |

#### 3-3C. 프롬프트 조립 체크리스트 (전송 전 8항목 자가 점검)

전송 직전 아래 8개가 프롬프트 문장 안에 실제로 들어 있는지 센다. **하나라도 비면 전송하지 않는다.**

1. 훅 문장 (한국어 주석으로 상단에 기록)
2. 사건 동사 — 뜯는 / 기울어진 / 김이 오르는 / 고개를 돌리는 / 흘러내리는
3. 물리량 번역 — 길이·높이·개수의 구체적 배수 (해당하는 글만)
4. **한국 지표 2개 이상** — 3-3 ② 표에서 물리적 형태로 (KoreaPlug 고유 항목)
5. 인물 흔적 — 손·뒷모습·군중 중 하나 (3장 중 최소 1장 필수)
6. 시선 유도점 1개 — `the only bright accent is ...`
7. 카메라·렌즈·빛
8. 제외 조건 세트 (3-3 ⑤ 말미 문장 그대로 — `no people`·`no text` 금지)

**최종 통과 조건 = ① 한 문장 테스트(사건) + ⑦ 썸네일 3초 테스트 + Nowhere 테스트(한국성).** 셋 중 하나라도 걸리면 채택하지 않는다.

또한 각 이미지에 대한 **영문 alt text** (60자 내외)도 미리 작성해 둔다.

**대표이미지(Featured Image) 선정:**

생성 이미지 중 아래 기준으로 1장을 `window._featuredImgIndex` 로 지정한다 (hasStockImg로 히어로를 생성했다면 일반적으로 히어로가 대표이미지).

- 글 제목·카테고리·한줄 요약을 검색 엔진 사용자가 처음 보게 될 썸네일로 상상했을 때 가장 직관적으로 내용을 전달하는 이미지
- 와이드 구도 + 선명한 피사체 + 글의 핵심 키워드를 시각화한 장면이 우선
- 음식·체험 글은 클로즈업이 더 클릭률이 높을 수 있음
- 판단 근거를 한 줄로 메모해 둔다

```javascript
window._featuredImgIndex = 0; // 0=이미지1, 1=이미지2, 2=이미지3 (히어로 생성 시 히어로 우선)
window._featuredReason = "이유";
```

---

### STEP 4: 글 구조 분석 → 이미지 삽입 위치 3곳 결정

STEP 3-1에서 확보한 `window._rawContent`(반드시 raw)를 사용한다.

⛔ **(v3.4) 헤딩 '개수' 분위(1/4·2/4·3/4)를 쓰지 않는다.** 헤딩이 문서 후반에 몰려 있으면 이미지가 전부 뒤쪽으로 쏠린다 (2026-08-12 실측: h2 8개의 개수 분위가 문서의 59%·74%·87% 지점에 해당 — 앞 절반이 통째로 빔). 대신 **h2의 문자 위치를 뽑아, 목표 비율에 가장 가까운 h2를 고른다.**

```javascript
const c = window._rawContent;
const h2 = []; const re = /<h2[^>]*>([\s\S]*?)<\/h2>/g; let m;
while ((m = re.exec(c)) !== null) h2.push({i: m.index, t: m[1].replace(/<[^>]*>/g, '').replace(/[?&=]/g, ' ').slice(0, 45)});
window._h2 = h2;
const L = c.length;
// 목표 비율(문자 기준) — 도입 / 중반 / 후반
const targets = [0.10, 0.45, 0.72];
window._insertPoints = targets.map(t => {
  const want = L * t;
  return h2.reduce((a, b) => Math.abs(b.i - want) < Math.abs(a.i - want) ? b : a).i;
});
// 눈으로 확인: 어떤 섹션 앞에 들어가는지 제목까지 본다
h2.map((x, n) => n + ' ' + Math.round(x.i / L * 100) + '% @' + x.i + ' :: ' + x.t).join('\n')
 + '\n--> picked: ' + window._insertPoints.join(', ')
```

⚠️ **선택된 h2의 제목을 반드시 눈으로 확인하고, 그 섹션 주제와 맞는 이미지를 배정한다.** 비율이 맞아도 FAQ·결론 섹션 앞이면 한 칸 당긴다. 같은 위치가 중복 선택되면 인접 h2로 분산한다. 자동 계산이 어색하면 `window._insertPoints = [h2[a].i, h2[b].i, h2[c].i]` 로 **인덱스를 손으로 지정**한다.

ℹ️ **(v4.0) `hasStockImg`로 히어로를 만드는 글은 글 맨 위(0%)가 히어로로 이미 채워진다.** 이때 본문 3장의 목표 비율은 `[0.10, 0.45, 0.72]` 대신 **`[0.30, 0.55, 0.72]`** 로 뒤로 밀어 잡는 편이 분포가 고르다 (2026-08-18 #137 실측: 히어로 2% + 본문 29%/47%/60%로 균등 배치 성공).

(v3) `genCount`가 3 미만이면 `window._insertPoints`에서 앞의 genCount개 위치만 사용한다 — 우선순위는 STEP 2의 이미지 1→3→2 순서를 따른다.

(v3.2) 다만 **이미 이미지가 있는 글에 1~2장을 보충하는 경우**에는 기계적으로 도입부를 쓰지 말고, 기존 이미지들의 본문 내 위치(index)를 먼저 구해 **이미지가 가장 오래 비어 있는 구간**의 헤딩을 고른다. 보충의 목적은 개수 채우기가 아니라 공백 메우기다.

ℹ️ **(v3.4) raw 위치와 렌더 후 화면 위치는 다르다.** ez-toc 목차는 렌더 시점에 첫 h2 앞으로 삽입되므로, raw에서 첫 h2 바로 앞에 넣은 이미지는 화면에서 **본문 도입 → 이미지 → 목차** 순으로 보인다. 이 배치는 정상이며 문제가 아니다. 최종 위치는 STEP 7.5에서 렌더 기준으로 실측한다.

---

### STEP 5: Google Flow에서 이미지 생성 및 캡처 (v4.0 / v5.5)

✅ **(v5.5) STEP 0-3에서 이미 Flow 탭을 열고 세션을 확인했으므로 그 탭을 그대로 이어 쓴다.** 새 탭을 열거나 재이동하지 않는다.

프로젝트 URL (참조용): `https://labs.google/fx/ko/tools/flow/project/6a6af995-4d64-4bbb-8e97-4be7aa267e6d`

⚠️ **(v5.5) 이 단계 도중에 세션이 끊겨 계정 선택·OAuth 화면이 뜨면** STEP 0-3의 만료 조치를 그대로 적용한다 — 클릭하지 말고, **STEP 8의 「중단 보고」 양식**으로 그때까지의 산출물(대상 글·분류·프롬프트 전문·삽입 위치)을 남기고 종료한다.

#### 5-1. 생성 설정 확인 (최초 1회)

하단 입력창 우측의 설정 칩(`Nano Banana 2 ▭ x2`)을 클릭해 아래 4개를 확인한다. 이미 맞으면 그대로 닫는다.

- 모드: **이미지** (동영상 아님)
- 비율: **16:9**
- 모델: **Nano Banana 2**
- 장수: **x2** — 패널 하단에 "생성 시 0크레딧이 사용됩니다" 표시 확인

⛔ **`에이전트` 버튼은 사용하지 않는다.** 켜면 프롬프트를 재해석해 의도와 다른 결과가 나온다.

#### 5-2. 프롬프트 연속 제출 (v4.2 — 대기하지 않는다)

⛔ **한 장씩 만들고 기다리는 방식을 금지한다.** STEP 3에서 완성해 둔 프롬프트 **전부(본문 3개 + 히어로 1개)를 연속으로 제출**한 뒤, 대기는 마지막에 **한 번만** 한다.

제출 1건은 `browser_batch` **1회 호출**로 처리한다:

```
browser_batch([
  {computer: left_click  → 입력창 (약 700, 622)},
  {computer: type        → 프롬프트 전문},
  {computer: left_click  → 전송 화살표 (약 1008, 657)},
  {computer: wait 3},
  {computer: screenshot scale 0.4}
])
```

스크린샷으로 **진행률 카드가 새로 2장 생겼는지**만 확인하고, 완료를 기다리지 말고 **곧바로 다음 프롬프트를 같은 방식으로 제출**한다. 제출 직후 입력창은 비워져 있으므로 바로 입력이 가능하다.

✅ **(2026-08-18 실측) 병렬 진행이 확인됐다** — 1차 제출분이 74%일 때 2차 제출분이 13%로 함께 돌았고, 4장이 **약 60초에 모두 완료**됐다. 프롬프트 4개(=이미지 8장 후보)까지 같은 방식으로 밀어 넣는다.

**전부 제출한 뒤 대기 — 이것도 1회 호출로 묶는다:**

```
browser_batch([
  {computer: wait 10}, {computer: wait 10}, {computer: wait 10},
  {computer: screenshot scale 0.45}
])
```

진행률이 99%에서 멈춘 것처럼 보여도 디코딩에 5~8초가 더 걸린다. 스크린샷에 **모든 카드가 실제 이미지로 바뀐 것**을 확인한 뒤 5-3으로 간다. 개별 카드가 **90초를 넘기면** 그 건만 재제출한다 (나머지는 그대로 둔다).

ℹ️ Gemini와 달리 **첫 클릭이 씹히지 않는다.**

#### 5-3. 채택본 선택 (v4.2 — 그리드 스크린샷 1장으로 판정)

⛔ **에디터 뷰에 들어가지 않는다.** 후보를 하나씩 클릭해 여는 것이 舊 실행에서 20회 왕복을 잡아먹은 원인이다.
5-2 마지막 스크린샷 **한 장에 모든 후보가 나란히 보이므로**, 그 화면에서 바로 판정한다. 세부가 안 보이면 `computer: zoom` 으로 해당 카드 영역만 확대한다 (에디터 진입보다 훨씬 싸다).

아래 기준으로 각 프롬프트의 2장 중 1장을 고른다.

- 핵심 피사체가 **실제 한국 형태**와 일치하는가 (STEP 3-2 기준)
- 🚨 **(v4.1) Nowhere 테스트**: 이 사진에서 한국 지표를 지우면 다른 나라 사진이 되는가? **그렇다면 둘 다 탈락**이다. 채택하지 말고 3-3 ②의 지표 표에서 요소를 더 뽑아 프롬프트를 다시 쓴다.
- 🚨 **(v4.1) 썸네일 테스트**: 이미지를 손톱만 하게 줄여도 "한국"이 읽히는가? 지표가 원경에만 흐릿하게 있으면 썸네일에서 사라진다.
- 글 제목을 아는 독자가 봤을 때 "글 내용과 맞는 이미지"라고 느낄 것인가
- 왜곡된 손·깨진 글자·서구식 형태 등 이상 요소가 없는가. **글자가 초점 안에 들어와 깨졌다면 탈락** — 배경·아웃포커스로 밀어 다시 만든다
- 🩻 **(v5.3) 해부 검사 — 인물이 있는 후보는 이것을 먼저 본다.** 머리·목·팔·다리 중 **없는 부위가 있는가?** 옷만 있고 그 안이 비어 있는가? 손가락이 6개인가? **하나라도 해당하면 즉시 탈락**이며, 다른 기준이 아무리 좋아도 채택하지 않는다. 후보 2장이 모두 걸리면 3-3 ③의 「몸통이 보이는 인물」 형식으로 수정 재생성한다. 그리드 썸네일에서 인물이 작아 판별이 어려우면 **그 카드만 `computer: zoom` 으로 확대해 확인한다** — 이 항목만은 확대 비용을 감수한다.
- **둘 다 부적합할 때만** 잘못된 부분을 물리적으로 더 명시한 **수정 프롬프트**로 재생성한다 (동일 프롬프트 재전송 금지). 수정 1회 후에도 어긋나면 해당 이미지 건너뜀.

ℹ️ 2장 중 고르는 구조라 舊 루틴의 "재시도 1회" 규정이 실제로 발동할 일은 거의 없다.

#### 5-4. 캡처 — 그리드에서 일괄 (v4.2 · 에디터 진입 폐지)

Flow 워터마크(✦)는 이미지 **모서리가 아니라 안쪽**, 상대좌표 **(0.925W, 0.875H)** 에 고정돼 있다 (2026-08-18 실측: 1376×768 기준 중심 ≈ (1273, 672), 크기 ≈ 56×56. 프로젝트 내 과거 이미지들도 동일 상대좌표). 따라서 **`cropRight = 150` 으로 우측만 잘라내면 세로 해상도 손실 없이 제거된다** → 1226×768.

✅ **(v4.2 실측) 그리드 썸네일은 표시폭이 318px여도 `naturalWidth` 는 원본 1376×768 그대로다.** 따라서 **에디터에 들어가지 않고 그리드에서 채택본들을 한 번에 캡처한다. 4장 실측 439ms, 호출 1회.**

그리드는 **최신순**이므로 방금 생성한 것들이 앞쪽에 온다. 5-3에서 고른 채택본의 그리드 인덱스를 `pick` 배열에 적어 넣는다 (예: 프롬프트1의 2장이 0·1번, 프롬프트2가 2·3번일 때 각각 앞쪽을 골랐다면 `[0, 2]`).

```javascript
// v4.2 일괄 캡처 — 최상위 await 사용, 1회 호출로 끝낸다
const pick = [0, 2, 4, 6];              // ← 5-3에서 채택한 그리드 인덱스 (순서 = 본문1,2,3,히어로)
const names = ['_img1', '_img2', '_img3', '_imgHero'];
const all = Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 400);
const out = [];
for (let k = 0; k < pick.length; k++) {
  const img = all[pick[k]];
  const cropRight = 150, cropBottom = 0;   // Flow 워터마크는 우측 크롭으로 제거
  const c = document.createElement('canvas');
  c.width  = img.naturalWidth  - cropRight;
  c.height = img.naturalHeight - cropBottom;
  c.getContext('2d').drawImage(img, 0, 0, c.width, c.height, 0, 0, c.width, c.height);
  const blob = await new Promise(r => c.toBlob(r, 'image/webp', 0.85));
  window[names[k]] = await new Promise(r => { const rd = new FileReader(); rd.onloadend = () => r(rd.result); rd.readAsDataURL(blob); });
  out.push(names[k] + ' ' + c.width + 'x' + c.height + ' ' + Math.round(blob.size / 1024) + 'KB');
}
out.join(' | ')
```

⚠️ **그리드 인덱스는 반드시 5-3 스크린샷과 대조해 확인한다.** 잘못 집으면 엉뚱한 옛 이미지가 캡처된다. 확신이 서지 않으면 캡처 전에 아래로 인덱스와 실물을 맞춰 본다:

```javascript
Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 400)
  .slice(0, 10).map((i, n) => n + ' ' + i.naturalWidth + 'x' + i.naturalHeight
  + ' @' + Math.round(i.getBoundingClientRect().top)).join('\n')
```

✅ **(v4.0 실측) Flow는 이미지를 `labs.google` 동일 출처로 서빙하므로 canvas taint가 발생하지 않는다.** 舊 v3.4~v3.5의 `SecurityError: canvas has been tainted` 복구 절차(URL 릴레이·IMGTAB 탭 생성·`location.href` 이동)는 **전부 불필요하며 삭제됐다.**

⛔ **(v4.2) 그리드를 떠나지 않는다.** 舊 v4.0은 "그리드 ↔ 에디터 이동은 SPA라 `window._img*` 가 보존된다"고 적어 두었는데, 사실이긴 하지만 **그렇다고 들어가도 된다는 뜻은 아니다.** 그리드로 돌아오면 **이미지가 지연 로딩으로 다시 붙는 데 20초 이상**이 걸리고(0and1Life 2026-08-18 실측: 콜드 로드 6초·14초 시점 0개 → 26초에 18개), 왕복 호출도 이미지당 6~7회가 추가된다. 캡처·판정 모두 그리드에서 끝나므로 **에디터에 들어갈 이유가 없다.**
**주소창 navigate·새로고침은 절대 금지** — `window._img*` 가 전부 날아간다.

위 한 번의 호출로 `_img1`·`_img2`·`_img3`·`_imgHero` 가 모두 채워진다. **이미지마다 5-2로 되돌아가는 반복은 v4.2에서 사라졌다.**

---

### STEP 6: Flow 탭에서 WP admin 새 창 열기 → postMessage로 이미지 업로드

**핵심:** Flow 탭에서 WP REST API를 직접 fetch하면 CORS로 차단된다. 기존 WP admin 탭에 대한 window 참조도 얻을 수 없다. 유일하게 작동하는 방법은 Flow 탭에서 `window.open()`으로 새 WP admin 창을 열고 그 참조에 postMessage를 보내는 것이다.

**6-1. Flow 탭에서 새 WP admin 창 열기:**

⛔ **(v3.3) 두 번째 인자 `'_blank'` 를 넘기지 않는다.** `'_blank'` 로 열린 탭은 Chrome MCP 탭 그룹 **밖에** 생성되어 `tabs_context_mcp` 목록에 나타나지 않고, 그 결과 6-2의 리스너 주입이 불가능해져 업로드 경로 전체가 막힌다.

```javascript
// Flow 탭에서 실행 — 새 tabId가 생성됨
window._wpWin = window.open('https://koreaplug.com/wp-admin/media-new.php');
window._wpWin ? 'window opened' : 'blocked'
// 6~8초 대기 후 tabs_context_mcp로 새 tabId 확인
```

**복구 절차** — 이미 `'_blank'` 로 열어 탭이 목록에 없다면, Flow 탭에서 아래를 실행해 닫고 위 코드로 다시 연다. `window._img*` 는 Flow 탭 heap에 그대로 남아 있으므로 **이미지 재생성은 필요 없다.**

```javascript
window._wpWin.close();
window._wpWin = window.open('https://koreaplug.com/wp-admin/media-new.php');
'reopened:' + !!window._wpWin
```

**6-2. 새 WP admin 탭에 postMessage 리스너 주입:**

⚠️ `media-new.php` 에는 **`wpApiSettings` 가 정의되어 있지 않다.** 리스너를 붙이기 전에 REST nonce를 먼저 확보해 `window._nonce` 에 담고, 리스너 안에서는 `wpApiSettings.nonce` 대신 `window._nonce` 를 쓴다:

```javascript
const s = Array.from(document.querySelectorAll('script:not([src])')).map(x => x.textContent).join('\n');
const m = s.match(/apiFetch\.createNonceMiddleware\(\s*["']([a-f0-9]+)["']/);
window._nonce = m ? m[1] : (window.wpApiSettings ? wpApiSettings.nonce : null);
'nonce: ' + (window._nonce ? 'ok' : 'MISSING')
```

새로 열린 WP admin 탭에서 실행:

```javascript
window._uploadedIds = [];
window._upErrors = [];
window.addEventListener('message', async (e) => {
  if (!e.data || !e.data.dataUrl) return;
  const {dataUrl, filename, altText} = e.data;
  try {
    const arr = dataUrl.split(','), mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    const u8 = new Uint8Array(bstr.length);
    for (let i = 0; i < bstr.length; i++) u8[i] = bstr.charCodeAt(i);
    const fd = new FormData();
    fd.append('file', new Blob([u8], {type: mime}), filename);
    const res = await fetch('/wp-json/wp/v2/media', {
      method: 'POST',
      headers: {'X-WP-Nonce': window._nonce},
      body: fd
    });
    const json = await res.json();
    if (json.id) {
      await fetch('/wp-json/wp/v2/media/' + json.id, {
        method: 'POST',
        headers: {'X-WP-Nonce': window._nonce, 'Content-Type': 'application/json'},
        body: JSON.stringify({alt_text: altText})
      });
      window._uploadedIds.push({id: json.id, url: json.source_url, alt: altText, tag: filename});
    } else {
      window._upErrors.push(filename + ' >> ' + JSON.stringify(json).slice(0, 150));
    }
  } catch (err) { window._upErrors.push(filename + ' >> ' + err.message); }
});
'listener ready'
```

**6-3. Flow 탭에서 이미지 순서대로 전송 (본문용 1→2→3, 히어로가 있으면 마지막):**

✅ **(v4.2) 4건을 한 호출에 이어서 보내고, 확인은 마지막에 한 번만 한다.** postMessage는 비동기로 큐에 쌓이므로 전송 사이마다 확인할 필요가 없다. 舊 방식은 전송 4회 + 대기 4회 + 확인 4회 = 12회를 썼지만, 아래처럼 하면 **2회**로 끝난다.

```javascript
// Flow 탭에서 1회 호출 — 4장 연속 전송 후 마지막에만 대기
const send = (d, f, a) => window._wpWin.postMessage({dataUrl: d, filename: f, altText: a}, 'https://koreaplug.com');
send(window._img1,    'koreaplug-SLUG-1.webp',    'ALT_1');
send(window._img2,    'koreaplug-SLUG-2.webp',    'ALT_2');
send(window._img3,    'koreaplug-SLUG-3.webp',    'ALT_3');
send(window._imgHero, 'koreaplug-SLUG-hero.webp', 'ALT_HERO');   // hasStockImg인 경우만
await new Promise(r => setTimeout(r, 9000));
'sent 4'
```

그 다음 WP admin 탭에서 **한 번만** 확인한다 (아래 확인용 스니펫). 개수가 모자라면 부족한 건만 다시 보낸다.

<details><summary>참고 — 舊 v4.0의 개별 전송 방식 (문제 발생 시 절체용)</summary>

각 전송 후 6~8초 대기. 전송 사이에 WP admin 탭에서 `window._uploadedIds.length` 로 업로드 완료 확인 후 다음 전송.

```javascript
// Flow 탭에서 순서대로 실행
window._wpWin.postMessage({dataUrl: window._img1, filename: 'koreaplug-SLUG-1.webp', altText: 'ALT_TEXT_1'}, 'https://koreaplug.com');
// 6~8초 대기
window._wpWin.postMessage({dataUrl: window._img2, filename: 'koreaplug-SLUG-2.webp', altText: 'ALT_TEXT_2'}, 'https://koreaplug.com');
// 6~8초 대기
window._wpWin.postMessage({dataUrl: window._img3, filename: 'koreaplug-SLUG-3.webp', altText: 'ALT_TEXT_3'}, 'https://koreaplug.com');
// (hasStockImg인 경우)
window._wpWin.postMessage({dataUrl: window._imgHero, filename: 'koreaplug-SLUG-hero.webp', altText: 'ALT_TEXT_HERO'}, 'https://koreaplug.com');
// 6~8초 대기 후 window._uploadedIds.length가 전송한 수와 같은지 확인
```

</details>

확인용 (WP admin 탭에서):

```javascript
'up:' + window._uploadedIds.length + ' err:' + window._upErrors.length
 + ' ids:' + window._uploadedIds.map(u => u.id).join(',')
 + ' tags:' + window._uploadedIds.map(u => u.tag.replace('koreaplug-SLUG', '')).join(',')
```

⚠️ 생성 이미지 파일명은 반드시 `koreaplug-` prefix를 유지한다 — STEP 2 분류기 ④단계가 이 prefix로 데코를 확정하므로, 규칙을 어기면 다음 실행에서 그 이미지가 미분류(unknown)로 떨어진다.

ℹ️ **(v3.4) 업로드 결과를 여러 탭에 나눠 받았다면**, `window._uploadedIds` 를 합치는 대신 WP admin 탭에서 미디어를 slug로 재조회해 한곳에 모은다:

```javascript
window._media = null;
fetch('/wp-json/wp/v2/media?search=koreaplug-SLUG&per_page=20&_fields=id,slug,source_url,alt_text', {
  headers: {'X-WP-Nonce': window._nonce}
}).then(r => r.json()).then(d => { window._media = {}; d.forEach(x => window._media[x.slug] = {id: x.id, url: x.source_url, alt: x.alt_text}); });
```

---

### STEP 7: 글에 이미지 삽입·교체 및 저장

WP admin 탭에서 아래를 실행한다.

```javascript
// 1) 최신 content 가져오기 — (v3.4) context=edit 필수, rendered 폴백 금지
window._finalContent = null;
fetch('/wp-json/wp/v2/posts/POST_ID?context=edit&_fields=content,featured_media,status,date', {
  headers: {'X-WP-Nonce': window._nonce}
}).then(r => r.json())
  .then(d => {
    window._finalContent = d.content.raw;
    window._curFeatured  = d.featured_media;
    window._origStatus   = d.status;      // (v3.4) 저장 POST에 그대로 되돌려 넣는다
    window._origDate     = d.date;
  });
// 3~4초 대기 후 아래로 검증
```

```javascript
// 1.5) (v3.4 필수) raw 건강 검진 — 하나라도 어긋나면 저장하지 말고 STEP 3-1 복구 절차로
const c = window._finalContent;
'raw:' + (typeof c === 'string' ? 'ok len' + c.length : 'MISSING')
 + ' blocks:' + ((c||'').match(/<!-- wp:/g)||[]).length
 + ' ezToc:'  + ((c||'').match(/ez-toc/g)||[]).length
 + ' h2:'     + ((c||'').match(/<h2/g)||[]).length
 + ' status:' + window._origStatus + ' date:' + window._origDate + ' fm:' + window._curFeatured
```

⚠️ 삽입 위치(`window._insertPoints`)는 **이 시점의 `window._finalContent` 기준으로 다시 계산한다.** STEP 4에서 구한 인덱스는 그 사이 본문이 바뀌면 어긋난다. (계산식은 STEP 4의 문자 위치 버전을 그대로 쓴다.)

🚨 **(v5.4) 삽입 전에 각 미디어의 `media_details` 를 받아 `srcset` 을 만든다. 이것을 빼면 리사이징이 통째로 무효가 된다.**

WordPress는 업로드 시 **`medium 300` · `medium_large 768` · `large 1024` · `full 1226` WebP 사본을 이미 생성해 둔다.** 그런데 舊 마크업은 `<img src>` 하나만 넣고 `srcset` 도 `wp-image-{ID}` 클래스도 없었다. 클래스가 없으면 WordPress의 `wp_filter_content_tags()` 가 이 `<img>` 를 첨부파일과 **매핑하지 못해 srcset 자동 주입을 건너뛴다.** 결과적으로 **만들어 둔 사본이 하나도 쓰이지 않고 전 기기가 항상 full 파일을 내려받았다** (2026-08-19 실측: 본문 래퍼 788px에 1226px 파일 전송, 3편 합계 **1,836KB**).

```javascript
// 2-0) (v5.4 필수) 업로드한 미디어의 사이즈 사본을 조회해 srcset 재료를 만든다
const ids = window._uploadedIds.map(u => u.id).join(',');
const md = await fetch('/wp-json/wp/v2/media?include=' + ids + '&per_page=20&_fields=id,source_url,media_details',
  {headers: {'X-WP-Nonce': window._nonce}}).then(r => r.json());
window._srcset = {};
md.forEach(m => {
  const d = m.media_details || {}, set = {};
  Object.values(d.sizes || {}).forEach(v => { if (v.mime_type === 'image/webp') set[v.width] = v.source_url; });
  set[d.width] = m.source_url;                       // full 포함
  const widths = Object.keys(set).map(Number).sort((a, b) => a - b).filter(w => w >= 300);
  window._srcset[m.id] = {w: d.width, h: d.height, srcset: widths.map(w => set[w] + ' ' + w + 'w').join(', ')};
});
Object.entries(window._srcset).map(([k, v]) => k + ' ' + v.w + 'x' + v.h + ' n=' + v.srcset.split(',').length).join('\n')
```

⛔ `n` 이 1이면 사이즈 사본이 아직 안 만들어졌거나 WebP 변환이 꺼져 있다. 그대로 진행하지 말고 **몇 초 뒤 재조회**한다.

```javascript
// 2) 역순으로 이미지 삽입 (뒤→앞 순서로 삽입해야 인덱스가 밀리지 않음)
// ⚠️ (v5.0) 스톡이 2개 이상인 글은 2.5에서 본문 이미지 일부가 교체에 소비된다.
//    그 경우 아래 uploads에서 소비분(window._bodyUsedInReplace)만큼 뒤에서 제외하고,
//    _insertPoints도 같은 개수만 사용한다. 스톡이 1개면 소비분 0이라 그대로 진행하면 된다.
const uploads = window._uploadedIds.filter(u => !u.tag.includes('hero')); // 본문용 3장만
const pts = window._insertPoints;    // [pos1, pos2, pos3]
let c = window._finalContent;

// (v5.4) 반응형 img 빌더 — 본문 이미지는 lazy, 히어로는 eager
window._buildImg = (u, opt) => {
  const s = window._srcset[u.id];
  return '<img class="wp-image-' + u.id + '"'
    + ' src="' + u.url + '"'
    + ' srcset="' + s.srcset + '"'
    + ' sizes="(max-width: 820px) 100vw, 820px"'
    + ' width="' + s.w + '" height="' + s.h + '"'
    + ' alt="' + u.alt + '"'
    + (opt && opt.hero ? ' loading="eager" fetchpriority="high"' : ' loading="lazy"')
    + ' decoding="async"'
    + ' style="' + (opt && opt.cover ? 'width:100%;height:100%;object-fit:cover;display:block;'
                                     : 'width:100%;display:block;height:auto;border-radius:8px;') + '" />';
};

for (let i = 2; i >= 0; i--) {
  const imgBlock = '\n<figure style="margin:20px 0">\n  ' + window._buildImg(uploads[i]) + '\n</figure>\n';
  c = c.slice(0, pts[i]) + imgBlock + c.slice(pts[i]);
}
window._newContent = c;
'inserted, new len: ' + c.length + ' order:' + uploads.map(u => u.tag.slice(-6)).join(',')
```

ℹ️ `sizes` 의 `820px` 는 KoreaPlug 본문 래퍼 폭이다 (Astra `full-width-container`, 실측 표시폭 788px). 테마를 바꾸면 이 값도 함께 고친다.
ℹ️ **원본 폭 1226은 줄이지 않는다.** dpr 2 기기에서는 788×2=1576px가 필요하므로 1226이 오히려 상한에 가깝다. 해결책은 원본 축소가 아니라 **브라우저가 srcset에서 고르게 하는 것**이다.

```javascript
// 2.5) (v5.0) 기존 스톡 이미지 교체 — 첫 번째만 히어로, 나머지는 본문 이미지로 순차 교체
// ⛔ v4.0처럼 전부 히어로로 바꾸면 스톡이 2개인 글에서 같은 이미지가 본문에 두 번 박힌다
//    (2026-08-18 0and1Life #88 Post 1160에서 실측 — [FEATURED_IMAGE_URL] 2곳)
// img 태그의 src와 alt만 바꾸고 나머지 마크업(제목 오버레이 등)은 유지한다
const hero = window._uploadedIds.find(u => u.tag && u.tag.includes('hero'));
const body = window._uploadedIds.filter(u => u.tag && !u.tag.includes('hero'));
if (hero) {
  let n = 0;
  window._newContent = window._newContent.replace(/<img[^>]*>/g, (tag) => {
    if (!/unsplash\.com|pexels\.com|pixabay\.com|FEATURED_IMAGE/.test(tag)) return tag;
    n++;
    const pick = (n === 1) ? hero : body[n - 2];   // 2번째부터는 본문 이미지를 순서대로 소비
    if (!pick) return tag;                          // 남는 이미지가 없으면 원본 유지 (STEP 8에 보고)
    // (v5.4) src/alt만 갈아끼우지 않고 srcset·크기·로딩 속성까지 함께 넣는다.
    //        원래 마크업의 style(제목 오버레이용 object-fit 등)은 그대로 승계한다.
    const st = (tag.match(/style="([^"]*)"/) || [])[1] || '';
    const s  = window._srcset[pick.id];
    let t = '<img class="wp-image-' + pick.id + '" src="' + pick.url + '"'
          + ' srcset="' + s.srcset + '" sizes="(max-width: 820px) 100vw, 820px"'
          + ' width="' + s.w + '" height="' + s.h + '" alt="' + pick.alt + '"'
          + (n === 1 ? ' loading="eager" fetchpriority="high"' : ' loading="lazy"')
          + ' decoding="async"'
          + (st ? ' style="' + st + '"' : '') + ' />';
    return t;
  });
  window._stockReplaced = n;
  window._bodyUsedInReplace = Math.max(0, n - 1);  // STEP 4 삽입 대상에서 제외한 개수와 일치해야 한다
}
'stockReplaced:' + window._stockReplaced + ' (hero 1 + body ' + window._bodyUsedInReplace + ')'
 + ' newLen:' + window._newContent.length
 + ' leftover:' + (window._newContent.match(/FEATURED_IMAGE|unsplash\.com/g) || []).length
```

```javascript
// 2.9) 저장 전 불가침 검증 (v3.4 — 필수)
const before = window._finalContent, after = window._newContent;
const cnt = (s, re) => (s.match(re) || []).length;
window._evGuard = {
  evClass: cnt(before, /evidence-capture/g) + '->' + cnt(after, /evidence-capture/g),  // 좌우 같아야 함
  evName:  cnt(before, /\/evidence-/g)      + '->' + cnt(after, /\/evidence-/g),       // 좌우 같아야 함
  pubSrc:  cnt(before, /go[-_.]kr/g)        + '->' + cnt(after, /go[-_.]kr/g),         // 좌우 같아야 함
  blocks:  cnt(before, /<!-- wp:/g)         + '->' + cnt(after, /<!-- wp:/g),          // 좌우 같아야 함
  ezToc:   cnt(before, /ez-toc/g)           + '->' + cnt(after, /ez-toc/g),            // 양쪽 다 0이어야 함
  h2:      cnt(before, /<h2/g)              + '->' + cnt(after, /<h2/g),               // 좌우 같아야 함
  h3:      cnt(before, /<h3/g)              + '->' + cnt(after, /<h3/g),               // 좌우 같아야 함
  table:   cnt(before, /<table/g)           + '->' + cnt(after, /<table/g),            // 좌우 같아야 함
  figPair: cnt(after, /<figure/g)           + '/'  + cnt(after, /<\/figure>/g),        // 짝이 맞아야 함
  imgTags: cnt(before, /<img/g)             + '->' + cnt(after, /<img/g),
  stock:   cnt(before, /unsplash\.com|FEATURED_IMAGE/g) + '->' + cnt(after, /unsplash\.com|FEATURED_IMAGE/g), // (v5.0) 교체 시 →0
  dupImg:  (() => { const s = (after.match(/src="[^"]*"/g) || []); return s.length - new Set(s).size; })(),   // (v5.0) 0이어야 함
  noAlt:   cnt(after, /<img(?![^>]*alt=)/g),                                           // 0이어야 함
  // (v5.4) 생성 이미지(koreaplug-)만 대상 — 증빙 캡처는 세지 않는다
  genImg:  (after.match(/<img[^>]*koreaplug-[^>]*>/g) || []).length,
  noSrcset:(after.match(/<img[^>]*koreaplug-[^>]*>/g) || []).filter(t => !/srcset=/.test(t)).length,   // 0이어야 함
  noWH:    (after.match(/<img[^>]*koreaplug-[^>]*>/g) || []).filter(t => !/width="/.test(t)).length,   // 0이어야 함
  noLoad:  (after.match(/<img[^>]*koreaplug-[^>]*>/g) || []).filter(t => !/loading="/.test(t)).length  // 0이어야 함
};
Object.entries(window._evGuard).map(([k, v]) => k + ': ' + v).join('\n')
```

⛔ 위 검증에서 하나라도 어긋나면 **저장하지 않는다.** 원인을 해결한 뒤 다시 만든다.
🆕 **(v5.4) `noSrcset`·`noWH`·`noLoad` 중 하나라도 0이 아니면 저장 금지다.** 반응형 속성이 빠진 이미지가 있다는 뜻이고, 그 상태로 저장하면 WordPress가 만들어 둔 사이즈 사본이 전부 사장돼 **모든 기기가 full 파일을 내려받는다.** 7-2-0의 `window._srcset` 이 채워졌는지부터 확인한다.
🆕 **(v5.0) `dupImg` 가 0이 아니면 같은 이미지가 본문에 두 번 들어간 것이다** — STEP 7-2.5의 순차 교체가 제대로 돌지 않았다는 뜻이므로 저장 금지. `stock` 이 →0이 아니면 교체되지 않은 플레이스홀더가 남은 것이다.

```javascript
// 3) content 저장 — (v3.4) status를 명시 동봉해 상태 전환을 막는다
window._saveResult = null;
fetch('/wp-json/wp/v2/posts/POST_ID', {
  method: 'POST',
  headers: {'X-WP-Nonce': window._nonce, 'Content-Type': 'application/json'},
  body: JSON.stringify({content: window._newContent, status: window._origStatus})
}).then(r => r.json())
  .then(d => { window._saveResult = {id: d.id, status: d.status, fm: d.featured_media}; });
// 6초 대기 후 확인 — status가 window._origStatus와 같아야 한다
```

🚨 **(v3.4) 상태 전환 방지 — 이 조항을 어기면 사용자 지시 위반이다.**
글의 `post_date` 가 미래이면, `content` 만 POST해도 WP가 `draft` → **`future`(예약발행)** 로 스스로 승격시킨다 (2026-08-12 #132 실측). 그래서 **모든 저장 POST의 body에 `status: window._origStatus` 를 반드시 포함**한다. 그럼에도 응답 `status` 가 원래 값과 다르면 **즉시 되돌린다**:

```javascript
// 상태가 바뀌었을 때만 실행 — 원래 상태로 복구
fetch('/wp-json/wp/v2/posts/POST_ID', {
  method: 'POST',
  headers: {'X-WP-Nonce': window._nonce, 'Content-Type': 'application/json'},
  body: JSON.stringify({status: window._origStatus})
}).then(r => r.json()).then(d => { window._restore = 'status:' + d.status; });
```

복구 사실은 STEP 8 보고에 **반드시 명시**한다.

```javascript
// 4) 대표이미지(featured image) 설정 — (v3.4) status 동봉. 실패해도 전체 태스크는 중단하지 않음
window._featuredResult = 'pending';
const heroUp = window._uploadedIds.find(u => u.tag && u.tag.includes('hero'));
const featuredId = heroUp ? heroUp.id : window._uploadedIds[window._featuredImgIndex ?? 0]?.id;
if (featuredId && window._curFeatured === 0) {          // 이미 지정돼 있으면 덮어쓰지 않는다
  fetch('/wp-json/wp/v2/posts/POST_ID', {
    method: 'POST',
    headers: {'X-WP-Nonce': window._nonce, 'Content-Type': 'application/json'},
    body: JSON.stringify({featured_media: featuredId, status: window._origStatus})
  }).then(r => r.json())
    .then(d => { window._featuredResult = (d.featured_media === featuredId)
      ? 'ok: mediaId=' + featuredId + ' status=' + d.status
      : 'failed: ' + JSON.stringify(d).substring(0, 100); })
    .catch(err => { window._featuredResult = 'error: ' + err.message; });
} else if (window._curFeatured !== 0) {
  window._featuredResult = 'skipped: already set (' + window._curFeatured + ')';
} else {
  window._featuredResult = 'skipped: uploadedIds not ready';
}
// 4초 대기 후 window._featuredResult 확인
```

⚠️ 이미 대표이미지가 지정된 글(`featured_media !== 0`)에 본문 이미지만 보충하는 경우에는 **대표이미지를 덮어쓰지 않는다.**

---

### STEP 7.5: 최종 육안 검증 (필수)

저장 후 **프론트엔드 프리뷰**(`https://koreaplug.com/?p=POST_ID&preview=true`)를 열고 **스크롤하며 삽입된 이미지 전부를 스크린샷으로 확인**한다.

**(v3.4) 먼저 기계 검증을 돌려 수치를 확보한다:**

```javascript
const H = document.documentElement.scrollHeight;
const imgs = Array.from(document.querySelectorAll('article img, .entry-content img')).filter(i => i.naturalWidth > 300);
imgs.map(i => i.src.split('/').pop().split('?')[0].replace('koreaplug-SLUG', 'KP').slice(0, 30)
  + ' nw' + i.naturalWidth + ' @' + Math.round((i.getBoundingClientRect().top + window.scrollY) / H * 100) + '%').join('\n')
 + '\n--- TOC:' + document.querySelectorAll('#ez-toc-container, .ez-toc-container').length
 + ' h2:' + document.querySelectorAll('article h2').length
 + ' tables:' + document.querySelectorAll('article table').length
 + ' broken:' + Array.from(document.querySelectorAll('article img')).filter(i => i.complete && i.naturalWidth === 0).length
```

- **TOC 컨테이너가 정확히 1개**인가? (2개면 본문에 목차가 박제된 것 — STEP 3-1 복구 절차 필요)
- 이미지가 **본문 전체에 고르게 퍼져 있는가?** 히어로 없는 글은 대략 10~15% / 45% / 70%, 히어로 있는 글은 0% / 30% / 50% / 65% 부근
- `broken` 이 0인가? 모든 `nw`(naturalWidth)가 정상인가? (v4.0 Flow 산출물은 원본 `1226`)
- 🖼️ **(v5.4) 브라우저가 실제로 축소본을 골랐는가?** 아래를 돌려 `currentSrc` 가 **`-1024x641` 또는 `-768x481`** 이면 정상이고, 전부 **`full`(접미사 없음)** 이면 `srcset` 이 안 먹은 것이다. 본문 아래쪽 이미지는 `lazy` 라 **스크롤해야 로드된다** — 스크롤 후 다시 측정한다.

```javascript
const g = Array.from(document.querySelectorAll('article img')).filter(i => /koreaplug-/.test(i.src));
g.map(i => i.currentSrc.split('/').pop().split('?')[0].replace(/^koreaplug-/, '~').replace(/[^A-Za-z0-9.\-~]/g, '')
  + ' disp' + Math.round(i.getBoundingClientRect().width)
  + ' srcset' + ((i.getAttribute('srcset') || '').split(',').length) + '개'
  + ' ' + (i.getAttribute('loading') || 'NONE')).join('\n')
 + '\n--- full받은수:' + g.filter(i => !/-\d+x\d+\.webp$/.test(i.currentSrc.split('?')[0])).length + ' (히어로 1장만 정상)'
```
- h2·표 개수가 삽입 전과 같은가?

**이어서 육안으로 확인한다:**

- 각 이미지의 피사체가 글 내용·주변 섹션과 맞는가?
- 🩻 **(v5.3) 인물이 있는 이미지를 프리뷰에서 다시 한번 본다** — 머리·목·팔·손가락이 온전한가? 이 항목은 그리드 판정(5-3)과 프리뷰(7.5) **두 번 확인한다.** 축소된 썸네일에서는 결손이 잘 안 보이기 때문이다. 결손이 발견되면 해당 이미지만 3-3 ③ 형식으로 재생성해 교체하고, 舊 미디어는 **삭제하지 않고 STEP 8에 삭제 대기로 보고한다.**
- 🚨 **(v4.1) 4장을 한 화면에 놓고 봤을 때 "한국 글"로 보이는가?** 각각은 통과했어도 4장이 전부 무인·무간판 정물이면 글 전체가 Nowhere가 된다. 이 경우 가장 밋밋한 1장을 골라 STEP 5부터 다시 만든다.
- 🚨 **(v4.1) 사람의 흔적이 최소 1장에 있는가? 한국 지표 영역이 3개 이상으로 흩어져 있는가?**
- 히어로/대표이미지가 정상 반영됐는가? (제목 오버레이 마크업이 보존됐는가)
- 증빙 캡처가 원래 자리에 그대로 있는가? (`window._evGuard` 확인)
- **워터마크 흔적(✦)이 남아 있지 않은가?** — 남아 있으면 STEP 5-4의 `cropRight` 값을 늘려 재캡처하거나, 이미 업로드된 파일을 koreaplug.com **동일 출처**에서 canvas로 다시 읽어 재크롭·재업로드한다.
- 표·TOC·내부링크 등 기존 요소가 삽입으로 깨지지 않았는가?
- **글 상태가 원래대로인가?** (`draft` 는 `draft` 그대로여야 한다)

**뒷정리:** 검증이 끝나면 이 루틴이 만든 탭(Flow 탭, media-new 탭)을 `tabs_close_mcp` 로 모두 닫는다. 사용자가 결과를 바로 볼 수 있도록 **프리뷰 탭 1개만 남긴다.**

---

### STEP 8: 완료 보고

#### 8-A. 중단 보고 (v5.5 신설 — 정상 완료하지 못한 모든 경우)

> 🚨 **신설 사유 (2026-08-25 실측)**: Flow 세션 만료로 STEP 5에서 중단했을 때, 舊 보고 양식에는 「Skip된 경우 그 이유」한 줄뿐이라 **STEP 3에서 만든 프롬프트 4개를 남길 자리가 없었다.** 프롬프트 설계는 본문 정독 + 3중 게이트(사건·정확성·한국성) 검증이 들어가는 **이 루틴에서 가장 비싼 단계**인데, 그것이 통째로 버려져 다음 실행이 처음부터 다시 해야 했다.

중단은 **실패가 아니라 중간 저장**으로 취급한다. 어느 단계에서 멈췄든, **그때까지 확정된 것을 전부, 재사용 가능한 형태로** 남긴다.

- **중단 지점과 사유**: 몇 번 STEP에서, 무엇 때문에 멈췄는가 (세션 만료 / raw 오염 / 미배포 / unknown 판정 대기 등)
- **사용자 조치 안내**: 무엇을 하면 재실행이 통과하는가 (구체적 URL 포함)
- **대상 글 표**: Notion #번호 · Post ID · slug · 날짜 · 처리/skip 판정
- **STEP 2 분류 결과**: 완료했다면 이미지별 판정 표와 evidence/stock/deco/genCount, raw 건강 검진 수치(len·blocks·ezToc·h2)
- **STEP 3 프롬프트 전문**: 완성한 프롬프트를 **영문 원문 그대로** 남긴다. 이미지별 **훅 문장**·**한 문장 테스트**·**한국 지표**·**alt text**·**대표이미지 선정 근거**를 함께 적어, 재실행 시 STEP 3을 건너뛰고 바로 제출할 수 있게 한다
- **STEP 4 삽입 위치**: `window._insertPoints` 값과 각 위치의 h2 제목, 증빙 figure 구간과의 충돌 검사 결과
- **건드리지 않은 것 명시**: 글 상태(시작 status = 종료 status), 본문 미수정, 미디어 미업로드 — **무엇을 하지 않았는지**를 분명히 적는다
- **탭 정리 여부**
- 루틴 자체의 구조적 결함이 원인이었다면 **수정할 조항 번호와 교체용 전문(前文)**을 함께 제시한다

⛔ 중단 시에도 **글 상태·본문·미디어는 절대 건드리지 않는다.** 부분 삽입 상태로 남기는 것을 금지한다 — 다음 실행의 STEP 2 분류가 어긋난다.

#### 8-B. 완료 보고 (정상 완료)

완료 후 아래 내용을 출력:

- 처리한 글 제목 및 Post ID
- **STEP 2 분류 결과 표**: 이미지별 `파일명 => 증빙/스톡/데코 [판정근거]`, 그리고 evidence/stock/deco/genCount
- `unknown`이 있었다면 수동 확인 결과와 재계산된 genCount
- 삽입·교체된 이미지 (media ID + 렌더 기준 위치 %)
- 최종 imgCount, 불가침 검증(`window._evGuard`) 결과 — **blocks·ezToc·h2·table 항목 포함**
- **(v3.4) 글 상태**: 시작 시 status → 종료 시 status. 전환이 발생했다면 복구 여부까지 명시
- 대표이미지: 선정된 이미지, 선정 이유, 설정 결과 (`window._featuredResult`)
- 피사체 정확성 검증: 각 이미지별 통과/재시도/건너뜀 여부, **2장 중 어느 쪽을 채택했는지**
- **(v4.1) 한국성 검증 표**: 이미지별로 ① 사용한 **한국 지표 2개 이상**을 명시 ② **Nowhere 테스트 통과 여부** ③ 사람의 흔적 유무. 4장 중 지표 영역이 몇 개로 흩어졌는지도 함께 적는다
- **(v5.0) 사건 설계 기록**: 이미지별 **훅 문장(본문 인용)**과 **한 문장 테스트 결과**(무슨 일이 벌어지는가). '있다/놓여 있다'로 끝난 건이 있으면 왜 채택했는지 사유를 남긴다
- **(v5.0) 스톡 교체 내역**: `window._stockReplaced`(교체 총수) / `window._bodyUsedInReplace`(교체에 소비된 본문 이미지 수) / `dupImg` 값. 교체되지 않고 남은 플레이스홀더가 있으면 개수와 위치를 보고한다
- Skip된 경우 그 이유
- **(v4.0) 생성 소요시간**: 이미지별 생성 대기 시간을 기록한다. 60초를 넘긴 건이 있으면 Flow 지연으로 보고한다
- **삭제 대기 미디어**: 재크롭 등으로 남은 원본 미디어 ID를 나열하고 **사용자 확인을 요청**한다 (임의 삭제 금지)
- 루틴 자체의 오류·개선점이 발견됐다면 **수정할 조항 번호와 교체용 전문(前文)**을 함께 제시한다 — 사용자가 붙여넣기만 하면 되도록

---

### 중요 주의사항

- 🔑 **(v5.5) 어떤 작업보다 먼저 STEP 0 「세션 사전 점검」을 수행한다.** WP 세션과 Flow 세션을 **한 번에** 확인하고, 하나라도 만료면 **Notion 조회조차 하지 않고 즉시 종료**한다. 실패할 실행은 1분 안에 실패시킨다 (2026-08-25 실측: Flow 만료 상태로 STEP 1~4를 완주한 뒤 STEP 5에서 중단 — 프롬프트 4개 낭비)
- 🔑 **(v5.5) 루틴은 어떤 서비스에도 로그인하지 않는다.** 자격증명 입력·인증 폼 제출·OAuth/SSO 동의·**계정 선택 화면 클릭**은 전부 금지. 계정이 이미 목록에 떠 있어도 클릭하지 않는다 — 그 클릭은 권한 부여 행위이며 사용자 승인 사항이다
- 🔑 **(v5.5) 중단 시에는 STEP 8-A 「중단 보고」 양식을 쓴다.** 특히 **STEP 3 프롬프트 전문**(훅 문장·한국 지표·alt text 포함)과 **STEP 4 삽입 위치**를 남겨, 재실행이 그 단계를 건너뛸 수 있게 한다
- Chrome이 열려 있고, koreaplug.com WP admin에 로그인되어 있어야 함
- **(v4.0) labs.google(Google Flow)에 로그인되어 있어야 함** — Flow 프로젝트 URL은 STEP 5 상단 참조. 세션 판정 기준은 STEP 0-3
- **(v4.0) Flow 설정은 `에이전트 미사용 / 이미지 / 16:9 / Nano Banana 2 / x2` 고정.** 에이전트를 켜면 프롬프트가 재해석된다
- **(v4.0) 워터마크는 `cropRight = 150` 으로 잘라낸다** (Flow 워터마크는 상대좌표 0.925W·0.875H의 이미지 안쪽에 있음). 덮기(fillRect) 방식은 배경에 디테일이 있으면 사각형이 눈에 띄므로 금지
- **(v4.0) 캡처 대상은 `getBoundingClientRect().width` 가 가장 큰 img** — 같은 페이지에 `naturalWidth 1376` 인 썸네일이 여러 개 있다
- **(v3.4) 본문을 읽는 모든 REST 요청에 `context=edit` 필수. `content.raw` 가 없으면 중단한다 — `|| content.rendered` 폴백은 원본을 파괴한다**
- **(v3.4) 모든 저장 POST에 `status: window._origStatus` 를 동봉한다. 저장 후 status가 바뀌었으면 즉시 되돌리고 보고한다**
- REST API 검색 시 `status=any` 파라미터 필수 (없으면 draft 글이 검색되지 않음)
- ⚡ **(v4.2) `fire-and-read` 2회 호출 패턴 폐기** — `javascript_tool` 은 최상위 `await` 를 지원하고 마지막 표현식을 반환한다 (2026-08-18 실측). `const d = await fetch(...).then(r=>r.json()); window._x = d; '요약'` 처럼 **fetch와 검증을 한 호출에 합친다.** window 변수 저장은 계속 하되, '읽기 위한 추가 호출'만 없앤다
- ⚡ **(v4.2) 이미지는 전부 제출 → 1회 대기 → 그리드에서 일괄 캡처.** 한 장씩 만들고 기다리는 방식 금지 (STEP 5-2·5-4). Flow는 생성 중에도 다음 프롬프트를 받으며, 그리드 썸네일이 원본 해상도를 그대로 갖고 있다
- ⚡ **(v4.2) `browser_batch` 를 기본으로 쓴다** — `click → type → click → wait → screenshot` 은 1회 호출. 10초 wait 반복도 한 배치에 묶는다
- ⚡ **(v4.2) 후보 판정은 그리드 스크린샷 1장으로.** 에디터 뷰 진입 금지 — 舊 실행에서 20회 왕복을 잡아먹은 원인이다. 세부가 필요하면 `computer: zoom` 을 쓴다
- Chrome MCP의 wait는 1회 최대 10초, scroll_amount는 최대 10 — 긴 대기는 나눠서 반복
- **이미지 생성 실패·부정확 시 재시도는 반드시 '수정된 프롬프트'로** (동일 프롬프트 재시도 금지). Flow는 1회에 2장을 주므로 먼저 **2장 중 채택**을 시도하고, 둘 다 부적합할 때만 수정 재시도한다. 수정 1회 후에도 부정확하면 해당 이미지 건너뜀
- **프롬프트 작성 전 본문을 반드시 읽고, 피사체 형태가 불확실하면 웹 검색으로 확인**
- 🖼️ **(v5.4) 본문에 넣는 모든 생성 이미지에 `srcset`·`sizes`·`width`·`height`·`loading`·`wp-image-{ID}` 를 붙인다.** 이걸 빼면 WordPress가 만들어 둔 축소 사본이 전부 사장되고 전 기기가 full 파일을 받는다 (2026-08-19 실측: 3편 1,836KB → 1,216KB, 모바일 792KB). 히어로만 `loading="eager" fetchpriority="high"`, 나머지는 `loading="lazy"` (STEP 7-2-0·7-2)
- 🩻 **(v5.3) 몸통이 보이는 인물에 `X only` 를 쓰지 않는다.** `shoulders and one hand only` 같은 표현은 모델이 열거되지 않은 부위(머리·목)를 실제로 삭제한다 (2026-08-19 #139 실측, 머리 없는 인물 생성). `only` 는 **손·발만 프레임에 있는 접사에서만** 허용하고, 인물에는 `seen from behind, the back of the head clearly visible, face turned away from the camera` 형식과 `complete natural human anatomy with no missing or cropped body parts, no headless figures, no floating clothing` 제외 조건을 함께 쓴다 (3-3 ③)
- 🩻 **(v5.3) 인물 이미지의 해부 검사는 5-3(그리드)과 7.5(프리뷰)에서 두 번 한다.** 머리·목·팔·손가락 결손은 **다른 모든 기준에 우선하는 즉시 탈락 사유**다
- 🚨 **(v4.1) `no people` 과 `no text` 를 기본 제외 조건으로 쓰지 않는다.** 이 두 줄이 "어디에나 있을 법한 텅 빈 이미지"를 만든 직접 원인이다 (2026-08-18 #137 실측, 4장 중 3장 Nowhere 판정). 표준 제외 세트는 `no readable paragraphs, no UI text, no logos, no watermark, no 3d render, no anime style, no posed model looking at camera, no generic stock photo look` 이며, 무인·무텍스트가 정말 필요한 정물 컷에서만 개별 추가한다
- 🚨 **(v4.1) 모든 이미지는 한국 지표 2개 이상 + Nowhere 테스트 통과가 필수다** (STEP 3-3). 형용사 "Korean"을 붙이는 것으로는 대체되지 않으며, 지표를 **물리적 형태로 묘사**해야 한다
- **(v4.1) 한글은 배경·아웃포커스에만 둔다** — 초점 안에 들어온 글자는 깨져 나온다. 원경 간판 덩어리·흐린 네온은 오히려 '한국' 신호로 적극 활용한다
- 글 제목(title)은 수정하지 않음
- 이미지 삽입 후 글 상태(publish/draft/future)는 변경하지 않음 — **발행·예약발행 전환은 어떤 경우에도 금지 (발행 결정은 항상 사용자 몫, 2026-08-01 사용자 지시)**
- **미디어 삭제는 어떤 경우에도 사용자 확인 후에만 수행한다** (2026-08-01 사용자 지시)
- (v3) **증빙 캡처 불가침**: 삽입·스톡 교체 어느 단계에서도 증빙 figure의 마크업·src·alt·figcaption을 수정하지 않는다. 저장 전 STEP 7-2.9로 확인한다
- (v3.2) **증빙 판정은 `evidence-capture` 클래스·`evidence-` 파일명만으로 하지 않는다.** v1.28(2026-08-02) 이전 글에는 이 마커가 없다. figcaption의 `Captured YYYY-MM-DD`, 공공 출처 도메인 파일명(`*-go-kr`, `korea-kr`, `kosis`, `hometax`, `work24`), alt의 조회·확인·캡처 단서까지 폴백으로 본다
- (v3.3) **`window.open` 에 `'_blank'` 금지** — 탭이 Chrome MCP 그룹 밖에 열려 리스너 주입이 불가능해진다 (STEP 6-1)
- (v3.3) **javascript_tool 반환값에 이미지 URL·쿼리스트링을 그대로 담지 않는다** — `[BLOCKED: Cookie/query string data]` 로 출력 전체가 막힌다. 집계값 먼저, 파일명은 축약·치환해서 출력
- **(v3.4) 삽입 위치는 h2의 '문자 위치' 기준으로 계산** — 헤딩 개수 분위는 이미지를 글 뒤쪽에 몰아넣는다 (STEP 4)
- **(v3.4) 장시간 window 상태가 필요한 작업은 `/wp-admin/` 대시보드가 아니라 `media-new.php` 에서 수행** — 대시보드는 간헐적으로 자체 리다이렉트를 일으킨다
