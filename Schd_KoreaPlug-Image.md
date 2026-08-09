# KoreaPlug 자동 이미지 삽입 태스크 (v3.3 — 레거시 증빙 인식·미분류 skip 금지·탭 그룹 등록 수정)

### 목적

Notion 글 현황 테이블에서 오늘 날짜에 작성된 WordPress 글을 찾아, **데코(생성) 이미지가 3장 미만인 글**에 Gemini로 생성한 이미지를 WebP 형식으로 삽입한다 — 단, **증빙+데코 합계가 5장을 넘지 않는 범위**에서만 (생성 수를 3→2→1장으로 자동 감축). 기존에 무관한 스톡(Unsplash 등) 이미지가 들어가 있으면 함께 교체한다.

> ⚠️ v3 변경 (2026-08-01): Draft 루틴이 발행 관문용 **증빙 캡처**(`figure class="evidence-capture"`, 파일명 `evidence-*`)를 본문에 넣기 시작하면서, 총 이미지 수 기준(舊 imgCount ≥ 3 → skip)으로는 모든 글이 스킵되어 이 루틴이 돌지 않았다. 판정은 **데코 개수**로 하되, 글이 이미지로 과밀해지지 않도록 **총량 상한 5장**(증빙+데코, 히어로 교체는 총량 불변이라 제외)을 함께 둔다. 증빙 캡처는 어떤 단계에서도 교체·이동·삭제하지 않는다.

> ⚠️ v3.2 변경 (2026-08-04): 舊 정규식 분류기는 **v1.28 이전에 작성된 레거시 글의 증빙 캡처를 인식하지 못했다.** Draft 루틴이 `evidence-` 파일명·`evidence-capture` 클래스를 붙이기 시작한 것은 v1.28(2026-08-02)부터라, 그 이전 글의 증빙은 마커가 없어 **데코로 오분류**된다. 0and1Life에서 먼저 실측된 사례: #70 결혼식 보증인원(Post 894)은 공공 출처(price.go.kr) 조회 캡처 2장이 데코로 잡혀 deco=4 → genCount 0 → skip. 이미지가 필요한 글인데 루틴이 3일 내내 그냥 지나쳤다. KoreaPlug도 v1.28 이전 글은 동일한 구멍이 있으므로 같은 수정을 적용한다. STEP 2를 **DOM 기반 8단계 우선순위 분류기**로 교체하고, **미분류(unknown)가 있으면 skip 금지** 가드를 신설한다.

> ⚠️ v3.3 변경 (2026-08-08): STEP 6-1의 `window.open(url, '_blank')` 로 연 WP admin 탭이 **Chrome MCP 탭 그룹 밖에 생성돼** `tabs_context_mcp` 목록에 나타나지 않았고, 그 결과 6-2의 postMessage 리스너를 주입할 수 없어 업로드 경로 전체가 막혔다 (2026-08-08 #129 실측). 두 번째 인자 `'_blank'` 를 **제거**하면 탭이 그룹에 정상 등록된다. 이미 `'_blank'` 로 열어버린 경우의 복구 절차도 6-1에 명시한다.

---

### STEP 1: Notion에서 오늘 날짜 글 찾기

Notion MCP를 사용해 https://app.notion.com/p/33cbfe4a2ae181b9a743cb7c194dea7f 페이지를 fetch한다.

⚠️ **WP 세션 만료 대응 (2026-08-03 신설)** — 이 루틴은 `wpApiSettings.nonce`(wp-admin 로그인 세션)에 전적으로 의존한다. `wp-admin/` 접근 시 `wp-login.php?...&reauth=1` 로 리다이렉트되면 세션이 만료된 것이다.
- ⛔ 루틴은 **로그인 폼을 대신 제출하지 않는다** (자격증명 입력·인증 폼 제출은 AI 금지 동작). 자동완성이 채워져 있어도 클릭 금지.
- 오류 로그에 "WP 세션 만료 — 사용자 직접 로그인 필요"를 기록하고 종료한다. 이미지 삽입은 수행하지 않으며, 대상 글의 상태는 건드리지 않는다.
- 사용자 조치 안내: "Chrome에서 https://koreaplug.com/wp-admin 에 직접 로그인하고 '기억하기'를 체크해 주세요."
- 다음 실행이 (v3.1의 2일 소급 규정에 따라) 어제 글까지 다시 훑으므로, 세션만 복구되면 누락분은 자동으로 따라잡는다.

(v3.1) **오늘 또는 어제 날짜**(YYYY-MM-DD)와 일치하는 **'draft 일자'** 또는 **'작성일자'** 행을 모두 찾는다. — 2일 소급 이유: 배포 루틴이 인증 문제 등으로 늦게 재실행되면 이 루틴이 도는 시점엔 글이 아직 WP에 없어 영영 누락된다 (2026-08-02 #122 실제 사례). 어제 글까지 봐야 다음 실행이 따라잡는다.
해당 행에서 **글 제목(영문)**, **카테고리**, **한줄 요약**을 추출한다.
대상이 여러 건이면 **오래된 날짜부터** 각각 STEP 2 판정을 거쳐, genCount>0 이거나 스톡 교체가 필요한 글만 순서대로 처리한다 (이미 충족된 글은 skip — 중복 삽입 방지는 STEP 2 판정이 보장).

오늘·어제 모두 대상 글이 없으면 "최근 2일 글 없음"을 출력하고 종료.

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

일치하는 글의 **Post ID**와 **이미지 3종 분류(증빙/스톡/데코)**를 확인한다.

(v3.2) 분류는 정규식을 본문 전체에 훑는 방식이 아니라, **이미지 하나씩 DOM으로 열어 8단계 우선순위**로 판정한다. 판정 근거(`why`)를 이미지별로 남겨 오분류를 사후 추적할 수 있게 한다.

```javascript
window._cls = window._postData.map(p => {
  const html = p.content.raw || p.content.rendered;
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
    const base = src.split('/').pop() || '';
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
    detail.push(base.slice(0, 52) + ' => ' + k + ' [' + why + ']');
  }

  const genCount = deco >= 3 ? 0 : Math.max(0, Math.min(3 - deco, 5 - evidence - deco)); // 총량 상한 5장
  return {id: p.id, title: p.title.rendered, status: p.status,
          evidence, stock, deco, genCount, hasStockImg: stock > 0, unknown, detail};
});
window._cls
```

⚠️ (v3.3 / 2026-08-08 실측) `javascript_tool` 의 반환 문자열에 이미지 URL·쿼리스트링이 그대로 섞이면 **`[BLOCKED: Cookie/query string data]`** 로 출력 전체가 막힌다. 결과를 읽을 때는 한 번에 전부 찍지 말고 ⓐ 집계값만(`ev/st/deco/gen/unk`) 먼저, ⓑ `detail` 은 글 단위로 나눠서, ⓒ 파일명에서 `?&=` 를 치환하거나 공통 prefix를 축약해 출력한다.

우선순위를 이 순서로 고정한 이유: 표준 마커(①②)가 있으면 그것이 가장 확실한 근거이므로 먼저 본다. 스톡(③)은 호스트로 확정된다. 이 루틴이 직접 만든 이미지(④)는 파일명 prefix로 확실히 데코이므로, 레거시 추정 규칙(⑤⑥⑦)이 이를 잘못 증빙으로 끌고 가지 않도록 **레거시 규칙보다 먼저** 판정한다. ⑤⑥⑦은 마커가 없는 옛 글에만 적용되는 폴백이다.

⛔ **(v3.2 신설) `unknown`이 비어 있지 않으면 genCount 값과 무관하게 즉시 skip하지 않는다.** `unknown`에 잡힌 이미지는 자동 판정이 실패한 것이다. 본문에서 해당 `<figure>`를 직접 열어 figcaption에 출처 기관·`Captured YYYY-MM-DD`가 있는지, 화면 캡처처럼 보이는지 눈으로 확인한 뒤 증빙/데코를 손으로 확정하고 **genCount를 다시 계산한 다음** 진행 여부를 정한다. 확인 결과는 STEP 8 보고에 이미지별로 남긴다.

> 이 가드가 필요한 이유 (2026-08-04 실측): 0and1Life #70(Post 894)은 증빙 2장이 데코로 오분류돼 genCount 0으로 계산됐고, 그 자리에서 종료되는 바람에 "애매하면 사람이 확인한다"는 아래 단계까지 **도달조차 하지 못했다.** 자동 분류가 틀렸다고 말할 기회 없이 skip된 것이 문제의 핵심이었다.

- **genCount가 0이면 본문 삽입을 skip하고 종료** (단, `hasStockImg: true`면 스톡 이미지 교체만 수행 — 교체는 총량을 늘리지 않으므로 상한과 무관). `unknown`이 있으면 위 가드를 먼저 수행한 뒤 판단한다.
- genCount가 1~2장이면 그 수만큼만 생성·삽입한다. 우선순위: **이미지 1(도입 훅) → 이미지 3(결론 시각화) → 이미지 2(중반 클로즈업)** — 증빙 캡처가 이미 있는 글에서는 중반 클로즈업의 역할을 증빙이 대신한다.
- **증빙 캡처는 절대 건드리지 않는다**: 교체·이동·삭제 금지, 삽입 위치가 증빙 figure 내부에 떨어지면 직전 헤딩 바로 앞으로 옮긴다.
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

**(v3.3 보강) 화면·디스플레이가 피사체인 글**: 한국 방송의 가림 처리는 서구식 가우시안 블러가 아니라 **각진 픽셀 블록(모자이크)**이다. `soft grey pixelated mosaic patch`, `the individual mosaic squares clearly larger and coarser than the surrounding picture detail` 처럼 **블록 형태와 거칠기를 명시**해야 의도한 결과가 나온다. 화면 안 장면까지 지정할 때는 `no readable text` 를 반드시 붙인다 (화면 속 자막·UI 텍스트가 깨진 글자로 생성됨).

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

**프롬프트 예시 (v3.3 신설 — 두 상태 비교형 히어로):**

글의 핵심이 'A일 때와 B일 때가 다르다'인 경우, 히어로는 **두 상태를 한 프레임에 나란히** 넣으면 썸네일만으로 주제가 읽힌다.

```
A clean straight-on wide photograph of two screens side by side on a light oak table in a bright modern Korean living room. On the left, a flat-screen television shows a Korean drama scene in which one object is covered by a grey pixelated mosaic patch. On the right, a tablet propped on a stand shows the exact same scene completely sharp and clear with no mosaic at all. Identical framing and identical colours on both screens so the single difference is obvious at a glance, soft diffused daylight from a large window, shot on Canon EOS R5 with 50mm f/1.2 lens, symmetrical eye-level composition, crisp screen glass and matte table textures, no people in the room, no readable text, no watermark, no logos, no anime style, no 3d render
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

⚠️ (v3.3 / 2026-08-08 실측) **FAQ 섹션이 h3로 여러 개 붙어 있는 글에서는 위 `h[23]` 계산이 이미지 3장을 전부 글 끝 FAQ 구간에 몰아넣는다.** (#129: h2 6개 + FAQ h3 5개 → 2/4·3/4 지점이 둘 다 FAQ 안으로 떨어짐.) 헤딩 목록을 뽑은 뒤 **h2와 h3의 개수·위치를 먼저 눈으로 확인하고**, h3가 문서 후반에 몰려 있으면 **h2만으로 분위를 계산한다**:

```javascript
const c = window._rawContent;
const h2 = []; const re2 = /<h2[^>]*>/g; let m2;
while ((m2 = re2.exec(c)) !== null) h2.push(m2.index);
const n = h2.length;
window._insertPoints = [h2[Math.floor(n*1/4)], h2[Math.floor(n*2/4)], h2[Math.floor(n*3/4)]];
window._insertPoints;
```

(v3) `genCount`가 3 미만이면 `window._insertPoints`에서 앞의 genCount개 위치만 사용한다 — 우선순위는 STEP 2의 이미지 1→3→2 순서를 따른다 (2장이면 1/4·3/4 지점, 1장이면 1/4 지점).

(v3.2) 다만 **이미 이미지가 있는 글에 1~2장을 보충하는 경우**에는 기계적으로 1/4 지점을 쓰지 말고, 기존 이미지들의 본문 내 위치(index)를 먼저 구해 **이미지가 가장 오래 비어 있는 구간**의 헤딩을 고른다. 보충의 목적은 개수 채우기가 아니라 공백 메우기다.

---

### STEP 5: Gemini에서 이미지 생성 및 캡처

Chrome MCP로 새 탭을 열고 `https://gemini.google.com` 으로 이동한다.

**이미지 생성 (프롬프트 1):**

1. 입력창 클릭 → 프롬프트 1 입력 → Enter
2. 대기 후 스크린샷으로 이미지 생성 완료 확인 (Chrome MCP의 wait는 1회 최대 10초 — 10초 대기 → 스크린샷 → 미완성이면 추가 대기 반복)

⚠️ 입력 후 화면이 초기 상태로 돌아가 있으면 전송이 안 된 것이다. 스크린샷으로 입력창에 프롬프트가 남아 있는지 확인하고, 남아 있으면 전송 버튼을 직접 클릭한다.

⚠️ (v3.3 / 2026-08-08 실측) **긴 프롬프트에서는 Enter 키가 거의 전송되지 않는다.** 처음부터 Enter를 생략하고 **전송 버튼(입력창 우측 원형 ↑, 대략 x=1048 / y=입력창 하단줄)을 클릭**하는 편이 빠르다. 타이핑 직후 곧바로 클릭하면 씹히는 경우가 있으므로 **타이핑 → 2~3초 대기 → 클릭 → 스크린샷으로 전송 여부 확인**의 순서를 지킨다. 스크린샷에 프롬프트가 그대로 남아 있으면 클릭을 1회 더 한다.

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

⚠️ 워터마크 덮개 색은 바로 왼쪽 1픽셀에서 뽑는다. 밝고 균일하지 않은 배경에서는 덮개 사각형이 눈에 띌 수 있다 — STEP 7.5 육안 검증에서 확인하고, 눈에 띄면 STEP 8 보고에 명시한다.

**이미지 2, 3 (및 hasStockImg 시 히어로):** "새 채팅" 버튼 클릭 → 프롬프트 입력 → 동일하게 검증 → `window._img2`, `window._img3`, `window._imgHero`에 저장.

⚠️ (v3.3) "새 채팅"은 사이드바 버튼 클릭(SPA 전환)으로만 한다. **주소창 navigate로 새 채팅을 열면 탭이 리로드되어 앞서 저장한 `window._img1` 등이 전부 날아간다.** 새 채팅 전환 후 `window._img1 ? 'yes' : 'NO'` 로 보존 여부를 한 번 확인하면 안전하다.

---

### STEP 6: Gemini 탭에서 WP admin 새 창 열기 → postMessage로 이미지 업로드

**핵심:** Gemini 탭에서 WP REST API를 직접 fetch하면 CORS로 차단된다. 기존 WP admin 탭에 대한 window 참조도 얻을 수 없다. 유일하게 작동하는 방법은 Gemini 탭에서 `window.open()`으로 새 WP admin 창을 열고 그 참조에 postMessage를 보내는 것이다.

**6-1. Gemini 탭에서 새 WP admin 창 열기:**

⛔ **(v3.3 / 2026-08-08 실측) 두 번째 인자 `'_blank'` 를 넘기지 않는다.** `'_blank'` 로 열린 탭은 Chrome MCP 탭 그룹 **밖에** 생성되어 `tabs_context_mcp` 목록에 나타나지 않고, 그 결과 6-2의 리스너 주입(`javascript_tool`)이 불가능해져 업로드 경로 전체가 막힌다. 인자 없이 `window.open(url)` 로 호출하면 그룹에 정상 등록된다.

```javascript
// Gemini 탭에서 실행 — 새 tabId가 생성됨
// ⚠️ '_blank' 를 넘기지 말 것 — 그룹 밖에 열려 리스너 주입 불가
window._wpWin = window.open('https://koreaplug.com/wp-admin/media-new.php');
window._wpWin ? 'window opened' : 'blocked'
// 6~8초 대기 후 새 탭 tabId 확인 (tabs_context_mcp로 확인)
```

**복구 절차** — 이미 `'_blank'` 로 열어 탭이 목록에 없다면, Gemini 탭에서 아래를 실행해 닫고 위 코드로 다시 연다. `window._img*` 는 Gemini 탭 heap에 그대로 남아 있으므로 **이미지 재생성은 필요 없다.**

```javascript
window._wpWin.close();
window._wpWin = window.open('https://koreaplug.com/wp-admin/media-new.php');
'reopened:' + !!window._wpWin
```

**6-2. 새 WP admin 탭에 postMessage 리스너 주입:**

⚠️ (2026-08-04 실측) `media-new.php` 에는 **`wpApiSettings` 가 정의되어 있지 않다.** 리스너를 붙이기 전에 REST nonce를 먼저 확보해 `window._nonce` 에 담고, 리스너 안에서는 `wpApiSettings.nonce` 대신 `window._nonce` 를 쓴다:

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

⚠️ 생성 이미지 파일명은 반드시 `koreaplug-` prefix를 유지한다 — STEP 2 분류기 ④단계가 이 prefix로 데코를 확정하므로, 규칙을 어기면 다음 실행에서 그 이미지가 미분류(unknown)로 떨어진다.

---

### STEP 7: 글에 이미지 삽입·교체 및 저장

WP admin 탭(6-2에서 연 탭)에서 `/wp-admin/post.php?post=POST_ID&action=edit` 로 이동한다.

로드 완료 후 REST API로 content를 수정하고 저장한다:

```javascript
// 1) 최신 content 가져오기
window._finalContent = null;
fetch('/wp-json/wp/v2/posts/POST_ID?status=any&_fields=content,featured_media', {
  headers: {'X-WP-Nonce': window._nonce}
}).then(r => r.json())
  .then(d => { window._finalContent = d.content.raw || d.content.rendered; window._curFeatured = d.featured_media; });
// 3~4초 대기 후 window._finalContent?.length 확인
```

⚠️ 삽입 위치(`window._insertPoints`)는 **이 시점의 `window._finalContent` 기준으로 다시 계산한다.** STEP 4에서 구한 인덱스는 그 사이 본문이 바뀌면 어긋난다. (계산식은 STEP 4의 h2 전용 버전을 그대로 쓴다.)

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
// 2.9) 저장 전 증빙 불가침 검증 (v3.2 — 필수)
// evidence-capture 클래스 수와 증빙 파일명·공공 출처 흔적이 모두 그대로 남아 있어야 한다
const before = window._finalContent, after = window._newContent;
const cnt = (s, re) => (s.match(re) || []).length;
window._evGuard = {
  evClass: cnt(before, /evidence-capture/g) + '->' + cnt(after, /evidence-capture/g),
  evName:  cnt(before, /\/evidence-/g)      + '->' + cnt(after, /\/evidence-/g),
  pubSrc:  cnt(before, /go[-_.]kr/g)        + '->' + cnt(after, /go[-_.]kr/g),
  imgTags: cnt(before, /<img/g)             + '->' + cnt(after, /<img/g)   // (v3.3) 증감 확인용
};
window._evGuard // 앞 세 항목은 좌우 값이 같아야 저장 진행
```

```javascript
// 3) content 저장 (featured_media는 별도 단계에서 처리)
window._saveResult = null;
fetch('/wp-json/wp/v2/posts/POST_ID', {
  method: 'POST',
  headers: {'X-WP-Nonce': window._nonce, 'Content-Type': 'application/json'},
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
    headers: {'X-WP-Nonce': window._nonce, 'Content-Type': 'application/json'},
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

⚠️ 이미 대표이미지가 지정된 글(`featured_media !== 0`)에 본문 이미지만 보충하는 경우에는 **대표이미지를 덮어쓰지 않는다.** (7-1에서 확보한 `window._curFeatured` 로 판정한다.)

---

### STEP 7.5: 최종 육안 검증 (필수)

저장 후 **프론트엔드 프리뷰**(`https://koreaplug.com/?p=POST_ID&preview=true`)를 열고 **스크롤하며 삽입된 이미지 전부를 스크린샷으로 확인**한다. (v3.3: 편집 화면보다 프리뷰가 실제 렌더 결과·이미지 배치 확인에 정확하다.)

- 각 이미지의 피사체가 글 내용·주변 섹션과 맞는가?
- 이미지 3장이 **본문 전체에 고르게 퍼져 있는가?** (FAQ 구간에 몰려 있으면 STEP 4 h2 전용 계산으로 다시 삽입)
- 히어로/대표이미지가 정상 반영됐는가?
- 증빙 캡처가 원래 자리에 그대로 있는가? (`window._evGuard` 세 항목 좌우 일치 확인)
- 워터마크 덮개 사각형이 눈에 띄지 않는가?
- 표·TOC·내부링크 등 기존 요소가 삽입으로 깨지지 않았는가?
- 어긋난 이미지가 발견되면 해당 이미지만 STEP 5부터 재생성해 교체하고, 불가하면 STEP 8 보고에 명시한다.

**뒷정리 (v3.3 신설):** 검증이 끝나면 이 루틴이 만든 탭(Gemini 탭, media-new 탭)을 `tabs_close_mcp` 로 닫는다. 사용자가 결과를 바로 볼 수 있도록 **프리뷰 탭 1개만 남긴다.**

---

### STEP 8: 완료 보고

완료 후 아래 내용을 출력:

- 처리한 글 제목 및 Post ID
- **STEP 2 분류 결과 표**: 이미지별 `파일명 => 증빙/스톡/데코 [판정근거]`, 그리고 evidence/stock/deco/genCount
- `unknown`이 있었다면 수동 확인 결과와 재계산된 genCount
- 삽입·교체된 이미지 URL (본문 3장 + 히어로 교체 여부)
- 최종 imgCount, 증빙 불가침 검증(`window._evGuard`) 결과
- 대표이미지: 선정된 이미지, 선정 이유, 설정 결과 (`window._featuredResult`)
- 피사체 정확성 검증: 각 이미지별 통과/재시도/건너뜀 여부
- Skip된 경우 그 이유
- (v3.3) 루틴 자체의 오류·개선점이 발견됐다면 **수정할 조항 번호와 교체용 전문(前文)**을 함께 제시한다 — 사용자가 붙여넣기만 하면 되도록.

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
- 이미지 삽입 후 글 상태(publish/draft/future)는 변경하지 않음 — **발행·예약발행 전환은 어떤 경우에도 금지 (발행 결정은 항상 사용자 몫, 2026-08-01 사용자 지시)**
- (v3) **증빙 캡처 불가침**: 삽입·스톡 교체 어느 단계에서도 증빙 figure의 마크업·src·alt·figcaption을 수정하지 않는다. 저장 전 STEP 7-2.9의 `window._evGuard` 로 확인한다
- (v3.2) **증빙 판정은 `evidence-capture` 클래스·`evidence-` 파일명만으로 하지 않는다.** v1.28(2026-08-02) 이전 글에는 이 마커가 없다. figcaption의 `Captured YYYY-MM-DD`, 공공 출처 도메인 파일명(`*-go-kr`, `korea-kr`, `kosis`, `hometax`, `work24`), alt의 조회·확인·캡처 단서까지 폴백으로 본다
- (v3.3) **`window.open` 에 `'_blank'` 금지** — 탭이 Chrome MCP 그룹 밖에 열려 리스너 주입이 불가능해진다 (STEP 6-1)
- (v3.3) **Gemini 새 채팅은 사이드바 버튼 클릭으로만** — 주소창 navigate는 탭을 리로드해 `window._img*` 를 날린다
- (v3.3) **javascript_tool 반환값에 이미지 URL·쿼리스트링을 그대로 담지 않는다** — `[BLOCKED: Cookie/query string data]` 로 출력 전체가 막힌다. 집계값 먼저, 파일명은 축약·치환해서 출력
- (v3.3) **삽입 위치는 h2 기준으로 계산** — FAQ h3가 많은 글에서 `h[23]` 분위는 이미지를 글 끝에 몰아넣는다 (STEP 4)
