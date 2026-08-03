# 0and1Life 자동 이미지 삽입 태스크 (v3.1 — 증빙 구분·총량 상한·2일 소급)

### 목적

Notion 글 현황 테이블에서 오늘 날짜에 draft된 WordPress 글을 찾아, **데코(생성) 이미지가 3장 미만인 글**에 Gemini로 생성한 이미지를 WebP 형식으로 삽입한다 — 단, **증빙+데코 합계가 5장을 넘지 않는 범위**에서만 (생성 수를 3→2→1장으로 자동 감축). 기존에 무관한 스톡(Unsplash 등) 이미지가 들어가 있으면 함께 교체한다.

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

(v3.1) **오늘 또는 어제 날짜**(YYYY-MM-DD)와 일치하는 **"Draft일"** 행을 모두 찾는다. — 2일 소급 이유: 배포 루틴이 인증 문제 등으로 늦게 재실행되면 이 루틴이 도는 시점엔 글이 아직 WP에 없어 영영 누락된다 (2026-08-02 #122 실제 사례). 어제 글까지 봐야 다음 실행이 따라잡는다.
해당 행에서 **글 제목(한국어)**, **서브카테고리**, **한줄 요약**을 추출한다.
대상이 여러 건이면 **오래된 날짜부터** 각각 STEP 2 판정을 거쳐, genCount>0 이거나 스톡 교체가 필요한 글만 순서대로 처리한다 (이미 충족된 글은 skip — 중복 삽입 방지는 STEP 2 판정이 보장).

오늘·어제 모두 대상 글이 없으면 "최근 2일 draft 글 없음"을 출력하고 종료.

---

### STEP 2: WordPress에서 해당 글 확인

Chrome MCP로 새 탭을 열고 `https://0and1life.com/wp-admin/` 으로 이동한다 (로그인 상태 필수).

아래 JavaScript를 **WP admin 탭에서** 실행해 글을 검색한다:

```javascript
window._postData = null;
fetch('/wp-json/wp/v2/posts?search=TITLE_KEYWORD&per_page=5&status=any&_fields=id,title,status,content', {
  headers: {'X-WP-Nonce': wpApiSettings.nonce}
}).then(r => r.json())
  .then(d => { window._postData = d; });
// 2~3초 대기 후 window._postData 확인
```

일치하는 글의 **Post ID**와 **이미지 3종 분류(증빙/스톡/데코)**를 확인한다 (v3):

```javascript
window._postData.map(p => {
  const html = p.content.rendered;
  const imgTags = html.match(/<img[^>]*>/g) || [];
  const evRe = /\/evidence-|evidence-capture/i;                      // 증빙 마커: 파일명·클래스
  const evLegacyRe = /alt="[^"]*(캡처|캡쳐|스크린샷|Captured|Screenshot)[^"]*"/i; // 마커 없는 기존 글 폴백
  const stockRe = /unsplash\.com|pexels\.com|pixabay\.com|FEATURED_IMAGE/;
  let evidence = 0, stock = 0, deco = 0;
  for (const t of imgTags) {
    if (evRe.test(t) || evLegacyRe.test(t)) evidence++;
    else if (stockRe.test(t)) stock++;
    else deco++;
  }
  // img 태그에 마커가 없어도 감싼 figure에 evidence-capture 클래스가 있으면 증빙으로 재분류
  const figEv = (html.match(/<figure[^>]*class="[^"]*evidence-capture[^"]*"[\s\S]{0,800}?<img/gi) || []).length;
  const move = Math.max(0, figEv - evidence);
  evidence += move; deco = Math.max(0, deco - move);
  const genCount = deco >= 3 ? 0 : Math.max(0, Math.min(3 - deco, 5 - evidence - deco)); // 총량 상한 5장
  return {id: p.id, title: p.title.rendered, status: p.status,
          evidence, stock, deco, genCount, hasStockImg: stock > 0};
})
```

분류가 애매한 자체 업로드 이미지(마커·alt 단서가 모두 없는 경우)는 본문에서 해당 `<figure>`를 직접 열어 figcaption에 출처 기관·`Captured YYYY-MM-DD`가 있는지 확인한다 — 있으면 증빙, 없으면 데코.

- **genCount가 0이면 본문 삽입을 skip하고 종료** (단, `hasStockImg: true`면 스톡 이미지 교체만 수행 — 교체는 총량을 늘리지 않으므로 상한과 무관).
- genCount가 1~2장이면 그 수만큼만 생성·삽입한다. 우선순위: **이미지 1(도입 훅) → 이미지 3(결론 시각화) → 이미지 2(중반 클로즈업)** — 증빙 캡처가 이미 있는 글에서는 중반 클로즈업의 역할을 증빙이 대신한다.
- **증빙 캡처는 절대 건드리지 않는다**: 교체·이동·삭제 금지, 삽입 위치가 증빙 figure 내부에 떨어지면 직전 헤딩 바로 앞으로 옮긴다.
- `hasStockImg: true`면 **히어로 교체용 이미지 1장을 추가 생성**한다 (총 4장). 이 히어로 이미지는 STEP 7-2.5에서 기존 스톡 이미지의 src/alt를 교체하는 데 사용하고, 대표이미지로도 설정한다.

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

- **핵심 피사체**: 글이 실제로 다루는 도구·앱·기기·장면이 무엇인가 (제목의 추상 키워드가 아니라 본문이 묘사하는 구체적 실물). 예: 글이 ChatGPT 화면 활용법을 다루면 이미지도 노트북 위 대화형 AI 화면이어야지, 막연한 '미래적 AI 그래픽'이면 안 된다.
- 본문이 언급하는 **구체적 도구·화면·환경·상황** (앱 이름, 작업 환경, 시간대, 감정선) — 그대로 프롬프트 재료가 됨
- 헤딩(h2/h3) 텍스트 — 각 이미지가 들어갈 위치 주변 섹션의 주제

#### 3-2. 피사체 정확성 원칙 (최우선 — 분위기보다 먼저)

> 프롬프트의 1순위는 '분위기'가 아니라 **'피사체 정확성'**이다. 핵심 피사체가 글 내용과 다르게 생성되면 아무리 분위기가 좋아도 그 이미지는 실패다.

1. **한국의 실제 환경·사물을 물리적으로 상세 묘사한다.** "Korean office"라고만 쓰면 Gemini는 서구식 사무실을 생성하기 쉽다. 한국 직장·주거·카페의 실제 디테일(파티션 책상, 스터디카페 좌석, 아파트 거실, 이케아식 홈오피스, 스타벅스 리저브 등)을 명시한다.
2. **기기·도구는 실물 형태로 묘사한다.** 예: 갤럭시/아이폰, 맥북/그램, 듀얼 모니터, 기계식 키보드 등 본문이 언급한 실제 기기를 그대로 쓴다. AI 관련 글이라도 추상적 홀로그램·로봇 그래픽이 아니라 **실제 화면·실제 작업 장면**으로 표현한다.
3. **형태를 정확히 모르면 웹 검색으로 실제 사진을 확인한 뒤** 프롬프트를 작성한다. 추측으로 쓰지 않는다.
4. **잘못 나오기 쉬운 형태를 명시적으로 배제한다.** 예: "no futuristic hologram, no robot, no sci-fi interface", "no Western-style cubicle office".

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

**이미지 3장의 역할 분담:**

이미지 1 (도입부): 글 주제를 한눈에 읽히게 하는 시각적 훅 — 썸네일로 봤을 때 "뭐지?" 하고 클릭하고 싶어지는 구도. 은유·대비·의외성 중 하나를 반드시 포함
이미지 2 (중반): 핵심 소재의 클로즈업 (유지하되, 화면·기기 반복 금지 — 글마다 다른 각도·재질·구도)
이미지 3 (후반): 글의 결론·효용을 시각화 — '만족한 사람' 공식 금지. 결과물·변화·before/after를 사물로 표현

3장의 다양성 규칙 (필수): 3장이 같은 스타일·같은 구도·같은 피사체 유형이면 실패. 최소 1장은 인물 없는 정물/은유 컷, 3장의 카메라 거리(원경/중경/접사)를 서로 다르게 한다

- **(hasStockImg인 경우) 히어로 이미지**: 제목을 가장 직관적으로 시각화한 장면 — 썸네일로 봤을 때 글 주제가 한눈에 읽히는 구도

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
window._insertPoints;
```

(v3) `genCount`가 3 미만이면 `window._insertPoints`에서 앞의 genCount개 위치만 사용한다 — 우선순위는 STEP 2의 이미지 1→3→2 순서를 따른다 (2장이면 1/4·3/4 지점, 1장이면 1/4 지점).

---

### STEP 5: Gemini에서 이미지 생성 및 캡처

Chrome MCP로 새 탭을 열고 `https://gemini.google.com` 으로 이동한다.

**이미지 생성**: 입력창 클릭 → 프롬프트 입력 → Enter → 대기 후 스크린샷으로 완료 확인 (Chrome MCP의 wait는 1회 최대 10초 — 10초 대기 → 스크린샷 → 미완성이면 추가 대기 반복)

**생성 결과 검증 (필수 — 캡처 전에 스크린샷으로 확인):**

- 핵심 피사체가 **글 내용·실제 한국 환경과 일치**하는가? (STEP 3-2 기준)
- 글 제목을 아는 독자가 봤을 때 "글 내용과 맞는 이미지"라고 느낄 것인가?
- 이상한 요소(왜곡된 손, 어색한 텍스트, SF풍 그래픽, 서구식 환경)가 없는가?
- **어긋나면 동일 프롬프트 재시도 금지.** 무엇이 틀렸는지 파악해 잘못된 부분을 물리적으로 더 명시한 **수정 프롬프트**로 새 채팅에서 재생성한다. 수정 재시도 1회 후에도 어긋나면 해당 이미지 건너뜀.

**이미지 캡처** (fire-and-read 패턴):

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

**이미지 2, 3 (및 hasStockImg 시 히어로)**: "새 채팅" 버튼 클릭 → 프롬프트 입력 → 동일하게 검증 → `window._img2`, `window._img3`, `window._imgHero`에 저장.

---

### STEP 6: Gemini 탭에서 WP admin 새 창 열기 → postMessage로 이미지 업로드

**핵심**: Gemini 탭에서 `window.open()`으로 새 WP admin 창을 열고 그 참조에 postMessage를 보낸다.

**6-1. Gemini 탭에서 새 WP admin 창 열기:**

```javascript
window._wpWin = window.open('https://0and1life.com/wp-admin/media-new.php', '_blank');
window._wpWin ? 'window opened' : 'blocked'
// 4초 대기 후 새 탭 tabId 확인
```

**6-2. 새 WP admin 탭에 postMessage 리스너 주입:**

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

```javascript
// 각 전송 후 6~8초 대기. 전송 사이 WP admin 탭에서 window._uploadedIds.length 확인.
window._wpWin.postMessage({dataUrl: window._img1, filename: '0and1life-SLUG-1.webp', altText: 'ALT_TEXT_1'}, 'https://0and1life.com');
// 6~8초 대기
window._wpWin.postMessage({dataUrl: window._img2, filename: '0and1life-SLUG-2.webp', altText: 'ALT_TEXT_2'}, 'https://0and1life.com');
// 6~8초 대기
window._wpWin.postMessage({dataUrl: window._img3, filename: '0and1life-SLUG-3.webp', altText: 'ALT_TEXT_3'}, 'https://0and1life.com');
// (hasStockImg인 경우)
window._wpWin.postMessage({dataUrl: window._imgHero, filename: '0and1life-SLUG-hero.webp', altText: 'ALT_TEXT_HERO'}, 'https://0and1life.com');
// 6~8초 대기 후 window._uploadedIds.length가 전송한 수와 같은지 확인
```

---

### STEP 7: 글에 이미지 삽입·교체 및 저장

WP admin 탭에서 `/wp-admin/post.php?post=POST_ID&action=edit` 로 이동.

```javascript
// 1) 최신 content 가져오기
window._finalContent = null;
fetch('/wp-json/wp/v2/posts/POST_ID?status=any&_fields=content', {
  headers: {'X-WP-Nonce': wpApiSettings.nonce}
}).then(r => r.json())
  .then(d => { window._finalContent = d.content.raw || d.content.rendered; });
// 3~4초 대기
```

```javascript
// 2) 역순으로 이미지 삽입 (뒤→앞 순서로 삽입해야 인덱스가 밀리지 않음)
const uploads = window._uploadedIds; // 앞 3개가 본문용
const pts = window._insertPoints;
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
// 3) content 저장
window._saveResult = null;
fetch('/wp-json/wp/v2/posts/POST_ID', {
  method: 'POST',
  headers: {'X-WP-Nonce': wpApiSettings.nonce, 'Content-Type': 'application/json'},
  body: JSON.stringify({content: window._newContent})
}).then(r => r.json())
  .then(d => { window._saveResult = {id: d.id, status: d.status, imgCount: (d.content?.rendered?.match(/<img/g)||[]).length}; });
// 6초 대기 후 window._saveResult 확인
```

```javascript
// 4) 대표이미지(featured image) 설정
// hasStockImg로 히어로를 생성했으면 히어로를, 아니면 window._featuredImgIndex 사용
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
      window._featuredResult = d.featured_media === featuredId ? 'ok: mediaId=' + featuredId : 'failed';
    }).catch(err => { window._featuredResult = 'error: ' + err.message; });
}
// 4초 대기 후 window._featuredResult 확인
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
- 대표이미지: 선정된 이미지, 선정 이유, 설정 결과
- 피사체 정확성 검증: 각 이미지별 통과/재시도/건너뜀 여부
- Skip된 경우 그 이유

---

### 중요 주의사항

- Chrome이 열려 있고, 0and1life.com WP admin에 로그인되어 있어야 함
- gemini.google.com에 로그인되어 있어야 함
- REST API 검색 시 `status=any` 파라미터 필수
- async JavaScript 결과는 항상 window 변수에 저장 후 별도 호출로 읽는다 (fire-and-read 패턴)
- Chrome MCP의 wait는 1회 최대 10초, scroll_amount는 최대 10 — 긴 대기는 나눠서 반복
- Gemini 이미지 캡처 시 `naturalWidth > 400` 필터로 생성된 이미지만 선택
- **이미지 생성 실패·부정확 시 재시도는 반드시 '수정된 프롬프트'로** (동일 프롬프트 재시도 금지, 새 채팅에서). 수정 재시도 1회 후에도 부정확하면 해당 이미지 건너뜀
- **프롬프트 작성 전 본문을 반드시 읽고, 피사체 형태가 불확실하면 웹 검색으로 확인**
- 이미지 삽입 후 글 상태(publish/draft)는 변경하지 않음 — **발행·예약발행 전환은 어떤 경우에도 금지 (발행 결정은 항상 사용자 몫, 2026-08-01 사용자 지시)**
- (v3) **증빙 캡처(`evidence-capture` figure) 불가침**: 삽입·스톡 교체 어느 단계에서도 증빙 figure의 마크업·src·alt·figcaption을 수정하지 않는다. 저장 전 `window._newContent`의 `evidence-capture` 등장 횟수가 원본과 동일한지 확인한다
- 글 제목(title)은 수정하지 않음
