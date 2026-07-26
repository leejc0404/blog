# KoreaPlug 자동 이미지 삽입 태스크 (v2 — 피사체 정확성 강화)

### 목적

Notion 글 현황 테이블에서 오늘 날짜에 작성된 WordPress 글을 찾아, 이미지가 3장 미만인 글에 Gemini로 생성한 이미지 3장을 WebP 형식으로 삽입한다. 기존에 무관한 스톡(Unsplash 등) 이미지가 들어가 있으면 함께 교체한다.

---

### STEP 1: Notion에서 오늘 날짜 글 찾기

Notion MCP를 사용해 https://app.notion.com/p/33cbfe4a2ae181b9a743cb7c194dea7f 페이지를 fetch한다.

오늘 날짜(YYYY-MM-DD 형식)와 일치하는 **'draft 일자'** 또는 **'작성일자'** 행을 찾는다.
해당 행에서 **글 제목(영문)**, **카테고리**, **한줄 요약**을 추출한다.

대상 글이 없으면 "오늘 날짜 글 없음"을 출력하고 종료.

---

### STEP 2: WordPress에서 해당 글 확인

Chrome MCP로 새 탭을 열고 `https://koreaplug.com/wp-admin/` 으로 이동한다 (로그인 상태 필수).

아래 JavaScript를 **WP admin 탭에서** 실행해 글을 검색한다. `status=any`가 반드시 필요하다 (draft 글은 기본 검색에서 제외됨).

```javascript
// WP admin 탭에서 실행 — wpApiSettings.nonce가 존재하는 컨텍스트여야 함
window._postData = null;
fetch('/wp-json/wp/v2/posts?search=TITLE_KEYWORD&per_page=5&status=any&_fields=id,title,status,content', {
  headers: {'X-WP-Nonce': wpApiSettings.nonce}
}).then(r => r.json())
  .then(d => { window._postData = d; });
// 2~3초 대기 후 window._postData 확인
```

일치하는 글의 **Post ID**, **이미지 수**, **기존 스톡 이미지 여부**를 확인한다:

```javascript
window._postData.map(p => ({
  id: p.id,
  title: p.title.rendered,
  status: p.status,
  imgCount: (p.content.rendered.match(/<img/g) || []).length,
  // 무관한 외부 스톡 이미지가 히어로로 들어가 있는 경우가 많음 — 교체 대상
  hasStockImg: /unsplash\.com|pexels\.com|pixabay\.com|FEATURED_IMAGE/.test(p.content.rendered)
}))
```

- **imgCount가 3장 이상이면 skip하고 종료** (단, `hasStockImg: true`면 본문 삽입은 건너뛰고 스톡 이미지 교체만 수행).
- `hasStockImg: true`면 **히어로 교체용 이미지 1장을 추가 생성**한다 (총 4장). 이 히어로 이미지는 STEP 7-4에서 기존 스톡 이미지의 src/alt를 교체하는 데 사용하고, 대표이미지로도 설정한다.

---

### STEP 3: 글 본문 분석 및 이미지 프롬프트 생성

#### 3-1. 본문을 먼저 읽는다 (필수)

제목·한줄 요약만으로 프롬프트를 만들면 글과 어긋난 이미지가 나온다. **반드시 본문 raw content를 가져와 읽고** 프롬프트를 만든다 (이 fetch 결과는 STEP 4에서 재사용):

```javascript
window._rawContent = null;
fetch('/wp-json/wp/v2/posts/POST_ID?status=any&_fields=content', {
  headers: {'X-WP-Nonce': wpApiSettings.nonce}
}).then(r => r.json())
  .then(d => { window._rawContent = d.content.raw || d.content.rendered; });
// 2~3초 대기 후 window._rawContent?.length 확인
```

본문에서 파악할 것:

- **핵심 피사체**: 글이 실제로 다루는 사물·기기·장소·음식이 무엇인가 (제목의 추상 키워드가 아니라 본문이 묘사하는 구체적 실물)
- 본문이 언급하는 **브랜드·형태·색·재질·사용 장면** (예: "black or silver rectangle with a numeric keypad", "Gateman, Samsung SDS" 같은 서술은 그대로 프롬프트 재료가 됨)
- 헤딩(h2/h3) 텍스트 — 각 이미지가 들어갈 위치 주변 섹션의 주제

#### 3-2. 피사체 정확성 원칙 (최우선 — 분위기보다 먼저)

> 프롬프트의 1순위는 '분위기'가 아니라 **'피사체 정확성'**이다. 핵심 피사체가 실물과 다르게 생성되면 아무리 분위기가 좋아도 그 이미지는 실패다.

1. **한국 고유 형태를 가진 피사체는 실제 형태를 물리적으로 상세 묘사한다.** 한국의 가전·기기·시설·음식·소품은 서구식 일반형과 형태가 다른 경우가 많다. "Korean digital door lock"처럼 이름만 쓰면 Gemini는 서구식 형태(둥근 도어노브 + 소형 사각 키패드)를 생성한다.
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

**이미지 3장의 역할 분담:**

- **이미지 1 (글 도입부)**: 글의 전체 분위기를 대표하는 와이드 장면 — 랜드마크, 전경, 공간감. **와이드 장면 안에도 핵심 피사체가 정확한 형태로 포함되어야 한다** (배경만 한국이고 피사체가 틀리면 실패).
- **이미지 2 (글 중반)**: 글의 핵심 소재를 클로즈업 — 음식 디테일, 문화 오브젝트, 체험 장면
- **이미지 3 (글 후반)**: 감성적 마무리 장면 — 저녁빛, 계절감, 여운이 있는 구도
- **(hasStockImg인 경우) 히어로 이미지**: 제목을 가장 직관적으로 시각화한 정면·와이드샷 — 썸네일로 봤을 때 글 주제가 한눈에 읽히는 구도

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

STEP 3-1에서 가져온 `window._rawContent`를 그대로 사용한다:

```javascript
const c = window._rawContent;
const headings = [];
const re = /<h[23][^>]*>/g;
let m;
while ((m = re.exec(c)) !== null) headings.push({index: m.index});
const n = headings.length;
window._insertPoints = [
  headings[Math.floor(n * 1/4)]?.index,
  headings[Math.floor(n * 2/4)]?.index,
  headings[Math.floor(n * 3/4)]?.index
];
window._insertPoints; // 확인
```

---

### STEP 5: Gemini에서 이미지 생성 및 캡처

Chrome MCP로 새 탭을 열고 `https://gemini.google.com` 으로 이동한다.

**이미지 생성 (프롬프트 1):**

1. 입력창 클릭 → 프롬프트 1 입력 → Enter
2. 대기 후 스크린샷으로 이미지 생성 완료 확인 (Chrome MCP의 wait는 1회 최대 10초 — 10초 대기 → 스크린샷 → 미완성이면 추가 대기 반복)

**생성 결과 검증 (필수 — 캡처 전에 스크린샷으로 확인):**

- 핵심 피사체가 **실제 한국 형태와 일치**하는가? (STEP 3-2에서 파악한 형태 기준)
- 글 제목을 아는 독자가 봤을 때 "글 내용과 맞는 이미지"라고 느낄 것인가?
- 이상한 요소(왜곡된 손, 어색한 텍스트, 서구식 형태)가 없는가?
- **어긋나면 동일 프롬프트 재시도 금지.** 무엇이 틀렸는지 파악해 잘못된 부분을 물리적으로 더 명시한 **수정 프롬프트**로 새 채팅에서 재생성한다 (예: 둥근 도어노브가 나왔다면 "absolutely no separate round doorknob, handle is integrated into the vertical lock panel" 추가). 수정 재시도 1회 후에도 어긋나면 해당 이미지 건너뜀.

**이미지 캡처:** async IIFE의 반환값은 Promise라 직접 결과를 받을 수 없으므로, 항상 fire-and-read 패턴을 사용한다 — 실행 후 2~3초 대기, 이후 `window._img1` 별도 호출로 확인.

```javascript
// 실행 → 2~3초 대기 → window._img1dims + ' / length: ' + window._img1?.length 으로 확인
(async () => {
  const imgs = Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 400);
  const img = imgs[imgs.length - 1];
  const cropRight = 40, cropBottom = 90;
  const canvas = document.createElement('canvas');
  canvas.width = img.naturalWidth - cropRight;
  canvas.height = img.naturalHeight - cropBottom;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height, 0, 0, canvas.width, canvas.height);
  // Gemini 워터마크(✦) 제거 — 우측 하단 55×55px를 바로 왼쪽 픽셀 색으로 덮음
  const pixel = ctx.getImageData(canvas.width - 70, canvas.height - 55, 1, 1).data;
  ctx.fillStyle = `rgb(${pixel[0]},${pixel[1]},${pixel[2]})`; ctx.fillRect(canvas.width - 55, canvas.height - 55, 55, 55);
  const webpBlob = await new Promise(r => canvas.toBlob(r, 'image/webp', 0.85));
  const dataUrl = await new Promise(r => { const rd = new FileReader(); rd.onloadend = () => r(rd.result); rd.readAsDataURL(webpBlob); });
  window._img1 = dataUrl;
  window._img1dims = canvas.width + 'x' + canvas.height;
})();
'fired'
```

**이미지 2, 3 (및 hasStockImg 시 히어로):** "새 채팅" 버튼 클릭 → 프롬프트 입력 → 동일하게 검증 → `window._img2`, `window._img3`, `window._imgHero`에 저장.

---

### STEP 6: Gemini 탭에서 WP admin 새 창 열기 → postMessage로 이미지 업로드

**핵심:** Gemini 탭에서 WP REST API를 직접 fetch하면 CORS로 차단된다. 기존 WP admin 탭에 대한 window 참조도 얻을 수 없다. 유일하게 작동하는 방법은 Gemini 탭에서 `window.open()`으로 새 WP admin 창을 열고 그 참조에 postMessage를 보내는 것이다.

**6-1. Gemini 탭에서 새 WP admin 창 열기:**

```javascript
// Gemini 탭에서 실행 — 새 tabId가 생성됨
window._wpWin = window.open('https://koreaplug.com/wp-admin/media-new.php', '_blank');
window._wpWin ? 'window opened' : 'blocked'
// 4초 대기 후 새 탭 tabId 확인 (tabs_context_mcp로 확인)
```

**6-2. 새 WP admin 탭에 postMessage 리스너 주입:**

새로 열린 WP admin 탭에서 실행:

```javascript
window._uploadedIds = [];
window.addEventListener('message', async (e) => {
  if (!e.data || !e.data.dataUrl) return;
  const {dataUrl, filename, altText} = e.data;
  const arr = dataUrl.split(','), mime = arr[0].match(/:(.*?);/)[1];
  const bstr = atob(arr[1]);
  const u8 = new Uint8Array(bstr.length);
  for (let i = 0; i < bstr.length; i++) u8[i] = bstr.charCodeAt(i);
  const fd = new FormData();
  fd.append('file', new Blob([u8], {type: mime}), filename);
  const res = await fetch('/wp-json/wp/v2/media', {
    method: 'POST',
    headers: {'X-WP-Nonce': wpApiSettings.nonce},
    body: fd
  });
  const json = await res.json();
  if (json.id) {
    await fetch('/wp-json/wp/v2/media/' + json.id, {
      method: 'POST',
      headers: {'X-WP-Nonce': wpApiSettings.nonce, 'Content-Type': 'application/json'},
      body: JSON.stringify({alt_text: altText})
    });
    window._uploadedIds.push({id: json.id, url: json.source_url, alt: altText, tag: filename});
    console.log('Uploaded: ' + json.id);
  }
});
'listener ready'
```

**6-3. Gemini 탭에서 이미지 순서대로 전송 (본문용 1→2→3, 히어로가 있으면 마지막):**

각 전송 후 6~8초 대기. 전송 사이에 WP admin 탭에서 `window._uploadedIds.length` 로 업로드 완료 확인 후 다음 전송.

```javascript
// Gemini 탭에서 순서대로 실행
window._wpWin.postMessage({dataUrl: window._img1, filename: 'koreaplug-SLUG-1.webp', altText: 'ALT_TEXT_1'}, 'https://koreaplug.com');
// 6~8초 대기
window._wpWin.postMessage({dataUrl: window._img2, filename: 'koreaplug-SLUG-2.webp', altText: 'ALT_TEXT_2'}, 'https://koreaplug.com');
// 6~8초 대기
window._wpWin.postMessage({dataUrl: window._img3, filename: 'koreaplug-SLUG-3.webp', altText: 'ALT_TEXT_3'}, 'https://koreaplug.com');
// (hasStockImg인 경우)
window._wpWin.postMessage({dataUrl: window._imgHero, filename: 'koreaplug-SLUG-hero.webp', altText: 'ALT_TEXT_HERO'}, 'https://koreaplug.com');
// 6~8초 대기 후 window._uploadedIds.length가 전송한 수와 같은지 확인
```

---

### STEP 7: 글에 이미지 삽입·교체 및 저장

WP admin 탭(6-2에서 연 탭)에서 `/wp-admin/post.php?post=POST_ID&action=edit` 로 이동한다.

로드 완료 후 REST API로 content를 수정하고 저장한다:

```javascript
// 1) 최신 content 가져오기
window._finalContent = null;
fetch('/wp-json/wp/v2/posts/POST_ID?status=any&_fields=content', {
  headers: {'X-WP-Nonce': wpApiSettings.nonce}
}).then(r => r.json())
  .then(d => { window._finalContent = d.content.raw || d.content.rendered; });
// 3~4초 대기 후 window._finalContent?.length 확인
```

```javascript
// 2) 역순으로 이미지 삽입 (뒤→앞 순서로 삽입해야 인덱스가 밀리지 않음)
const uploads = window._uploadedIds; // [{id, url, alt}, ...] — 앞 3개가 본문용
const pts = window._insertPoints;    // [pos1, pos2, pos3]
let c = window._finalContent;

for (let i = 2; i >= 0; i--) {
  const {id, url, alt} = uploads[i];
  const imgBlock = `\n<figure style="margin:20px 0">\n  <img style="width:100%;display:block;height:auto;border-radius:8px;" src="${url}" alt="${alt}" />\n</figure>\n`;
  c = c.slice(0, pts[i]) + imgBlock + c.slice(pts[i]);
}
window._newContent = c;
'new content len: ' + c.length
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
      let t = tag.replace(/src="[^"]*"/, `src="${hero.url}"`);
      t = t.match(/alt="[^"]*"/) ? t.replace(/alt="[^"]*"/, `alt="${hero.alt}"`)
                                 : t.replace('<img', `<img alt="${hero.alt}"`);
      return t;
    }
    return tag;
  });
  window._heroReplaced = replaced; // 확인용
}
```

```javascript
// 3) content 저장 (featured_media는 별도 단계에서 처리)
window._saveResult = null;
fetch('/wp-json/wp/v2/posts/POST_ID', {
  method: 'POST',
  headers: {'X-WP-Nonce': wpApiSettings.nonce, 'Content-Type': 'application/json'},
  body: JSON.stringify({content: window._newContent})
}).then(r => r.json())
  .then(d => { window._saveResult = {id: d.id, status: d.status, imgCount: (d.content?.rendered?.match(/<img/g)||[]).length}; });
// 6초 대기 후 window._saveResult 확인 — imgCount가 (기존+3)이면 성공
```

```javascript
// 4) 대표이미지(featured image) 설정 — 실패해도 전체 태스크는 중단하지 않음
// hasStockImg로 히어로를 생성했으면 히어로를, 아니면 STEP 3의 window._featuredImgIndex 사용
window._featuredResult = 'skipped';
const heroUp = window._uploadedIds.find(u => u.tag && u.tag.includes('hero'));
const featuredId = heroUp ? heroUp.id : window._uploadedIds[window._featuredImgIndex ?? 0]?.id;
if (featuredId) {
  fetch('/wp-json/wp/v2/posts/POST_ID', {
    method: 'POST',
    headers: {'X-WP-Nonce': wpApiSettings.nonce, 'Content-Type': 'application/json'},
    body: JSON.stringify({featured_media: featuredId})
  }).then(r => r.json())
    .then(d => {
      if (d.featured_media === featuredId) {
        window._featuredResult = 'ok: mediaId=' + featuredId;
      } else {
        window._featuredResult = 'failed: ' + JSON.stringify(d).substring(0, 100);
      }
    })
    .catch(err => { window._featuredResult = 'error: ' + err.message; });
} else {
  window._featuredResult = 'skipped: uploadedIds not ready';
}
// 4초 대기 후 window._featuredResult 확인
// 'ok' 이외의 결과는 STEP 8 보고에 기록하고 계속 진행
```

---

### STEP 7.5: 최종 육안 검증 (필수)

저장 후 편집 화면을 새로고침하고 **스크롤하며 삽입된 이미지 전부를 스크린샷으로 확인**한다:

- 각 이미지의 피사체가 글 내용·주변 섹션과 맞는가?
- 히어로/대표이미지가 정상 반영됐는가?
- 어긋난 이미지가 발견되면 해당 이미지만 STEP 5부터 재생성해 교체하고, 불가하면 STEP 8 보고에 명시한다.

---

### STEP 8: 완료 보고

완료 후 아래 내용을 출력:

- 처리한 글 제목 및 Post ID
- 삽입·교체된 이미지 URL (본문 3장 + 히어로 교체 여부)
- 최종 imgCount
- 대표이미지: 선정된 이미지, 선정 이유, 설정 결과 (`window._featuredResult`)
- 피사체 정확성 검증: 각 이미지별 통과/재시도/건너뜀 여부
- Skip된 경우 그 이유

---

### 중요 주의사항

- Chrome이 열려 있고, koreaplug.com WP admin에 로그인되어 있어야 함
- gemini.google.com에 로그인되어 있어야 함
- REST API 검색 시 `status=any` 파라미터 필수 (없으면 draft 글이 검색되지 않음)
- async JavaScript 결과는 항상 window 변수에 저장 후 별도 호출로 읽는다 (fire-and-read 패턴)
- Chrome MCP의 wait는 1회 최대 10초, scroll_amount는 최대 10 — 긴 대기는 나눠서 반복
- Gemini 이미지 캡처 시 `naturalWidth > 400` 필터로 생성된 이미지만 선택
- **이미지 생성 실패·부정확 시 재시도는 반드시 '수정된 프롬프트'로** (동일 프롬프트 재시도 금지, 새 채팅에서). 수정 재시도 1회 후에도 부정확하면 해당 이미지 건너뜀
- **프롬프트 작성 전 본문을 반드시 읽고, 피사체 형태가 불확실하면 웹 검색으로 확인**
- 글 제목(title)은 수정하지 않음
- 이미지 삽입 후 글 상태(publish/draft)는 변경하지 않음
