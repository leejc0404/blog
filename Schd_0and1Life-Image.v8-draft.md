# 0and1Life 자동 이미지 삽입 태스크 (v8.0 — 실행 본문)

> 📚 **이 파일은 매 실행마다 처음부터 끝까지 읽는 '실행 본문'이다.** 실측 사례, 舊 버전 이력, 드물게 쓰는 절차(설명컷 SVG/HF 제작, 리비전 복구, 헤더 B형 병합, Flow UI 장애 대응)는 `Schd_0and1Life-Image.부록.md`에 있다.
> 부록은 **통째로 읽지 않는다.** 본문이 `→ 부록 §X`로 가리킬 때만 `grep -n "§X\|^#### X" 부록.md`로 줄 번호를 찾아 `sed -n 'a,bp'`로 그 절만 읽는다.
> 우선순위는 **본문 > 부록**이다. 부록의 舊 규칙이 본문과 다르면 본문을 따른다.

## 0. 실행 환경 · 공통 원칙

- **연결 폴더 루트 `CR`** = `get_device_info.connectedFolders` 첫 항목. `$HOME/mnt/Claude`와 같다. 사용자 이름(`win`/`USER`)을 경로에 박아 쓰지 않는다.
- **셸 모드**(`device_bash` 있음) / **브리지 모드**(없음): 브리지 모드면 `device_list_dir`·`device_stage_files`·`device_commit_files`로 바꿔 수행한다 → 부록 §실행 환경 공통.
- **브라우저**: Chrome(`mcp__claude-in-chrome__*`)을 쓴다. WP·Flow 로그인 세션이 Chrome에 있다. 탭은 새로 만들고, 끝나면 프리뷰 탭 1개만 남긴다.
- **비용 0원**: 유료 모델·크레딧 차감 옵션·유료 생성 서비스(Higgsfield 등)는 쓰지 않는다.
- **금지**: 발행·예약 전환, 제목 수정, 미디어·글 삭제(필요하면 보고만), 증빙 figure 수정, 자격증명 입력·로그인 폼 제출.
- **알림·보고는 한글**. 실행 시작 KST 시각(HH:MM)을 기억해 마지막 실행 기록에 쓴다.

### 0-1. 토큰 절약 규칙 (v8.0 신설 · 매 실행 적용)

1. **도구 호출 목표: 대상 1건 기준 40회 이하.** 넘으면 STEP 8에 사유를 적는다.
2. **JS는 한 호출에 '실행 + 검증 + 요약 반환'까지** 넣는다(최상위 `await` 지원). 읽기만 하는 추가 호출을 만들지 않는다.
3. **반환값은 숫자·짧은 이름만.** URL·쿼리스트링·본문 HTML을 반환하면 `[BLOCKED: Cookie/query string data]`로 막히거나 토큰을 낭비한다. 본문 확인은 `innerText`에서 URL을 지운 앞부분 2,000자 이내로 한다.
4. **상태 확인에 스크린샷을 쓰지 않는다.** 스크린샷은 ⓐ 후보 채택 판정 ⓑ 원본 확대 검수 ⓒ 최종 육안 확인에만 쓰고 `scale 0.4~0.6`으로 찍는다.
5. 클릭·입력·대기·확인은 `browser_batch`로 묶는다. 단, Flow에서 **'타이핑→클릭→다음 타이핑'은 한 배치에 넣지 않는다**(STEP 5).
6. 이미 충족된 글(넣을 장수 0, 스톡 없음)은 본문을 읽지 않고 건너뛴다.

## 1. 목적과 상한 (v7.5 네이버 모바일 포맷 유지)

최근 2일 안에 수정된 WP draft·future 글 가운데 **데코 이미지가 2장 미만인 글**에 이미지를 채운다.

- **총량 상한: 글당 이미지 3장(히어로 포함).** 보통 히어로 1 + Writer가 넣은 증빙 1 + 본문 1이다.
- **본문 영상은 0~1개**이고 이미지 장수와 따로 센다. 모션 MP4·공식 유튜브를 합쳐 1개까지다.
- 본문에 `div.o1-chart`나 숫자 `<table>`이 있으면 같은 숫자를 다시 그린 설명컷은 넣지 않는다.
- **넣지 않는 위치**: 📌 요약 박스(`.o1-summary`) 앞·안, `✅ 오늘 할 일`(`.o1-todo`) 안, `p.o1-step`과 다음 H2 사이, `[ez-toc]`와 첫 `p.o1-step` 사이. **섹션의 굵은 답 문단 바로 뒤**에 넣는다.
- **캡션은 한국어 한 줄**이다: `그림: … 직접 계산` / `{기관·브랜드} {자료명} · YYYY-MM-DD 확인` / `영상: {채널명} 공식 유튜브 · YYYY-MM-DD 확인`. 영어 `Captured`·`Source:`는 쓰지 않는다.

## 2. 이미지 종류와 판정 순서 (v8.0 — '진짜처럼'의 핵심)

> 독자가 사진을 '진짜'라고 느끼는 가장 확실한 방법은 **진짜를 쓰는 것**이다. AI 생성은 진짜를 구할 수 없을 때의 대체 수단이다.

본문 슬롯마다 **아래 순서로 위에서부터 처음 맞는 것**을 고른다. 히어로도 같은 순서지만 ③은 쓰지 않는다.

| 순서 | 종류 | 고르는 경우 | 절차 |
|---|---|---|---|
| ① | **공식 실물 이미지** (`official`) | 글이 특정 제품·앱·서비스·매장·시설·기관을 다루고, 그 **실제 모습**이 독자 판단에 도움이 될 때 | STEP 3-A |
| ② | **공식 유튜브 영상** (`video`) | 사용법·절차·현장처럼 **움직임으로 봐야 이해되는** 내용이고, 공식 채널 영상이 있을 때. 글당 1개, 이미지 장수와 별도 | STEP 3-B |
| ③ | **Claude 설명컷** (`still`/`motion`) | 차트·표에 **없는** 판단 기준(조건 분기)이나 체크리스트일 때 | STEP 3-C |
| ④ | **Flow 촬영컷** (`photo`) | 위 셋이 없거나 맞지 않을 때. 장소·상황·분위기를 보여주는 자리 | STEP 3-D · 5 |

- **히어로**: 제품·앱 글이면 공식 제품·앱 대표 이미지(①)를 쓰고, 그 외 글은 Flow 촬영컷(④)을 쓴다. **UI 스크린샷과 글자가 많은 배너는 히어로로 쓰지 않는다**(제목 오버레이와 겹친다).
- 공식 실물은 증빙(evidence)으로 분류되므로 넣으면 생성 장수가 자동으로 줄어든다. 총량 상한 3장은 그대로다.
- 판정 결과를 `window._slotTypes = ['official']`처럼 삽입 순서대로 적는다(히어로는 따로 `window._heroType = 'photo' | 'official'`).

## STEP 1. 대상 찾기 (WP REST 1회)

새 탭에서 `https://0and1life.com/wp-admin/media-new.php`로 가서 아래를 **한 호출**로 실행한다. `wp-login.php?…reauth=1`로 튕기면 세션이 만료된 것이다. 로그인하지 말고 STEP 8에 "WP 세션 만료 — 사용자 직접 로그인 필요"를 적은 뒤 종료한다.

```javascript
const s = Array.from(document.querySelectorAll('script:not([src])')).map(x => x.textContent).join('\n');
const m = s.match(/apiFetch\.createNonceMiddleware\(\s*["']([a-f0-9]+)["']/);
window._nonce = m ? m[1] : (window.wpApiSettings ? wpApiSettings.nonce : null);
let out = 'url:' + location.pathname + ' nonce:' + (window._nonce ? 'ok' : 'MISSING');
if (window._nonce) {
  const since = new Date(Date.now() - 2 * 864e5).toISOString().slice(0, 19);
  const d = await fetch('/wp-json/wp/v2/posts?status=draft,future&modified_after=' + since
    + '&per_page=20&context=edit&orderby=modified&order=asc&_fields=id,title,status,content,date,modified,featured_media,slug',
    {headers: {'X-WP-Nonce': window._nonce}}).then(r => r.json());
  window._targets = d;
  out += '\n' + d.map(p => p.id + ' | ' + p.status + ' | ' + p.modified.slice(0, 16) + ' | fm:' + p.featured_media + ' | ' + p.slug
    + ' | raw:' + (typeof p.content?.raw === 'string' ? 'ok' : 'RAW-MISSING')).join('\n');
}
out
```

- 0건이면 "최근 2일 draft 글 없음"으로 실행 기록만 남기고 끝낸다(알림 없음). Notion 확인이 필요하면 → 부록 §STEP 1.
- `RAW-MISSING`이 하나라도 있으면 진행하지 않는다. `context=edit`가 없거나 nonce 권한 문제다. `content.rendered`로 대신하는 것은 금지다(원본을 파괴한다).

## STEP 2. 분류 — 넣을 장수 계산

```javascript
window._cls = window._targets.map(p => {
  const html = p.content.raw, div = document.createElement('div'); div.innerHTML = html;
  const R = {evC: /evidence-capture/i, evN: /^evidence-/i, stock: /unsplash\.com|pexels\.com|pixabay\.com|FEATURED_IMAGE/i,
    gen: /^(0and1life|koreaplug)-/i, cap: /Captured\s*\d{4}\s*[-.\/]\s*\d{1,2}\s*[-.\/]\s*\d{1,2}/i,
    src: /(go[-_.]kr|korea[-_.]kr|kosis|hometax|work24|price[-_.]go)/i,
    alt: /(캡처|캡쳐|스크린샷|Captured|Screenshot|조회한|조회 결과|확인한|고지서|명세서|모의계산)/i,
    legacy: /-\d{2,4}x\d{2,4}\.(jpe?g|png|webp|gif)$|\.(jpe?g|png|gif)$/i};
  let evidence = 0, stock = 0, deco = 0; const unknown = [];
  for (const img of div.querySelectorAll('img')) {
    const src = img.getAttribute('src') || '', base = (src.split('/').pop() || '').split('?')[0];
    const fig = img.closest('figure'), cl = fig?.getAttribute('class') || '', cap = fig?.querySelector('figcaption')?.textContent || '';
    const alt = img.getAttribute('alt') || '';
    if (R.evC.test(cl) || R.evN.test(base)) evidence++;
    else if (R.stock.test(src)) stock++;
    else if (R.gen.test(base)) deco++;
    else if (R.cap.test(cap) || R.src.test(base) || R.alt.test(alt)) evidence++;
    else { deco++; if (!R.legacy.test(base)) unknown.push(base.slice(0, 40)); }
  }
  deco += div.querySelectorAll('figure.ol-motion, figure.motion-figure').length;
  const video = div.querySelectorAll('figure.ol-motion, figure.ol-video, iframe[src*="youtube"]').length;
  const genCount = deco >= 2 ? 0 : Math.max(0, Math.min(2 - deco, 3 - evidence - deco - stock));
  return {id: p.id, status: p.status, fm: p.featured_media, slug: p.slug, evidence, stock, deco, video, genCount,
    hasStockImg: stock > 0, unknown, chart: div.querySelectorAll('.o1-chart').length, table: div.querySelectorAll('table').length,
    blocks: (html.match(/<!-- wp:/g) || []).length, ezToc: (html.match(/ez-toc-/g) || []).length};
});
window._cls.map(c => c.id + ' ' + c.status + ' fm:' + c.fm + ' ev:' + c.evidence + ' stk:' + c.stock + ' deco:' + c.deco
  + ' vid:' + c.video + ' gen:' + c.genCount + ' unk:' + c.unknown.length + ' chart:' + c.chart + ' tbl:' + c.table
  + ' blocks:' + c.blocks + ' ezToc:' + c.ezToc).join('\n')
```

- **처리 대상** = `genCount > 0` 또는 `hasStockImg`인 글. 오래된 것부터 처리한다.
- `hasStockImg`면 히어로 1장을 별도로 만들어 스톡 자리를 바꾼다(총량 변화 없음).
- `unknown`이 있으면 바로 건너뛰지 않는다. 해당 figure의 캡션·모양을 보고 증빙인지 데코인지 손으로 정한 뒤 다시 계산한다(`.webp`만 해당).
- `ezToc > 0` 또는 `blocks = 0`이면 원본이 오염된 것이다. 삽입하지 말고 보고한다 → 부록 §3-1 리비전 복구.
- **최종 총량 `evidence + deco + stock + genCount ≤ 3`**을 생성 전에 한 번 더 센다.

## STEP 3. 본문 읽기 → 슬롯 결정

대상 글 본문을 **한 호출**로 읽는다. 텍스트 앞 2,000자와 구조 위치표만 반환한다.

```javascript
const p = window._targets.find(x => x.id === POST_ID); const c = p.content.raw, L = c.length;
window._rawContent = c;
const d = document.createElement('div'); d.innerHTML = c;
const txt = d.innerText.replace(/https?:\/\/\S+/g, ' ').replace(/[?&=]/g, '').replace(/\n\s*\n+/g, '\n');
const marks = [];
for (const [re, n] of [[/<h2[^>]*>([\s\S]*?)<\/h2>/g, 'H2'], [/<figure[^>]*>/g, 'FIG'], [/class="(o1-[a-z]+)/g, 'O1'], [/\[ez-toc\]/g, 'TOC']])
  for (const m of c.matchAll(re)) marks.push(Math.round(m.index / L * 100) + '% ' + n + ' ' + (m[1] || '').replace(/<[^>]*>/g, '').slice(0, 30));
txt.slice(0, 2000) + '\n=====\n' + marks.sort((a, b) => parseInt(a) - parseInt(b)).join('\n')
```

뒷부분이 필요하면 `txt.indexOf('섹션 제목')`부터 1,500자씩 더 읽는다. 전체를 반복해서 읽지 않는다.

본문에서 아래 네 가지를 적는다(STEP 8에 그대로 쓴다).

1. **실물 대상**: 글에 나오는 제품·앱·서비스·회사·장소·기관의 정확한 이름(예: `G마켓 꼭 멤버십 라이프+`, `디즈니+`)
2. **훅 문장 2개**: 독자가 가장 놀랄 문장을 원문 그대로 적는다. 숫자가 충돌하거나 손해가 확정되는 문장이다.
3. **계절·시간·장소**: 글 날짜의 계절(11~2월은 겨울 옷차림·난방), 등장 장소(거실·편의점·은행 창구·병원 접수대 등)
4. **삽입 후보 위치**: 슬롯 1 = 훅 문장이 있는 섹션의 굵은 답 문단 뒤. 증빙 figure ±5%pt 안은 피한다.

그다음 §2 표 순서대로 슬롯 종류를 정한다.

### 3-A. 공식 실물 이미지 (`official`) — v8.0 강화

**쓸 수 있는 출처 (이것만 쓴다)**

| 출처 | 찾는 법 | 비고 |
|---|---|---|
| 기업·기관 **공식 뉴스룸·보도자료 첨부 이미지** | `WebSearch "{대상} 보도자료 이미지"` → 공식 도메인 결과만 | 가장 안전하다. 제품 단독컷 우선 |
| 공식 사이트 **대표 이미지(og:image)** | 공식 페이지를 탭으로 열고 `document.querySelector('meta[property="og:image"]')?.content` | 글자가 많은 배너면 쓰지 않는다 |
| **앱스토어·플레이스토어 개발사 스크린샷** | 공식 앱 페이지 | 앱 화면 설명용. 히어로 금지 |
| 공식 SNS·유튜브 썸네일 | 공식 계정(인증 배지 또는 공식 사이트에서 링크됨) | 썸네일은 `maxresdefault.jpg` |
| 아마존 제품 이미지 | 제휴 링크용 | **다운로드·업로드 금지, 핫링크만**, srcset 없음 |

**쓰지 않는다**: 출처를 모르는 이미지, 타인 블로그·카페·언론사 기자가 찍은 사진, 워터마크 스톡, 광고 모델 얼굴이 크게 나온 컷, 이름·전화번호·계정 ID·차량번호가 보이는 화면, 가격이 적힌 옛 프로모션 배너(본문 가격과 어긋나면 신뢰가 깨진다).

**품질 기준**: 원본 폭 1,000px 이상 권장, 600px 미만이면 쓰지 않는다(확대 금지). 설명에 필요한 영역만 크롭한다.

**호출 예산**: 대상 1개당 찾기 3회(검색 1 + 페이지 확인 2)까지다. 못 찾으면 다음 순서(②~④)로 넘어가고 STEP 8에 "공식 실물 없음"을 남긴다.

**캡처·업로드 (같은 출처 탭 경로)**: WP media-new 탭(STEP 6-1 리스너가 있는 탭)에서 `window.open(이미지URL)`로 연다. `'_blank'`는 넘기지 않는다. 열린 탭에서 아래를 실행하면 그 탭이 이미지 자신의 출처라 캔버스가 막히지 않는다.

```javascript
// 이미지 탭에서 실행 — CROP: [x, y, w, h] 비율(전체면 [0,0,1,1]) · N: 슬롯 번호(히어로면 'hero')
const CROP = [0, 0, 1, 1], N = '1', SLUG = 'SLUG', ALT = 'ALT 한국어 60자 안팎';
const im = document.images[0], W = im.naturalWidth, H = im.naturalHeight;
const sx = W * CROP[0], sy = H * CROP[1], sw = W * CROP[2], sh = H * CROP[3], k = Math.min(1, 1100 / sw);
const c = document.createElement('canvas'); c.width = Math.round(sw * k); c.height = Math.round(sh * k);
const x = c.getContext('2d'); x.imageSmoothingQuality = 'high'; x.drawImage(im, sx, sy, sw, sh, 0, 0, c.width, c.height);
const url = c.toDataURL('image/webp', 0.85);   // ⛔ toBlob은 멈출 수 있다(2026-11-28 실측) — toDataURL만 쓴다
window.opener.postMessage({dataUrl: url, filename: 'evidence-' + SLUG + '-' + N + '.webp', altText: ALT}, 'https://0and1life.com');
'src ' + W + 'x' + H + ' -> ' + c.width + 'x' + c.height + ' ' + Math.round(url.length * 0.75 / 1024) + 'KB sent'
```

- 캔버스 오류(`Tainted`)가 나면 그 이미지는 다른 출처에서 리다이렉트된 것이다. 같은 이미지의 원본 URL로 한 번만 다시 열고, 그래도 안 되면 포기한다.
- 파일명이 `evidence-`로 시작해야 다음 회차 분류기가 증빙으로 센다.
- 캡션 예: `G마켓 꼭 멤버십 안내 이미지 · 2026-11-28 확인`. `window._cap[N]`에 넣는다.
- 아마존은 업로드하지 않고 STEP 7에서 `<img src="아마존 URL" loading="lazy">`로 직접 넣는다.

### 3-B. 공식 유튜브 영상 (`video`) — v8.0 신설

**넣는 조건 (모두 만족)**

- 본문에 영상(모션 MP4·유튜브)이 아직 없다(`video == 0`).
- 사용법·가입·해지 절차, 매장·시설 현장, 기관의 제도 안내처럼 **글을 읽고 바로 따라 할 장면**이 영상에 있다.
- **공식 채널**이다: 인증 배지가 있거나, 공식 사이트·공식 SNS에서 그 채널로 링크된다. 언론사 뉴스 클립·개인 리뷰어는 쓰지 않는다.
- 업로드 2년 이내, 한국어(자막 포함), 가능하면 3분 이하. 영상 속 가격·조건이 본문과 다르면 쓰지 않는다.

**찾는 법 (호출 3회까지)**: `WebSearch "{대상} 공식 유튜브 {핵심 동작}"`(standard) 1회 → 후보 영상 페이지를 열어 채널명·업로드일·길이를 확인한다. **임베드 허용 확인**: `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=ID&format=json`을 탭에서 열어 JSON이 나오면 허용된 것이다(401·404면 쓰지 않는다).

**마크업** (STEP 7이 만든다 · 쿠키 없는 도메인 · 지연 로딩)

```html
<figure class="ol-video" style="margin:20px 0">
  <div style="position:relative;aspect-ratio:16/9;border-radius:8px;overflow:hidden;background:#000">
    <iframe src="https://www.youtube-nocookie.com/embed/VIDEO_ID?rel=0" title="영상 제목 한국어" loading="lazy"
      allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen
      style="position:absolute;inset:0;width:100%;height:100%;border:0"></iframe>
  </div>
  <figcaption style="font-size:13px;color:#777;margin-top:6px">영상: {채널명} 공식 유튜브 · YYYY-MM-DD 확인</figcaption>
</figure>
```

- 영상은 이미지 장수에 넣지 않는다. 다만 **같은 내용의 사진·설명컷과 연달아 두지 않는다**(인접 이미지와 5%pt 이상 떨어뜨린다).
- 영상만으로 정보를 전하지 않는다. 핵심 내용은 본문 텍스트에 이미 있어야 한다.

### 3-C. Claude 설명컷 (`still`/`motion`)

- 차트·표가 이미 있는 글에서는 **그 숫자를 다시 그리지 않는다.** 차트에 없는 조건 분기(예: `48만원 미만 → 남음 / 48~81만원 → 다시 계산 / 81만원 초과 → 국내가 쌈`)나 체크리스트만 만든다.
- 정적 WebP가 기본이다. 모션 MP4는 글당 1개, 움직임이 이해를 도울 때만 쓴다. 인라인 SVG는 본문에 넣지 않는다.
- 숫자·글자는 본문 그대로 쓰고, 최소 글자 크기와 줄당 약 24자를 지킨다. 업로드 전에 렌더 결과를 Read로 직접 본다.
- 제작 절차(HF 템플릿 · SVG 규격 · 검증기 · 렌더 · 업로드) → 부록 §3-10.

### 3-D. Flow 촬영컷 (`photo`) — v8.0 사실감 규칙

> 판정 질문 두 개: **"지인이 단톡방에 올린 휴대폰 사진이라고 하면 믿겠는가?"**, **"이 사진이 이 글의 그 장면이라고 바로 알겠는가?"**

**① AI 티가 나는 다섯 가지와 해법**

| AI 티 | 원인 | 프롬프트 해법 |
|---|---|---|
| 화면 속 가짜 UI(색 블록·의미 없는 글자) | 모델이 한글 UI를 못 그린다 | 화면을 **비스듬히 돌려 반사광으로 내용이 안 보이게** 하거나 **화면이 꺼져 있거나 프레임 밖**으로 둔다. `phone screen turned away / angled with window reflection, content not visible` |
| 텅 빈 간판·표지판 | 글자 금지 조건과 충돌한다 | 간판이 **프레임에 안 들어오게 타이트하게** 잡거나 **멀리서 흐리게** 둔다. 간판을 정면으로 넣지 않는다 |
| 너무 정돈된 공간 | 스톡 사진 학습 | **생활 흔적 2개**를 명시한다: 충전 케이블, 접힌 영수증, 반쯤 마신 텀블러, 겉옷이 걸린 의자 등 |
| 계절·시간이 글과 다름 | 지정 안 함 | 글 날짜의 계절 옷차림·소품을 넣는다(11~2월: 니트 소매·패딩·가습기·귤, 6~8월: 반팔·선풍기) |
| 플라스틱 피부·완벽한 손 | 연출 조명 | 손은 **한 손만, 일상 동작 중간**. `natural skin texture, short unpolished nails, slightly creased knit sleeve` |

**② 한국 실물 디테일 사전 (장소별로 2~3개 골라 쓴다)**

| 장소 | 디테일 |
|---|---|
| 아파트 거실 | 벽걸이 TV와 셋톱박스, 원목 거실장, 패브릭 소파와 니트 담요, 베란다 확장 창, 에어컨 스탠드 |
| 주방·식탁 | 인덕션, 전기밥솥, 락앤락 반찬통, 원목 식탁, 멀티탭 |
| 편의점 | 계산대 카드 단말기, 비닐봉투 걸이, 핫바 온장고, 1+1 스티커는 흐리게 |
| 은행·관공서 창구 | 번호표 발권기, 투명 아크릴 칸막이, 대기 의자 줄, 서류 받침대 |
| 병원 접수 | 접수 창구 유리, 대기 번호 화면(흐리게), 소독제 펌프 |
| 사무실 | 파티션 책상, 듀얼 모니터, 사원증 목걸이, 텀블러, 포스트잇 |
| 카페·스터디카페 | 원목 테이블, 노트북, 아이스 아메리카노 플라스틱 컵, 콘센트 타워 |
| 대중교통 | 지하철 손잡이, 버스 하차벨, 교통카드 단말기 |

**③ 프롬프트 골격 v8.0** (영문 그대로 쓰고 `[ ]`만 채운다 · 400~700자)

```
Candid smartphone photo taken on an iPhone 15 Pro main camera (24mm), handheld at eye level, slightly imperfect framing, like a photo a friend sent in a group chat.
[계절] [시간대] at a real Korean [장소]: [한국 실물 디테일 2~3개], [생활 흔적 2개].
[한 손이 하는 일상 동작 — 중간 순간]. [화면 처리: phone screen angled with soft window reflection, content not visible].
Bright natural daylight from a window, true-to-life colors, natural skin texture, ordinary everyday mood, most of the scene in focus.
no readable text, no logos, no watermark, no fake user interface, no colorful placeholder blocks, no signage facing camera, no dark or moody lighting, no cinematic color grading, no heavy bokeh, no floating objects, no surreal elements, no visible face, no posed model, no 3D render look, photorealistic
```

- 손해·경고성 글은 둘째 줄 앞에 `overcast day,`, 넷째 줄을 `Soft diffused daylight, calm quiet mood, normal exposure, true-to-life colors.`로 바꾼다.
- ⛔ 금지: 공중에 뜬 물체, 불타는 봉투 같은 초현실 은유, 범용 은유(모래시계·저울·전구·돼지저금통·악수), 풀프레임 렌즈 명시, 밤 장면·단일 조명.
- 히어로는 **중경**(공간이 보이게), 본문은 **근접**(손과 물건)으로 거리를 다르게 한다. 같은 주인공 소재를 두 장에 쓰지 않는다.
- alt는 한국어 60자 안팎으로, **장면을 사실대로** 쓴다("거실에서 휴대폰을 든 손" 수준. 없는 내용을 쓰지 않는다).

**④ 원본 확대 검수 (v8.0 신설 · 채택 전 필수)** — 그리드 썸네일만 보면 손가락·화면 글자 이상을 놓친다. `zoom` 도구는 Flow 탭을 망가뜨리므로 쓰지 않는다. 대신 원본 픽셀을 캔버스로 확대해 덮어 보고 스크린샷 1장을 찍는다.

```javascript
// 그리드 탭에서 실행 — IDX: 후보 인덱스 2개, BOX: 확인할 영역 비율 [x, y, w, h] (손·화면 부분)
const IDX = [0, 1], BOX = [0.35, 0.25, 0.45, 0.6];
const g = Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 1000);
const ov = document.createElement('div'); ov.id = 'ol-inspect';
ov.style.cssText = 'position:fixed;inset:0;z-index:999999;background:#000;display:flex;gap:8px;padding:8px';
for (const n of IDX) {
  const im = g[n], W = im.naturalWidth, H = im.naturalHeight, c = document.createElement('canvas');
  c.width = W * BOX[2]; c.height = H * BOX[3];
  c.getContext('2d').drawImage(im, W * BOX[0], H * BOX[1], c.width, c.height, 0, 0, c.width, c.height);
  c.style.cssText = 'flex:1;min-width:0;object-fit:contain;width:50%;height:auto;align-self:center';
  ov.appendChild(c);
}
document.body.appendChild(ov); 'overlay on'
// 스크린샷 1장으로 판정한 뒤: document.getElementById('ol-inspect').remove()
```

검수 항목: 손가락 개수·관절, 화면·간판의 가짜 글자, 물건 모양 왜곡, 한국 기물인지 여부. 둘 다 탈락이면 **'더 극적으로'가 아니라 '더 평범하게'** 고쳐 1회만 다시 만든다. 그래도 안 되면 그 슬롯은 비운다.

## STEP 4. 삽입 위치 확정

- 위치는 **h2 개수가 아니라 문자 위치**로 정한다. 슬롯마다 "섹션 h2 → 그 뒤 첫 굵은 답 문단의 `</p>` 끝"을 삽입점으로 삼는다.
- 증빙 figure ±5%pt 안, §1의 금지 위치에는 넣지 않는다. 비율보다 **섹션 주제와 이미지 내용이 맞는 것**을 우선한다.
- 스톡 플레이스홀더가 N개면 첫째는 히어로가, 나머지 (N−1)개는 본문 이미지가 교체로 채운다. 그만큼 새 삽입 수를 줄인다.
- 삽입점은 STEP 7에서 **최신 raw 기준으로 다시 계산**한다.

## STEP 5. Flow 생성 (촬영컷이 0장이면 건너뛴다)

프로젝트: `https://labs.google/fx/ko/tools/flow/project/6a6af995-4d64-4bbb-8e97-4be7aa267e6d` (`flow.google.com`으로 리다이렉트된다).

- 계정 선택 화면이면 `leejc0404@gmail.com`만 클릭한다. 비밀번호 화면이 나오거나 계정이 없으면 멈추고 "Flow 세션 만료"로 보고한다. 이때 STEP 3까지 만든 프롬프트 전문을 보고에 남긴다.

**5-1. 설정 확인 (한 호출)** — 설정 칩을 열어 모델 목록 아래 `생성 시 0 크레딧` 표시를 확인한다.

```javascript
const bs = () => Array.from(document.querySelectorAll('button'));
const cfg = bs().find(x => /설정 트리거/.test(x.getAttribute('aria-label') || ''));
cfg.click(); await new Promise(r => setTimeout(r, 1500));
const txt = t => (t.textContent || '').replace(/\s+/g, ' ').trim();
const st = bs().filter(b => /^(image이미지|videocam동영상|crop_16_916:9|x[1-4])$/.test(txt(b))).map(b => txt(b) + ':' + (b.getAttribute('aria-pressed') || b.getAttribute('aria-selected') || b.getAttribute('aria-checked')));
const credit = (document.body.innerText.match(/생성 시[^\n]{0,20}크레딧[^\n]{0,10}/) || ['credit:?'])[0];
const agent = bs().find(b => /spark/.test(txt(b)));
document.body.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
'cfg:' + txt(cfg) + ' | ' + st.join(' ') + ' | ' + credit + ' | agent:' + (agent ? txt(agent) + ':' + agent.getAttribute('aria-pressed') : 'na')
```

- 통과 조건: `이미지:true`, `16:9:true`, `x2:true`, 모델이 `Nano Banana Pro`이면서 `0 크레딧`, 에이전트(spark) `false`.
- Pro가 0크레딧이 아니거나 애매하면 `Nano Banana 2`로 바꾼다. 틀린 항목은 패널에서 바로잡는다 → 부록 §5-1.

**5-2. 투입 (건별 · 동시 2건까지)**

1. `.ProseMirror`에 focus를 준다 → `pm:true` 확인 → `computer:type`으로 프롬프트 입력
2. 전송 버튼이 풀릴 때까지 폴링하고 좌표를 읽는다(아래 코드)
3. 좌표를 클릭하고 3초 뒤 `boxLen < 20`이면 전송 성공이다. 20 이상이면 다음 프롬프트를 치지 않고 2로 돌아간다

```javascript
window._findSend = () => { const pm = document.querySelector('.ProseMirror'); let b = pm;
  for (let i = 0; i < 6; i++) { b = b.parentElement; if (b.querySelectorAll('button').length >= 3) break; }
  const a = Array.from(b.querySelectorAll('button')); return a[a.length - 1]; };
let res = 'wait'; for (let t = 0; t < 6; t++) { if (!window._findSend().disabled) { res = 'enabled'; break; } await new Promise(r => setTimeout(r, 5000)); }
const r = window._findSend().getBoundingClientRect(), sc = SHOT_W / innerWidth;   // SHOT_W = 스크린샷 좌표계 폭(결과에 표시됨, 예 1120)
res + ' len:' + document.querySelector('.ProseMirror').textContent.trim().length + ' xy:' + Math.round((r.left + r.width / 2) * sc) + ',' + Math.round((r.top + r.height / 2) * sc)
```

**5-3. 완료 대기**: 30초 폴링(6×5초)을 쓴다. CDP 상한이 45초라 그 이상 기다리지 않는다. 미완료면 같은 호출을 반복한다. 두 번 연속 값이 같거나 타임아웃이 나면 스크린샷 1장으로 확인한다.

**5-4. 채택**: ⓐ `outline` 마킹(0 빨강·1 연두·2 하늘·3 자홍)과 그리드 스크린샷 1장으로 인덱스를 확인한다. 최신 결과가 인덱스 0이다. ⓑ 후보 쌍마다 3-D ④ 원본 확대 검수를 한다. ⓒ 채택한다. ⛔ `computer:zoom` 금지.

**5-5. 캡처 — 그리드 탭에서 바로 (v8.0 · 2026-11-28 실측 반영)**

그리드 이미지 출처를 먼저 본다. `flow.google.com`(페이지와 같은 출처)이면 그리드 탭에서 바로 캡처한다. `flow-content.google`(다른 출처)일 때만 옛 '이미지 탭' 경로를 쓴다 → 부록 §5-5.

```javascript
// 그리드 탭 · PICK: 채택 인덱스, KEYS: 슬롯 이름(같은 순서)
const PICK = [2, 1], KEYS = ['_imgHero', '_img1'];
const g = Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 1000);
g.forEach(i => { i.style.outline = 'none'; });
const host = new URL(g[0].src).host, out = [];
PICK.forEach((n, k) => {
  const im = g[n], cw = im.naturalWidth - 150, ch = im.naturalHeight, s = Math.min(1, 1100 / cw);   // 우측 150px = 워터마크 제거
  const c = document.createElement('canvas'); c.width = Math.round(cw * s); c.height = Math.round(ch * s);
  const x = c.getContext('2d'); x.imageSmoothingQuality = 'high'; x.drawImage(im, 0, 0, cw, ch, 0, 0, c.width, c.height);
  window[KEYS[k]] = c.toDataURL('image/webp', 0.85);   // ⛔ toBlob·new Image() 로드는 멈춘다(2026-11-28) — 쓰지 않는다
  out.push(KEYS[k] + ' ' + c.width + 'x' + c.height + ' ' + Math.round(window[KEYS[k]].length * 0.75 / 1024) + 'KB');
});
window._wpWin = window.open('https://0and1life.com/wp-admin/media-new.php');   // ⛔ '_blank' 금지
'host:' + host + ' | ' + out.join(' | ') + ' | wp:' + !!window._wpWin
```

- 정상값은 `1100x689`, 장당 30~70KB다. `Tainted`가 나면 출처가 바뀐 것이다 → 부록 §5-5.

## STEP 6. 업로드 (postMessage)

**6-1.** 새로 열린 WP 탭을 `tabs_context_mcp`로 확인한다. 같은 배치에서 탭을 닫은 직후 다른 탭을 쓰면 그룹 오류가 나므로, 닫은 뒤에는 다시 조회한다. 그다음 리스너를 붙인다.

```javascript
const s = Array.from(document.querySelectorAll('script:not([src])')).map(x => x.textContent).join('\n');
window._nonce = (s.match(/apiFetch\.createNonceMiddleware\(\s*["']([a-f0-9]+)["']/) || [])[1] || window.wpApiSettings?.nonce;
window._uploadedIds = []; window._upErrors = [];
window.addEventListener('message', async e => {
  if (!e.data?.dataUrl) return; const {dataUrl, filename, altText} = e.data;
  try {
    const [h, b64] = dataUrl.split(','), mime = h.match(/:(.*?);/)[1], bin = atob(b64), u8 = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    const fd = new FormData(); fd.append('file', new Blob([u8], {type: mime}), filename);
    const j = await fetch('/wp-json/wp/v2/media', {method: 'POST', headers: {'X-WP-Nonce': window._nonce}, body: fd}).then(r => r.json());
    if (!j.id) return window._upErrors.push(filename + ' ' + JSON.stringify(j).slice(0, 120));
    await fetch('/wp-json/wp/v2/media/' + j.id, {method: 'POST', headers: {'X-WP-Nonce': window._nonce, 'Content-Type': 'application/json'}, body: JSON.stringify({alt_text: altText})});
    window._uploadedIds.push({id: j.id, url: j.source_url, alt: altText, tag: filename});
  } catch (err) { window._upErrors.push(filename + ' ' + err.message); }
});
'nonce:' + (window._nonce ? 'ok' : 'MISSING') + ' listener ready'
```

**6-2.** 그리드 탭에서 `window._wpWin.postMessage({dataUrl, filename: '0and1life-' + SLUG + '-' + n + '.webp', altText}, 'https://0and1life.com')`를 슬롯마다 연속 전송한다(n = `hero`·`1`·`2`). 공식 실물은 3-A 코드가 같은 리스너로 보낸다.

**6-3.** WP 탭에서 한 번만 폴링한다(최대 20초). `up:N err:0`과 `id+태그`만 반환한다. 도착 순서는 섞이므로 STEP 7에서 **파일명 태그로 매핑**한다.

## STEP 7. 삽입 · 교체 · 저장 (WP 탭 · 두 호출)

**7-1. 조립 + 검증 (한 호출)** — `POST_ID`, `SLOTS`만 채운다. `SLOTS`는 삽입할 본문 슬롯 목록이다: `{n:'1', type:'photo'|'official'|'still'|'motion'|'video', h2:'섹션 제목 일부', cap:'캡션(사진은 빈 문자열)', vid:'유튜브 ID', vtitle:'영상 제목'}`.

```javascript
const POST_ID = 0, SLOTS = [{n: '1', type: 'photo', h2: '섹션 제목 일부', cap: ''}];
const d = await fetch('/wp-json/wp/v2/posts/' + POST_ID + '?context=edit&_fields=content,featured_media,status,date', {headers: {'X-WP-Nonce': window._nonce}}).then(r => r.json());
const before = d.content.raw; window._finalContent = before; window._postId = POST_ID; window._origStatus = d.status; window._curFeatured = d.featured_media;
window._byTag = {}; window._uploadedIds.forEach(u => { const m = u.tag.match(/-(hero|\d)\.webp$/); if (m) window._byTag[m[1]] = u; });
const capH = t => t ? '\n    <figcaption style="font-size:13px;color:#777;margin-top:6px">' + t + '</figcaption>' : '';
const imgH = (u, lazy) => '<img class="wp-image-' + u.id + '"' + (lazy ? ' loading="lazy" decoding="async"' : '') + ' style="width:100%;display:block;height:auto;border-radius:8px;" src="' + u.url + '" alt="' + u.alt + '" />';
const mv = window._mv || {}; let c = before; const skipped = [];
// 뒤 슬롯부터 넣어야 앞 인덱스가 밀리지 않는다
const pts = SLOTS.map(s => { const h = [...c.matchAll(/<h2[^>]*>([\s\S]*?)<\/h2>/g)].find(m => m[1].includes(s.h2)); return h ? c.indexOf('</p>', h.index) + 4 : -1; });
SLOTS.map((s, i) => [s, pts[i]]).sort((a, b) => b[1] - a[1]).forEach(([s, at]) => {
  let blk = null; const u = window._byTag[s.n];
  if (at < 4) return skipped.push(s.n + ':h2');
  if (s.type === 'photo' && u) blk = '<figure style="margin:20px 0">\n    ' + imgH(u, true) + '\n  </figure>';
  if (s.type === 'official' && u) blk = '<figure class="evidence-capture" style="margin:20px 0">\n    ' + imgH(u, true) + capH(s.cap) + '\n  </figure>';
  if (s.type === 'still' && mv[s.n]?.still) blk = '<figure style="margin:20px 0">\n    ' + imgH({...mv[s.n].still, alt: mv[s.n].alt}, true).replace('<img ', '<img width="1280" height="720" ') + capH(s.cap) + '\n  </figure>';
  if (s.type === 'motion' && mv[s.n]?.mp4) blk = '<figure class="ol-motion" style="margin:20px 0">\n    <video src="' + mv[s.n].mp4.url + '" poster="' + mv[s.n].poster.url + '" width="1280" height="720" autoplay muted loop playsinline preload="metadata" aria-label="' + mv[s.n].alt + '" style="width:100%;height:auto;display:block;border-radius:8px;"></video>' + capH(s.cap) + '\n  </figure>';
  if (s.type === 'video' && s.vid) blk = '<figure class="ol-video" style="margin:20px 0">\n    <div style="position:relative;aspect-ratio:16/9;border-radius:8px;overflow:hidden;background:#000"><iframe src="https://www.youtube-nocookie.com/embed/' + s.vid + '?rel=0" title="' + s.vtitle + '" loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="position:absolute;inset:0;width:100%;height:100%;border:0"></iframe></div>' + capH(s.cap) + '\n  </figure>';
  if (!blk) return skipped.push(s.n + ':' + s.type);
  c = c.slice(0, at) + '\n  ' + blk + c.slice(at);
});
// 스톡 교체 — 첫째는 히어로(fetchpriority, lazy 금지), 둘째부터는 남은 본문 이미지
const hero = window._byTag['hero']; let k = 0;
if (hero) c = c.replace(/<img[^>]*>/g, t => {
  if (!/unsplash\.com|pexels\.com|pixabay\.com|FEATURED_IMAGE/.test(t) || ++k > 1) return t;
  t = t.replace(/src="[^"]*"/, 'src="' + hero.url + '"').replace(/alt="[^"]*"/, 'alt="' + hero.alt + '"');
  t = /class="/.test(t) ? t.replace(/class="([^"]*)"/, 'class="$1 wp-image-' + hero.id + '"') : t.replace('<img', '<img class="wp-image-' + hero.id + '"');
  return /fetchpriority=/.test(t) ? t.replace(/\sloading="lazy"/, '') : t.replace('<img', '<img fetchpriority="high"');
});
window._newContent = c;
const n = (s, re) => (s.match(re) || []).length, A = before, B = c;
const G = {evC: [n(A, /evidence-capture/g), n(B, /evidence-capture/g)], blocks: [n(A, /<!-- wp:/g), n(B, /<!-- wp:/g)],
  ezToc: [n(A, /ez-toc-/g), n(B, /ez-toc-/g)], toc: [n(A, /\[ez-toc\]/g), n(B, /\[ez-toc\]/g)], h1: [n(A, /<h1/g), n(B, /<h1/g)],
  h2: [n(A, /<h2/g), n(B, /<h2/g)], table: [n(A, /<table/g), n(B, /<table/g)], img: [n(A, /<img/g), n(B, /<img/g)],
  stock: [n(A, /unsplash\.com|FEATURED_IMAGE/g), n(B, /unsplash\.com|FEATURED_IMAGE/g)]};
const flags = {figPair: n(B, /<figure/g) === n(B, /<\/figure>/g), dupImg: (B.match(/src="[^"]*"/g) || []).length - new Set(B.match(/src="[^"]*"/g)).size,
  noAlt: n(B, /<img(?![^>]*alt=)/g), noWpCls: (B.match(/<img[^>]*>/g) || []).filter(x => /(0and1life|evidence)-/.test(x) && !/wp-image-\d+/.test(x)).length,
  heroLazy: (B.match(/<img[^>]*>/g) || []).filter(x => /fetchpriority="high"/.test(x) && /loading="lazy"/.test(x)).length,
  absCap: n(B, /<figcaption[^>]*position\s*:\s*absolute/g), fixed26: n(B, /font-size:26px/g), svgAdded: n(B, /<svg/g) - n(A, /<svg/g),
  video: n(B, /class="ol-(motion|video)"/g)};
const same = ['evC', 'blocks', 'toc', 'h1', 'h2', 'table'].every(x => G[x][0] === G[x][1]);
const ok = same && G.ezToc[1] === 0 && flags.figPair && !flags.dupImg && !flags.noAlt && !flags.noWpCls && !flags.heroLazy
  && !flags.absCap && !flags.fixed26 && flags.svgAdded === 0 && flags.video <= 1;
window._saveOk = ok;
(ok ? 'GUARD PASS' : 'GUARD FAIL') + ' skipped:' + (skipped.join(',') || 'none') + ' | '
  + Object.entries(G).map(([a, v]) => a + ' ' + v[0] + ' to ' + v[1]).join(' ; ') + ' | ' + Object.entries(flags).map(([a, v]) => a + ' ' + v).join(' ; ')
```

- `GUARD FAIL`이면 저장하지 않는다. 원인을 고쳐 다시 조립한다.
- 히어로 figure가 **제목 오버레이형(A형 · `figure > figcaption > h1`)**이면 그대로 둔다. 제목이 단색 박스에 따로 있는 B형이거나 `position:absolute` 캡션(C형)이면 → 부록 §7-2.6·§7-2.6b로 병합·정규화한 뒤 다시 검증한다.
- 헤더 메타 줄의 "읽는 데 약 N분"은 B·C형을 정규화할 때만 뺀다. A형 글에서는 보고만 한다.

**7-2. 저장 + 상태 보존 + 대표이미지 + 재확인 (한 호출)**

```javascript
if (!window._saveOk) throw new Error('guard fail');
const H = {'X-WP-Nonce': window._nonce, 'Content-Type': 'application/json'}, P = '/wp-json/wp/v2/posts/' + window._postId;   // 7-1에서 저장한 ID
const s = await fetch(P, {method: 'POST', headers: H, body: JSON.stringify({content: window._newContent, status: window._origStatus})}).then(r => r.json());
let out = 'save ' + s.status;
if (s.status !== window._origStatus) out += ' RESTORED ' + (await fetch(P, {method: 'POST', headers: H, body: JSON.stringify({status: window._origStatus})}).then(r => r.json())).status;
const fid = window._byTag['hero']?.id;
if (fid && window._curFeatured === 0) out += ' fm ' + (await fetch(P, {method: 'POST', headers: H, body: JSON.stringify({featured_media: fid, status: window._origStatus})}).then(r => r.json())).featured_media;
const chk = await fetch(P + '?context=edit&_fields=content,status,featured_media', {headers: {'X-WP-Nonce': window._nonce}}).then(r => r.json());
out + ' | recheck ' + chk.status + ' fm ' + chk.featured_media + ' sameLen ' + (chk.content.raw.length === window._newContent.length)
  + ' video ' + (chk.content.raw.match(/class="ol-(motion|video)"/g) || []).length + ' iframe ' + (chk.content.raw.match(/<iframe/g) || []).length
```

- 상태가 원래와 다르면 즉시 되돌리고(코드가 자동으로 함) 보고한다.
- 저장 뒤 `video`나 `iframe` 개수가 줄었으면 WP가 걸러낸 것이다. 모션이면 포스터 `<img>`로 바꾸고, 유튜브면 그 figure를 빼고 다시 저장한다. 그리고 🔴로 보고한다.
- 대표이미지가 이미 지정된 글은 덮어쓰지 않는다.

## STEP 7.5. 프리뷰 검증 (호출 3회 이내)

`https://0and1life.com/?p=POST_ID&preview=true`를 연다.

**① 기계 검증 + 모바일 실측 (한 호출)**

```javascript
const H = document.documentElement.scrollHeight, out = [];
for (const im of document.querySelectorAll('.entry-content img')) {
  if (im.loading === 'lazy') { im.scrollIntoView({block: 'center'}); await new Promise(r => setTimeout(r, 700)); }
  out.push(im.src.split('/').pop().split('?')[0].replace(/^(0and1life|evidence)-.*?-(hero|\d)/, '$1-$2').slice(0, 26) + ' nw' + im.naturalWidth
    + ' @' + Math.round((im.getBoundingClientRect().top + scrollY) / H * 100) + '% srcset ' + (im.srcset ? 'Y' : 'N') + ' cls ' + (/wp-image-\d+/.test(im.className) ? 'Y' : 'N') + ' ' + (im.getAttribute('loading') || 'eager'));
}
for (const f of document.querySelectorAll('.entry-content figure.ol-video iframe, .entry-content figure.ol-motion video'))
  out.push(f.tagName + ' @' + Math.round((f.getBoundingClientRect().top + scrollY) / H * 100) + '% w' + Math.round(f.getBoundingClientRect().width));
const fr = document.createElement('iframe'); fr.style.cssText = 'position:fixed;left:-4000px;top:0;width:375px;height:1000px;border:0';
fr.src = location.pathname + location.search + '&nc=' + Date.now(); document.body.appendChild(fr);
await new Promise(r => { fr.onload = r; setTimeout(r, 15000); }); await new Promise(r => setTimeout(r, 1500));
const fg = fr.contentDocument.querySelector('.entry-content figure'), cp = fg?.querySelector('figcaption');
const m375 = cp ? Math.round(cp.getBoundingClientRect().top - fg.getBoundingClientRect().top) : 'NO-HERO'; fr.remove();
scrollTo(0, 0);
out.join(' ; ') + ' || TOC ' + document.querySelectorAll('#ez-toc-container, .ez-toc-container').length + ' broken '
  + [...document.querySelectorAll('.entry-content img')].filter(i => i.complete && !i.naturalWidth).length
  + ' h1InFig ' + (document.querySelector('.entry-content figure h1') ? 'Y' : 'N') + ' mobileMargin ' + m375 + 'px'
  + ' svg ' + document.querySelectorAll('.entry-content svg').length
```

- 통과 조건: 생성·공식 이미지가 모두 `srcset Y · cls Y`, 히어로는 `eager`, 본문은 `lazy`, `TOC 1`, `broken 0`, `h1InFig Y`, `mobileMargin ≥ 0`(10 미만이면 320px로 한 번 더 잰다), 인접 이미지·영상 간격 5%pt 이상.
- 대표이미지 테마 블록(`.featured-image.page-header-image-single`)은 `display:none`이다. 히어로가 두 번 잡혀도 결함이 아니다.

**② 육안 확인 (스크린샷 2장, `scale 0.6`)**: 맨 위(히어로 + 제목)와 새 본문 이미지 위치. 워터마크 흔적·글과 맞지 않는 장면·가짜 화면 글자를 본다. 유튜브는 플레이어 썸네일이 보이면 통과다.

**③ 뒷정리**: 이 루틴이 연 탭(Flow 그리드·이미지·WP)을 닫고 프리뷰 탭 1개만 남긴다.

## STEP 8. 보고 · 알림

**보고는 아래 형식으로 25줄 안에 쓴다.** 해당 없는 줄은 뺀다.

```
대상: #ID 제목 (status 전→후) · 판정 ev/stk/deco/gen
건너뜀: #ID(사유) …
슬롯: hero=photo|official · 1=photo|official|still|motion|video …
  - 슬롯별 한 줄: 종류 · 미디어ID · 위치% · 근거 훅 문장 · (공식이면 출처 도메인·확인일·개인정보 없음 / 영상이면 채널·길이·업로드일 / 사진이면 "무슨 일이 벌어지는가" 한 문장)
공식 실물·영상: 찾음/없음 + 검색 호출 수
Flow: 모델 · 0크레딧 확인 · 채택 인덱스 · 원본 확대 검수 결과 · 재생성 여부
검증: GUARD PASS · srcset/cls · mobileMargin · broken 0
효율: 도구 호출 수 · CDP 타임아웃 수 · zoom 0
확인 필요: 삭제 대기 미디어 / Writer 쪽 문제 / 지침 개선안(조항 번호 + 붙여넣을 전문)
```

**알림(PushNotification)**: 이미지를 넣었거나, 사용자가 해야 할 일(세션 만료·저장 실패·삭제 확인·지침 개선)이 있을 때만 1회 보낸다. 대상 없음·전부 건너뜀이면 보내지 않는다. 첫 문장은 결과 한 줄로 쓴다.

## 마지막 STEP. 실행 기록 한 줄 (모든 경로에서 필수)

`{CR}\control_tower\runs\YYYY-MM.jsonl`에 한 줄 덧붙인다. 기존 줄은 고치지 않는다. 자격증명·URL 쿼리스트링은 넣지 않는다. `result`는 `성공`·`부분`·`건너뜀`·`실패` 중 하나다.

```bash
python3 - <<'PY'
import json, os, datetime
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
root = os.path.expanduser("~/mnt/Claude/control_tower/runs"); os.makedirs(root, exist_ok=True)
rec = {"routine": "4. 0and1life auto image insert", "file": "Schd_0and1Life-Image.md",
       "date": now.strftime("%Y-%m-%d"), "start": "{시작 HH:MM}", "end": now.strftime("%H:%M"),
       "result": "{성공|부분|건너뜀|실패}", "count": 0, "summary": "{60자 이내 한 줄}", "warnings": []}
with open(os.path.join(root, now.strftime("%Y-%m") + ".jsonl"), "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
PY
```
