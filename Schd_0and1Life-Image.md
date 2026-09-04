# 0and1Life 자동 이미지 삽입 태스크 (v6.1 — Flow 도메인 이전 대응: 교차 출처 캡처 경로 · 동시 생성 상한)

### 목적

Notion 글 현황 테이블에서 오늘 날짜에 draft된 WordPress 글을 찾아, **데코(생성) 이미지가 3장 미만인 글**에 **Google Flow(Nano Banana 2)** 로 생성한 이미지를 WebP 형식으로 삽입한다 — 단, **증빙+데코 합계가 5장을 넘지 않는 범위**에서만 (생성 수를 3→2→1장으로 자동 감축). 기존에 무관한 스톡(Unsplash 등) 이미지가 들어가 있으면 함께 교체한다.

> 🚨 **v4.0 일괄 개정 (2026-08-18) — 이 파일은 v3.1에 머물러 있어 KoreaPlug 대비 3세대(v3.2·v3.3·v3.4) 뒤처져 있었다.** KoreaPlug에서 실전으로 검증된 아래 수정을 **전부 백포트**하고, 여기에 v4.0(Flow 교체)을 함께 적용한다. 두 사이트의 루틴은 이제 사이트 고유값(도메인·Notion 페이지·파일명 prefix·프롬프트 철학)을 제외하면 동일한 구조다.
>
> - **v3.2 백포트**: STEP 2 분류기를 정규식 훑기에서 **DOM 기반 8단계 우선순위 분류기**로 교체하고, **미분류(unknown) 존재 시 skip 금지** 가드를 신설. 이 결함이 최초로 실측된 곳이 바로 0and1Life다 — #70 결혼식 보증인원(Post 894)은 공공 출처(price.go.kr) 조회 캡처 2장이 데코로 오분류돼 deco=4 → genCount 0 → skip 처리되었고, **이미지가 필요한 글을 3일 내내 그냥 지나쳤다.**
> - **v3.3 백포트**: `window.open(url, '_blank')` 의 **`'_blank'` 제거**. 이 인자가 있으면 탭이 Chrome MCP 그룹 밖에 생성돼 `tabs_context_mcp` 에 안 잡히고, postMessage 리스너 주입이 불가능해져 업로드 경로 전체가 막힌다.
> - **v3.4 백포트 (가장 중요)**: 모든 본문 fetch에 **`context=edit` 필수**, 모든 저장 POST에 **원래 status 동봉**, 저장 전 **불가침 검증(`_evGuard`)**, 삽입 위치를 **문자 위치 기준**으로 산출. 舊 `d.content.raw || d.content.rendered` 폴백은 **본문 원본을 파괴한다** (Gutenberg 블록 주석 소실 + ez-toc 목차가 정적 HTML로 본문에 박제). KoreaPlug에서 4편이 오염된 채 발행된 뒤에야 발견됐다.
>
> ⚠️ **선행 점검 권고**: 이 루틴이 v3.1로 돌던 기간에 처리된 0and1Life 글들도 **동일하게 오염됐을 가능성이 높다.** STEP 3-1의 raw 건강 검진(`ezToc`/`blocks`)을 최근 처리분에 먼저 돌려보고, 오염이 확인되면 리비전 복구 절차를 적용한다.

> 🚀 **v4.0 변경 (2026-08-18) — 이미지 생성처를 gemini.google.com에서 Google Flow로 교체한다.**
> 2026-08-18 KoreaPlug에서 동일 프롬프트로 실측한 비교:
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
> 결정적 이점은 속도가 아니라 **구조적 안정성**이다. Flow는 이미지를 `labs.google` **동일 출처**로 서빙하므로 `SecurityError: canvas has been tainted` 가 **원천적으로 발생하지 않는다.** 또 x2로 2장을 받아 **좋은 쪽을 고르는 구조**라 舊 "수정 재시도 1회" 규정이 실제로 발동할 일이 거의 없다.

> ⚡ **v5.1 변경 (2026-08-18) — 실행 시간 단축. 병목은 이미지 생성이 아니라 화면 왕복이었다.**
> 2026-08-18 회차는 2편·5장에 약 95회의 도구 호출이 들었다. 원인을 재보니 생성(장당 50~56초)보다 **UI 왕복과 대기 방식**이 더 컸다.
>
> | # | 조치 | 근거 (2026-08-18 실측) | 절감 |
> |---|---|---|---|
> | 1 | **에디터 진입 폐지 · 그리드에서 판정·캡처** | 그리드 썸네일이 이미 원본 해상도 `naturalWidth 1376×768`(표시 318px). 에디터에 갈 이유가 없었다 | 호출 **~30회** |
> | 2 | **프롬프트 N개 연속 투입 후 일괄 수확** | 진행률 87%·99% 중에도 입력창이 비어 있고 활성 (**1회차 큐잉 검증 필요**) | 55초×N 직렬 → **1회 대기** |
> | 3 | **진행 확인을 스크린샷 → JS 문자열 폴링** | 진행률 확인 스크린샷 12장 중 절반이 "아직 99%" | 호출 ~10회 + 토큰 |
> | 4 | **`browser_batch` 로 클릭·입력·전송 묶기** | 95회 전부 단발 호출이었다 | 왕복 지연 절반 이하 |
> | 5 | **업로드 5건 연속 전송 후 1회 폴링** | 건별 8초 대기 ×5 = 40초, 업로드는 서로 독립 | ~35초 + 호출 4회 |
> | 6 | **대상 탐색을 WP REST 우선으로** | Notion fetch 98,515자 → 한도 초과 → grep 차단 → python 우회로 호출 4회 | 호출 4~5회 + 대용량 덤프 |
>
> ⛔ **가장 중요한 한 줄: 캡처가 끝날 때까지 Flow 그리드를 떠나지 않는다.** 콜드/복귀 로드 실측이 6초 0개 · 14초 0개 · **26초 18개**였다. 그리드를 한 번 떠날 때마다 이 20여 초를 다시 낸다.
> 예상 효과: 5장 기준 **약 25~30분 → 8~10분**, 평상시 1편 3~4장은 **5분 안쪽**.

> 🎯 **v5.0 변경 (2026-08-18) — 프롬프트 철학을 '정확한 그림'에서 '읽게 만드는 그림'으로 바꾼다.**
> v4.0 첫 실전(2026-08-18, Post 1153·1160)에서 5장 전부가 **기술적으로는 통과했는데 사용자 평가는 "무난하고 추상적"** 이었다. 원인을 뜯어보니 프롬프트 규칙 자체에 있었다.
>
> | 결함 | v4.0 규칙이 유도한 것 | v5.0의 교정 |
> |---|---|---|
> | **사건이 없다** | "장소·사물을 정확히 묘사하라"만 있고 **무슨 일이 벌어지는지**에 대한 요구가 없음 → 빈 로비·정리된 책상만 나옴 | 3-2 ① **한 문장 테스트**: "지금 무슨 일이 벌어지는가"를 말할 수 없으면 재설계 |
> | **글의 숫자가 안 보인다** | 본문의 30배·100만↔50만 같은 **충돌하는 수치**를 프롬프트에 안 넣음 | 3-2 ③ 숫자를 **높이·길이·개수·두께**로 번역해 반드시 화면에 넣는다 |
> | **사람을 과하게 뺐다** | "인물 최대 1장" → 실무에서 항상 0명 → 온기·긴장 소멸 | 3-4 **손·팔·부분 컷 권장**. 금지 대상은 '카메라 보고 웃는 모델'뿐 |
> | **범용 은유 남발** | 모래시계·저울·전구가 어느 글에나 붙음 | 3-2 ⑥ **범용 은유 금지 목록** 신설 |
> | **밋밋해도 채택** | 5-3 채택 기준이 '정확성'뿐 | 5-3에 **밋밋함 탈락 사유** 추가 |
>
> 함께 고친 기능 결함: **`[FEATURED_IMAGE_URL]` 플레이스홀더가 2곳인 글에서 v4.0 코드가 같은 히어로를 2번 박아 넣었다** (STEP 7-2.5). 2026-08-18 #88에서 수동 회피했고, v5.0에서 정식 조항으로 고쳤다 — 첫 번째만 히어로, 나머지는 본문 이미지로 순차 교체하고 그만큼 STEP 4의 삽입 개수를 줄인다.

> ⚠️ v3 변경 (2026-08-01): Draft 루틴이 발행 관문용 **증빙 캡처**(`figure class="evidence-capture"`, 파일명 `evidence-*`)를 본문에 넣기 시작하면서, 총 이미지 수 기준(舊 imgCount ≥ 3 → skip)으로는 모든 글이 스킵되어 이 루틴이 돌지 않았다. 판정은 **데코 개수**로 하되, 글이 이미지로 과밀해지지 않도록 **총량 상한 5장**(증빙+데코, 히어로 교체는 총량 불변이라 제외)을 함께 둔다. 증빙 캡처는 어떤 단계에서도 교체·이동·삭제하지 않는다.

---

### STEP 1: 대상 글 찾기 (v5.1 — WP 우선, Notion은 보조)

> 🚀 **(v5.1) 탐색 순서를 뒤집는다.** 이 루틴이 실제로 필요한 건 **WP의 draft 글**이지 Notion 행이 아니다.
> 2026-08-18 실측: EFFICIENCY 페이지 `notion-fetch` 가 **98,515자로 토큰 한도를 초과** → 파일 저장 → `grep` 은 "Omitted long matching line" 으로 차단 → bash python 슬라이스로 우회. **대상 2건을 찾는 데만 호출 4회와 대용량 덤프**가 들었다.
> 아래 WP 질의 **1회**로 같은 결과가 나온다. Notion은 결과가 0건이거나 제목·서브카테고리 확인이 필요할 때만 연다.

**1-A. WP REST로 최근 2일 draft를 직접 조회한다 (1순위 · 호출 1회)**

`media-new.php` 에서 nonce를 확보한 뒤(STEP 2 상단 코드) 실행한다.

```javascript
window._targets = null;
const since = new Date(Date.now() - 2 * 864e5).toISOString().slice(0, 19);   // 어제~오늘
fetch('/wp-json/wp/v2/posts?status=draft,future&modified_after=' + since
      + '&per_page=20&context=edit&orderby=modified&order=asc'
      + '&_fields=id,title,status,content,date,modified,featured_media,slug',
      {headers: {'X-WP-Nonce': window._nonce}})
  .then(r => r.json()).then(d => { window._targets = d; });
'fired'
```

```javascript
(window._targets || []).map(p => p.id + ' | ' + p.status + ' | ' + p.modified.slice(0, 10)
  + ' | fm:' + p.featured_media + ' | ' + p.slug
  + ' | raw:' + (p.content && typeof p.content.raw === 'string' ? 'ok len' + p.content.raw.length : 'RAW-MISSING')).join('\n')
```

- 결과를 그대로 STEP 2 분류기(`window._postData`)에 넘긴다 — **검색·재조회 불필요**
- `orderby=modified&order=asc` 라서 **오래된 것부터** 처리되어 기존 규칙(오래된 날짜 우선)과 일치한다
- 0건이면 1-B로 넘어간다

**1-B. Notion 확인 (0건일 때 · 또는 제목·서브카테고리가 필요할 때만)**

**두 페이지 모두** `notion-fetch`로 확인한다.

- EFFICIENCY: `https://app.notion.com/p/37cbfe4a2ae1819f8664ff3d38fffe56`
- 나의이야기: `https://app.notion.com/p/37cbfe4a2ae181b9a9ced0b937edd344`

테이블 컬럼: `# | 제목 | 한줄 요약 | SEO | 서브카테고리 | 아웃→ | ←인 | 작성일 | Draft일`

⚠️ **WP 세션 만료 대응 (2026-08-03 신설)** — 이 루틴은 `wpApiSettings.nonce`(wp-admin 로그인 세션)에 전적으로 의존한다. `wp-admin/` 접근 시 `wp-login.php?...&reauth=1` 로 리다이렉트되면 세션이 만료된 것이다.
- ⛔ 루틴은 **로그인 폼을 대신 제출하지 않는다** (자격증명 입력·인증 폼 제출은 AI 금지 동작). 자동완성이 채워져 있어도 클릭 금지.
- 오류 로그에 "WP 세션 만료 — 사용자 직접 로그인 필요"를 기록하고 종료한다. 이미지 삽입은 수행하지 않으며, 대상 글의 상태는 건드리지 않는다.
- 사용자 조치 안내: "Chrome에서 https://0and1life.com/wp-admin 에 직접 로그인하고 '기억하기'를 체크해 주세요."
- 다음 실행이 (v3.1의 2일 소급 규정에 따라) 어제 글까지 다시 훑으므로, 세션만 복구되면 누락분은 자동으로 따라잡는다.

⚠️ **(v4.0 백포트) Notion 페이지가 커서 fetch 결과가 토큰 한도를 넘으면** 결과가 파일로 저장된다. 이때 전체를 다시 읽지 말고, 저장된 파일에 `grep`(최근 날짜 문자열) 또는 python 슬라이스로 **표 끝부분과 로그 tail만** 확인한다.

ℹ️ **(v4.0) `grep` 결과가 "Omitted long matching line"으로 막히면** 매치 창을 좁힌다. `.{0,300}날짜.{0,300}` 는 막히고 **`.{0,90}2026-08-18.{0,90}` 는 통과**한다 (2026-08-18 실측). 글 번호로 찾을 때는 `.{0,90}#7[0-5].{0,90}` 처럼 범위 패턴을 쓰면 최근 회차 로그가 한 번에 잡힌다.

(v3.1) **오늘 또는 어제 날짜**(YYYY-MM-DD)와 일치하는 **"Draft일"** 행을 모두 찾는다. — 2일 소급 이유: 배포 루틴이 인증 문제 등으로 늦게 재실행되면 이 루틴이 도는 시점엔 글이 아직 WP에 없어 영영 누락된다 (2026-08-02 #122 실제 사례). 어제 글까지 봐야 다음 실행이 따라잡는다.
해당 행에서 **글 제목(한국어)**, **서브카테고리**, **한줄 요약**을 추출한다.
대상이 여러 건이면 **오래된 날짜부터** 각각 STEP 2 판정을 거쳐, genCount>0 이거나 스톡 교체가 필요한 글만 순서대로 처리한다 (이미 충족된 글은 skip — 중복 삽입 방지는 STEP 2 판정이 보장).

오늘·어제 모두 대상 글이 없으면 "최근 2일 draft 글 없음"을 출력하고 종료.

---

### STEP 2: WordPress에서 해당 글 확인

Chrome MCP로 새 탭을 열고 `https://0and1life.com/wp-admin/media-new.php` 로 이동한다 (로그인 상태 필수).

⚠️ **(v3.4 백포트) `/wp-admin/` 대시보드는 간헐적으로 자체 리다이렉트를 일으켜 window 변수를 날린다** (2026-08-12 실측: `index.php` → `edit-comments.php`). 장시간 window 상태를 유지해야 하는 이 루틴은 **처음부터 `media-new.php` 에서 작업한다.**

⚠️ `media-new.php` 에는 `wpApiSettings` 가 정의되어 있지 않다. REST nonce를 먼저 확보해 `window._nonce` 에 담고, 이후 모든 fetch에서 이 값을 쓴다:

```javascript
const s = Array.from(document.querySelectorAll('script:not([src])')).map(x => x.textContent).join('\n');
const m = s.match(/apiFetch\.createNonceMiddleware\(\s*["']([a-f0-9]+)["']/);
window._nonce = m ? m[1] : (window.wpApiSettings ? wpApiSettings.nonce : null);
'url:' + location.pathname + ' nonce:' + (window._nonce ? 'ok' : 'MISSING')
```

⛔ **(v3.4 백포트) 본문을 읽는 모든 fetch에 `context=edit` 를 반드시 붙인다.** 붙이지 않으면 `content.raw` 가 응답에 없어 `|| content.rendered` 폴백이 발동하고, 이후 저장 단계에서 **렌더링된 HTML이 원본 본문을 덮어쓴다.**

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
// (v3.4 백포트 · 필수) raw 확보 검증 — raw가 없으면 여기서 중단한다
window._postData.map(p => p.id + ' | ' + p.status + ' | ' + p.date + ' | fm:' + p.featured_media + ' | ' + p.slug
  + ' | raw:' + (p.content && typeof p.content.raw === 'string' ? 'ok len' + p.content.raw.length : 'RAW-MISSING')).join('\n')
```

⛔ 하나라도 `RAW-MISSING` 이면 **더 진행하지 않는다.** nonce 권한 또는 `context=edit` 누락 문제이므로, 원인을 해결한 뒤 재실행한다. rendered 폴백으로 진행하는 것은 금지한다.

(v3.2 백포트) 분류는 정규식을 본문 전체에 훑는 방식이 아니라, **이미지 하나씩 DOM으로 열어 8단계 우선순위**로 판정한다. 판정 근거(`why`)를 이미지별로 남겨 오분류를 사후 추적할 수 있게 한다.

```javascript
window._cls = window._postData.map(p => {
  const html = p.content.raw;                 // (v3.4) rendered 폴백 제거 — raw만 사용
  const div = document.createElement('div'); div.innerHTML = html;

  const evClassRe = /evidence-capture/i;                                      // ① figure 클래스 (v1.28 표준)
  const evNameRe  = /^evidence-/i;                                            // ② 파일명 prefix (v1.28 표준)
  const stockRe   = /unsplash\.com|pexels\.com|pixabay\.com|FEATURED_IMAGE/i;  // ③ 스톡·플레이스홀더
  const genNameRe = /^(0and1life|koreaplug)-/i;                               // ④ 이 루틴이 만든 생성 이미지
  const evCapRe   = /Captured\s*\d{4}\s*[-.\/]\s*\d{1,2}\s*[-.\/]\s*\d{1,2}/i; // ⑤ figcaption 촬영일 (레거시)
  const evSrcRe   = /(go[-_.]kr|korea[-_.]kr|kosis|hometax|work24|price[-_.]go)/i; // ⑥ 공공 출처 도메인 흔적 (레거시)
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

⚠️ (v3.3 백포트) `javascript_tool` 의 반환 문자열에 이미지 URL·쿼리스트링이 그대로 섞이면 **`[BLOCKED: Cookie/query string data]`** 로 출력 전체가 막힌다. 결과를 읽을 때는 한 번에 전부 찍지 말고 ⓐ 집계값만(`ev/st/deco/gen/unk`) 먼저, ⓑ `detail` 은 글 단위로 나눠서, ⓒ 파일명에서 `?&=` 를 치환하거나 공통 prefix를 축약해 출력한다. `.replace(/<img[^>]*>/g,'[IMG]')` 같은 치환도 **원본 문자열에 URL이 남아 있으면 소용없다** — 반드시 파일명만 잘라서 출력할 것.

ℹ️ **(v4.0) 본문 텍스트를 읽을 때도 같은 차단이 걸린다.** 본문에서 링크·이미지를 제거해도 `<a href>` 의 URL이 textContent에 남으면 막히므로, `https?:\/\/\S+` 를 공백으로 치환하고 `[?&=]` 를 제거한 뒤 출력한다.

우선순위를 이 순서로 고정한 이유: 표준 마커(①②)가 있으면 그것이 가장 확실한 근거이므로 먼저 본다. 스톡(③)은 호스트로 확정된다. 이 루틴이 직접 만든 이미지(④)는 파일명 prefix로 확실히 데코이므로, 레거시 추정 규칙(⑤⑥⑦)이 이를 잘못 증빙으로 끌고 가지 않도록 **레거시 규칙보다 먼저** 판정한다. ⑤⑥⑦은 마커가 없는 옛 글에만 적용되는 폴백이다.

⛔ **(v3.2 백포트) `unknown`이 비어 있지 않으면 genCount 값과 무관하게 즉시 skip하지 않는다.** `unknown`에 잡힌 이미지는 자동 판정이 실패한 것이다. 본문에서 해당 `<figure>`를 직접 열어 figcaption에 출처 기관·`Captured YYYY-MM-DD`가 있는지, 화면 캡처처럼 보이는지 눈으로 확인한 뒤 증빙/데코를 손으로 확정하고 **genCount를 다시 계산한 다음** 진행 여부를 정한다. 확인 결과는 STEP 8 보고에 이미지별로 남긴다.

> 이 가드가 필요한 이유 (2026-08-04 0and1Life 실측): #70(Post 894)은 증빙 2장이 데코로 오분류돼 genCount 0으로 계산됐고, 그 자리에서 종료되는 바람에 "애매하면 사람이 확인한다"는 아래 단계까지 **도달조차 하지 못했다.** 자동 분류가 틀렸다고 말할 기회 없이 skip된 것이 문제의 핵심이었다.

⛔ **(v3.4 백포트) Notion에 대상 행이 있는데 WP 검색 결과가 0건이면 '미배포'로 판정하고 즉시 종료한다.** 배포 루틴이 아직 글을 올리지 못한 상태이므로 이미지 생성·업로드를 일절 수행하지 않는다. 보고에 ① 미배포로 판정된 글 번호·제목·예상 slug ② WP 최신 수정 글의 날짜 ③ "배포 루틴 재실행 후 이 루틴을 다시 돌리면 자동으로 따라잡는다"는 안내를 남긴다.

- **genCount가 0이면 본문 삽입을 skip하고 종료** (단, `hasStockImg: true`면 스톡 이미지 교체만 수행 — 교체는 총량을 늘리지 않으므로 상한과 무관). `unknown`이 있으면 위 가드를 먼저 수행한 뒤 판단한다.
- genCount가 1~2장이면 그 수만큼만 생성·삽입한다. 우선순위: **이미지 1(도입 훅) → 이미지 3(결론 시각화) → 이미지 2(중반 클로즈업)** — 증빙 캡처가 이미 있는 글에서는 중반 클로즈업의 역할을 증빙이 대신한다.
- **증빙 캡처는 절대 건드리지 않는다**: 교체·이동·삭제 금지, 삽입 위치가 증빙 figure 내부에 떨어지면 직전 헤딩 바로 앞으로 옮긴다.
- `hasStockImg: true`면 **히어로 교체용 이미지 1장을 추가 생성**한다 (총 4장). 이 히어로 이미지는 STEP 7-2.5에서 기존 스톡 이미지의 src/alt를 교체하는 데 사용하고, 대표이미지로도 설정한다.
- **(v3.4 백포트) `status` 와 `date` 를 여기서 기록해 둔다.** STEP 7의 저장 POST에 원래 status를 동봉해야 상태 전환을 막을 수 있다.

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
// (v3.4 백포트 · 필수) raw 건강 검진 — 블록 주석이 있고 ez-toc 흔적이 없어야 정상 원본이다
const c = window._rawContent;
'len:' + (c ? c.length : 'NULL')
 + ' blocks:' + ((c || '').match(/<!-- wp:/g) || []).length
 + ' ezToc:'  + ((c || '').match(/ez-toc/g) || []).length
 + ' pTags:'  + ((c || '').match(/<p>/g) || []).length
```

⛔ **`ezToc` 가 0이 아니거나 `blocks` 가 0이면 그 글의 `post_content` 는 이미 오염된 상태다.** v3.1 이하로 돌던 과거 실행이 rendered를 저장했다는 뜻이다. 이때는 삽입을 진행하지 말고, 먼저 **리비전에서 원본을 복구**한 뒤 진행한다:

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

> KoreaPlug 실측 복구 사례(2026-08-12, Post 3376): 오염본 raw 20,592자(blocks 0 / ez-toc 66) → 리비전 3377의 원본 raw 15,422자(blocks 2 / ez-toc 0)를 기준으로 이미지를 다시 삽입해 정상화했다.
> **0and1Life 선행 과제**: 이 루틴이 v3.1로 돌던 기간에 처리된 글들은 미점검 상태다. 다음 실행 때 최근 처리분부터 위 검진을 돌려보고, 오염 목록을 STEP 8 보고에 남긴 뒤 **사용자 확인 후** 복구한다.

본문에서 파악할 것:

- 🆕 **(v5.0) 훅 문장 3~4개 (최우선)**: 독자가 가장 놀랄 문장을 **원문 그대로** 뽑는다. 대개 숫자가 충돌하는 문장(“의원은 6,868원이고 응급실은 22만원입니다”), 통념이 깨지는 문장, 손해가 확정되는 문장이다. 이미지 1장당 훅 1개를 배정하며, 이것이 프롬프트의 출발점이다
- 🆕 **(v5.0) 충돌하는 수치 쌍**: A와 B의 배수·차액. 3-2 ③의 물리량 번역 재료가 된다
- **핵심 피사체**: 글이 실제로 다루는 도구·앱·기기·장면이 무엇인가 (제목의 추상 키워드가 아니라 본문이 묘사하는 구체적 실물). 예: 글이 ChatGPT 화면 활용법을 다루면 이미지도 노트북 위 대화형 AI 화면이어야지, 막연한 '미래적 AI 그래픽'이면 안 된다.
- 본문이 언급하는 **구체적 도구·화면·환경·상황** (앱 이름, 작업 환경, 시간대, 감정선) — 그대로 프롬프트 재료가 됨
- 헤딩(h2/h3) 텍스트 — 각 이미지가 들어갈 위치 주변 섹션의 주제

#### 3-2. 장면 설계 원칙 (v5.0 — 최우선. 정확성보다도 먼저 통과해야 한다)

> 이 루틴의 이미지는 '글을 설명하는 삽화'가 아니라 **'글을 계속 읽게 만드는 장치'**다.
> 정확하기만 한 이미지는 실패다. **정확하면서 사건이 있는** 이미지만 채택한다.

**① 한 문장 테스트 (필수 · 프롬프트 작성 직후 스스로 물어본다)**
"이 이미지를 처음 보는 사람이 **지금 무슨 일이 벌어지는지** 한 문장으로 말할 수 있는가?"
- ❌ "응급실 입구가 있다" · "책상에 서류가 놓여 있다" → **상태 서술 = 탈락**
- ✅ "영수증 한 장이 카운터에서 흘러내려 바닥까지 늘어져 있다" · "봉투 하나가 타서 재만 남았다" → **사건 서술 = 통과**
한 문장이 '있다/놓여 있다'로 끝나면 그 프롬프트는 버리고 다시 쓴다.

**② 본문에서 '훅 문장' 1개를 먼저 뽑는다 (필수 · 기록 대상)**
프롬프트를 쓰기 전에, 본문에서 독자가 가장 놀랄 문장 한 줄을 그대로 인용해 적어둔다. 그 문장 **한 줄만**을 그림으로 옮긴다. 이미지마다 훅 문장이 다르면 3장이 자동으로 달라진다.
> 예(#87): "의원은 6,868원이고 응급실은 22만원입니다. 서른 배가 넘어요."
> 예(#88): "외벌이 부부의 결혼세액공제는 100만원이 아니라 50만원입니다."
훅 문장은 STEP 8 보고에 이미지별로 **반드시 남긴다.**

**③ 숫자를 사물의 물리량으로 번역한다 (문자로 쓰지 않는다)**
글의 핵심 수치는 화면에서 **눈으로 세지거나 비교되는 형태**여야 한다. 글자는 어차피 깨지므로 절대 쓰지 않는다.
| 본문 수치 | 번역 |
|---|---|
| 30배 차이 | 영수증 **길이** (손바닥 한 장 vs 바닥까지 늘어진 한 장) |
| 100만 ↔ 50만 | 지폐 다발 **두께** / 동전 더미 **높이** 정확히 2배 |
| 4일 중 1일만 다름 | 같은 물건 4개 중 **하나만 색·방향이 다름** |
| 7년 유예 | 같은 물건이 **한참 뒤로 밀려 원근상 작게** |
| 90% 본인부담 | 10등분된 것 중 **9조각이 한쪽으로** |

**④ 긴장 요소를 최소 1개 넣는다 (정적 배치 금지)**
다음 중 하나 이상이 프롬프트에 명시돼야 한다 — 기울어짐 / 떨어지는 중 / 반쯤 열림·찢김 / 한쪽만 켜짐 / 넘치기 직전 / 손이 막 놓거나 집는 순간 / 그림자가 물체보다 큼 / 한 개만 줄에서 이탈.

**⑤ 시선 유도점은 1개만 둔다**
화면에서 가장 밝은 곳(또는 가장 채도가 높은 곳)이 **훅 문장의 주어와 일치**해야 한다. 밝은 곳이 두 군데면 주제가 흐려진다. `the only bright accent in the frame is X` 처럼 못 박는다.

**⑥ 범용 은유 금지 목록 (글이 그 물건 자체를 다루지 않는 한 사용 금지)**
⛔ 모래시계 · 저울 · 전구 · 퍼즐 조각 · 체스말 · 화살표 그래픽 · 돼지저금통 · 악수 · 계산기와 안경 플랫레이 · 창밖 도시야경 단독 컷 · 텅 빈 사무실/로비 · 정렬된 문구류 톱뷰.
이 목록은 **어느 글에 붙여도 말이 되기 때문에** 금지한다. 어느 글에나 어울린다는 건 이 글의 이미지가 아니라는 뜻이다.

**⑦ 썸네일 3초 테스트**
완성된 이미지를 폭 320px로 줄였다고 상상한다. 그 크기에서 주제가 안 읽히면 피사체가 너무 작거나 배경이 복잡한 것이다 — 피사체를 화면의 **1/3 이상** 차지하게 다시 잡는다.

#### 3-3. 피사체 정확성 원칙 (2순위 — 사건이 있어야 그다음이다)

> 사건 설계를 통과했더라도 피사체가 글과 다르면 그 이미지는 실패다. 둘 다 만족해야 채택한다.

1. **한국의 실제 환경·사물을 물리적으로 상세 묘사한다.** "Korean office"라고만 쓰면 생성 모델은 서구식 사무실을 만들기 쉽다. 한국 직장·주거·병원·관공서의 실제 디테일(파티션 책상, 스터디카페 좌석, 아파트 거실, 구청 민원실 번호표기, 종합병원 접수 창구 등)을 명시한다.
2. **기기·도구·서류는 실물 형태로 묘사한다.** 갤럭시/아이폰, 맥북/그램, 듀얼 모니터, A4 고지서, 감열지 영수증 등 본문이 언급한 실물을 그대로 쓴다. AI 관련 글이라도 홀로그램·로봇이 아니라 **실제 화면·실제 작업 장면**으로 표현한다.
3. **형태를 정확히 모르면 웹 검색으로 실제 사진을 확인한 뒤** 프롬프트를 작성한다. 추측으로 쓰지 않는다.
4. **잘못 나오기 쉬운 형태를 명시적으로 배제한다.** 예: "no futuristic hologram, no robot, no sci-fi interface", "no Western-style cubicle office".
5. **글자는 배제한다.** UI·자막·문서 텍스트는 깨진 글자로 생성되므로 `no readable text`, `the form is blank with printed rule lines only`, `interface reduced to plain blocks and lines` 처럼 **글자 없는 형태로 지정**한다. 단 ③의 물리량 번역은 글자가 아니므로 제한 없이 쓴다.

#### 3-4. 인물 사용 규칙 (v5.0 완화 — 사람 흔적은 오히려 권장)

v4.0의 "인물 최대 1장" 규칙이 실무에서 "항상 0명"으로 굳어져 장면이 차가워졌다. **개입의 흔적이 있으면 사건이 생긴다.**

- ✅ **권장**: 손·팔뚝·어깨 일부, 뒷모습, 실루엣, 화면 밖으로 나가는 신체 일부. "막 놓는 손", "집으려는 손", "카운터 너머로 내미는 손"
- ✅ 3장 중 **1~2장까지** 신체 부분 컷 허용 (기존 '최대 1장' 폐지)
- ⛔ **금지**: 카메라를 보고 웃는 정면 모델, 전신이 또렷한 연출 인물, 스톡 사진식 팀 회의 장면
- ⛔ 얼굴이 프레임에 들어와야 한다면 초점을 빼거나 프레임 밖으로 잘라낸다

#### 3-5. 조명·카메라·기법

- **시간·빛**: 단순 낮/밤이 아니라 분위기를 명시. "soft morning light from floor-to-ceiling windows", "evening blue hour with city lights reflection", "single overhead fluorescent with hard shadows"
- **카메라·렌즈**: "shot on Sony A7R V with 35mm f/1.8 lens", "Fujifilm X-T5 with 56mm f/1.2"
- **구도·깊이감**: "shallow depth of field", "eye-level", "over-the-shoulder", "worm's eye view"
- **제외 조건 세트**(항상 말미에 부착): `no readable text, no watermark, no logos, no anime style, no generic stock photo look, no posed corporate model smiling at camera, photorealistic`
- 창의적 실사 기법 적극 허용: 미니어처/틸트시프트, 극단적 매크로, 톱뷰 플랫레이, 장노출 빛궤적, 강한 색 대비 조명, 얕은 초점의 전경 가림(foreground occlusion)

**두 상태 비교형**: 글의 핵심이 'A일 때와 B일 때가 다르다'면 **같은 평면 위 두 개의 사물**로 놓는다. 조명·프레이밍 동일 지정이 핵심이다 (`Identical lighting and identical framing on both items so the contrast is obvious at a glance`). 다만 v5.0에서는 여기에 **③ 물리량 번역**과 **④ 긴장 요소**를 반드시 얹는다 — 두 물건을 그냥 나란히 놓기만 하면 그게 바로 '무난함'이다.

#### 3-6. 나쁜 예 → 좋은 예 (2026-08-18 실전 자기비판)

| 글 | v4.0 산출 (통과했지만 무난) | v5.0 재설계 |
|---|---|---|
| #87 의원 6,868원 vs 응급실 22만원 | 야간 응급실 입구, 사람 없음, 붉은 조명 — **상태 서술** | 응급실 접수 창구 위 감열지 영수증 한 장이 카운터 끝으로 흘러내려 **바닥까지 길게 늘어져 있고**, 그 옆에 손바닥만 한 의원 영수증. 붉은 응급 사인이 긴 쪽만 비춘다 → 30배를 **길이**로 |
| #88 결혼세액공제 100만 vs 50만 | 동전 두 더미 (높이는 2배지만 **아무 일도 안 일어남**) | 봉투에서 지폐 다발이 반쯤 빠져나오다 멈췄고, 옆 봉투는 **정확히 절반 두께에서 잘린 단면**을 보인다. 잘린 절반이 책상 밖으로 떨어지는 중 |
| #88 소멸형 vs 지연형 | 봉투 두 개 (재 + 달력 뒤) — **v5.0 기준으로도 통과**. 타버린 재와 밀려난 위치라는 사건이 있음 | 유지. 이 컷이 v5.0이 원하는 수준의 하한선이다 |
| #88 12월 31일 기한 | 창가 모래시계 — **⑥ 범용 은유 위반** | 12월 마지막 주 달력장이 **한 장 뜯겨 나가 공중에 떠 있고**, 그 아래 접수 도장이 찍히다 만 서류. 또는 구청 창구 셔터가 **반쯤 내려온 틈**으로 서류를 밀어 넣는 손 |

#### 3-7. 이미지 역할 분담과 다양성

- **이미지 1 (도입부)**: 훅 문장 중 가장 충격적인 것 1개를 그대로 시각화. 썸네일에서 "뭐지?" 가 나와야 한다
- **이미지 2 (중반)**: 판단이 갈리는 지점의 클로즈업. 두 상태 비교형이 잘 맞는 자리
- **이미지 3 (후반)**: 결론·행동을 사물로. '만족한 사람' 공식 금지, **결과물·변화·잔여물**로 표현
- **(hasStockImg) 히어로**: 제목 한 줄을 그대로 그림으로. 대표이미지로도 쓰이므로 ⑦ 3초 테스트를 가장 엄격히 적용

**다양성 규칙(필수)**: ⓐ 3장의 카메라 거리(원경/중경/접사)를 서로 다르게 ⓑ 최소 1장은 인물 흔적 없는 정물 ⓒ 최소 1장은 신체 부분 컷 ⓓ 같은 소재(달력·영수증·동전 등)를 두 장에서 주인공으로 쓰지 않는다.

⚠️ **히어로와 본문 이미지의 소재가 겹치지 않게 배분한다.** 히어로가 A를 다뤘다면 본문은 B·C·D를 맡는다.

#### 3-8. 프롬프트 조립 체크리스트 (전송 전 7항목 자가 점검)

전송 직전 아래 7개가 프롬프트 문장 안에 실제로 들어 있는지 센다. **하나라도 비면 전송하지 않는다.**

1. 훅 문장(한국어 주석으로 상단에 기록)
2. 사건 동사 — 흘러내리는 / 떨어지는 / 잘린 / 타버린 / 밀어 넣는
3. 물리량 번역 — 길이·높이·두께·개수의 구체적 배수
4. 한국 실물 디테일 — 장소·기물의 실제 형태
5. 시선 유도점 1개 — `the only bright accent is ...`
6. 카메라·렌즈·빛
7. 제외 조건 세트(3-5 말미 문장 그대로)

각 이미지에 대한 **한국어·영문 alt text** (60자 내외)도 미리 작성해 둔다.

**대표이미지(Featured Image) 선정:**

생성 이미지 중 아래 기준으로 1장을 지정한다 (hasStockImg로 히어로를 생성했다면 일반적으로 히어로가 대표이미지).

- 검색 결과 썸네일로 봤을 때 글 내용을 가장 직관적으로 전달하는 이미지
- 선명한 피사체 + 글의 핵심 키워드를 시각화한 장면 우선
- 판단 근거를 한 줄로 메모해 둔다

```javascript
window._featuredImgIndex = 0; // 0=이미지1, 1=이미지2, 2=이미지3 (히어로 생성 시 히어로 우선)
window._featuredReason = "이유";
```

---

#### 3-9. 실물 이미지 사용 원칙 (v5.8 — 2026-08-28 전면 개정)

> 🚨 **개정 사유 (2026-08-28 사용자 지시)**: v5.7은 "글의 핵심이 화면 자체일 때만" 캡처를 허용해, **실물이 있는 글에 실물 이미지를 넣는 것 자체를 막아버렸다.** 방향이 반대였다. 이 루틴은 **Flow 생성 이미지만 써야 하는 루틴이 아니다.** 글에 실제로 존재하는 물건·서비스·회사·장소가 나오고 그 실물 이미지가 필요하다고 판단되면 **넣는다.** 생성은 기본값일 뿐 의무가 아니다.
>
> "웹 이미지를 쓰면 구글이 노출을 안 시켜준다"는 우려는 **사실이 아니다.** 구글에 중복·스톡 이미지에 대한 랭킹 페널티는 없다. 중복본이 **구글 이미지 검색에서 대표 1개만 노출**될 뿐, 웹 검색 순위와는 무관하다.

**① 규칙은 세 줄이다**

1. **공식 출처에서 직접 가져온 이미지는 그냥 쓴다** — 제조사 프레스킷·미디어킷, 공식 사이트·공식 앱 화면 캡처, 공식 SNS·유튜브 채널 이미지, 맥락 안에 들어간 로고.
2. **아마존 제품 이미지는 핫링크만 쓴다.** 다운로드해 WP 미디어에 올리지 않는다 (제휴 약관 위반 → 계정 정지 리스크). `srcset` 도 붙이지 않는다.
3. **출처를 모르는 이미지는 쓰지 않는다.** 구글 이미지 검색 결과, 타인 블로그·유튜버가 찍은 사진, 워터마크 스톡. **이것이 유일한 실질 위험선이다** (Getty·AFP 계열의 자동 탐지 청구).

**② 최소 실무 조건 2개**

- figcaption에 **출처 + 확인일(`Captured YYYY-MM-DD` 또는 `Source: 브랜드 프레스킷, YYYY-MM-DD`)** 을 병기한다.
- **개인정보가 보이는 화면은 제외한다** — 이름·전화번호·주소·계정 ID·얼굴·차량번호. 피할 수 없으면 그 이미지는 포기한다.

**③ 언제 넣는가 — 판단은 단순하다**

글에 **실제로 존재하는 대상**(제품, 앱, 서비스, 회사, 시설, 공공 조회 화면)이 나오고 그 **실제 모습이 독자에게 필요하다고 느껴지면 넣는다.** 특히 아래는 생성 이미지가 **원리적으로 실패**하므로 실물을 쓴다.

- **특정 제품의 형태** — Flow는 그 제품을 본 적이 없으므로 반드시 그럴듯한 가짜를 만든다. 그 제품을 아는 독자에게는 즉시 들킨다
- 앱·웹 UI, 지도, 대시보드, 공문서 양식, 표지판 문구
- 수치·조문·요금표처럼 독자가 출처를 눈으로 봐야 믿는 것

반대로 **분위기·맥락·감성 컷은 계속 생성 이미지가 맡는다.** 제품 글에서도 제품을 클로즈업하지 않는 **사용 맥락 컷**은 생성이 더 낫다 (제품이 프레임에서 작고 초점 밖이면 형태 오류가 드러나지 않는다).

**④ 파이프라인**

| 조달 경로 | 처리 |
|---|---|
| 프레스킷 · 공식 사이트 캡처 · 공식 채널 이미지 | WebP 변환 → WP 미디어 업로드 → STEP 7의 `srcset`·`sizes`·`width/height`·`loading` 동일 적용 |
| **아마존 제휴 이미지** | **업로드 금지.** `<img src="아마존 URL">` 핫링크로 별도 삽입, `srcset` 없음 |

- 파일명·마크업은 증빙 규격을 따른다 — `evidence-*`, `<figure class="evidence-capture">`. STEP 2 분류기 ①②단계에 걸려 **증빙(evidence)으로 계산**된다.
- 따라서 `genCount = min(3 - deco, 5 - evidence - deco)` 가 자동 적용된다. **실물 1장을 넣으면 생성이 1장 줄어든다.** 총량 상한 5장은 그대로 유지한다.
- 아마존 핫링크는 WP 미디어가 아니라 분류기에 안 잡힌다. 총량 감각에는 포함해 관리한다.
- **캡처는 전체 페이지 통짜로 넣지 않는다.** 설명에 필요한 영역만 크롭하고, 크롭 후 폭이 **600px 미만이면 쓰지 않는다**(본문 표시폭에서 뭉개진다). 확대 보간 금지.
- 히어로(대표이미지)는 **제품 글이면 제품 공식 이미지**, 그 외에는 생성 이미지를 쓴다. **UI 스크린샷은 히어로로 쓰지 않는다** — 제목 오버레이와 겹쳐 읽히지 않고 썸네일 클릭률이 낮다.

**⑤ 보고**

STEP 8 보고에 실물 이미지별로 ⓐ 조달 경로(프레스킷 / 공식 캡처 / 공식 채널 / 아마존) ⓑ 출처 도메인 ⓒ 확인일 ⓓ **개인정보 노출 없음 확인** 을 남긴다. 판단이 애매하면 넣지 말고 보고에만 적어 사용자 판단을 받는다.

---

### STEP 4: 글 구조 분석 → 이미지 삽입 위치 3곳 결정

STEP 3-1에서 확보한 `window._rawContent`(반드시 raw)를 사용한다.

⛔ **(v3.4 백포트) 헤딩 '개수' 분위(1/4·2/4·3/4)를 쓰지 않는다.** 헤딩이 문서 후반에 몰려 있으면 이미지가 전부 뒤쪽으로 쏠린다 (2026-08-12 실측: h2 8개의 개수 분위가 문서의 59%·74%·87% 지점에 해당 — 앞 절반이 통째로 빔). 대신 **h2의 문자 위치를 뽑아, 목표 비율에 가장 가까운 h2를 고른다.**

🆕 **(v5.3) 증빙 캡처 인접 구간은 삽입 후보에서 자동 배제한다.** 증빙은 이미 그 섹션의 시각 자료 역할을 하고 있으므로, 그 옆에 생성 이미지를 또 넣으면 두 장이 붙어 버리고 나머지 구간이 비게 된다. **증빙 figure의 문자 위치 ±5%pt 안에 있는 h2는 후보에서 뺀다.**

> 2026-08-19 실측(Post 1175): 자동 계산이 고른 27% 지점이 증빙(29%)과 **305자 거리**였다. 그 h2 바로 뒤에 두 문단, 그다음이 증빙이라 사실상 연속 배치였다. 손으로 43/57/70%로 옮겨 회피했고, v5.3에서 아래 코드로 자동화한다.

```javascript
const c = window._rawContent;
const h2 = []; const re = /<h2[^>]*>([\s\S]*?)<\/h2>/g; let m;
while ((m = re.exec(c)) !== null) h2.push({i: m.index, t: m[1].replace(/<[^>]*>/g, '').replace(/[?&=]/g, ' ').slice(0, 45)});
window._h2 = h2;
const L = c.length;

// (v5.3) 증빙·기존 이미지의 문자 위치를 모두 모아 배제 구간을 만든다
const occupied = [];
const figRe = /<figure[^>]*>[\s\S]*?<\/figure>/g; let f;
while ((f = figRe.exec(c)) !== null) {
  if (/evidence-capture|\/evidence-/i.test(f[0])) occupied.push(f.index);   // 증빙
}
const banned = (pos) => occupied.some(o => Math.abs(o - pos) < L * 0.05);   // ±5%pt
window._occupied = occupied.map(o => Math.round(o / L * 100) + '%');

// 목표 비율(문자 기준) — 도입 / 중반 / 후반
const targets = [0.10, 0.45, 0.72];
const pool = h2.filter(x => !banned(x.i));                                  // 배제 후 후보
const picked = [];
window._insertPoints = targets.map(t => {
  const want = L * t;
  const cand = pool.filter(x => !picked.includes(x.i));
  const best = cand.reduce((a, b) => Math.abs(b.i - want) < Math.abs(a.i - want) ? b : a);
  picked.push(best.i);
  return best.i;
});
// 눈으로 확인: 어떤 섹션 앞에 들어가는지 제목까지 본다
h2.map((x, n) => n + ' ' + Math.round(x.i / L * 100) + '% @' + x.i + (banned(x.i) ? ' [BANNED]' : '') + ' :: ' + x.t).join('\n')
 + '\n--> evidence at ' + window._occupied.join(',')
 + '\n--> picked: ' + window._insertPoints.map(p => Math.round(p / L * 100) + '%@' + p).join(', ')
```

⚠️ **선택된 h2의 제목을 반드시 눈으로 확인하고, 그 섹션 주제와 맞는 이미지를 배정한다.** 비율이 맞아도 FAQ·결론 섹션 앞이면 한 칸 당긴다. 같은 위치가 중복 선택되면 인접 h2로 분산한다. 자동 계산이 어색하면 `window._insertPoints = [h2[a].i, h2[b].i, h2[c].i]` 로 **인덱스를 손으로 지정**한다.

🆕 **(v5.3) 배제 규칙을 적용해도 섹션 주제가 안 맞으면 주제를 우선한다.** 비율은 균등 분포를 위한 수단이지 목적이 아니다. 2026-08-19 회차는 배제 후 후보 중에서도 ⓐ 차액을 다루는 「우리 경우는 얼마나 차이 나나요」에 영수증 길이 이미지 ⓑ 재발권·취소 손실을 다루는 「이미 산 항공권은 어떻게 되나요」에 지폐 낙하 이미지 ⓒ 체크리스트 「8월이 가기 전에 확인할 4가지」에 여권 4권 이미지를 배정해, 43/57/70%로 **비율과 주제가 동시에 맞는 조합**을 찾았다.

ℹ️ **(v4.0) `hasStockImg`로 히어로를 만드는 글은 글 맨 위(0%)가 히어로로 이미 채워진다.** 이때 본문 3장의 목표 비율은 `[0.10, 0.45, 0.72]` 대신 **`[0.30, 0.55, 0.72]`** 로 뒤로 밀어 잡는 편이 분포가 고르다 (2026-08-18 실측: 히어로 2% + 본문 29%/47%/60%로 균등 배치 성공).

(v3) `genCount`가 3 미만이면 `window._insertPoints`에서 앞의 genCount개 위치만 사용한다 — 우선순위는 STEP 2의 이미지 1→3→2 순서를 따른다.

🆕 **(v5.0) 스톡 플레이스홀더가 2개 이상이면 삽입 개수를 그만큼 줄인다.**
`[FEATURED_IMAGE_URL]`·Unsplash 태그가 본문에 **N개** 있으면, 첫 번째는 히어로가 가져가고 **나머지 (N−1)개 자리는 본문 이미지가 교체로 소비**한다 (STEP 7-2.5). 따라서 실제로 **새로 삽입할 위치는 `genCount − (N−1)` 개**다. 이 값을 무시하고 genCount개를 그대로 삽입하면 총량 상한 5장을 넘긴다.

```javascript
// 삽입 위치 개수 확정 — STEP 2의 stock 수(window._cls[i].stock)를 그대로 쓴다
const stockN = window._cls[0].stock;                       // 예: 2
window._replaceSlots = Math.max(0, stockN - 1);            // 본문 이미지가 교체로 소비할 개수 (예: 1)
window._insertN = Math.max(0, window._insertPoints.length - window._replaceSlots);
window._insertPoints = window._insertPoints.slice(0, window._insertN);
'stock:' + stockN + ' replaceSlots:' + window._replaceSlots + ' insertN:' + window._insertN
```

> 2026-08-18 #88 실측: stock 2 · genCount 3 → 교체 소비 1장(45% 자리) + 신규 삽입 2장(20%·71%) + 히어로 1 + 증빙 1 = **정확히 5장**. 교체 자리는 이미 본문 흐름에 맞게 배치돼 있으므로 **삽입 목표 비율 계산에서 그 구간은 빼고 잡는다.**

(v3.2 백포트) 다만 **이미 이미지가 있는 글에 1~2장을 보충하는 경우**에는 기계적으로 도입부를 쓰지 말고, 기존 이미지들의 본문 내 위치(index)를 먼저 구해 **이미지가 가장 오래 비어 있는 구간**의 헤딩을 고른다. 보충의 목적은 개수 채우기가 아니라 공백 메우기다.

ℹ️ **(v3.4 백포트) raw 위치와 렌더 후 화면 위치는 다르다.** ez-toc 목차는 렌더 시점에 첫 h2 앞으로 삽입되므로, raw에서 첫 h2 바로 앞에 넣은 이미지는 화면에서 **본문 도입 → 이미지 → 목차** 순으로 보인다. 이 배치는 정상이며 문제가 아니다. 최종 위치는 STEP 7.5에서 렌더 기준으로 실측한다.

---

### STEP 5: Google Flow에서 이미지 생성 및 캡처 (v5.1 — 그리드 상주 · 일괄 처리)

Chrome MCP로 새 탭을 열고 사용자의 Flow 프로젝트로 이동한다:

`https://labs.google/fx/ko/tools/flow/project/6a6af995-4d64-4bbb-8e97-4be7aa267e6d`

🌐 **(v6.1) 이 URL은 `https://flow.google.com/project/6a6af995-4d64-4bbb-8e97-4be7aa267e6d` 로 리다이렉트된다** (2026-09-04 실측). 탭 목록에 `flow.google.com` 이 보이면 정상이다. 그리드 이미지는 **`flow-content.google`** 에서 서빙되므로 **페이지와 이미지의 출처가 다르다** — 5-5의 교차 출처 캡처 경로가 필요한 이유다.

ℹ️ KoreaPlug와 동일한 프로젝트를 공용으로 쓴다. 사이트별로 프로젝트를 분리하고 싶으면 이 URL만 교체하면 되며, 나머지 절차는 동일하다.

⚠️ **Flow 세션 만료 대응 (2026-08-26 신설)** — 프로젝트 URL 접속 시 `accounts.google.com/.../accountchooser` 또는 `/signin/oauth/v3/consent` 로 리다이렉트되면 labs.google 세션이 만료된 것이다. 2026-08-26 실측: `/tools/flow` 로 다시 들어가도 동일하게 튕기므로 **자동 복구되지 않는다.**

- ✅ **계정 선택 화면(accountchooser)에서 `leejc0404@gmail.com` 을 클릭하는 것은 허용된다** (2026-08-26 사용자 지시). 이어지는 OAuth 동의 화면의 `계속`·`허용` 도 같은 지시에 포함된다.
- ⛔ **다만 비밀번호 입력 화면이 나오면 즉시 중단한다.** 자격증명 입력은 어떤 경우에도 루틴이 대신하지 않는다. 이때는 아래 보고 절차를 따른다.
- ⛔ 계정 목록에 `leejc0404@gmail.com` 이 없으면(= 브라우저 프로필에서 로그아웃됨) 임의로 다른 계정을 고르지 않는다. 중단하고 보고한다.
- 중단 시 보고에 "Flow 세션 만료 — 사용자 직접 로그인 필요"를 기록하고, **STEP 3까지의 산출물(대상 글·분류표·삽입 위치·프롬프트 전문)을 함께 남긴 뒤** 종료한다. 글 본문·상태는 건드리지 않는다.
- 사용자 조치 안내: "Chrome에서 https://labs.google/fx/ko/tools/flow 에 직접 로그인해 주세요."
- 다음 실행이 STEP 1의 2일 소급 규정으로 따라잡으므로 누락은 발생하지 않는다.

#### 5-1. 생성 설정 확인 (v5.6 — 매 실행 필수. '최초 1회'로 끝내지 않는다)

⛔ **① 에이전트 토글 상태를 눈으로 확인한다. 이것이 가장 먼저다.**

입력창 좌하단 `에이전트` 칩이 **밝은 배경 = ON**, **어두운 배경 = OFF** 다. ON이면 클릭해 끈다. 확인은 **(v6.1) `zoom` 이 아니라 아래 JS 한 줄로 한다** (v5.9 zoom 금지와의 모순 해소). 설정 칩의 텍스트에 `crop_16_9` 와 `x2`, `Nano Banana 2` 가 함께 잡히면 ②의 4개 항목도 이 한 줄로 끝난다.

```javascript
// (v6.1) 에이전트 OFF · 설정 칩 확인 — 2026-09-04 실측 UI 기준
const bs = Array.from(document.querySelectorAll('button'));
const ag = bs.find(x => /에이전트/.test(x.textContent || ''));
const cfg = bs.find(x => /설정 트리거/.test(x.getAttribute('aria-label') || ''));
'agentPressed:' + (ag ? ag.getAttribute('aria-pressed') : 'na')          // false 여야 정상
 + ' cfg:' + (cfg ? (cfg.textContent || '').replace(/\s+/g, ' ').slice(0, 60) : 'na')   // "Nano Banana 2 crop_16_9 x2" 여야 정상
```

- `agentPressed:true` 면 칩을 클릭해 끄고 다시 확인한다
- `cfg` 에 `crop_16_9`·`x2`·`Nano Banana 2` 중 하나라도 빠지면 ②의 설정 패널을 열어 고친다. `Lite` 가 섞여 있으면 모델이 잘못 잡힌 것이다

> 🚨 **2026-08-26 KoreaPlug 실측 (같은 Flow 프로젝트를 공유하므로 이 루틴도 동일 위험)**: 토글 ON 상태로 제출한 프롬프트가 별도 채팅 세션(`제목 없는 세션`)으로 넘어가 재해석됐고("I'm going to generate 2 images based on your detailed description…"), **2장 모두 `실패`** 로 끝났다. 세션 패널이 그리드를 덮어 **실패 사실을 즉시 알아채지도 못했다.** 舊 지침은 "에이전트를 쓰지 않는다"고만 적고 **상태 확인 절차가 없었다.**
> 복구: 세션 패널 우상단 `✕` 로 닫으면 그리드가 돌아온다. 실패분은 WP에 올라가지 않으므로 삭제 대기 항목이 아니다.

⛔ **② 설정 칩을 열어 4개를 모두 확인한다. 기본값이 실행마다 달라져 있다.**

- 모드: **이미지** (동영상 아님)
- 비율: **16:9**
- 장수: **x2** — 2026-08-25는 `x1`(동영상 모드), 2026-08-26은 `x1`(이미지 모드)이었다. 칩이 `x1 x2 x3 x4` 로 붙어 있어 **x3를 잘못 누르기 쉬우니** 저장 전 재확인
- 모델: **Nano Banana 2** — 2026-08-26 실측 기본값은 **`Nano Banana 2 Lite`** 였다. 드롭다운에 `Nano Banana Pro / Nano Banana 2 / Nano Banana 2 Lite` 셋이 뜨므로 **가운데**를 고른다
- 마지막에 **저장** 버튼을 누른다. 누르지 않으면 반영되지 않는다

확인 후 입력바에 **`Nano Banana 2 ▭ x2`** 가 표시되면 정상이다. 이 표시가 5-2 투입 전 마지막 관문이다.

🆕 **(v5.5) 패널은 `동영상` 모드로 열려 있을 수 있다.** 2026-08-25 실측: 칩이 `동영상 · 720p · 4s · x1` 이었다. **`이미지` 를 먼저 누르면 패널의 두 번째 줄이 `프레임/애셋` 에서 `16:9 / 4:3 / 1:1 / 3:4 / 9:16` 으로 통째로 바뀐다** — 즉 `이미지` 클릭 전에 잡아 둔 비율 버튼 좌표는 무효다. 순서를 반드시 **① 이미지 → ② 16:9 → ③ 모델 → ④ x2** 로 지키고, ①과 ② 사이에 스크린샷을 한 장 넣어 좌표를 다시 읽는다.

🆕 **(v5.5) 그리드 상단의 필터 칩을 먼저 확인한다.** `최신순` 옆에 `동영상 ✕` 같은 칩이 남아 있으면 **이미지가 하나도 안 보여** 그리드가 빈 것처럼 오인된다. 칩의 `✕` 를 눌러 해제한 뒤 진행한다.

#### 5-2. 프롬프트 투입 — 건별 검증 · 동시 2건 상한 (v6.1)

> 🚀 **v5.1 핵심은 유지한다: 그리드를 떠나지 않는다.** 다만 v5.2가 "확정 동작"으로 못 박은 **무제한 연속 투입은 현재 Flow에서 성립하지 않는다.**
> 2026-09-04 실측: 2쌍(4장)이 진행 중일 때 전송 버튼이 **`disabled`** 로 바뀌어 3번째 클릭이 무시됐고, 프롬프트는 입력창에 남았다. 그 상태에서 `browser_batch` 안의 다음 `type` 이 이어져 **프롬프트 2+3이 한 문장으로 섞여 전송**됐다 — 폐기물 2장, 재투입 2건. 동시 진행은 **2건까지**다.

**투입 절차 (이미지 N장 = N회 반복 · 한 건이 끝나야 다음 건을 타이핑한다):**

1. 입력창 클릭 → **포커스 검증(아래)** → 프롬프트 타이핑
2. **전송 버튼 `disabled` 해제를 폴링**한다 (아래 ②). 동시 2건이 진행 중이면 한 쌍이 끝날 때까지(약 20~55초) 버튼이 잠겨 있다
3. 버튼이 풀리면 **좌표를 JS로 읽어** 클릭 → **`boxLen` 검증**(아래 ③) → 통과해야 다음 건으로
4. ⛔ **한 `browser_batch` 에 "타이핑 → 클릭 → 다음 타이핑" 을 넣지 않는다.** 배치는 검증 결과를 보고 멈추지 못한다. 허용되는 묶음은 **`타이핑 → disabled 폴링`** 과 **`클릭 → 대기 → boxLen`** 두 종류뿐이며, 그 사이에는 반드시 반환값을 읽는다

🚨 **(v5.5) 첫 프롬프트는 반드시 포커스를 검증하고 넣는다.** 2026-08-25 실측: 하단 입력창을 노렸다고 생각한 클릭이 **상단 검색창에 들어가** 1,000자짜리 프롬프트가 통째로 유실됐고, 그 부작용으로 `동영상` 필터까지 걸렸다.

```javascript
// ① 입력 직전 — 포커스가 하단 프롬프트 입력창(.ProseMirror)에 있는지 확인하고, 전송 버튼 탐색기를 고정한다
window._findSend = () => {
  const pm = document.querySelector('.ProseMirror'); let box = pm;
  for (let i = 0; i < 6; i++) { box = box.parentElement; if (box.querySelectorAll('button').length >= 3) break; }
  const bs = Array.from(box.querySelectorAll('button')); return bs[bs.length - 1];   // 마지막 버튼 = 생성 시작(→)
};
const a = document.activeElement; const sc = 1568 / innerWidth; const b = window._findSend(); const r = b.getBoundingClientRect();
'active:' + a.tagName + ' pm:' + a.classList.contains('ProseMirror') + ' top:' + Math.round(a.getBoundingClientRect().top)
 + ' innerH:' + innerHeight
 + ' send:' + Math.round((r.left + r.width / 2) * sc) + ',' + Math.round((r.top + r.height / 2) * sc)
 + ' sendLabel:' + (b.getAttribute('aria-label') || '-') + ' dis:' + b.disabled
```

- `pm:true` 이고 `top` 이 `innerH` 의 80% 이상이면 정상이다 (2026-09-04 실측: `top 750 / innerH 863`, `sendLabel:생성 시작`, 좌표 `1009,658`)
- 상단 검색창(`top` 이 100 미만)이 잡혔다면 **타이핑하지 말고** ⓐ 검색창 `✕` 로 닫고 ⓑ 필터 칩을 해제한 뒤 ⓒ 다시 하단 입력창을 클릭한다
- ⛔ **(v6.1) 舊 `aria-label` 에 `arrow_forward` 를 찾는 셀렉터는 잡히지 않는다.** 현재 UI는 `aria-label="생성 시작"` 이고 `arrow_forward` 는 아이콘 텍스트다. `[role="textbox"]` 도 없다 — 입력창은 `.ProseMirror` 다
- 2번째 프롬프트부터는 전송 직후 포커스가 입력창에 유지되므로 포커스 검증은 생략해도 된다. **좌표는 매번 다시 읽는다** (입력창이 위로 자라도 버튼 y는 대개 유지되지만 가정하지 않는다)

```javascript
// ② 타이핑 직후 — 전송 버튼이 풀릴 때까지 최대 30초 폴링 (CDP 45초 상한 안쪽). 'wait' 면 같은 호출 반복
let res = 'wait';
for (let t = 0; t < 6; t++) { if (!window._findSend().disabled) { res = 'enabled'; break; } await new Promise(r => setTimeout(r, 5000)); }
res + ' len:' + document.querySelector('.ProseMirror').textContent.trim().length
```

- **빈 입력창에서도 버튼은 `disabled`** 다. 그러므로 이 폴링은 반드시 **타이핑 뒤에** 돌린다
- `enabled` 가 나오기 전에는 클릭하지 않는다. 클릭이 씹혀도 텍스트는 남아 있으므로 재타이핑은 불필요하다

```javascript
// ③ 클릭 직후(2~3초 대기 후) — 입력창이 비었는지로 전송 성공을 판정한다
'boxLen:' + document.querySelector('.ProseMirror').textContent.trim().length   // 20 미만이면 전송 성공 (placeholder 14자)
```

- `boxLen` 이 20 이상이면 **전송이 안 된 것이다.** 다음 프롬프트를 타이핑하지 말고 ②로 돌아가 버튼이 풀리길 기다렸다가 다시 클릭한다. **이 확인을 건너뛰면 두 프롬프트가 한 문장으로 섞여 둘 다 버려야 한다** (2026-08-31·2026-09-04 두 번 실측)
- `sc` 환산이 필요한 이유: **스크린샷 폭(1568)과 뷰포트 폭(`innerWidth`)이 다를 수 있다.** 2026-09-04 실측 `innerWidth 1920 → sc 0.817`

**(v5.0) 전송 전에 STEP 3-8의 7항목 체크리스트를 반드시 센다.** 하나라도 비면 전송하지 않고 프롬프트를 고친다.

⛔ **(v6.1) v5.2의 "남은 프롬프트를 전부 연속 투입" 조항은 폐기한다.** 2026-08-18의 "1차 74% 진행 중 2차 투입 → 병렬 시작" 실측은 여전히 맞다 — 다만 그것이 **2건 상한 안**의 이야기였을 뿐이다. 3건째부터는 버튼이 잠긴다. 4장 기준 실제 흐름은 `1·2 투입(병렬) → 1쌍 완료 대기 → 3 투입 → 1쌍 완료 대기 → 4 투입` 이고, 총 소요는 약 3~4분이다.

⏱ 한 쌍당 **약 20~55초**(2026-08-18 실측 50~56초), 2쌍 병렬 시 **약 60초**. **한 쌍이 90초를 넘기면 그 건만 재전송**한다 (나머지는 그대로 둔다).

#### 5-3. 완료 대기 — 30초 분할 폴링 (v5.3 · CDP 45초 상한 대응)

⛔ **진행 상태 확인에 스크린샷을 먼저 쓰지 않는다.** 2026-08-18 회차는 진행률 확인용 스크린샷만 12장을 찍었고 그중 절반이 "아직 99%"였다. 스크린샷은 호출·토큰 모두 비싸다. 아래 **문자열 반환 폴링**을 1순위로 쓴다.

🚨 **(v5.3 최중요 정정) `javascript_tool` 안의 대기에는 상한이 없다는 v5.1·v5.2의 서술은 틀렸다.**
Chrome MCP는 이 도구를 CDP `Runtime.evaluate` 로 실행하며 **45초 하드 타임아웃**이 걸려 있다. 2026-08-19 실측:

| 시도 | 루프 | 결과 |
|---|---|---|
| 1회차 | `t < 24` (최대 120초) | ❌ `CDP Runtime.evaluate timed out after 45000ms` |
| 2회차 | `t < 7` (최대 35초) | ❌ 동일 — 렌더 부하 중이면 35초도 넘긴다 |
| 폴백 | `computer:wait` + 스크린샷 | ✅ 정상 |

→ **폴링 1회의 상한을 30초(6×5초)로 고정하고, 미완료면 같은 호출을 다시 던진다.** 한 호출에 전부 담으려 하지 않는다.

🚨 **(v5.5) `prog()` 셀렉터를 그리드 하위로 한정하고, 정체(stall) 판정을 함께 쓴다.**
2026-08-25 실측: 8장이 **전부 완성된 뒤에도** `prog:4 big:18` 이 3회 연속(약 90초) 그대로 반환됐다. `div,span,p` 전체를 훑는 舊 셀렉터가 **진행률 카드가 아닌 `%` 텍스트**(설정 패널 잔상 등)를 계속 잡은 것이다. 결국 스크린샷을 찍고서야 완료를 알았다 — 폴링이 오히려 시간을 잡아먹었다.

```javascript
// (v5.5) 완료 판정 — ⓐ 그리드 하위로 한정한 진행률 카드 ⓑ 이전 호출 대비 정체 여부
// 기대치 = 투입한 프롬프트 수 × 2 (그리드 기존분은 지연 로딩으로 개수가 흔들리므로 절대값 비교를 피한다)
const gridRoot = document.querySelector('main') || document.body;
const prog = () => Array.from(gridRoot.querySelectorAll('div,span,p'))
  .filter(e => e.children.length === 0
            && /^\d{1,3}%$/.test((e.textContent || '').trim())
            && e.closest('img,video,[class*=card],[class*=grid],[class*=tile]') !== null   // 카드 안에 있는 것만
            && e.getBoundingClientRect().width > 0).length;                                 // 화면에 보이는 것만
const big = () => Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 1000).length;

const prev = window._pollPrev || {p: -1, b: -1, same: 0};
let res = 'wait';
for (let t = 0; t < 6; t++) {                        // ⛔ 30초 — CDP 45초 상한 안쪽으로 고정
  if (prog() === 0) { res = 'done big' + big(); break; }
  await new Promise(r => setTimeout(r, 5000));
}
// 정체 판정: 직전 호출과 prog·big 이 모두 같으면 진행이 멈춘 것 → 스크린샷 1장으로 눈으로 확인한다
const now = {p: prog(), b: big()};
now.same = (now.p === prev.p && now.b === prev.b) ? prev.same + 1 : 0;
window._pollPrev = now;
'prog:' + now.p + ' big:' + now.b + ' same:' + now.same + ' ' + res
```

- 반환값이 `wait` 면 **같은 코드를 그대로 다시 호출**한다. 4쌍 기준 보통 2~3회면 끝난다
- 🆕 **`same` 이 2 이상이면 폴링을 신뢰하지 않는다.** 값이 두 번 연속 안 움직였다는 뜻이므로 **스크린샷 1장을 찍어 눈으로 완료를 확인**하고, 완료면 그대로 5-4로 넘어간다. `prog` 이 0이 아니어도 화면에 진행률 카드가 없으면 **완료다**
- **2회 연속 CDP 타임아웃이 나면 폴링을 포기하고** `browser_batch` 의 `computer:wait 8초 → screenshot` 으로 전환한다. 진행률 카드가 전부 사라졌으면 완료다
- 진행률 카드가 사라진 직후에도 썸네일은 **블러 플레이스홀더로 잠깐 남는다.** 이때 캡처하면 흐린 이미지가 저장되므로, `big()` 이 목표치를 채운 뒤 **8초를 더 준다**

ℹ️ **(v5.1 실측) 그리드 이미지는 지연 로딩된다.** 2026-08-18 콜드 로드 측정: 6초·14초 시점 `img 0개`, **26초에 18개**. 그래서 ⓐ 완료 판정을 **절대 개수가 아니라 `prog()===0`** 로 잡고 ⓑ **그리드를 떠났다가 돌아오는 동작 자체를 피한다**(돌아오면 이 20여 초를 다시 낸다).

⚠️ **(v5.3) 스크린샷 호출도 30초 CDP 상한에 걸린다.** 2026-08-19에 `Page.captureScreenshot timed out after 30000ms` 가 4회 발생했다. 전부 **직후 단독 재호출로 성공**했으므로, 배치 안에서 스크린샷이 실패하면 실패로 처리하지 말고 **스크린샷만 따로 한 번 더 부른다.**

#### 5-4. 채택 판정 — 그리드에서 끝낸다 (v5.1 에디터 진입 폐지 · v5.9 `zoom` 금지)

> 🚀 **(v5.1 실측) Flow 그리드 썸네일은 원본 해상도다.** 2026-08-18 확인: `naturalWidth 1376×768`, 화면 표시 폭만 318px. **캡처도 판정도 그리드에서 전부 가능하므로 에디터 뷰에 들어갈 이유가 없다.**
> 舊 절차(썸네일 클릭 → 로딩 → 스크린샷 → ← 클릭 → 그리드 재로딩 → 재클릭 → 스크린샷)는 이미지당 6~7회 호출이었고, 5장이면 30회를 넘겼다. **전부 삭제한다.**

판정 절차:

1. **그리드 전체 스크린샷 1장**을 찍는다 (전 이미지 후보가 한 화면에 들어온다)
2. 각 쌍에서 아래 기준으로 채택본을 고른다
3. 손 왜곡·글자 잔존처럼 세밀한 확인이 필요하면 **전체 스크린샷을 한 장 더 찍는다.** ⛔ **(v5.9) `computer:zoom` 은 쓰지 않는다** — 아래 경고 참조

⛔ **(v5.9) Flow 탭에서 `computer:zoom` 을 호출하지 않는다. 탭이 복구 불가능하게 망가진다.**
2026-08-31 실측: zoom 호출이 `Page.captureScreenshot` 타임아웃과 함께 탭에 **뷰포트 에뮬레이션을 고착**시켰다 — `outerWidth 1920×1040` 인데 `innerWidth/innerHeight` 가 **981×184** 로 굳었고, `resize_window` 를 두 번 불러도 돌아오지 않았다. 그 상태에서 고정 좌표 클릭이 전부 빗나가 프롬프트가 유실되고 검색창·필터가 오염됐다.

- 세밀 확인이 필요하면 **전체 스크린샷을 다시 찍는다.** 4열 기준 카드 폭이 313px라 손·글자 이상은 대개 이 크기에서도 보인다
- 그래도 판별이 안 되면 **5-5의 RGB 서명**으로 쌍을 먼저 확정한 뒤, 애매한 카드 1장만 **canvas로 뽑아 dataURL로 확인**한다 (캔버스 경로는 뷰포트와 무관하다)
- **이미 고착됐다면 유일한 복구는 탭 폐기·재생성이다** — `tabs_close_mcp` 로 닫고 새 탭에서 프로젝트 URL을 다시 연다. `window._img*` 는 사라지지만 **그리드의 생성물은 그대로 남아 있으므로 재생성은 불필요**하고, 캡처만 다시 하면 된다 (그리드 재로딩 약 20초)

- 🆕 **(v5.0) 밋밋함 판정 — 이 항목을 가장 먼저 본다.** 이미지를 보고 **"지금 무슨 일이 벌어지는가"를 한 문장으로 말할 수 있는가**(3-2 ①). 말할 수 없거나 문장이 '있다/놓여 있다'로 끝나면 **정확해도 탈락**이다
- 🆕 **(v5.0) 훅 문장이 화면에 실제로 구현됐는가** — ③ 물리량(길이·높이·두께 배수)이 눈으로 비교되는가. 배수가 애매하면 탈락
- 핵심 피사체가 **글 내용·실제 한국 환경**과 일치하는가 (STEP 3-3 기준)
- 글 제목을 아는 독자가 봤을 때 "글 내용과 맞는 이미지"라고 느낄 것인가
- 왜곡된 손·어색한 텍스트·SF풍 그래픽·서구식 환경 등 이상 요소가 없는가
- 다양성 규칙(3-7)을 해치지 않는가 — 앞서 채택한 이미지와 카메라 거리·피사체 유형·주인공 소재가 겹치면 다른 쪽을 고른다
- 🆕 **(v5.0) 썸네일 3초 테스트** — 그리드 썸네일 크기(318px)에서 주제가 읽히는가. 안 읽히면 피사체를 더 크게 잡아 재생성. **그리드 판정은 이 테스트를 자동으로 수행하는 셈**이라 v5.1에서 오히려 정확해졌다
- **둘 다 부적합할 때만** 재생성한다. 이때 **밋밋함이 사유면 '더 정확하게'가 아니라 '사건을 추가'하는 방향으로** 고친다 — 동사(흘러내리는·잘린·떨어지는)와 배수를 문장에 넣는다. 동일 프롬프트 재전송 금지. 수정 1회 후에도 어긋나면 해당 이미지 건너뜀.

#### 5-5. 캡처 — 이미지 탭에서 일괄 · 크롭 후 다운스케일 (v5.4 · v5.9 RGB 서명 · v6.1 교차 출처 경로)

Flow 워터마크(✦)는 이미지 **모서리가 아니라 안쪽**, 상대좌표 **(0.925W, 0.875H)** 에 고정돼 있다 (2026-08-18 실측: 1376×768 기준 중심 ≈ (1273, 672), 크기 ≈ 56×56). 따라서 **`cropRight = 150` 으로 우측만 잘라내면 세로 해상도 손실 없이 제거된다** → 1226×768.

🆕 **(v5.4) 크롭 뒤 목표 폭으로 다운스케일한다.** v4.0에서 Flow로 갈아타며 원본이 **984×469(46만px) → 1226×768(94만px)로 2.05배** 커졌는데, 다운스케일 단계가 없어 그대로 업로드됐다. **본문 표시 폭은 728px**이므로 1226px는 1.68배 과잉이다 (2026-08-19 실측: Post 1175 4장이 57~98KB, KoreaPlug 계열은 최대 154KB).

🌐 **(v6.1) 캡처는 그리드 탭이 아니라 '이미지 탭'에서 한다.** 그리드 이미지는 `flow-content.google` 에서 오고 페이지는 `flow.google.com` 이라 **그리드 탭의 canvas 는 taint 된다** (2026-09-04 실측: 4장 전부 `Tainted canvases may not be exported`, `fetch(cors)`·`crossOrigin='anonymous'` 도 차단). 대신 **이미지 URL 자체를 새 탭으로 열면 그 탭의 출처가 `flow-content.google` 이 되어 같은 호스트의 나머지 이미지도 same-origin 으로 그릴 수 있다.** 그리드 탭은 그대로 두므로 v5.1의 "그리드를 떠나지 않는다"도 지켜진다.

```javascript
// ⓐ Flow 그리드 탭에서 실행 — 채택본 URL을 모아 첫 URL을 새 탭으로 연다 (나머지는 fragment 로 실어 보낸다)
// PICK = 그리드에서 고른 채택본의 인덱스 배열 (좌상단 0부터, 최신이 앞) · 순서는 KEYS(hero, 1, 2, 3)와 맞춘다
const PICK = [8, 4, 3, 1];
const grid = Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 1000);
grid.forEach(i => { i.style.outline = 'none'; });   // (v5.5) 인덱스 대조용 테두리 제거
const urls = PICK.map(n => grid[n] ? grid[n].src : null);
window._imgUrls = urls;
window._imgWin = window.open(urls[0] + '#' + encodeURIComponent(JSON.stringify(urls)));   // ⛔ '_blank' 금지 (v3.3)
(window._imgWin ? 'opened' : 'blocked') + ' missing:' + urls.filter(u => !u).length
// 5초 대기 후 tabs_context_mcp 로 새 tabId 확인 — 제목이 "<uuid> (1376×768)" 로 뜬다
```

- URL에는 서명 쿼리(`Expires`·`Signature`)가 붙어 있다. **javascript_tool 반환값에 URL을 찍지 않는다** — `[BLOCKED: Cookie/query string data]` 로 출력 전체가 막힌다. `hasQuery`·`pathLen` 같은 요약만 찍는다
- fragment(`#…`)는 서버로 전송되지 않으므로 서명을 깨뜨리지 않는다. 2026-09-04 실측: hash 760자, 정상 로드, `document.contentType image/jpeg`, `document.images[0].naturalWidth 1376`
- 서명 URL은 **약 15~20분** 뒤 만료된다. 캡처는 채택 판정 직후에 바로 한다

```javascript
// ⓑ 이미지 탭(출처 flow-content.google)에서 실행 — 4장을 same-origin 으로 그려 크롭·다운스케일·WebP 변환
const urls = JSON.parse(decodeURIComponent(location.hash.slice(1)));
const KEYS = ['_imgHero', '_img1', '_img2', '_img3'];   // hasStockImg 가 아니면 '_imgHero' 를 빼고 PICK 도 3개로
const TARGET_W = 1100;                                  // (v5.4) 목표 폭 — 아래 '왜 1100인가' 참조
const out = [];
for (let k = 0; k < urls.length; k++) {
  if (!urls[k]) { out.push(KEYS[k] + ':MISSING'); continue; }
  try {
    const im = new Image();
    await new Promise((res, rej) => { im.onload = res; im.onerror = () => rej(new Error('load')); im.src = urls[k]; });
    const cw = im.naturalWidth - 150, ch = im.naturalHeight;   // 워터마크 우측 크롭
    const scale = Math.min(1, TARGET_W / cw);                  // (v5.4) 확대는 하지 않는다
    const c = document.createElement('canvas');
    c.width  = Math.round(cw * scale);
    c.height = Math.round(ch * scale);
    const ctx = c.getContext('2d');
    ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';   // (v5.4) 축소 화질 보존
    ctx.drawImage(im, 0, 0, cw, ch, 0, 0, c.width, c.height);   // 크롭 + 축소를 한 번에
    const blob = await new Promise(r => c.toBlob(r, 'image/webp', 0.85));
    window[KEYS[k]] = await new Promise(r => { const rd = new FileReader(); rd.onloadend = () => r(rd.result); rd.readAsDataURL(blob); });
    out.push(KEYS[k] + ':' + c.width + 'x' + c.height + ' ' + Math.round(blob.size / 1024) + 'KB');
  } catch (e) { out.push(KEYS[k] + ':ERR ' + e.message.slice(0, 60)); }
}
window._capDims = out.join(' | ');
window._capDims   // 전부 1100x689 이어야 정상 (2026-09-04 실측: 45/64/65/40KB)
```

- 이제 `window._img*` 는 **이미지 탭**에 있다. STEP 6의 `window.open(WP)` 과 postMessage 는 **이 탭에서** 실행한다 (Flow 그리드 탭이 아니다)
- 이미지 탭은 STEP 6-3 전송이 끝난 뒤 `tabs_close_mcp` 로 닫는다. 그리드 탭은 STEP 7.5 뒷정리 때 닫는다

**왜 1100인가 (900이 아니라)**: 리사이즈본은 WordPress가 자동 생성하는데, **원본이 1024px 미만이면 `large`(1024) 사이즈가 아예 만들어지지 않는다.** 900px로 줄이면 srcset 후보가 300/768/900만 남아 **2배 DPI 화면에서 눈에 띄게 뭉개진다.** 1100px는 ⓐ `large 1024` 생성을 보장하고 ⓑ 원본을 1226 대비 **약 25% 줄이며** ⓒ 아래 7-2의 srcset과 합쳐지면 1배속 독자에게는 768px본(약 35KB)만 전송된다 — 실전송량 기준 **60~80% 감소**다.
**용량을 더 줄여야 하면 `TARGET_W` 만 900으로 낮춘다.** 화질 손실을 감수하는 선택이므로 값을 바꿨다면 STEP 8에 명시한다.

⚠️ **인덱스 확인 필수.** 캡처 전에 아래로 그리드 순서를 한 번 찍어 **어느 인덱스가 어느 프롬프트의 산출인지** 대조한다 (새 이미지가 앞쪽에 쌓인다).

```javascript
Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 1000)
  .slice(0, 12).map((i, n) => n + ':' + i.naturalWidth + 'x' + i.naturalHeight).join(' ')
```

🚨 **(v5.5) 인덱스 대조에 `getBoundingClientRect()` 좌표를 쓰지 않는다 — 화면과 어긋난다.**
2026-08-25 실측: `innerWidth 1568 / dpr 1` 인데도 이미지 rect가 **`left:16` 과 `left:325` 단 두 값**(= 2열)으로 나왔다. 화면은 명백히 **4열**이었다. 좌표로 "몇 번째 칸인지"를 추론하면 **엉뚱한 이미지를 캡처한다.**

대신 **`outline` 마킹 1회**로 DOM 순서와 시각 순서가 일치하는지 눈으로 못 박는다. 호출 2개(마킹+스크린샷)면 끝나고, 이후 모든 인덱스를 신뢰할 수 있다.

```javascript
// (v5.5) 앞 4장에 색 테두리를 입힌다 — 0:빨강 1:연두 2:하늘 3:자홍
const all = Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 1000);
all.forEach((im, n) => {
  im.style.outline = '6px solid ' + (n===0?'red':n===1?'lime':n===2?'cyan':n===3?'magenta':'transparent');
  im.style.outlineOffset = '-6px';
});
'marked ' + all.length
```

- 이어서 스크린샷 1장을 찍어 **빨강이 좌상단 첫 칸인지** 확인한다. 일치하면 DOM 순서 = 시각 순서(좌→우, 위→아래)이므로 그대로 `PICK` 인덱스를 쓴다
- 캡처 코드(위 블록) 첫머리에서 `grid.forEach(i => { i.style.outline = 'none'; })` 로 테두리를 지운다. **테두리는 CSS이므로 `drawImage` 결과에는 들어가지 않지만**, 다음 스크린샷을 헷갈리지 않게 지우는 편이 낫다

🆕 **(v5.9) `outline` 마킹이 흔들리면 RGB 서명으로 쌍을 확정한다 (호출 1회 · 스크린샷 불필요).**
스크린샷 스케일이 뷰포트와 어긋나면 색 테두리조차 신뢰하기 어렵다. 이때는 **각 이미지를 8×5로 축소해 평균 RGB를 뽑는다.** 프롬프트가 다르면 색 온도가 확실히 갈리므로 **어느 인덱스가 어느 프롬프트의 산출인지 즉시 확정된다.**

```javascript
// (v5.9) 앞 8장의 평균 RGB 서명 — 프롬프트별 색 온도로 쌍을 가른다
const all = Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 1000);
const out = [];
for (let n = 0; n < 8; n++) {
  const im = all[n]; if (!im) { out.push(n + ':MISSING'); continue; }
  const c = document.createElement('canvas'); c.width = 8; c.height = 5;
  const x = c.getContext('2d'); x.drawImage(im, 0, 0, 8, 5);
  const d = x.getImageData(0, 0, 8, 5).data;
  let r = 0, g = 0, b = 0;
  for (let i = 0; i < d.length; i += 4) { r += d[i]; g += d[i + 1]; b += d[i + 2]; }
  const px = d.length / 4;
  out.push(n + ':rgb(' + Math.round(r / px) + ',' + Math.round(g / px) + ',' + Math.round(b / px) + ')');
}
out.join(' ')
```

- 2026-08-31 실측: 우편함 컷 `rgb(140,121,87)`·`rgb(114,93,68)`(따뜻한 갈색) vs 병원 창구 컷 `rgb(94,97,91)`·`rgb(106,108,104)`(중성 회색). **인접한 두 인덱스가 비슷한 값을 가지면 그 둘이 한 쌍**이다
- 이 값과 **투입 순서(최신이 인덱스 0, 마지막에 넣은 프롬프트가 앞)** 를 맞추면 좌표·레이아웃을 전혀 보지 않고 `PICK` 을 확정할 수 있다
- 쌍 안에서 어느 쪽을 채택할지는 **전체 스크린샷 1장**으로 판단한다 — RGB는 **쌍 식별용이지 품질 판정용이 아니다**
- 레이아웃 열 수는 창 크기에 따라 4열·5열로 바뀐다. `getBoundingClientRect()` 의 `top` 값이 같은 것끼리 한 행이므로, 행 구성이 궁금하면 rect를 **행 판정에만** 쓰고 **인덱스 확정에는 쓰지 않는다**

⛔ **(v6.1) v4.0의 "Flow는 동일 출처라 canvas taint가 없다"는 서술은 폐기한다.** 2026-09-04부터 페이지(`flow.google.com`)와 이미지(`flow-content.google`)의 출처가 다르다. 그리드 탭에서 `drawImage → toBlob` 을 시도하면 반드시 실패하므로 위 ⓐ→ⓑ 경로만 쓴다. RGB 서명(위)도 같은 이유로 **그리드 탭에서는 `getImageData` 가 taint 로 막힌다** — 서명이 필요하면 이미지 탭에서 URL 배열을 순회하며 같은 방식으로 뽑는다.

⛔ **(v5.1) 캡처가 끝날 때까지 그리드를 떠나지 않는다.** 주소창 navigate·새로고침은 `window._imgUrls`·`window._imgWin` 을 날린다. 에디터 진입은 SPA라 변수는 보존되지만 **복귀 시 그리드 재로딩 20여 초를 다시 내므로 금지**한다. (v6.1) 이미지 탭은 **별도 탭**이므로 이 규칙과 충돌하지 않는다.

---

### STEP 6: 이미지 탭에서 WP admin 새 창 열기 → postMessage로 이미지 업로드 (v6.1 — 실행 탭이 바뀌었다)

**핵심:** `window._img*` 를 가진 탭에서 WP REST API를 직접 fetch하면 CORS로 차단된다. 기존 WP admin 탭에 대한 window 참조도 얻을 수 없다. 유일하게 작동하는 방법은 그 탭에서 `window.open()`으로 새 WP admin 창을 열고 그 참조에 postMessage를 보내는 것이다.

🌐 **(v6.1) `window._img*` 는 이제 Flow 그리드 탭이 아니라 5-5의 이미지 탭(`flow-content.google`)에 있다.** 그러므로 6-1·6-3은 **이미지 탭에서** 실행한다. Flow 그리드 탭에서 실행하면 `window[key]` 가 전부 undefined 라 `sent:0` 이 된다.

**6-1. 이미지 탭에서 새 WP admin 창 열기:**

⛔ **(v3.3 백포트) 두 번째 인자 `'_blank'` 를 넘기지 않는다.** `'_blank'` 로 열린 탭은 Chrome MCP 탭 그룹 **밖에** 생성되어 `tabs_context_mcp` 목록에 나타나지 않고, 그 결과 6-2의 리스너 주입이 불가능해져 업로드 경로 전체가 막힌다.

```javascript
// 이미지 탭(flow-content.google)에서 실행 — 새 tabId가 생성됨
window._wpWin = window.open('https://0and1life.com/wp-admin/media-new.php');
window._wpWin ? 'window opened' : 'blocked'
// 6~8초 대기 후 tabs_context_mcp로 새 tabId 확인
```

**복구 절차** — 이미 `'_blank'` 로 열어 탭이 목록에 없다면, 이미지 탭에서 아래를 실행해 닫고 위 코드로 다시 연다. `window._img*` 는 이미지 탭 heap에 그대로 남아 있으므로 **이미지 재생성은 필요 없다.**

```javascript
window._wpWin.close();
window._wpWin = window.open('https://0and1life.com/wp-admin/media-new.php');
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

**6-3. 이미지 탭에서 전 이미지를 한 번에 전송 (v5.1 — 건별 대기 폐지 · v6.1 실행 탭 변경):**

⛔ **(v5.1) 전송 사이에 6~8초씩 기다리지 않는다.** 업로드는 서로 독립적이고 리스너가 비동기라 **연속 전송해도 안전**하다. v4.0 방식(건별 8초 대기 + 건별 확인)은 5장 기준 약 40초와 호출 8회를 그냥 버렸다.

```javascript
// 이미지 탭에서 1회 실행 — 전 이미지를 연속 전송
const SLUG = 'SLUG';
const SEND = [
  ['_imgHero', 'hero', 'ALT_HERO'],   // hasStockImg인 경우만
  ['_img1',    '1',    'ALT_1'],
  ['_img2',    '2',    'ALT_2'],
  ['_img3',    '3',    'ALT_3']
];
let sent = 0;
for (const [key, n, alt] of SEND) {
  if (!window[key]) continue;
  window._wpWin.postMessage({
    dataUrl: window[key],
    filename: '0and1life-' + SLUG + '-' + n + '.webp',
    altText: alt
  }, 'https://0and1life.com');
  sent++;
}
'sent:' + sent
```

전송 후 WP admin 탭에서 **1회만 폴링**한다 (건별 확인 폐지):

```javascript
// 목표 개수에 도달할 때까지 최대 40초 폴링 — 호출 1회로 끝난다
window._upPoll = null;
(async () => {
  for (let t = 0; t < 20; t++) {
    if (window._uploadedIds.length + window._upErrors.length >= N_SENT) break;
    await new Promise(r => setTimeout(r, 2000));
  }
  window._upPoll = 'up:' + window._uploadedIds.length + ' err:' + window._upErrors.length
    + ' ids:' + window._uploadedIds.map(u => u.id).join(',')
    + ' tags:' + window._uploadedIds.map(u => u.tag.replace('0and1life-' + 'SLUG', '')).join(',');
})();
'polling'
```

```javascript
window._upPoll + (window._upErrors.length ? '\nERR: ' + window._upErrors.join(' | ') : '')
```

ℹ️ **(v6.1) `window._uploadedIds` 는 업로드 '도착 순'이라 hero·1·2·3 순서가 보장되지 않는다** (2026-09-04 실측: `hero,3,1,2`). STEP 7에서는 배열 인덱스가 아니라 **파일명 태그로 매핑**한다 — `window._byTag = {}; window._uploadedIds.forEach(u => { const m = u.tag.match(/-(hero|\d)\.webp$/); window._byTag[m[1]] = u; });` 후 `[_byTag['1'], _byTag['2'], _byTag['3']]` 를 본문 순서로 쓴다.

⚠️ 생성 이미지 파일명은 반드시 `0and1life-` prefix를 유지한다 — STEP 2 분류기 ④단계가 이 prefix로 데코를 확정하므로, 규칙을 어기면 다음 실행에서 그 이미지가 미분류(unknown)로 떨어진다.

ℹ️ **(v3.4 백포트) 업로드 결과를 여러 탭에 나눠 받았다면**, `window._uploadedIds` 를 합치는 대신 WP admin 탭에서 미디어를 slug로 재조회해 한곳에 모은다:

```javascript
window._media = null;
fetch('/wp-json/wp/v2/media?search=0and1life-SLUG&per_page=20&_fields=id,slug,source_url,alt_text', {
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
// 1.5) (v3.4 백포트 · 필수) raw 건강 검진 — 하나라도 어긋나면 저장하지 말고 STEP 3-1 복구 절차로
const c = window._finalContent;
'raw:' + (typeof c === 'string' ? 'ok len' + c.length : 'MISSING')
 + ' blocks:' + ((c||'').match(/<!-- wp:/g)||[]).length
 + ' ezToc:'  + ((c||'').match(/ez-toc/g)||[]).length
 + ' h2:'     + ((c||'').match(/<h2/g)||[]).length
 + ' status:' + window._origStatus + ' date:' + window._origDate + ' fm:' + window._curFeatured
```

⚠️ 삽입 위치(`window._insertPoints`)는 **이 시점의 `window._finalContent` 기준으로 다시 계산한다.** STEP 4에서 구한 인덱스는 그 사이 본문이 바뀌면 어긋난다.

🚨 **(v5.4) 삽입 `<img>` 에 `class="wp-image-{미디어ID}"` 와 `loading="lazy"` 를 반드시 넣는다. 이게 이 루틴 최대의 성능 결함이었다.**
WordPress의 `wp_filter_content_tags()` 는 **`wp-image-{ID}` 클래스가 붙은 img에만** `srcset`·`sizes` 를 자동 주입한다. 클래스가 없으면 WP가 만들어 둔 300/768/1024px 리사이즈본이 **하나도 쓰이지 않고 모든 독자가 원본을 통째로 내려받는다.**

> 2026-08-19 실측: 발행분 751·894·1095 전부 `srcset 0 / wp-image 클래스 0 / lazy 0`. Post 1175도 동일 — 표시 폭 728px 자리에 1226px 원본이 그대로 전송되고 있었다. **Flow 전환 이전부터 있던 결함**이며, v4.0의 해상도 증가가 이를 두 배로 키웠다.

```javascript
// 2) 역순으로 이미지 삽입 (뒤→앞 순서로 삽입해야 인덱스가 밀리지 않음)
// (v6.1) 도착 순이 아니라 태그 순으로 — 6-3 하단 참조
window._byTag = {}; window._uploadedIds.forEach(u => { const m = u.tag.match(/-(hero|\d)\.webp$/); window._byTag[m[1]] = u; });
const uploads = [window._byTag['1'], window._byTag['2'], window._byTag['3']].filter(Boolean); // 본문용 3장, 본문 순서
const pts = window._insertPoints;    // [pos1, pos2, pos3]
let c = window._finalContent;

for (let i = 2; i >= 0; i--) {
  const {id, url, alt} = uploads[i];                       // (v5.4) id 필수 — srcset 주입의 열쇠
  const imgBlock = '\n<figure style="margin:20px 0">\n  <img class="wp-image-' + id + '" loading="lazy" decoding="async" style="width:100%;display:block;height:auto;border-radius:8px;" src="' + url + '" alt="' + alt + '" />\n</figure>\n';
  c = c.slice(0, pts[i]) + imgBlock + c.slice(pts[i]);
}
window._newContent = c;
'inserted, new len: ' + c.length + ' order:' + uploads.map(u => u.tag.slice(-6)).join(',')
 + ' wpImgClass:' + ((c.match(/wp-image-\d+/g) || []).length)
```

⚠️ **히어로(첫 화면 이미지)에는 `loading="lazy"` 를 붙이지 않는다.** LCP 요소를 지연 로딩하면 오히려 느려진다. 7-2.5의 스톡 교체 코드가 히어로를 다루므로 그쪽에서 `fetchpriority="high"` 를 넣는다.

```javascript
// 2.5) (v5.0) 기존 스톡 이미지 교체 — 첫 번째만 히어로, 나머지는 본문 이미지로 순차 교체
// ⛔ v4.0처럼 전부 히어로로 바꾸면 스톡이 2개인 글에서 같은 이미지가 본문에 두 번 박힌다
//    (2026-08-18 #88 Post 1160에서 실측 — [FEATURED_IMAGE_URL] 2곳)
// img 태그의 src와 alt만 바꾸고 나머지 마크업(제목 오버레이 등)은 유지한다
const hero = window._uploadedIds.find(u => u.tag && u.tag.includes('hero'));
const body = window._uploadedIds.filter(u => u.tag && !u.tag.includes('hero'));
if (hero) {
  let n = 0;
  window._newContent = window._newContent.replace(/<img[^>]*>/g, (tag) => {
    if (!/unsplash\.com|pexels\.com|pixabay\.com|FEATURED_IMAGE/.test(tag)) return tag;
    n++;
    const pick = (n === 1) ? hero : body[n - 2];   // 2번째부터는 본문 이미지를 순서대로 소비
    if (!pick) return tag;                          // 남는 이미지가 없으면 원본 유지 (플레이스홀더는 STEP 8에 보고)
    let t = tag.replace(/src="[^"]*"/, 'src="' + pick.url + '"');
    t = t.match(/alt="[^"]*"/) ? t.replace(/alt="[^"]*"/, 'alt="' + pick.alt + '"')
                               : t.replace('<img', '<img alt="' + pick.alt + '"');
    // (v5.4) wp-image 클래스 주입 — 기존 class 속성이 있으면 뒤에 덧붙인다
    t = t.match(/class="[^"]*"/) ? t.replace(/class="([^"]*)"/, 'class="$1 wp-image-' + pick.id + '"')
                                 : t.replace('<img', '<img class="wp-image-' + pick.id + '"');
    // (v5.4) 히어로는 LCP 요소다 — lazy 금지, 우선 로딩 지정
    if (n === 1) { if (!/fetchpriority=/.test(t)) t = t.replace('<img', '<img fetchpriority="high"'); }
    else if (!/loading=/.test(t)) { t = t.replace('<img', '<img loading="lazy" decoding="async"'); }
    return t;
  });
  window._stockReplaced = n;
  window._bodyUsedInReplace = Math.max(0, n - 1);  // STEP 4에서 삽입 대상에서 제외한 개수와 일치해야 한다
}
'stockReplaced:' + window._stockReplaced + ' (hero 1 + body ' + window._bodyUsedInReplace + ')'
 + ' newLen:' + window._newContent.length
 + ' leftover:' + (window._newContent.match(/FEATURED_IMAGE|unsplash\.com/g) || []).length
```

🆕 **(v5.5) 2.6) 히어로 헤더 오버레이 병합 — 제목이 '그냥 초록 박스'로 남지 않게 한다**

2026-08-25 Post 1278 사용자 지적: **"제목쪽이 그냥 초록색으로 되어 있다."**
원인은 Writer가 만든 본문 구조였다. 원래 이 사이트의 표준 헤더는 **히어로 이미지 위에 제목을 얹는 오버레이형 `<figure>`** 인데(아래 A), 그날 본문은 **초록 헤더 박스 + 그 아래 독립 히어로 `<figure>`** 로 쪼개져 있었다(아래 B). 7-2.5는 `<img>` 의 `src`·`alt` 만 갈아끼우므로 **B는 B인 채로 남는다** — 히어로를 아무리 잘 만들어도 제목 자리는 여전히 단색이다.

```html
<!-- A. 표준(목표) — v6.0 반응형 그리드 스택. position:absolute 를 쓰지 않는다 -->
<figure style="display:grid; margin:0 0 28px; border-radius:16px; overflow:hidden; background:#111;">
  <img class="wp-image-{ID}" fetchpriority="high" style="grid-area:1/1; width:100%; display:block; height:auto; align-self:start;" src="{HERO_URL}" alt="{ALT}" />
  <div style="grid-area:1/1; background:linear-gradient(180deg, rgba(0,0,0,.15) 0%, rgba(0,0,0,.72) 100%);"></div>
  <figcaption style="grid-area:1/1; align-self:end; padding:clamp(14px,3.6vw,26px) clamp(14px,3.2vw,24px); color:#fff;">
    <h1 style="font-size:clamp(16px,4.4vw,26px); line-height:1.35; font-weight:800; margin:0 0 8px; color:#fff;">{제목}</h1>
    <p style="margin:0; font-size:clamp(11px,2.9vw,13px); opacity:.85;">{날짜} · 읽는 시간 {N}분</p>
  </figcaption>
</figure>

<!-- B. 결함형 — 색 헤더 박스 + 아래에 히어로가 따로 (이 구조를 A로 병합한다) -->

<!-- C. 舊 결함형(v5.5~v5.9) — 구조는 A인데 캡션이 position:absolute + 고정 26px.
     모바일에서 캡션이 이미지보다 커져 윗부분이 잘린다. 발견 즉시 A로 정규화한다 -->
```

⛔ **(v6.0) `position:absolute` 캡션은 금지한다.** 절대 위치 캡션은 **자기 높이가 figure 높이에 반영되지 않으므로**, 좁은 화면에서 반드시 넘친다. 위 A의 그리드 스택은 행 높이가 `max(이미지, 캡션)` 이라 **figure가 캡션을 따라 커지고 넘침이 구조적으로 불가능**하다. 넘쳐서 생긴 여백은 그라디언트 `<div>`(기본 `stretch`)와 `figure{background:#111}` 이 덮으므로 흰 글자가 그대로 읽힌다.

⛔ **(v6.0) 히어로 제목·메타의 `font-size` 와 `padding` 은 반드시 `clamp()` 로 쓴다.** 고정 26px은 320px 화면에서 제목 65자를 **6줄**로 밀어내 캡션을 304px까지 키운다 (이미지는 180px). `clamp(16px,4.4vw,26px)` 이면 같은 제목이 **4줄·145px** 로 줄어 이미지 안에 들어간다. 데스크톱에서는 상한 26px에 걸려 **종전과 픽셀 단위로 동일**하다.

**판정과 병합 절차 (저장 전, 7-2.5 직후에 수행):**

```javascript
// (v5.5) 헤더 박스 + 독립 히어로 → 오버레이형 figure 하나로 병합
const hero2 = window._byTag ? window._byTag['hero'] : window._uploadedIds.find(u => /hero/.test(u.tag));
const d = document.createElement('div'); d.innerHTML = window._newContent;

// ① 제목·날짜를 담은 헤더 블록 찾기 — h1을 품고 있고 배경색이 지정된 첫 요소
const h1 = d.querySelector('h1');
const headerBox = h1 ? h1.closest('[style*="background"]') : null;
// ② 히어로 figure 찾기 — 방금 교체한 hero URL을 가진 img의 figure
const heroImg = hero2 ? d.querySelector('img[src="' + hero2.url + '"]') : null;
const heroFig = heroImg ? heroImg.closest('figure') : null;

window._headerMerge = {
  h1: !!h1, headerBox: !!headerBox, heroFig: !!heroFig,
  alreadyOverlay: !!(heroFig && heroFig.querySelector('h1'))     // 이미 A형이면 손대지 않는다
};
JSON.stringify(window._headerMerge)
```

- `alreadyOverlay: true` → **이미 표준 A형이다. 아무것도 하지 않는다.**
- `headerBox: true && heroFig: true && alreadyOverlay: false` → **B형이다. 아래로 병합한다.**
- `headerBox: false` → 테마가 제목을 출력하는 구조다. **병합하지 않고** STEP 8에 "헤더 박스 없음 — 병합 대상 아님"으로 남긴다

```javascript
// 병합 실행 — 헤더 박스의 제목·날짜를 히어로 figure 안으로 옮기고 헤더 박스는 제거한다
if (window._headerMerge.headerBox && window._headerMerge.heroFig && !window._headerMerge.alreadyOverlay) {
  const titleHtml = h1.outerHTML.replace(/<h1([^>]*)>/, '<h1 style="font-size:clamp(16px,4.4vw,26px); line-height:1.35; font-weight:800; margin:0 0 8px; color:#fff;">');
  const metaEl = headerBox.querySelector('p');
  const metaHtml = metaEl ? metaEl.outerHTML.replace(/<p([^>]*)>/, '<p style="margin:0; font-size:clamp(11px,2.9vw,13px); opacity:.85;">') : '';

  // (v6.0) 그리드 스택 — 세 자식을 같은 칸에 겹치고, 행 높이는 max(이미지, 캡션)이 된다
  heroFig.setAttribute('style', 'display:grid; margin:0 0 28px; border-radius:16px; overflow:hidden; background:#111;');
  heroImg.setAttribute('style', 'grid-area:1/1; width:100%; display:block; height:auto; align-self:start;');
  if (!/fetchpriority=/.test(heroImg.outerHTML)) heroImg.setAttribute('fetchpriority', 'high');
  heroImg.removeAttribute('loading');                       // 히어로는 LCP — lazy 금지

  // 기존 figcaption(회색 캡션)은 오버레이 캡션으로 대체한다
  const oldCap = heroFig.querySelector('figcaption');
  if (oldCap) oldCap.remove();

  const shade = document.createElement('div');
  shade.setAttribute('style', 'grid-area:1/1; background:linear-gradient(180deg, rgba(0,0,0,.15) 0%, rgba(0,0,0,.72) 100%);');
  heroFig.appendChild(shade);

  const cap = document.createElement('figcaption');
  cap.setAttribute('style', 'grid-area:1/1; align-self:end; padding:clamp(14px,3.6vw,26px) clamp(14px,3.2vw,24px); color:#fff;');
  cap.innerHTML = titleHtml + metaHtml;
  heroFig.appendChild(cap);

  // 히어로 figure를 헤더 박스 자리로 올리고, 헤더 박스를 제거한다
  headerBox.parentNode.insertBefore(heroFig, headerBox);
  headerBox.remove();

  window._newContent = d.innerHTML;
  window._headerMerged = true;
}
'merged:' + !!window._headerMerged
 + ' h1InFigure:' + ((window._newContent.match(/<figure[^>]*>[\s\S]*?<h1/g) || []).length)
 + ' newLen:' + window._newContent.length
```

⚠️ **병합 후 반드시 확인할 것**
- `h1InFigure` 가 **1** 이어야 한다. 0이면 제목이 figure 밖에 남은 것이고, 2 이상이면 h1이 중복 생성된 것이다
- `<h1>` 개수는 **병합 전후가 같아야 한다** (아래 2.9의 `h1Cnt` 항목)
- 히어로 `<img>` 에 `loading="lazy"` 가 남아 있으면 안 된다 (LCP 저하)
- 이 병합은 **총 이미지 수를 바꾸지 않는다** — 히어로를 옮겨 붙일 뿐이므로 상한 5장 계산과 무관하다

ℹ️ **근본 원인은 Writer 루틴의 헤더 템플릿이다.** 이 조항은 사후 교정이므로, B형이 **2회 이상 연속으로 감지되면** STEP 8에 "Writer 헤더 템플릿 점검 필요"를 🔴로 올린다.

🆕 **2.6b) (v6.0) 반응형 정규화 — 병합 여부와 무관하게 매번 수행한다**

`alreadyOverlay: true` 로 병합을 건너뛴 글에도 **舊 절대위치 캡션(C형)이 그대로 남아 있을 수 있다.** 그래서 반응형 스타일 적용은 병합의 일부가 아니라 **독립된 정규화 단계**로 항상 돌린다.

```javascript
// (v6.0) 히어로 figure를 반응형 그리드 스택으로 정규화한다 — A형·B형 병합분·C형 모두에 적용
const d2 = document.createElement('div'); d2.innerHTML = window._newContent;
const hf = Array.from(d2.querySelectorAll('figure')).find(f => f.querySelector('figcaption h1'));
window._norm = 'no-hero';
if (hf) {
  const im = hf.querySelector('img');
  const cp = hf.querySelector('figcaption');
  const t1 = cp.querySelector('h1');
  const mp = cp.querySelector('p');
  let sh = Array.from(hf.children).find(x => x.tagName === 'DIV');
  if (!sh) { sh = document.createElement('div'); hf.insertBefore(sh, cp); }   // 그라디언트가 없던 글 보강
  hf.setAttribute('style', 'display:grid; margin:0 0 28px; border-radius:16px; overflow:hidden; background:#111;');
  im.setAttribute('style', 'grid-area:1/1; width:100%; display:block; height:auto; align-self:start;');
  im.removeAttribute('loading');
  if (!/fetchpriority=/.test(im.outerHTML)) im.setAttribute('fetchpriority', 'high');
  sh.setAttribute('style', 'grid-area:1/1; background:linear-gradient(180deg, rgba(0,0,0,.15) 0%, rgba(0,0,0,.72) 100%);');
  cp.setAttribute('style', 'grid-area:1/1; align-self:end; padding:clamp(14px,3.6vw,26px) clamp(14px,3.2vw,24px); color:#fff;');
  t1.setAttribute('style', 'font-size:clamp(16px,4.4vw,26px); line-height:1.35; font-weight:800; margin:0 0 8px; color:#fff;');
  if (mp) mp.setAttribute('style', 'margin:0; font-size:clamp(11px,2.9vw,13px); opacity:.85;');
  window._newContent = d2.innerHTML;
  window._norm = 'ok';
}
window._norm
 + ' gridArea:' + ((window._newContent.match(/grid-area:1\/1/g) || []).length)      // 히어로 있으면 3
 + ' clamp:' + ((window._newContent.match(/clamp\(/g) || []).length)                // 히어로 있으면 4
 + ' absCap:' + ((window._newContent.match(/<figcaption[^>]*position\s*:\s*absolute/g) || []).length)  // 0이어야 함
```

- **`gridArea` 3 · `clamp` 4 · `absCap` 0** 이 정상값이다. 하나라도 어긋나면 저장하지 않는다
- 이 단계는 **이미지 개수·본문 텍스트·h1 개수를 바꾸지 않는다** — 스타일 속성만 덮어쓴다
- 그라디언트 `<div>` 가 없던 옛 글에는 **한 개 삽입**되므로 `<div>` 카운트만 +1 될 수 있다. `_evGuard` 의 `imgTags`·`h1Cnt`·`figPair` 는 그대로여야 한다

```javascript
// 2.9) 저장 전 불가침 검증 (v3.4 백포트 — 필수)
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
  wpImgCls:cnt(before, /wp-image-\d+/g) + '->' + cnt(after, /wp-image-\d+/g),          // (v5.4) 이번에 넣은 이미지 수만큼 늘어야 함
  noWpCls: (() => { const t = after.match(/<img[^>]*>/g) || [];                        // (v5.4) 0이어야 함
             return t.filter(x => /0and1life-/.test(x) && !/wp-image-\d+/.test(x)).length; })(),
  lazyCnt: cnt(after, /loading="lazy"/g),                                              // (v5.4) 히어로 제외 본문 이미지 수와 같아야 함
  h1Cnt:   cnt(before, /<h1/g) + '->' + cnt(after, /<h1/g),                            // (v5.5) 좌우 같아야 함 (헤더 병합해도 h1은 1개)
  h1InFig: (after.match(/<figure[^>]*>[\s\S]*?<h1/g) || []).length,                    // (v5.5) 병합했으면 1, 안 했으면 0
  heroLazy:(() => { const t = after.match(/<img[^>]*>/g) || [];                        // (v5.5) 0이어야 함 — 히어로에 lazy 금지
             return t.filter(x => /fetchpriority="high"/.test(x) && /loading="lazy"/.test(x)).length; })(),
  absCap:  cnt(after, /<figcaption[^>]*position\s*:\s*absolute/g),                   // (v6.0) 0이어야 함
  gridArea:cnt(after, /grid-area:1\/1/g),                                            // (v6.0) 히어로 있으면 3
  clampCnt:cnt(after, /clamp\(/g),                                                   // (v6.0) 히어로 있으면 4
  fixed26: cnt(after, /font-size:26px/g)                                             // (v6.0) 0이어야 함 — 고정 26px 잔존
};
Object.entries(window._evGuard).map(([k, v]) => k + ': ' + v).join('\n')
```

⛔ 위 검증에서 하나라도 어긋나면 **저장하지 않는다.** 원인을 해결한 뒤 다시 만든다.
🆕 **(v5.4) `noWpCls` 가 0이 아니면 그 이미지는 srcset을 못 받는다** — 클래스 주입이 빠진 것이므로 저장 금지. `wpImgCls` 증가분이 이번에 넣은 이미지 수와 다른 경우도 마찬가지다.
🆕 **(v5.0) `dupImg` 가 0이 아니면 같은 이미지가 본문에 두 번 들어간 것이다** — STEP 7-2.5의 순차 교체가 제대로 돌지 않았다는 뜻이므로 저장 금지. `stock` 이 →0이 아니면 교체되지 않은 플레이스홀더가 남은 것이다.
🚨 **(v6.0) `absCap` 또는 `fixed26` 이 0이 아니면 저장 금지.** 전자는 절대위치 캡션이, 후자는 고정 26px 폰트가 남아 있다는 뜻이고 **둘 다 모바일에서 제목이 잘리는 원인**이다. 히어로가 있는 글이라면 `gridArea` 는 **3**, `clampCnt` 는 **4** 여야 한다 (히어로가 없는 글은 둘 다 0).

🆕 **(v5.5) `h1Cnt` 좌우가 다르거나 `heroLazy` 가 0이 아니면 저장 금지.** 전자는 헤더 병합이 제목을 잃거나 복제한 것이고, 후자는 LCP 요소에 지연 로딩이 붙은 것이다. `h1InFig` 는 병합을 수행했으면 **1**, `alreadyOverlay`/`headerBox 없음` 으로 건너뛰었으면 **0 또는 1** 이면 정상이다.

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

🚨 **(v3.4 백포트) 상태 전환 방지 — 이 조항을 어기면 사용자 지시 위반이다.**
글의 `post_date` 가 미래이면, `content` 만 POST해도 WP가 `draft` → **`future`(예약발행)** 로 스스로 승격시킨다. 그래서 **모든 저장 POST의 body에 `status: window._origStatus` 를 반드시 포함**한다. 그럼에도 응답 `status` 가 원래 값과 다르면 **즉시 되돌린다**:

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

저장 후 **프론트엔드 프리뷰**(`https://0and1life.com/?p=POST_ID&preview=true`)를 열고 **스크롤하며 삽입된 이미지 전부를 스크린샷으로 확인**한다.

**(v3.4 백포트) 먼저 기계 검증을 돌려 수치를 확보한다:**

```javascript
const H = document.documentElement.scrollHeight;
const imgs = Array.from(document.querySelectorAll('article img, .entry-content img')).filter(i => i.naturalWidth > 300);
imgs.map(i => i.src.split('/').pop().split('?')[0].replace('0and1life-SLUG', 'OL').slice(0, 30)
  + ' nw' + i.naturalWidth + ' @' + Math.round((i.getBoundingClientRect().top + window.scrollY) / H * 100) + '%').join('\n')
 + '\n--- TOC:' + document.querySelectorAll('#ez-toc-container, .ez-toc-container').length
 + ' h2:' + document.querySelectorAll('article h2').length
 + ' tables:' + document.querySelectorAll('article table').length
 + ' broken:' + Array.from(document.querySelectorAll('article img')).filter(i => i.complete && i.naturalWidth === 0).length
```

- **TOC 컨테이너가 정확히 1개**인가? (2개면 본문에 목차가 박제된 것 — STEP 3-1 복구 절차 필요)
- 이미지가 **본문 전체에 고르게 퍼져 있는가?** 히어로 없는 글은 대략 10~15% / 45% / 70%, 히어로 있는 글은 0% / 30% / 50% / 65% 부근
- `broken` 이 0인가? 모든 `nw`(naturalWidth)가 정상인가? (**v5.4 산출물은 `nw 1100`**, v4.0~v5.3 산출물은 1226)
- h2·표 개수가 삽입 전과 같은가?

🆕 **(v5.4) srcset 주입 여부를 렌더 기준으로 확인한다 — 이 검사가 통과해야 다운스케일 효과가 실제로 난다:**

```javascript
Array.from(document.querySelectorAll('.entry-content img')).filter(i => i.naturalWidth > 300)
  .map((i, n) => n + ' disp:' + Math.round(i.getBoundingClientRect().width) + 'px'
    + ' nw:' + i.naturalWidth
    + ' srcset:' + (i.getAttribute('srcset') ? 'YES(' + (i.getAttribute('srcset').split(',').length) + ')' : 'NO')
    + ' sizes:' + (i.getAttribute('sizes') ? 'YES' : 'NO')
    + ' cls:' + (/wp-image-\d+/.test(i.className) ? 'YES' : 'NO')
    + ' loading:' + (i.getAttribute('loading') || 'none')).join('\n')
```

  - 생성 이미지는 전부 `srcset:YES` · `cls:YES` 여야 한다. **하나라도 `NO` 면 그 이미지는 원본이 통째로 전송되고 있다**
  - 히어로는 `loading:none`(또는 `eager`), 본문 이미지는 `loading:lazy` 여야 한다
  - 증빙 캡처는 Draft 루틴 소관이라 `NO` 가 나올 수 있다 — 이 루틴에서 고치지 말고 **STEP 8에 별도 항목으로 보고**한다

**이어서 육안으로 확인한다:**

- 🆕 **(v5.0) 이미지마다 "무슨 일이 벌어지는가"를 한 문장으로 말할 수 있는가?** 전부 '있다/놓여 있다'로 끝나면 그 회차는 프롬프트 설계가 실패한 것이다 — 보고에 명시하고 다음 회차 개선안을 남긴다
- 🆕 **(v5.0) 같은 이미지가 두 번 나오지 않는가?** (스톡 2개 교체 시 특히 확인 — `dupImg` 와 육안 둘 다)
- 🆕 **(v5.3) 같은 src가 2회 잡혔다고 곧바로 중복으로 보고하지 않는다 — 가시성을 먼저 확인한다.** GeneratePress 계열 테마는 대표이미지를 `.featured-image.page-header-image-single` 로 한 번 더 출력하는데, 이 사이트는 **CSS로 `display:none` 처리**돼 있어 화면에는 히어로가 1장만 보인다. 아래로 판정한다:

```javascript
const f = document.querySelector('.featured-image.page-header-image-single');
f ? (() => { const cs = getComputedStyle(f);
  return 'display:' + cs.display + ' vis:' + cs.visibility
   + ' h:' + Math.round(f.getBoundingClientRect().height)
   + ' offsetParent:' + (f.offsetParent ? 'yes' : 'no'); })()
  : 'no theme featured-image block'
```

  `display:none` · `h:0` · `offsetParent:no` 이면 **정상이며 결함이 아니다.** 2026-08-19 Post 1175에서 기계 검증이 히어로를 `0%`·`2%` 두 번 잡았으나 실제 화면은 1장이었고, Post 1160도 동일 구조였다. 이 확인 없이 "중복"으로 보고하면 멀쩡한 배치를 뜯게 된다.
- 각 이미지의 피사체가 글 내용·주변 섹션과 맞는가?
- 🆕 **(v5.3) 생성 이미지와 증빙 캡처가 붙어 있지 않은가?** 렌더 기준으로 **두 이미지 사이 간격이 5%pt 미만**이면 STEP 4의 배제 규칙이 제대로 안 돈 것이다. 2026-08-19 정상 사례: 히어로 2% → 증빙 29% → 38% → 53% → 70%
- 다양성 규칙(3-7)이 지켜졌는가 — 같은 구도·같은 피사체 유형·같은 주인공 소재가 반복되지 않는가?
- 히어로/대표이미지가 정상 반영됐는가?
- 🆕 **(v5.5) 제목이 히어로 이미지 위에 얹혀 있는가?** 글 맨 위를 스크린샷으로 보고, **제목 자리가 단색 박스(초록 등)로 남아 있으면 실패**다 — 7-2.6 병합이 안 돌았거나 조건 판정이 어긋난 것이다. 아래로 렌더 기준 확인:

```javascript
const fig = document.querySelector('.entry-content figure h1, article figure h1');
const box = document.querySelector('.entry-content h1, article h1');
'h1InFigure:' + (fig ? 'YES' : 'NO')
 + ' | h1Bg:' + (box && box.parentElement ? getComputedStyle(box.parentElement).backgroundColor : '-')
 + ' | heroTop:' + (() => { const i = document.querySelector('.entry-content img'); return i ? Math.round(i.getBoundingClientRect().top + window.scrollY) : '-'; })()
```

  `h1InFigure:YES` 면 정상이다. `NO` 이고 `h1Bg` 가 투명이 아닌 색이면 **초록 박스가 그대로 남은 상태**이므로 7-2.6을 다시 돌린다
- 🆕 **(v6.0) 모바일 375px에서 제목이 이미지 안에 온전히 들어가는가?** 데스크톱만 보면 절대 발견되지 않는 결함이다 (2026-08-31에 13건이 이 방식으로 누락돼 있었다). **`resize_window` 는 이 사이트에서 뷰포트를 바꾸지 못하므로**(`innerWidth` 가 그대로다) **같은 원점 아이프레임으로 실측**한다:

```javascript
// (v6.0) 375px 아이프레임 실측 — 프리뷰/발행 페이지에서 실행
const f = document.createElement('iframe');
f.style.cssText = 'position:fixed;left:-4000px;top:0;width:375px;height:1000px;border:0';
f.src = location.pathname + '?nc=' + Date.now();
document.body.appendChild(f);
await new Promise(r => { f.onload = r; setTimeout(r, 15000); });
await new Promise(r => setTimeout(r, 2000));
const d = f.contentDocument;
const fig = d.querySelector('.entry-content figure');
const cap = fig && fig.querySelector('figcaption');
const h1 = cap && cap.querySelector('h1');
const out = !fig ? 'NO-HERO' : (() => {
  const fb = fig.getBoundingClientRect(), cb = cap.getBoundingClientRect();
  const over = -Math.round(cb.top - fb.top);
  return 'vw' + f.contentWindow.innerWidth + ' figH' + Math.round(fb.height)
    + ' capH' + Math.round(cb.height) + ' 여유' + (-over) + 'px'
    + ' fs' + f.contentWindow.getComputedStyle(h1).fontSize + (over > 0 ? '  ❌넘침' : '  ✅');
})();
f.remove(); out
```

  - **여유가 0 이상이면 통과.** 음수면 제목 윗줄이 잘린 것이므로 7-2.6b를 다시 돌린다
  - 여유가 **10px 미만이면 320px(구형 아이폰 SE)에서 위험**하므로 `f.style.width` 를 `320px` 로 바꿔 한 번 더 본다
  - 2026-08-31 기준 정상 예시: 375px에서 `figH204 capH145 여유60px fs16.5px ✅`, 320px에서 여유 6px
- 증빙 캡처가 원래 자리에 그대로 있는가? (`window._evGuard` 확인)
- **워터마크 흔적(✦)이 남아 있지 않은가?** — 남아 있으면 STEP 5-4의 `cropRight` 값을 늘려 재캡처하거나, 이미 업로드된 파일을 0and1life.com **동일 출처**에서 canvas로 다시 읽어 재크롭·재업로드한다.
- 표·TOC·내부링크 등 기존 요소가 삽입으로 깨지지 않았는가?
- **글 상태가 원래대로인가?** (`draft` 는 `draft` 그대로여야 한다)

**뒷정리:** 검증이 끝나면 이 루틴이 만든 탭(Flow 그리드 탭, 이미지 탭, media-new 탭)을 `tabs_close_mcp` 로 모두 닫는다. ⚠️ **(v6.1) 탭을 닫은 직후 같은 `browser_batch` 안에서 다른 탭에 navigate 하면 "not in the same group" 오류가 난다** (2026-09-04 실측). 닫기는 배치 마지막에 두거나, 닫은 뒤 `tabs_context_mcp` 를 한 번 다시 부른다. 사용자가 결과를 바로 볼 수 있도록 **프리뷰 탭 1개만 남긴다.**

---

### STEP 8: 완료 보고

완료 후 아래 내용을 출력:

- 처리한 글 제목 및 Post ID
- **STEP 2 분류 결과 표**: 이미지별 `파일명 => 증빙/스톡/데코 [판정근거]`, 그리고 evidence/stock/deco/genCount
- `unknown`이 있었다면 수동 확인 결과와 재계산된 genCount
- 삽입·교체된 이미지 (media ID + 렌더 기준 위치 %)
- 최종 imgCount, 불가침 검증(`window._evGuard`) 결과 — **blocks·ezToc·h2·table 항목 포함**
- **(v3.4) 글 상태**: 시작 시 status → 종료 시 status. 전환이 발생했다면 복구 여부까지 명시
- **(v4.0) raw 오염 점검 결과**: v3.1 이하로 처리된 글에서 `ezToc>0` 또는 `blocks=0` 이 발견되면 해당 Post ID를 모두 나열하고 **사용자 확인 후 복구**를 제안한다
- 대표이미지: 선정된 이미지, 선정 이유, 설정 결과 (`window._featuredResult`)
- 🆕 **(v5.0) 이미지별 훅 문장**: 본문에서 뽑은 인용 한 줄과, 그것을 어떤 물리량(길이·높이·두께 배수)으로 번역했는지
- 🆕 **(v5.0) 장면 설계 검증**: 이미지별 "무슨 일이 벌어지는가" 한 문장. 상태 서술이면 그 이유와 재생성 여부
- 🆕 **(v5.0) 스톡 교체 내역**: 스톡 N개 중 히어로 1 + 본문 (N−1), `dupImg` 값, 남은 플레이스홀더 수
- 피사체 정확성 검증: 각 이미지별 통과/재시도/건너뜀 여부, **2장 중 어느 쪽을 채택했는지**
- Skip된 경우 그 이유
- **(v4.0) 생성 소요시간**: 이미지별 생성 대기 시간을 기록한다. 한 쌍이 90초를 넘긴 건이 있으면 Flow 지연으로 보고한다
- 🆕 **(v5.1) 실행 효율**: 총 도구 호출 수와 Flow 구간 소요시간. 그리드 이탈 횟수(**0이어야 정상**), 대상 탐색 경로(WP 1회 / Notion 폴백)
- 🆕 **(v5.3) 삽입 위치 대 증빙 간격**: 렌더 기준 이미지 위치를 나열하고, 인접 두 장의 최소 간격이 **5%pt 이상**인지 명시한다. 자동 배제 규칙이 후보를 몇 개 잘라냈는지도 함께 적는다
- 🆕 **(v5.4) 이미지 전송 최적화 결과**: 캡처 해상도(`TARGET_W` 값 포함)와 장당 KB, 렌더 기준 `srcset:YES/NO` · `cls:YES/NO` · `loading` 값. 생성 이미지 중 하나라도 `NO` 면 실패로 보고한다. 증빙 캡처가 `NO` 인 것은 Draft 루틴 소관이므로 별도 항목으로 분리해 적는다
- 🆕 **(v5.3) CDP 타임아웃 발생 횟수**: `Runtime.evaluate`(45초)·`Page.captureScreenshot`(30초) 각각 몇 회였고 어떻게 복구했는지. 폴링 폴백이 발동했다면 그 사실을 남긴다 — 이 수치가 다음 회차의 루프 상한을 조정하는 근거가 된다
- 🆕 **(v6.1) 투입 대기 기록**: 전송 버튼 `disabled` 로 대기한 건수와 대기 시간, `boxLen` 실패로 재클릭한 건수, 프롬프트 병합 사고 여부(**0이어야 정상**). 병합이 났다면 Flow 그리드에 남은 폐기물 인덱스를 적는다 (WP 미업로드라 삭제 대기 항목은 아니다)
- 🆕 **(v6.1) 캡처 경로**: 이미지 탭 출처(`flow-content.google`)·해시 길이·`_capDims`. 그리드 탭에서 taint 오류가 났다면 그 사실을 남긴다
- 🆕 **(v5.5) 헤더 병합 결과**: `window._headerMerge` 판정값(`headerBox`/`heroFig`/`alreadyOverlay`)과 `merged` 여부, 렌더 기준 `h1InFigure:YES/NO`. **B형(초록 박스+독립 히어로)이 감지됐다면 그 사실을 반드시 남기고, 2회 연속이면 🔴 「Writer 헤더 템플릿 점검 필요」로 올린다**
- 🆕 **(v5.5) UI 오탐 발생 여부**: ⓐ 5-3 폴링의 `same` 이 2 이상으로 올라가 스크린샷 폴백을 썼는지 ⓑ 5-2 포커스 검증에서 상단 검색창이 잡혀 재클릭했는지 ⓒ 필터 칩 해제가 필요했는지. **세 항목 모두 "없음"이면 한 줄로 "UI 오탐 없음"만 적는다**
- 🆕 **(v5.9) 뷰포트·전송 사고 기록**: ⓐ `zoom` 호출 횟수(**0이어야 정상**) ⓑ 뷰포트 고착이 발생했다면 그 시점과 탭 재생성 여부 ⓒ 전송 검증(`boxLen`)에서 실패로 잡혀 재클릭한 건수 ⓓ 인덱스 확정에 쓴 방법(`outline` 마킹 / RGB 서명). **모두 정상이면 한 줄로 "뷰포트·전송 사고 없음"만 적는다**
- 🆕 **(v6.0) 모바일 히어로 검증 결과**: 375px 아이프레임 실측의 `figH`/`capH`/`여유`/`fs` 를 그대로 적고, 여유가 10px 미만이면 320px 재측정 값도 함께 남긴다. `_evGuard` 의 `absCap`·`fixed26`(둘 다 0) · `gridArea`(3) · `clampCnt`(4)도 명시한다
- **삭제 대기 미디어**: 재크롭 등으로 남은 원본 미디어 ID를 나열하고 **사용자 확인을 요청**한다 (임의 삭제 금지)
- 루틴 자체의 오류·개선점이 발견됐다면 **수정할 조항 번호와 교체용 전문(前文)**을 함께 제시한다 — 사용자가 붙여넣기만 하면 되도록

---

### 중요 주의사항

- 📸 **(v5.8) 이 루틴은 Flow 생성 이미지만 쓰는 루틴이 아니다** (STEP 3-9). 글에 실제로 존재하는 제품·앱·서비스·기관이 나오고 실물 이미지가 필요하면 **넣는다.** 규칙은 셋 — ① **공식 출처**(프레스킷·공식 사이트 캡처·공식 채널)는 그냥 쓴다 ② **아마존 이미지는 핫링크만**, 자체 업로드 금지 ③ **출처 불명 이미지는 쓰지 않는다**(유일한 금지선). figcaption에 출처+확인일 병기, 개인정보 화면 제외. 실물 1장은 증빙으로 계산돼 생성이 1장 줄어든다
- Chrome이 열려 있고, 0and1life.com WP admin에 로그인되어 있어야 함
- **(v4.0 · v6.1) Google Flow(`flow.google.com`, 舊 labs.google)에 로그인되어 있어야 함** — Flow 프로젝트 URL은 STEP 5 상단 참조. `labs.google` URL은 `flow.google.com` 으로 리다이렉트된다
- 🌐 **(v6.1) 그리드 탭에서 canvas 캡처를 하지 않는다.** 이미지가 `flow-content.google` 교차 출처라 반드시 taint 된다. 5-5의 ⓐ(그리드 탭에서 `window.open(URL#URL들)`) → ⓑ(이미지 탭에서 `new Image()` 캡처) 경로만 쓰고, STEP 6은 **이미지 탭에서** 실행한다
- ⛔ **(v6.1) Flow 동시 생성은 2건까지다.** 3번째부터 전송 버튼이 `disabled` 로 잠긴다. 타이핑 → `disabled` 해제 폴링 → 클릭 → `boxLen` 검증을 **건별로** 돌리고, **한 배치에 두 번의 타이핑을 넣지 않는다** (2026-09-04: 프롬프트 2+3 병합 전송 실측)
- 🆕 **(2026-08-26) Flow가 계정 선택 화면으로 튕기면 `leejc0404@gmail.com` 을 클릭해 진행한다** (사용자 사전 승인). **비밀번호 입력 화면이 나오면 즉시 중단**하고 STEP 5 상단의 세션 만료 대응 절차를 따른다
- 🎛 **(v5.6) Flow 설정 `에이전트 OFF / 이미지 / 16:9 / Nano Banana 2 / x2` 를 매 실행 눈으로 확인한다 (STEP 5-1).** '최초 1회'가 아니다 — 기본값이 실행마다 `x1`·`Nano Banana 2 Lite`·`동영상` 으로 돌아가 있었다. **에이전트 ON이면 프롬프트가 별도 채팅 세션으로 넘어가 재해석되고 생성이 전량 실패한다** (2026-08-26 KoreaPlug 실측: 2장 모두 `실패`, 세션 패널이 그리드를 덮어 인지도 늦었다 — 같은 Flow 프로젝트를 공유하므로 이 루틴도 동일 위험). 설정 변경 후 **저장** 버튼 필수
- **(v4.0) 워터마크는 `cropRight = 150` 으로 잘라낸다** (Flow 워터마크는 상대좌표 0.925W·0.875H의 이미지 안쪽에 있음). 덮기(fillRect) 방식은 배경에 디테일이 있으면 사각형이 눈에 띄므로 금지
- 🆕 **(v5.4) 크롭 뒤 `TARGET_W = 1100` 으로 다운스케일한다.** 1024 미만으로 줄이면 WP가 `large` 사이즈를 만들지 않아 2배 DPI 화면이 뭉개진다 — 900 이하로 낮췄다면 STEP 8에 명시
- 🚨 **(v5.4) 삽입하는 모든 `<img>` 에 `class="wp-image-{미디어ID}"` 를 넣는다.** 이 클래스가 없으면 WordPress가 `srcset`·`sizes` 를 주입하지 않아 **리사이즈본이 전혀 쓰이지 않는다.** 저장 전 `_evGuard.noWpCls === 0` 을 반드시 확인
- 🆕 **(v5.4) 본문 이미지는 `loading="lazy" decoding="async"`, 히어로는 `fetchpriority="high"`.** 히어로는 LCP 요소이므로 lazy를 붙이면 오히려 느려진다
- **(v4.0 · v6.1) 캡처 대상은 `naturalWidth > 1000` 인 그리드 img 의 `src` URL** — 그리드에서 고른 인덱스의 URL을 이미지 탭으로 넘겨 그린다. 렌더 폭은 판정에 쓰지 않는다
- **(v3.4) 본문을 읽는 모든 REST 요청에 `context=edit` 필수. `content.raw` 가 없으면 중단한다 — `|| content.rendered` 폴백은 원본을 파괴한다**
- **(v3.4) 모든 저장 POST에 `status: window._origStatus` 를 동봉한다. 저장 후 status가 바뀌었으면 즉시 되돌리고 보고한다**
- REST API 검색 시 `status=any` 파라미터 필수 (없으면 draft 글이 검색되지 않음)
- ⚡ **(v5.2) `fire-and-read` 2회 호출 패턴 폐기** — `javascript_tool` 은 최상위 `await` 를 지원하고 마지막 표현식 값을 그대로 반환한다 (2026-08-18 실측: `await new Promise(...)` 가 2.2초 뒤 값 반환). `const d = await fetch(...).then(r=>r.json()); window._x = d; '요약'` 처럼 **fetch·폴링·캡처와 그 검증을 한 호출에 합친다.** window 변수 저장은 계속 하되, '읽기 위한 추가 호출'만 없앤다. STEP 2·3·5·7에서 호출이 절반으로 준다
- 🚨 **(v5.3) Chrome MCP의 실제 상한은 세 개다. 전부 지킨다**
  - `computer:wait` — **1회 10초**
  - `javascript_tool` (CDP `Runtime.evaluate`) — **45초**. 그러므로 JS 내부 `setTimeout` 루프는 **최대 30초(6×5초)** 로 잡고, 미완료면 같은 호출을 반복한다 (STEP 5-3)
  - `computer:screenshot` (CDP `Page.captureScreenshot`) — **30초**. 배치 안에서 실패하면 **스크린샷만 단독으로 한 번 더** 부른다 (2026-08-19 실측 4회 전부 재호출로 성공)
- ⛔ **(v5.3) "JS 안에서는 시간 제한이 없다"는 v5.1·v5.2의 서술은 폐기한다.** 이 오해 때문에 2026-08-19 회차가 120초·35초 루프로 **2회 연속 타임아웃**을 냈다
- Chrome MCP의 scroll_amount는 최대 10 — 그리드 내 스크롤은 페이지 이동이 아니므로 캡처 전에 써도 무방하다 (하위 행의 후보를 볼 때 필요)
- 🆕 **(v5.1) 캡처 완료 전까지 Flow 그리드를 떠나지 않는다** — 에디터 진입·새로고침·주소창 이동 모두 금지. 복귀 시 그리드 재로딩에 20여 초가 든다 (실측 6s·14s 0개 → 26s 18개)
- 🆕 **(v5.1) 에디터 뷰는 쓰지 않는다.** 그리드 썸네일이 원본 해상도(1376×768)이므로 판정·캡처 모두 그리드에서 끝낸다. 세밀 확인은 **전체 스크린샷 재촬영**으로 한다 — **(v5.9) `zoom` 금지**
- 🆕 **(v5.1) 진행 상태 확인에 스크린샷을 먼저 쓰지 않는다.** JS 폴링이 반환하는 짧은 문자열로 판단한다. 스크린샷은 ⓐ 그리드 채택 판정 1장 ⓑ 최종 육안 검증 ⓒ **(v5.3) 폴링이 2회 연속 CDP 타임아웃일 때의 폴백**에만 쓴다
- 🆕 **(v5.3) 삽입 위치는 증빙 캡처의 ±5%pt 구간을 피한다** (STEP 4). 비율이 맞아도 증빙 옆이면 다른 h2를 고르고, 배제 후에도 섹션 주제가 안 맞으면 **주제를 비율보다 우선**한다
- 🆕 **(v5.3) 테마의 대표이미지 헤더(`.featured-image.page-header-image-single`)는 `display:none` 이다.** 기계 검증에서 히어로가 두 번 잡히는 것은 **정상**이며, `getComputedStyle` 확인 없이 중복으로 보고하지 않는다 (STEP 7.5)
- 🆕 **(v5.1) 클릭·입력·전송·대기는 `browser_batch` 로 묶어 1회 호출로 처리한다**
- 🆕 **(v5.1) 업로드 postMessage는 연속 전송 후 1회만 폴링**한다. 건별 대기 금지
- 🆕 **(v5.1) 대상 탐색은 WP REST(`status=draft,future&modified_after=`)가 1순위**, Notion은 0건이거나 제목·서브카테고리가 필요할 때만
- **이미지 생성 실패·부정확 시 재시도는 반드시 '수정된 프롬프트'로** (동일 프롬프트 재시도 금지). Flow는 1회에 2장을 주므로 먼저 **2장 중 채택**을 시도하고, 둘 다 부적합할 때만 수정 재시도한다. 수정 1회 후에도 부정확하면 해당 이미지 건너뜀
- **프롬프트 작성 전 본문을 반드시 읽고, 피사체 형태가 불확실하면 웹 검색으로 확인**
- 🆕 **(v5.0) 프롬프트는 '정확한 묘사'가 아니라 '사건 묘사'다.** 한 문장 테스트(3-2 ①)를 통과하지 못한 프롬프트는 전송하지 않는다. 전송 전 3-8의 7항목을 센다
- 🆕 **(v5.0) 본문 훅 문장 1개를 인용해 적고 그 한 줄만 그린다.** 훅 문장 없이 제목만 보고 만든 프롬프트는 무효
- 🆕 **(v5.0) 범용 은유 금지**(모래시계·저울·전구·퍼즐·돼지저금통·악수·빈 사무실·창밖 야경 단독 등) — 어느 글에나 어울리는 이미지는 이 글의 이미지가 아니다
- 🆕 **(v5.0) 손·팔 등 신체 부분 컷은 권장**(3장 중 1~2장). 금지 대상은 카메라 보고 웃는 정면 모델뿐
- 🆕 **(v5.0) 스톡 플레이스홀더가 2개 이상이면 첫 번째만 히어로, 나머지는 본문 이미지로 교체**하고 그만큼 삽입 개수를 줄인다 (STEP 4 · 7-2.5). 저장 전 `dupImg` 0 확인 필수
- 🚨 **(v5.5) 히어로 교체로 끝내지 말고 헤더 구조까지 본다** — 제목이 단색 박스에 남아 있으면 히어로가 아무리 좋아도 실패다. 7-2.6의 병합 판정을 매 회차 수행하고, `h1InFigure` 를 렌더 기준으로 확인한다
- 🆕 **(v5.5) 진행률 폴링을 맹신하지 않는다.** `prog()` 는 그리드 하위·가시 요소로 한정하고, 값이 **두 번 연속 안 움직이면(`same >= 2`) 스크린샷으로 판정**한다 (2026-08-25: 완료 후에도 `prog:4` 가 90초간 유지됨)
- 🆕 **(v5.5) 캡처 인덱스는 좌표가 아니라 `outline` 마킹으로 확인한다.** `getBoundingClientRect()` 가 4열 화면을 2열로 보고한 실측이 있다 (2026-08-25)
- 🆕 **(v5.5) Flow 첫 입력은 `document.activeElement` 로 포커스를 검증한 뒤 타이핑한다.** 상단 검색창에 들어가면 프롬프트가 유실되고 필터 칩까지 걸린다
- 🆕 **(v5.5) Flow 설정 패널은 `동영상` 으로 열려 있을 수 있고, `이미지` 를 누르면 비율 버튼 줄이 통째로 바뀐다.** ① 이미지 → ② 16:9 → ③ 모델 → ④ x2 순서를 지키고 ①과 ② 사이에 스크린샷으로 좌표를 다시 읽는다
- 🧨 **(v5.9) Flow 탭에서 `computer:zoom` 을 사용하지 않는다.** 2026-08-31 실측: zoom 호출이 `Page.captureScreenshot` 타임아웃과 함께 탭에 **뷰포트 에뮬레이션(981×184)을 고착**시켰고 `resize_window` 로 복구되지 않았다. 그 상태에서 프롬프트 1건이 전송되지 못하고 입력창에 잔류했으며, 상단 검색창 오염과 `동영상` 필터 칩이 동시에 걸렸다. 세밀 확인은 **전체 스크린샷 재촬영** 또는 **5-5의 RGB 서명**으로 대체한다. **이미 고착됐다면 유일한 복구는 탭을 닫고 새 탭에서 프로젝트를 다시 여는 것이다**
- 🆕 **(v5.9 · v6.1) 전송 버튼 좌표는 매번 JS로 확인하고, 전송 성공을 문자열로 검증한다.** `.ProseMirror` 입력창의 컨테이너에서 **마지막 버튼**(`aria-label="생성 시작"`, `window._findSend()`)의 rect를 스크린샷 좌표계로 환산해 클릭하고, 직후 `.ProseMirror` 의 `textContent.trim().length` 가 **20 미만**인지 확인한다. 舊 `arrow_forward` aria-label·`[role="textbox"]` 셀렉터는 현재 UI에 없다. 20 이상이면 전송 실패이므로 **다음 프롬프트를 타이핑하지 않는다** — 이어붙으면 두 프롬프트가 한 문장으로 섞여 둘 다 버려야 한다
- 🆕 **(v5.9) 스크린샷 좌표계와 뷰포트가 다를 수 있다.** 클릭 전에 `innerWidth` 를 읽어 `sc = 1568 / innerWidth` 로 환산한다. 그리드 열 수(4열/5열)도 창 크기에 따라 바뀌므로 **캡처 인덱스는 DOM 순서 + RGB 서명으로만 확정**하고 좌표로 추론하지 않는다
- 📱 **(v6.0) 히어로 제목 오버레이에 `position:absolute` 를 쓰지 않는다.** 절대위치 캡션은 자기 높이가 figure에 반영되지 않아 **좁은 화면에서 반드시 넘치고 `overflow:hidden` 에 잘린다.** `figure{display:grid}` + 세 자식 `grid-area:1/1` + `img{align-self:start}` / `figcaption{align-self:end}` 로 쓴다 (STEP 7-2.6 템플릿 A)
- 📱 **(v6.0) 히어로 제목·메타의 `font-size`·`padding` 은 `clamp()` 로만 쓴다.** 제목 `clamp(16px,4.4vw,26px)`, 메타 `clamp(11px,2.9vw,13px)`, 패딩 `clamp(14px,3.6vw,26px) clamp(14px,3.2vw,24px)`. 고정 26px은 375px 화면에서 캡션을 304px까지 키운다(이미지는 180px) — **제목 앞 2~3줄이 사라진다**
- 📱 **(v6.0) 저장 전 `_evGuard.absCap === 0` 과 `_evGuard.fixed26 === 0` 을 반드시 확인한다.** 히어로가 있는 글이면 `gridArea` 3 · `clampCnt` 4
- 📱 **(v6.0) 검증은 데스크톱만 보지 않는다.** `resize_window` 는 이 사이트에서 `innerWidth` 를 바꾸지 못하므로, **같은 원점 375px 아이프레임**으로 실측한다 (STEP 7.5). 2026-08-31에 오버레이 글 13건 전부가 데스크톱 검증만 통과한 채 모바일에서 잘려 있었다
- 🆕 **(v6.0) 히어로가 이미 오버레이형이어도 스타일 정규화는 매번 돌린다** (7-2.6b). `alreadyOverlay: true` 로 병합을 건너뛴 글에 舊 절대위치 캡션이 그대로 남아 있는 경우가 실제로 다수였다
- 글 제목(title)은 수정하지 않음
- 이미지 삽입 후 글 상태(publish/draft/future)는 변경하지 않음 — **발행·예약발행 전환은 어떤 경우에도 금지 (발행 결정은 항상 사용자 몫, 2026-08-01 사용자 지시)**
- **미디어 삭제는 어떤 경우에도 사용자 확인 후에만 수행한다** (2026-08-01 사용자 지시)
- (v3) **증빙 캡처 불가침**: 삽입·스톡 교체 어느 단계에서도 증빙 figure의 마크업·src·alt·figcaption을 수정하지 않는다. 저장 전 STEP 7-2.9로 확인한다
- (v3.2) **증빙 판정은 `evidence-capture` 클래스·`evidence-` 파일명만으로 하지 않는다.** v1.28(2026-08-02) 이전 글에는 이 마커가 없다. figcaption의 `Captured YYYY-MM-DD`, 공공 출처 도메인 파일명(`*-go-kr`, `korea-kr`, `kosis`, `hometax`, `work24`, `price-go`), alt의 조회·확인·캡처 단서까지 폴백으로 본다
- (v3.3) **`window.open` 에 `'_blank'` 금지** — 탭이 Chrome MCP 그룹 밖에 열려 리스너 주입이 불가능해진다 (STEP 6-1)
- (v3.3) **javascript_tool 반환값에 이미지 URL·쿼리스트링을 그대로 담지 않는다** — `[BLOCKED: Cookie/query string data]` 로 출력 전체가 막힌다. 집계값 먼저, 파일명은 축약·치환해서 출력
- **(v3.4) 삽입 위치는 h2의 '문자 위치' 기준으로 계산** — 헤딩 개수 분위는 이미지를 글 뒤쪽에 몰아넣는다 (STEP 4)
- **(v3.4) 장시간 window 상태가 필요한 작업은 `/wp-admin/` 대시보드가 아니라 `media-new.php` 에서 수행** — 대시보드는 간헐적으로 자체 리다이렉트를 일으킨다
