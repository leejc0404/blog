# KoreaPlug 자동 이미지 삽입 태스크 (v4.0 — 생성처를 Google Flow로 교체·워터마크 우측 크롭·taint 원천 제거)

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

### STEP 1: Notion에서 오늘 날짜 글 찾기

Notion MCP를 사용해 https://app.notion.com/p/33cbfe4a2ae181b9a743cb7c194dea7f 페이지를 fetch한다.

⚠️ **WP 세션 만료 대응 (2026-08-03 신설)** — 이 루틴은 `wpApiSettings.nonce`(wp-admin 로그인 세션)에 전적으로 의존한다. `wp-admin/` 접근 시 `wp-login.php?...&reauth=1` 로 리다이렉트되면 세션이 만료된 것이다.
- ⛔ 루틴은 **로그인 폼을 대신 제출하지 않는다** (자격증명 입력·인증 폼 제출은 AI 금지 동작). 자동완성이 채워져 있어도 클릭 금지.
- 오류 로그에 "WP 세션 만료 — 사용자 직접 로그인 필요"를 기록하고 종료한다. 이미지 삽입은 수행하지 않으며, 대상 글의 상태는 건드리지 않는다.
- 사용자 조치 안내: "Chrome에서 https://koreaplug.com/wp-admin 에 직접 로그인하고 '기억하기'를 체크해 주세요."
- 다음 실행이 (v3.1의 2일 소급 규정에 따라) 어제 글까지 다시 훑으므로, 세션만 복구되면 누락분은 자동으로 따라잡는다.

⚠️ **Notion 페이지가 커서 fetch 결과가 토큰 한도를 넘으면** 결과가 파일로 저장된다. 이때 전체를 다시 읽지 말고, 저장된 파일에 `grep`(최근 날짜 문자열) 또는 python 슬라이스로 **표 끝부분과 로그 tail만** 확인한다 (2026-08-18 실측: 72,436자 초과).

ℹ️ **(v4.0) `grep` 결과가 "Omitted long matching line"으로 막히면** 매치 창을 좁힌다. `.{0,300}날짜.{0,300}` 는 막히고 **`.{0,90}2026-08-18.{0,90}` 는 통과**한다 (2026-08-18 실측). 글 번호로 찾을 때는 `.{0,90}#13[5-8].{0,90}` 처럼 범위 패턴을 쓰면 최근 회차 로그가 한 번에 잡힌다.

(v3.1) **오늘 또는 어제 날짜**(YYYY-MM-DD)와 일치하는 **'draft 일자'** 또는 **'작성일자'** 행을 모두 찾는다. — 2일 소급 이유: 배포 루틴이 인증 문제 등으로 늦게 재실행되면 이 루틴이 도는 시점엔 글이 아직 WP에 없어 영영 누락된다 (2026-08-02 #122 실제 사례). 어제 글까지 봐야 다음 실행이 따라잡는다.
해당 행에서 **글 제목(영문)**, **카테고리**, **한줄 요약**을 추출한다.
대상이 여러 건이면 **오래된 날짜부터** 각각 STEP 2 판정을 거쳐, genCount>0 이거나 스톡 교체가 필요한 글만 순서대로 처리한다 (이미 충족된 글은 skip — 중복 삽입 방지는 STEP 2 판정이 보장).

오늘·어제 모두 대상 글이 없으면 "최근 2일 글 없음"을 출력하고 종료.

---

### STEP 2: WordPress에서 해당 글 확인

Chrome MCP로 새 탭을 열고 `https://koreaplug.com/wp-admin/media-new.php` 로 이동한다 (로그인 상태 필수).

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

#### 3-2. 피사체 정확성 원칙 (최우선 — 분위기보다 먼저)

> 프롬프트의 1순위는 '분위기'가 아니라 **'피사체 정확성'**이다. 핵심 피사체가 실물과 다르게 생성되면 아무리 분위기가 좋아도 그 이미지는 실패다.

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

#### 3-3. 분위기·라이팅 원칙 (2순위)

피사체 정확성이 확보된 뒤, 아래 순서로 조합해 사실감을 높인다. 추상적 표현보다 구체적인 물리 조건으로 묘사한다. 외국인에게 '진짜 한국(Real Korea)'의 매력을 직관적으로 전달할 수 있도록 로컬 고유의 질감과 분위기를 극대화한다.

- **장면 핵심** — 외국인이 흥미를 느끼는 구체적인 한국의 장소·사물·행위. 예: "a bubbling stone pot of kimchi-jjigae on a scratched stainless steel table", "a narrow alleyway in Euljiro lined with retro neon signs and stacked plastic stools"
- **시간·날씨·빛** — 단순한 낮/밤 대신 한국 특유의 서정적이거나 화려한 빛 명시. 예: "late afternoon cinematic side lighting", "rain-slicked asphalt reflecting colorful neon lights at night", "soft overcast daylight hitting traditional architecture"
- **카메라·렌즈 명시** — 예: "shot on Leica M11 with 35mm f/1.4 lens", "Sony A7R V with 90mm macro lens", "shot on Fujifilm X-T5 with 23mm cinematic lens"
- **구도·깊이감** — 예: "intense shallow depth of field with cinematic background blur", "low-angle dramatic perspective showing leading lines", "eye-level macro close-up"
- **텍스처·디테일 강조** — 예: "glistening condensation on a cold green bottle", "fine texture of red chili oil and rising steam", "weathered wooden pillars showing age rings"
- **제외 조건** — 예: "no people, no text, no watermark, no logos, no 3d render, no anime style"

**프롬프트 예시 (Food 카테고리):**

```
A boiling, bubbling stone pot of kimchi-jjigae with thick slices of pork belly and soft tofu blocks, placed on a scratched stainless steel round table inside a cozy Korean tavern, glistening condensation on a cold green bottle next to it, late afternoon warm window light creating sharp highlights on the broth surface, shot on Sony A7R V with 90mm macro lens, eye-level close-up, cinematic shallow depth of field, hyperrealistic food photography capturing rising steam and fine texture of red chili oil, no people, no text, no watermark, no logos
```

**프롬프트 예시 (Travel 카테고리):**

```
A narrow atmospheric alleyway in Euljiro, Seoul, with weathered concrete walls, retro Korean neon signs glowing in twilight, stacked blue and orange plastic stools outside a small restaurant, ground is slightly wet reflecting the neon lights, dramatic blue hour lighting with warm gold neon highlights, shot on Leica M11 with 35mm f/1.4 lens, low-angle perspective showing leading lines into the alley, crisp architectural and metallic textures, ultra-realistic street photography, no people, no text, no watermark, no logos
```

**프롬프트 예시 (Culture 카테고리):**

```
A close-up shot of hands intricately folding a colorful silk Bojagi (traditional Korean wrapping cloth) on a clean wooden floor of a quiet Hanok, detailed fabric texture with subtle satin sheen and traditional patterns, warm morning sunlight streaming through paper-screen windows (Changhoji) creating soft shadows, shot on Fujifilm X-T5 with 35mm lens, shallow depth of field, focused on the precise finger movements and the knot texture, warm and peaceful mood, no people, no text, no watermark, no logos
```

**프롬프트 예시 (Lifecycle 카테고리):**

```
An elaborate and colorful Doljanchi (Korean first birthday) celebration table set up inside a bright modern space with traditional accents, featuring neat stacks of traditional rice cakes (Mujeigae-tteok) on brass plates, a small wooden thread spool, a calligraphy brush, and a brass bowl, soft natural diffused daylight from a large window illuminating the textures of the silk tablecloth, shot on Canon EOS R5 with 50mm f/1.2 lens, elegant low-angle perspective, crisp focus on the symbolic objects in the foreground with a soft bokeh background, cheerful and vibrant mood, no people, no text, no watermark, no logos
```

**프롬프트 예시 (기기·시설 피사체 — 피사체 정확성 적용):**

```
A close-to-medium shot of a beige steel apartment entrance door in Seoul, fitted with an authentic modern Korean digital door lock (Gateman/Samsung SDS style) — a tall vertical rectangular brushed-silver metal panel mounted flush on the door, a touch-sensitive numeric keypad glowing faintly blue in the upper section, a slim horizontal push-down lever handle integrated into the lower section of the same panel, absolutely no separate round doorknob, soft afternoon window light casting gentle shadows across the door, shot on Sony A7R V with 50mm f/1.8 lens, eye-level straight-on composition centered on the lock panel, crisp texture of brushed metal and matte painted steel door, no people, no text, no watermark, no logos
```

**프롬프트 예시 (v3.3 — 두 상태 비교형 히어로):**

글의 핵심이 'A일 때와 B일 때가 다르다'인 경우, 히어로는 **두 상태를 한 프레임에 나란히** 넣으면 썸네일만으로 주제가 읽힌다.

```
A clean straight-on wide photograph of two screens side by side on a light oak table in a bright modern Korean living room. On the left, a flat-screen television shows a Korean drama scene in which one object is covered by a grey pixelated mosaic patch. On the right, a tablet propped on a stand shows the exact same scene completely sharp and clear with no mosaic at all. Identical framing and identical colours on both screens so the single difference is obvious at a glance, soft diffused daylight from a large window, shot on Canon EOS R5 with 50mm f/1.2 lens, symmetrical eye-level composition, crisp screen glass and matte table textures, no people in the room, no readable text, no watermark, no logos, no anime style, no 3d render
```

**프롬프트 예시 (v3.4 — 두 상태 비교형 히어로, 실사 풍경형):**

화면·소품이 아니라 **풍경 자체가 두 상태**인 글에서는, 하나의 실제 장면 안에 두 상태가 공존하는 구도를 찾으면 합성 느낌 없이 대비가 만들어진다.

```
A high aerial drone photograph of a wide Korean expressway just outside Seoul on a public holiday morning, showing two opposite traffic states in one single frame. The outbound carriageway on the right side is completely jammed bumper to bumper with hundreds of cars crawling in every lane, stretching unbroken all the way to the horizon. The inbound carriageway on the left side of the same central barrier is almost totally empty, with only two or three lone cars on wide open asphalt. Identical road width and identical lighting on both sides so the contrast is obvious at a glance, a low concrete median barrier and green roadside trees separating them, clusters of tall Korean apartment towers and forested hills in the hazy background, soft early-autumn morning light, shot on Sony A7R V with 70mm lens, high three-quarter aerial perspective looking down the length of the road, crisp asphalt and car roof textures, ultra realistic documentary aerial photography, no readable text, no watermark, no logos, no 3d render, no anime style
```

**프롬프트 예시 (v4.0 — 두 상태 비교형 히어로, 정물 대비형 / 2026-08-18 #137 채택본):**

두 상태를 **같은 평면 위 두 개의 사물**로 놓으면 가장 단순하고 썸네일에서 가장 잘 읽힌다.

```
A clean straight-on wide photograph of the interior of a Seoul metro train car, centered on an empty long brushed stainless steel bench seat with slim vertical dividers, and exactly two items placed side by side on that seat. On the left, a tall sealed transparent plastic cup of iced coffee with a domed lid and heavy condensation running down the cup. On the right, an open brown paper takeout bag with hot fried chicken visible spilling out of the top and faint steam rising from it. Identical lighting and identical framing on both items so the contrast between sealed-and-cold and open-and-hot is obvious at a glance. Behind the seat, brushed stainless steel wall panels, vertical stainless grab poles, a row of blue hanging strap handles above, cool white LED ceiling lighting, dark tinted train windows. No people at all, no readable text, no watermark, no logos, no 3d render, no anime style. Shot on Sony A7R V with 35mm lens, eye-level symmetrical composition, crisp metal, plastic and paper textures, ultra realistic documentary photography.
```

**이미지 3장의 역할 분담:**

- **이미지 1 (글 도입부)**: 글의 전체 분위기를 대표하는 와이드 장면 — 랜드마크, 전경, 공간감. **와이드 장면 안에도 핵심 피사체가 정확한 형태로 포함되어야 한다** (배경만 한국이고 피사체가 틀리면 실패).
- **이미지 2 (글 중반)**: 글의 핵심 소재를 클로즈업 — 음식 디테일, 문화 오브젝트, 체험 장면
- **이미지 3 (글 후반)**: 감성적 마무리 장면 — 저녁빛, 계절감, 여운이 있는 구도
- **(hasStockImg인 경우) 히어로 이미지**: 제목을 가장 직관적으로 시각화한 정면·와이드샷 — 썸네일로 봤을 때 글 주제가 한눈에 읽히는 구도

⚠️ **(v3.4) 히어로와 본문 이미지의 소재가 겹치지 않게 배분한다.** 히어로가 이미 A를 다뤘다면 본문 3장은 B·C·D를 맡는다. 같은 피사체가 두 번 나오면 글이 단조로워진다.

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

### STEP 5: Google Flow에서 이미지 생성 및 캡처 (v4.0)

Chrome MCP로 새 탭을 열고 사용자의 Flow 프로젝트로 이동한다:

`https://labs.google/fx/ko/tools/flow/project/6a6af995-4d64-4bbb-8e97-4be7aa267e6d`

#### 5-1. 생성 설정 확인 (최초 1회)

하단 입력창 우측의 설정 칩(`Nano Banana 2 ▭ x2`)을 클릭해 아래 4개를 확인한다. 이미 맞으면 그대로 닫는다.

- 모드: **이미지** (동영상 아님)
- 비율: **16:9**
- 모델: **Nano Banana 2**
- 장수: **x2** — 패널 하단에 "생성 시 0크레딧이 사용됩니다" 표시 확인

⛔ **`에이전트` 버튼은 사용하지 않는다.** 켜면 프롬프트를 재해석해 의도와 다른 결과가 나온다.

#### 5-2. 프롬프트 투입

입력창 클릭 → 프롬프트 입력 → **우측 화살표(→) 버튼 클릭**.
프롬프트 작성 원칙(STEP 3-2 피사체 정확성, 3-3 분위기)은 **그대로 유지**한다. 프롬프트 앞에 `Generate a photorealistic image.` 같은 지시문을 붙일 필요는 없다.

⏱ 그리드 상단에 진행률(%)이 실시간 표시되며 **약 20초**에 2장이 완료된다 (2026-08-18 실측: 10% → 76% → 완료). Chrome MCP의 wait 10초를 2~3회 반복하면 충분하다. **60초를 넘기면 지연으로 보고 재전송**한다.

ℹ️ Gemini와 달리 **첫 클릭이 씹히지 않는다.** 그래도 전송 직후 스크린샷으로 그리드에 진행률 카드 2장이 생겼는지 한 번 확인한다.

#### 5-3. 2장 중 채택본 선택 (필수)

그리드에서 새로 생성된 2장의 썸네일을 각각 클릭해 **에디터 뷰에서 육안 검증**한다.

- 핵심 피사체가 **실제 한국 형태**와 일치하는가 (STEP 3-2 기준)
- 글 제목을 아는 독자가 봤을 때 "글 내용과 맞는 이미지"라고 느낄 것인가
- 왜곡된 손·어색한 텍스트·서구식 형태 등 이상 요소가 없는가
- **둘 다 부적합할 때만** 잘못된 부분을 물리적으로 더 명시한 **수정 프롬프트**로 재생성한다 (동일 프롬프트 재전송 금지). 수정 1회 후에도 어긋나면 해당 이미지 건너뜀.

ℹ️ 2장 중 고르는 구조라 舊 루틴의 "재시도 1회" 규정이 실제로 발동할 일은 거의 없다.

#### 5-4. 캡처 (채택본을 에디터 뷰에 띄운 상태에서 실행)

Flow 워터마크(✦)는 이미지 **모서리가 아니라 안쪽**, 상대좌표 **(0.925W, 0.875H)** 에 고정돼 있다 (2026-08-18 실측: 1376×768 기준 중심 ≈ (1273, 672), 크기 ≈ 56×56. 프로젝트 내 과거 이미지들도 동일 상대좌표). 따라서 **`cropRight = 150` 으로 우측만 잘라내면 세로 해상도 손실 없이 제거된다** → 1226×768.

```javascript
// 실행 → 2~3초 대기 → window._img1dims 로 확인
(async () => {
 try {
  const imgs = Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 400);
  const main = imgs.sort((a, b) => b.getBoundingClientRect().width - a.getBoundingClientRect().width)[0];
  const cropRight = 150, cropBottom = 0;   // (v4.0) Flow 워터마크는 우측 크롭으로 제거
  const c = document.createElement('canvas');
  c.width  = main.naturalWidth  - cropRight;
  c.height = main.naturalHeight - cropBottom;
  c.getContext('2d').drawImage(main, 0, 0, c.width, c.height, 0, 0, c.width, c.height);
  const blob = await new Promise(r => c.toBlob(r, 'image/webp', 0.85));
  window._img1 = await new Promise(r => { const rd = new FileReader(); rd.onloadend = () => r(rd.result); rd.readAsDataURL(blob); });
  window._img1dims = c.width + 'x' + c.height + ' ' + Math.round(blob.size / 1024) + 'KB';
 } catch (e) { window._img1dims = 'FAIL: ' + e.message; }
})();
'fired'
```

⚠️ **에디터 뷰에는 사이드바 썸네일·히스토리 이미지도 함께 존재하므로 `naturalWidth` 만으로 고르면 안 된다.** 반드시 **화면상 표시 폭(`getBoundingClientRect().width`)이 가장 큰 img** 를 채택한다. (2026-08-18 실측: 같은 페이지에 `naturalWidth 1376` 인 img가 7~8개 존재)

✅ **(v4.0 실측) Flow는 이미지를 `labs.google` 동일 출처로 서빙하므로 canvas taint가 발생하지 않는다.** 舊 v3.4~v3.5의 `SecurityError: canvas has been tainted` 복구 절차(URL 릴레이·IMGTAB 탭 생성·`location.href` 이동)는 **전부 불필요하며 삭제됐다.**

✅ **(v4.0 실측) 그리드 ↔ 에디터 이동은 SPA 라우팅이라 `window._img*` 가 보존된다.** URL이 `/edit/...` 로 바뀌어도 리로드가 아니므로 이미지 4장을 순차 캡처해도 안전하다. 단 **주소창 navigate·새로고침은 여전히 금지** — 변수가 날아간다.

이미지 2·3·히어로는 좌상단 **←** 로 그리드에 돌아가 5-2부터 반복하고, 각각 `window._img2`, `window._img3`, `window._imgHero` 에 저장한다. 매 캡처 후 `'1:' + !!window._img1 + ' 2:' + !!window._img2 + ...` 로 보존 여부를 확인한다.

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

```javascript
// 2) 역순으로 이미지 삽입 (뒤→앞 순서로 삽입해야 인덱스가 밀리지 않음)
const uploads = window._uploadedIds.filter(u => !u.tag.includes('hero')); // 본문용 3장만
const pts = window._insertPoints;    // [pos1, pos2, pos3]
let c = window._finalContent;

for (let i = 2; i >= 0; i--) {
  const {url, alt} = uploads[i];
  const imgBlock = '\n<figure style="margin:20px 0">\n  <img style="width:100%;display:block;height:auto;border-radius:8px;" src="' + url + '" alt="' + alt + '" />\n</figure>\n';
  c = c.slice(0, pts[i]) + imgBlock + c.slice(pts[i]);
}
window._newContent = c;
'inserted, new len: ' + c.length + ' order:' + uploads.map(u => u.tag.slice(-6)).join(',')
```

```javascript
// 2.5) (hasStockImg인 경우) 기존 스톡 이미지의 src/alt를 히어로 이미지로 교체
// img 태그의 src와 alt만 바꾸고 나머지 마크업(제목 오버레이 등)은 유지한다
const hero = window._uploadedIds.find(u => u.tag && u.tag.includes('hero'));
if (hero) {
  let replaced = 0;
  window._newContent = window._newContent.replace(/<img[^>]*>/g, (tag) => {
    if (/unsplash\.com|pexels\.com|pixabay\.com|FEATURED_IMAGE/.test(tag)) {
      replaced++;
      let t = tag.replace(/src="[^"]*"/, 'src="' + hero.url + '"');
      t = t.match(/alt="[^"]*"/) ? t.replace(/alt="[^"]*"/, 'alt="' + hero.alt + '"')
                                 : t.replace('<img', '<img alt="' + hero.alt + '"');
      return t;
    }
    return tag;
  });
  window._heroReplaced = replaced; // 확인용
}
'heroReplaced:' + window._heroReplaced + ' newLen:' + window._newContent.length
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
  stock:   cnt(before, /unsplash\.com/g)    + '->' + cnt(after, /unsplash\.com/g),      // 히어로 교체 시 →0
  noAlt:   cnt(after, /<img(?![^>]*alt=)/g)                                            // 0이어야 함
};
Object.entries(window._evGuard).map(([k, v]) => k + ': ' + v).join('\n')
```

⛔ 위 검증에서 하나라도 어긋나면 **저장하지 않는다.** 원인을 해결한 뒤 다시 만든다.

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
- `broken` 이 0인가? 모든 `nw`(naturalWidth)가 정상인가? (v4.0 Flow 산출물은 `nw 1226`)
- h2·표 개수가 삽입 전과 같은가?

**이어서 육안으로 확인한다:**

- 각 이미지의 피사체가 글 내용·주변 섹션과 맞는가?
- 히어로/대표이미지가 정상 반영됐는가? (제목 오버레이 마크업이 보존됐는가)
- 증빙 캡처가 원래 자리에 그대로 있는가? (`window._evGuard` 확인)
- **워터마크 흔적(✦)이 남아 있지 않은가?** — 남아 있으면 STEP 5-4의 `cropRight` 값을 늘려 재캡처하거나, 이미 업로드된 파일을 koreaplug.com **동일 출처**에서 canvas로 다시 읽어 재크롭·재업로드한다.
- 표·TOC·내부링크 등 기존 요소가 삽입으로 깨지지 않았는가?
- **글 상태가 원래대로인가?** (`draft` 는 `draft` 그대로여야 한다)

**뒷정리:** 검증이 끝나면 이 루틴이 만든 탭(Flow 탭, media-new 탭)을 `tabs_close_mcp` 로 모두 닫는다. 사용자가 결과를 바로 볼 수 있도록 **프리뷰 탭 1개만 남긴다.**

---

### STEP 8: 완료 보고

완료 후 아래 내용을 출력:

- 처리한 글 제목 및 Post ID
- **STEP 2 분류 결과 표**: 이미지별 `파일명 => 증빙/스톡/데코 [판정근거]`, 그리고 evidence/stock/deco/genCount
- `unknown`이 있었다면 수동 확인 결과와 재계산된 genCount
- 삽입·교체된 이미지 (media ID + 렌더 기준 위치 %)
- 최종 imgCount, 불가침 검증(`window._evGuard`) 결과 — **blocks·ezToc·h2·table 항목 포함**
- **(v3.4) 글 상태**: 시작 시 status → 종료 시 status. 전환이 발생했다면 복구 여부까지 명시
- 대표이미지: 선정된 이미지, 선정 이유, 설정 결과 (`window._featuredResult`)
- 피사체 정확성 검증: 각 이미지별 통과/재시도/건너뜀 여부, **2장 중 어느 쪽을 채택했는지**
- Skip된 경우 그 이유
- **(v4.0) 생성 소요시간**: 이미지별 생성 대기 시간을 기록한다. 60초를 넘긴 건이 있으면 Flow 지연으로 보고한다
- **삭제 대기 미디어**: 재크롭 등으로 남은 원본 미디어 ID를 나열하고 **사용자 확인을 요청**한다 (임의 삭제 금지)
- 루틴 자체의 오류·개선점이 발견됐다면 **수정할 조항 번호와 교체용 전문(前文)**을 함께 제시한다 — 사용자가 붙여넣기만 하면 되도록

---

### 중요 주의사항

- Chrome이 열려 있고, koreaplug.com WP admin에 로그인되어 있어야 함
- **(v4.0) labs.google(Google Flow)에 로그인되어 있어야 함** — Flow 프로젝트 URL은 STEP 5 상단 참조
- **(v4.0) Flow 설정은 `에이전트 미사용 / 이미지 / 16:9 / Nano Banana 2 / x2` 고정.** 에이전트를 켜면 프롬프트가 재해석된다
- **(v4.0) 워터마크는 `cropRight = 150` 으로 잘라낸다** (Flow 워터마크는 상대좌표 0.925W·0.875H의 이미지 안쪽에 있음). 덮기(fillRect) 방식은 배경에 디테일이 있으면 사각형이 눈에 띄므로 금지
- **(v4.0) 캡처 대상은 `getBoundingClientRect().width` 가 가장 큰 img** — 같은 페이지에 `naturalWidth 1376` 인 썸네일이 여러 개 있다
- **(v3.4) 본문을 읽는 모든 REST 요청에 `context=edit` 필수. `content.raw` 가 없으면 중단한다 — `|| content.rendered` 폴백은 원본을 파괴한다**
- **(v3.4) 모든 저장 POST에 `status: window._origStatus` 를 동봉한다. 저장 후 status가 바뀌었으면 즉시 되돌리고 보고한다**
- REST API 검색 시 `status=any` 파라미터 필수 (없으면 draft 글이 검색되지 않음)
- async JavaScript 결과는 항상 window 변수에 저장 후 별도 호출로 읽는다 (fire-and-read 패턴)
- Chrome MCP의 wait는 1회 최대 10초, scroll_amount는 최대 10 — 긴 대기는 나눠서 반복
- **이미지 생성 실패·부정확 시 재시도는 반드시 '수정된 프롬프트'로** (동일 프롬프트 재시도 금지). Flow는 1회에 2장을 주므로 먼저 **2장 중 채택**을 시도하고, 둘 다 부적합할 때만 수정 재시도한다. 수정 1회 후에도 부정확하면 해당 이미지 건너뜀
- **프롬프트 작성 전 본문을 반드시 읽고, 피사체 형태가 불확실하면 웹 검색으로 확인**
- 글 제목(title)은 수정하지 않음
- 이미지 삽입 후 글 상태(publish/draft/future)는 변경하지 않음 — **발행·예약발행 전환은 어떤 경우에도 금지 (발행 결정은 항상 사용자 몫, 2026-08-01 사용자 지시)**
- **미디어 삭제는 어떤 경우에도 사용자 확인 후에만 수행한다** (2026-08-01 사용자 지시)
- (v3) **증빙 캡처 불가침**: 삽입·스톡 교체 어느 단계에서도 증빙 figure의 마크업·src·alt·figcaption을 수정하지 않는다. 저장 전 STEP 7-2.9로 확인한다
- (v3.2) **증빙 판정은 `evidence-capture` 클래스·`evidence-` 파일명만으로 하지 않는다.** v1.28(2026-08-02) 이전 글에는 이 마커가 없다. figcaption의 `Captured YYYY-MM-DD`, 공공 출처 도메인 파일명(`*-go-kr`, `korea-kr`, `kosis`, `hometax`, `work24`), alt의 조회·확인·캡처 단서까지 폴백으로 본다
- (v3.3) **`window.open` 에 `'_blank'` 금지** — 탭이 Chrome MCP 그룹 밖에 열려 리스너 주입이 불가능해진다 (STEP 6-1)
- (v3.3) **javascript_tool 반환값에 이미지 URL·쿼리스트링을 그대로 담지 않는다** — `[BLOCKED: Cookie/query string data]` 로 출력 전체가 막힌다. 집계값 먼저, 파일명은 축약·치환해서 출력
- **(v3.4) 삽입 위치는 h2의 '문자 위치' 기준으로 계산** — 헤딩 개수 분위는 이미지를 글 뒤쪽에 몰아넣는다 (STEP 4)
- **(v3.4) 장시간 window 상태가 필요한 작업은 `/wp-admin/` 대시보드가 아니라 `media-new.php` 에서 수행** — 대시보드는 간헐적으로 자체 리다이렉트를 일으킨다
