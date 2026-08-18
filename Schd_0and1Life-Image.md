# 0and1Life 자동 이미지 삽입 태스크 (v4.0 — Flow 생성처 교체 + v3.2~v3.4 일괄 백포트)

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

> ⚠️ v3 변경 (2026-08-01): Draft 루틴이 발행 관문용 **증빙 캡처**(`figure class="evidence-capture"`, 파일명 `evidence-*`)를 본문에 넣기 시작하면서, 총 이미지 수 기준(舊 imgCount ≥ 3 → skip)으로는 모든 글이 스킵되어 이 루틴이 돌지 않았다. 판정은 **데코 개수**로 하되, 글이 이미지로 과밀해지지 않도록 **총량 상한 5장**(증빙+데코, 히어로 교체는 총량 불변이라 제외)을 함께 둔다. 증빙 캡처는 어떤 단계에서도 교체·이동·삭제하지 않는다.

---

### STEP 1: Notion에서 오늘 날짜 글 찾기

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

- **핵심 피사체**: 글이 실제로 다루는 도구·앱·기기·장면이 무엇인가 (제목의 추상 키워드가 아니라 본문이 묘사하는 구체적 실물). 예: 글이 ChatGPT 화면 활용법을 다루면 이미지도 노트북 위 대화형 AI 화면이어야지, 막연한 '미래적 AI 그래픽'이면 안 된다.
- 본문이 언급하는 **구체적 도구·화면·환경·상황** (앱 이름, 작업 환경, 시간대, 감정선) — 그대로 프롬프트 재료가 됨
- 헤딩(h2/h3) 텍스트 — 각 이미지가 들어갈 위치 주변 섹션의 주제

#### 3-2. 피사체 정확성 원칙 (최우선 — 분위기보다 먼저)

> 프롬프트의 1순위는 '분위기'가 아니라 **'피사체 정확성'**이다. 핵심 피사체가 글 내용과 다르게 생성되면 아무리 분위기가 좋아도 그 이미지는 실패다.

1. **한국의 실제 환경·사물을 물리적으로 상세 묘사한다.** "Korean office"라고만 쓰면 생성 모델은 서구식 사무실을 만들기 쉽다. 한국 직장·주거·카페의 실제 디테일(파티션 책상, 스터디카페 좌석, 아파트 거실, 이케아식 홈오피스, 스타벅스 리저브 등)을 명시한다.
2. **기기·도구는 실물 형태로 묘사한다.** 예: 갤럭시/아이폰, 맥북/그램, 듀얼 모니터, 기계식 키보드 등 본문이 언급한 실제 기기를 그대로 쓴다. AI 관련 글이라도 추상적 홀로그램·로봇 그래픽이 아니라 **실제 화면·실제 작업 장면**으로 표현한다.
3. **형태를 정확히 모르면 웹 검색으로 실제 사진을 확인한 뒤** 프롬프트를 작성한다. 추측으로 쓰지 않는다.
4. **잘못 나오기 쉬운 형태를 명시적으로 배제한다.** 예: "no futuristic hologram, no robot, no sci-fi interface", "no Western-style cubicle office".
5. **(v4.0 보강) 화면 안의 글자는 반드시 배제한다.** UI·자막·문서 텍스트는 깨진 글자로 생성되므로 `no readable text on the screen`, `interface reduced to plain blocks and lines` 처럼 **글자 없는 형태로 지정**한다.

#### 3-3. 분위기·라이팅 원칙 (2순위)

0and1Life는 AI·효율·라이프스타일 한국 블로그다. 이미지는 글의 핵심 개념을 가장 흥미롭게 시각화하는 장면을 담는다. 사실적(photorealistic)이되, 뻔하지 않아야 한다.

장면 핵심: 글의 핵심 소재·개념 그 자체를 주인공으로 삼는다. 인물은 기본값이 아니라 선택지 중 하나이며, 3장 중 최대 1장까지만 허용한다.

예: 개념의 시각적 은유: "five subscription app cards arranged like a hand of playing cards on a desk, one card being pulled out" (구독 정리)
소재 정물: "a passport, boarding pass and smartphone showing a glowing route map, laid flat on a world map" (AI 여행)
극적 대비·과장: "a tiny desk lamp illuminating one neat stack of coins beside a towering messy pile of receipts" (절약)

인물을 쓸 경우에도 얼굴 정면의 '번듯한 모델' 구도 금지 — 손·뒷모습·실루엣 등 부분 컷 우선

- **시간·빛**: 단순 낮/밤 대신 분위기 명시. 예: "soft morning light from floor-to-ceiling windows", "evening blue hour with city lights reflection"
- **카메라·렌즈**: "shot on Sony A7R V with 35mm f/1.8 lens", "Fujifilm X-T5 with 23mm cinematic lens"
- **구도·깊이감**: "shallow depth of field", "eye-level perspective", "over-the-shoulder angle"
- **제외 조건**: "no text, no watermark, no logos, no anime style, photorealistic" + "no generic stock photo look, no posed corporate model smiling at camera"

사실성은 유지하되, 창의적 실사 기법은 적극 허용: 미니어처/틸트시프트, 극단적 매크로, 톱뷰 플랫레이, 장노출 빛궤적, 강한 색 대비 조명 등

**(v4.0 신설) 두 상태 비교형 히어로**: 글의 핵심이 'A일 때와 B일 때가 다르다'인 경우, 두 상태를 **같은 평면 위 두 개의 사물**로 놓으면 썸네일에서 주제가 즉시 읽힌다. 조명·프레이밍을 동일하게 지정하는 것이 핵심이다 (`Identical lighting and identical framing on both items so the contrast is obvious at a glance`). KoreaPlug 2026-08-18 실측에서 2장 모두 통과한 구조다.

**이미지 3장의 역할 분담:**

이미지 1 (도입부): 글 주제를 한눈에 읽히게 하는 시각적 훅 — 썸네일로 봤을 때 "뭐지?" 하고 클릭하고 싶어지는 구도. 은유·대비·의외성 중 하나를 반드시 포함
이미지 2 (중반): 핵심 소재의 클로즈업 (유지하되, 화면·기기 반복 금지 — 글마다 다른 각도·재질·구도)
이미지 3 (후반): 글의 결론·효용을 시각화 — '만족한 사람' 공식 금지. 결과물·변화·before/after를 사물로 표현

3장의 다양성 규칙 (필수): 3장이 같은 스타일·같은 구도·같은 피사체 유형이면 실패. 최소 1장은 인물 없는 정물/은유 컷, 3장의 카메라 거리(원경/중경/접사)를 서로 다르게 한다

- **(hasStockImg인 경우) 히어로 이미지**: 제목을 가장 직관적으로 시각화한 장면 — 썸네일로 봤을 때 글 주제가 한눈에 읽히는 구도

⚠️ **(v3.4 백포트) 히어로와 본문 이미지의 소재가 겹치지 않게 배분한다.** 히어로가 이미 A를 다뤘다면 본문 3장은 B·C·D를 맡는다. 같은 피사체가 두 번 나오면 글이 단조로워진다.

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

### STEP 4: 글 구조 분석 → 이미지 삽입 위치 3곳 결정

STEP 3-1에서 확보한 `window._rawContent`(반드시 raw)를 사용한다.

⛔ **(v3.4 백포트) 헤딩 '개수' 분위(1/4·2/4·3/4)를 쓰지 않는다.** 헤딩이 문서 후반에 몰려 있으면 이미지가 전부 뒤쪽으로 쏠린다 (2026-08-12 실측: h2 8개의 개수 분위가 문서의 59%·74%·87% 지점에 해당 — 앞 절반이 통째로 빔). 대신 **h2의 문자 위치를 뽑아, 목표 비율에 가장 가까운 h2를 고른다.**

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

ℹ️ **(v4.0) `hasStockImg`로 히어로를 만드는 글은 글 맨 위(0%)가 히어로로 이미 채워진다.** 이때 본문 3장의 목표 비율은 `[0.10, 0.45, 0.72]` 대신 **`[0.30, 0.55, 0.72]`** 로 뒤로 밀어 잡는 편이 분포가 고르다 (2026-08-18 실측: 히어로 2% + 본문 29%/47%/60%로 균등 배치 성공).

(v3) `genCount`가 3 미만이면 `window._insertPoints`에서 앞의 genCount개 위치만 사용한다 — 우선순위는 STEP 2의 이미지 1→3→2 순서를 따른다.

(v3.2 백포트) 다만 **이미 이미지가 있는 글에 1~2장을 보충하는 경우**에는 기계적으로 도입부를 쓰지 말고, 기존 이미지들의 본문 내 위치(index)를 먼저 구해 **이미지가 가장 오래 비어 있는 구간**의 헤딩을 고른다. 보충의 목적은 개수 채우기가 아니라 공백 메우기다.

ℹ️ **(v3.4 백포트) raw 위치와 렌더 후 화면 위치는 다르다.** ez-toc 목차는 렌더 시점에 첫 h2 앞으로 삽입되므로, raw에서 첫 h2 바로 앞에 넣은 이미지는 화면에서 **본문 도입 → 이미지 → 목차** 순으로 보인다. 이 배치는 정상이며 문제가 아니다. 최종 위치는 STEP 7.5에서 렌더 기준으로 실측한다.

---

### STEP 5: Google Flow에서 이미지 생성 및 캡처 (v4.0)

Chrome MCP로 새 탭을 열고 사용자의 Flow 프로젝트로 이동한다:

`https://labs.google/fx/ko/tools/flow/project/6a6af995-4d64-4bbb-8e97-4be7aa267e6d`

ℹ️ KoreaPlug와 동일한 프로젝트를 공용으로 쓴다. 사이트별로 프로젝트를 분리하고 싶으면 이 URL만 교체하면 되며, 나머지 절차는 동일하다.

#### 5-1. 생성 설정 확인 (최초 1회)

하단 입력창 우측의 설정 칩(`Nano Banana 2 ▭ x2`)을 클릭해 아래 4개를 확인한다. 이미 맞으면 그대로 닫는다.

- 모드: **이미지** (동영상 아님)
- 비율: **16:9**
- 모델: **Nano Banana 2**
- 장수: **x2** — 패널 하단에 "생성 시 0크레딧이 사용됩니다" 표시 확인

⛔ **`에이전트` 버튼은 사용하지 않는다.** 켜면 프롬프트를 재해석해 의도와 다른 결과가 나온다.

#### 5-2. 프롬프트 투입

입력창 클릭 → 프롬프트 입력 → **우측 화살표(→) 버튼 클릭**.
프롬프트 작성 원칙(STEP 3-2 피사체 정확성, 3-3 분위기)은 **그대로 유지**한다.

⏱ 그리드 상단에 진행률(%)이 실시간 표시되며 **약 20초**에 2장이 완료된다. Chrome MCP의 wait 10초를 2~3회 반복하면 충분하다. **60초를 넘기면 지연으로 보고 재전송**한다.

ℹ️ Gemini와 달리 **첫 클릭이 씹히지 않는다.** 그래도 전송 직후 스크린샷으로 그리드에 진행률 카드 2장이 생겼는지 한 번 확인한다.

#### 5-3. 2장 중 채택본 선택 (필수)

그리드에서 새로 생성된 2장의 썸네일을 각각 클릭해 **에디터 뷰에서 육안 검증**한다.

- 핵심 피사체가 **글 내용·실제 한국 환경**과 일치하는가 (STEP 3-2 기준)
- 글 제목을 아는 독자가 봤을 때 "글 내용과 맞는 이미지"라고 느낄 것인가
- 왜곡된 손·어색한 텍스트·SF풍 그래픽·서구식 환경 등 이상 요소가 없는가
- 3장 다양성 규칙(3-3)을 해치지 않는가 — 앞서 채택한 이미지와 카메라 거리·피사체 유형이 겹치면 다른 쪽을 고른다
- **둘 다 부적합할 때만** 잘못된 부분을 물리적으로 더 명시한 **수정 프롬프트**로 재생성한다 (동일 프롬프트 재전송 금지). 수정 1회 후에도 어긋나면 해당 이미지 건너뜀.

#### 5-4. 캡처 (채택본을 에디터 뷰에 띄운 상태에서 실행)

Flow 워터마크(✦)는 이미지 **모서리가 아니라 안쪽**, 상대좌표 **(0.925W, 0.875H)** 에 고정돼 있다 (2026-08-18 실측: 1376×768 기준 중심 ≈ (1273, 672), 크기 ≈ 56×56). 따라서 **`cropRight = 150` 으로 우측만 잘라내면 세로 해상도 손실 없이 제거된다** → 1226×768.

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

⚠️ **에디터 뷰에는 사이드바 썸네일·히스토리 이미지도 함께 존재하므로 `naturalWidth` 만으로 고르면 안 된다.** 반드시 **화면상 표시 폭(`getBoundingClientRect().width`)이 가장 큰 img** 를 채택한다.

✅ **(v4.0 실측) Flow는 이미지를 `labs.google` 동일 출처로 서빙하므로 canvas taint가 발생하지 않는다.** 舊 Gemini 경로의 `SecurityError: canvas has been tainted` 복구 절차는 **전부 불필요하며 삭제됐다.**

✅ **(v4.0 실측) 그리드 ↔ 에디터 이동은 SPA 라우팅이라 `window._img*` 가 보존된다.** URL이 `/edit/...` 로 바뀌어도 리로드가 아니므로 이미지 4장을 순차 캡처해도 안전하다. 단 **주소창 navigate·새로고침은 여전히 금지** — 변수가 날아간다.

이미지 2·3·히어로는 좌상단 **←** 로 그리드에 돌아가 5-2부터 반복하고, 각각 `window._img2`, `window._img3`, `window._imgHero` 에 저장한다. 매 캡처 후 `'1:' + !!window._img1 + ' 2:' + !!window._img2 + ...` 로 보존 여부를 확인한다.

---

### STEP 6: Flow 탭에서 WP admin 새 창 열기 → postMessage로 이미지 업로드

**핵심:** Flow 탭에서 WP REST API를 직접 fetch하면 CORS로 차단된다. 기존 WP admin 탭에 대한 window 참조도 얻을 수 없다. 유일하게 작동하는 방법은 Flow 탭에서 `window.open()`으로 새 WP admin 창을 열고 그 참조에 postMessage를 보내는 것이다.

**6-1. Flow 탭에서 새 WP admin 창 열기:**

⛔ **(v3.3 백포트) 두 번째 인자 `'_blank'` 를 넘기지 않는다.** `'_blank'` 로 열린 탭은 Chrome MCP 탭 그룹 **밖에** 생성되어 `tabs_context_mcp` 목록에 나타나지 않고, 그 결과 6-2의 리스너 주입이 불가능해져 업로드 경로 전체가 막힌다.

```javascript
// Flow 탭에서 실행 — 새 tabId가 생성됨
window._wpWin = window.open('https://0and1life.com/wp-admin/media-new.php');
window._wpWin ? 'window opened' : 'blocked'
// 6~8초 대기 후 tabs_context_mcp로 새 tabId 확인
```

**복구 절차** — 이미 `'_blank'` 로 열어 탭이 목록에 없다면, Flow 탭에서 아래를 실행해 닫고 위 코드로 다시 연다. `window._img*` 는 Flow 탭 heap에 그대로 남아 있으므로 **이미지 재생성은 필요 없다.**

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

**6-3. Flow 탭에서 이미지 순서대로 전송 (본문용 1→2→3, 히어로가 있으면 마지막):**

각 전송 후 6~8초 대기. 전송 사이에 WP admin 탭에서 `window._uploadedIds.length` 로 업로드 완료 확인 후 다음 전송.

```javascript
// Flow 탭에서 순서대로 실행
window._wpWin.postMessage({dataUrl: window._img1, filename: '0and1life-SLUG-1.webp', altText: 'ALT_TEXT_1'}, 'https://0and1life.com');
// 6~8초 대기
window._wpWin.postMessage({dataUrl: window._img2, filename: '0and1life-SLUG-2.webp', altText: 'ALT_TEXT_2'}, 'https://0and1life.com');
// 6~8초 대기
window._wpWin.postMessage({dataUrl: window._img3, filename: '0and1life-SLUG-3.webp', altText: 'ALT_TEXT_3'}, 'https://0and1life.com');
// (hasStockImg인 경우)
window._wpWin.postMessage({dataUrl: window._imgHero, filename: '0and1life-SLUG-hero.webp', altText: 'ALT_TEXT_HERO'}, 'https://0and1life.com');
// 6~8초 대기 후 window._uploadedIds.length가 전송한 수와 같은지 확인
```

확인용 (WP admin 탭에서):

```javascript
'up:' + window._uploadedIds.length + ' err:' + window._upErrors.length
 + ' ids:' + window._uploadedIds.map(u => u.id).join(',')
 + ' tags:' + window._uploadedIds.map(u => u.tag.replace('0and1life-SLUG', '')).join(',')
```

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
- `broken` 이 0인가? 모든 `nw`(naturalWidth)가 정상인가? (v4.0 Flow 산출물은 `nw 1226`)
- h2·표 개수가 삽입 전과 같은가?

**이어서 육안으로 확인한다:**

- 각 이미지의 피사체가 글 내용·주변 섹션과 맞는가?
- 3장 다양성 규칙(3-3)이 지켜졌는가 — 같은 구도·같은 피사체 유형이 반복되지 않는가?
- 히어로/대표이미지가 정상 반영됐는가?
- 증빙 캡처가 원래 자리에 그대로 있는가? (`window._evGuard` 확인)
- **워터마크 흔적(✦)이 남아 있지 않은가?** — 남아 있으면 STEP 5-4의 `cropRight` 값을 늘려 재캡처하거나, 이미 업로드된 파일을 0and1life.com **동일 출처**에서 canvas로 다시 읽어 재크롭·재업로드한다.
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
- **(v4.0) raw 오염 점검 결과**: v3.1 이하로 처리된 글에서 `ezToc>0` 또는 `blocks=0` 이 발견되면 해당 Post ID를 모두 나열하고 **사용자 확인 후 복구**를 제안한다
- 대표이미지: 선정된 이미지, 선정 이유, 설정 결과 (`window._featuredResult`)
- 피사체 정확성 검증: 각 이미지별 통과/재시도/건너뜀 여부, **2장 중 어느 쪽을 채택했는지**
- Skip된 경우 그 이유
- **(v4.0) 생성 소요시간**: 이미지별 생성 대기 시간을 기록한다. 60초를 넘긴 건이 있으면 Flow 지연으로 보고한다
- **삭제 대기 미디어**: 재크롭 등으로 남은 원본 미디어 ID를 나열하고 **사용자 확인을 요청**한다 (임의 삭제 금지)
- 루틴 자체의 오류·개선점이 발견됐다면 **수정할 조항 번호와 교체용 전문(前文)**을 함께 제시한다 — 사용자가 붙여넣기만 하면 되도록

---

### 중요 주의사항

- Chrome이 열려 있고, 0and1life.com WP admin에 로그인되어 있어야 함
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
- (v3.2) **증빙 판정은 `evidence-capture` 클래스·`evidence-` 파일명만으로 하지 않는다.** v1.28(2026-08-02) 이전 글에는 이 마커가 없다. figcaption의 `Captured YYYY-MM-DD`, 공공 출처 도메인 파일명(`*-go-kr`, `korea-kr`, `kosis`, `hometax`, `work24`, `price-go`), alt의 조회·확인·캡처 단서까지 폴백으로 본다
- (v3.3) **`window.open` 에 `'_blank'` 금지** — 탭이 Chrome MCP 그룹 밖에 열려 리스너 주입이 불가능해진다 (STEP 6-1)
- (v3.3) **javascript_tool 반환값에 이미지 URL·쿼리스트링을 그대로 담지 않는다** — `[BLOCKED: Cookie/query string data]` 로 출력 전체가 막힌다. 집계값 먼저, 파일명은 축약·치환해서 출력
- **(v3.4) 삽입 위치는 h2의 '문자 위치' 기준으로 계산** — 헤딩 개수 분위는 이미지를 글 뒤쪽에 몰아넣는다 (STEP 4)
- **(v3.4) 장시간 window 상태가 필요한 작업은 `/wp-admin/` 대시보드가 아니라 `media-new.php` 에서 수행** — 대시보드는 간헐적으로 자체 리다이렉트를 일으킨다
