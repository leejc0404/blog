# KoreaPlug 자동 이미지 삽입 태스크 (v8.0)

> 버전 요약: **v8.0 (2026-11-28)** 실행본/참고본 분리(1,889줄 → 약 560줄) · STEP 1을 WP REST 우선으로(Notion 41만 자 조회 제거) · 사실감 강화(A 슬롯을 제품·음식까지 확대, Openverse 추가, Flow 결함 검수 7항목) · Flow 모델 목록 갱신(Pro / 2 Lite / 2.1)
> 이전 규칙의 근거·사고 기록·예시 프롬프트·舊 방식은 **`Schd_KoreaPlug-Image_ref.md`(v7.3 원문)** 에 있다. 매 실행마다 읽지 않는다. 본문에 `→ ref` 표시가 있는 곳만, 막혔을 때 `grep -n` 으로 그 절만 찾아 읽는다.

> 🖥️ **실행 환경 공통** — 이 블록이 아래 경로·셸 전제보다 우선한다.
> - **연결 폴더 루트 `CR`** = `get_device_info.connectedFolders` 첫 항목. `{CR}`·`$HOME/mnt/Claude` 는 같은 폴더다. 사용자 이름(`win`/`USER`)을 경로에 박아 쓰지 않는다.
> - **셸 모드**: `mcp__remote-devices__device_bash` 가 있으면 PC 셸에서 그대로. **브리지 모드**(없으면): 읽기 = `device_stage_files`, 쓰기 = 클라우드에서 만들어 `device_commit_files`(`expectedMtimeMs`). 종료하지 않는다.
> - 자격증명 값은 출력하지 않는다. 삭제는 문서가 허용한 것만, 브리지 모드에서는 보고에만 남긴다.

---

## 0. 목적과 고정 규칙

**목적**: 최근 2일(KST 오늘·어제)에 생긴 KoreaPlug 글 중 **데코 이미지가 3장 미만인 글**에 이미지를 넣는다. 증빙+데코 합계 5장 이하(3→2→1장 자동 감축). 스톡(Unsplash 등)이 있으면 히어로로 교체한다.

**사실감 원칙 (v8.0)** — 독자가 "실제로 누가 가서 찍은 것"으로 믿는 순서대로 조달한다.

| 슬롯 | 이 자리에서 독자가 봐야 하는 것 | 1순위 | 2순위 |
|---|---|---|---|
| **A 실물** | 특정 장소·시설·**제품·음식·탈것**의 실제 모습 | 무료 라이선스 실사진 (§3-5) | Flow (B 문법) |
| **B 순간** | 사람이 거기서 무엇을 하는가 | Flow 기록 사진 (§3-3) | — |
| **C 설명** | 언제·얼마·어떤 순서·어디로 | Claude 모션 그래픽 (§3-6) | 정지 그래픽 |

- **제품·브랜드 음식이 피사체면 A가 의무다.** Flow는 그 제품을 본 적이 없어 그럴듯한 가짜를 만든다 (2026-11-28 #215: 스초생 실물 사진 채택 — 생성으로는 불가능했던 컷).
- 히어로·대표이미지는 A 또는 B만. **Flow(B)는 글당 최대 2장**(히어로 포함). C는 글당 1장 기본, 최대 2장.
- **기본 배치**: 히어로 B · 슬롯1 B · 슬롯2 A · 슬롯3 C. A를 못 찾으면 슬롯2를 C(두 번째 모션) 또는 생략.

**절대선 (어떤 경우에도)**
- 💸 비용 0원. 크레딧 차감 서비스·유료 스톡·유료 MCP(Higgsfield 등) 금지.
- 🔒 글 상태 불변: 모든 저장 POST에 `status: _origStatus` 동봉, 바뀌면 즉시 되돌리고 보고. 발행·예약 전환 금지. 제목 수정 금지.
- 🧾 본문 읽기는 `context=edit` + `content.raw` 만. `rendered` 폴백 금지.
- 🧷 증빙(`evidence-*`, `figure.evidence-capture`)은 이동·수정·삭제 금지.
- 🗑 미디어·Flow 항목 삭제 금지 → 보고에 「삭제 대기」로만. Flow에서 「휴지통으로 이동됨」 토스트를 보면 **무엇보다 먼저 「실행취소」**.
- 🔑 로그인: 계정 선택 화면의 `leejc0404@gmail.com` 클릭과 기존 범위 OAuth 「계속」만 허용(2026-08-26 사전 승인). 비밀번호·2단계 코드·다른 계정·신규 권한은 즉시 중단.

**토큰·호출 예산 (v8.0)** — 목표 **글 1편 25회 안팎**

1. 이 문서는 `sed -n '1,300p'` · `'301,$p'` **2회**로 읽는다. 참고본은 필요할 때만 grep.
2. `javascript_tool` 출력은 **약 1,000자에서 잘린다.** 반환은 집계·짧은 문자열만. 긴 본문은 `window._txt` 에 담고 `slice(0,950)` · `slice(950,1900)` … 을 **한 `browser_batch`에 6개까지** 묶어 읽는다.
3. 반환 문자열에 **URL 쿼리스트링·`?&=`** 가 섞이면 `[BLOCKED]` 로 전체가 막힌다. 파일명만 자르고 `[?&=]` 를 지운다.
4. fetch+검증, 삽입+가드, 저장+대표이미지는 **각각 1회 호출**로 합친다(아래 스니펫이 이미 합쳐져 있다).
5. 스크린샷은 판정이 필요할 때만. Flow 탭은 `scale`·`zoom` 금지(뷰포트 고착 → ref §5-3). 미리보기·위키 확인 탭은 `scale 0.5` 허용.
6. 클라우드 Bash는 `upload.wikimedia.org`·`thumb.wikimedia.org` 에 접속하지 못한다(2026-11-28 실측). 이미지 확인은 **브라우저 임시 탭**에서 한다.

---

## STEP 0. 세션 점검 (1~2회 호출 · 실패하면 1분 안에 끝낸다)

1. `tabs_context_mcp{createIfEmpty:true}` → 탭이 1개면 `tabs_create_mcp`. 두 tabId를 **WP / FLOW** 로 정한다.
2. 아래 배치 1회:
```
browser_batch([
  {navigate: 'https://koreaplug.com/wp-admin/media-new.php', tabId: WP},
  {navigate: 'https://labs.google/fx/ko/tools/flow/project/6a6af995-4d64-4bbb-8e97-4be7aa267e6d', tabId: FLOW},
  {computer: wait 10}, {computer: wait 5},
  {computer: screenshot, tabId: FLOW}          ← scale 없이
])
```
   - Flow URL은 `flow.google.com/project/…` 로 리다이렉트된다(정상). 상단 「가장 오래된 제작물이 곧 만료됩니다」 배너는 무시한다(「선택」 누르지 않음).
3. WP 판정 + **STEP 1 후보 조회를 같은 호출로** 한다 (STEP 1 스니펫 그대로 실행). `nonce:MISSING` 이거나 `wp-login.php` 로 갔으면 WP 만료.
4. Flow 판정: 그리드와 하단 입력바가 보이면 정상. `accountchooser` 면 `leejc0404@gmail.com` 클릭 → OAuth 「계속」 → 복귀 확인. 비밀번호 화면이면 중단.
5. 하나라도 만료면 **즉시 STEP 8-A 보고 후 종료**(연 탭은 닫는다). 다음 실행의 2일 소급이 누락분을 따라잡는다.

---

## STEP 1. 대상 글 찾기 — WP REST 우선 (v8.0)

> Notion 글 현황 페이지는 41만 자(2026-11-28 실측)라 조회만으로 토큰을 크게 쓴다. 대상 판정은 WP가 더 정확하다(본문 이미지를 직접 센다).

WP 탭에서 1회 (STEP 0-3 겸용):

```javascript
const s = Array.from(document.querySelectorAll('script:not([src])')).map(x => x.textContent).join('\n');
const m = s.match(/apiFetch\.createNonceMiddleware\(\s*["']([a-f0-9]+)["']/);
window._nonce = m ? m[1] : (window.wpApiSettings ? wpApiSettings.nonce : null);
const kst = new Date(Date.now() + 9*3600e3); kst.setUTCHours(0,0,0,0);
const since = new Date(kst.getTime() - 24*3600e3).toISOString().slice(0,19);   // KST 어제 00:00 (사이트 시간대 KST 기준 벽시계 값)
const H = {headers: {'X-WP-Nonce': window._nonce}};
const a = await fetch('/wp-json/wp/v2/posts?status=any&per_page=20&after=' + since + '&_fields=id,status,date,slug', H).then(r => r.json());
const b = await fetch('/wp-json/wp/v2/posts?status=draft,pending&per_page=20&orderby=modified&_fields=id,status,date,modified,slug', H).then(r => r.json());
const seen = {}; window._cand = [...a, ...b.filter(p => p.modified >= since)].filter(p => !seen[p.id] && (seen[p.id] = 1));
'url:' + location.pathname + ' nonce:' + (window._nonce ? 'ok' : 'MISSING') + ' since:' + since + '\n'
 + window._cand.map(p => p.id + ' ' + p.status + ' ' + p.date + ' ' + p.slug.slice(0, 50)).join('\n')
```

- `after` 는 글 날짜 기준이라 **오늘·어제 작성된 draft, 오늘·어제 발행분, 이후로 예약된 future 글**이 모두 잡힌다. 이미 처리된 글은 STEP 2에서 `gen:0` 으로 걸러진다.
- **후보 0건이면** 그때만 Notion으로 확인한다: `notion-fetch` 결과 파일에서 `.{0,90}Draft 배포 실행: YYYY-MM-DD.{0,90}`(오늘·어제)를 python으로 찾아 그 블록 2,500자만 읽는다. 배포 로그에 신규 draft가 있는데 WP에 없으면 **미배포 → 8-A 보고 후 종료**. 로그도 없으면 「최근 2일 글 없음」으로 종료.
- 여러 건이면 **오래된 날짜부터** 처리한다(§7.9).

---

## STEP 2. 분류 + 본문 건강검진 + h2 위치 (1회 호출)

```javascript
const ids = window._cand.map(p => 'include[]=' + p.id).join('&');
window._postData = await fetch('/wp-json/wp/v2/posts?' + ids + '&status=any&per_page=20&context=edit&_fields=id,title,status,content,date,featured_media,slug', {headers: {'X-WP-Nonce': window._nonce}}).then(r => r.json());
const RE = {evC: /evidence-capture/i, evN: /^evidence-/i, stock: /unsplash\.com|pexels\.com|pixabay\.com|FEATURED_IMAGE/i, gen: /^(koreaplug|0and1life)-/i,
  cap: /Captured\s*\d{4}\s*[-.\/]\s*\d{1,2}\s*[-.\/]\s*\d{1,2}/i, pub: /(go[-_.]kr|korea[-_.]kr|kosis|hometax|work24)/i,
  alt: /(캡처|캡쳐|스크린샷|Captured|Screenshot|조회한|조회 결과|확인한|고지서|명세서|모의계산)/i};
window._cls = window._postData.map(p => {
  const c = p.content.raw; if (typeof c !== 'string') return {id: p.id, err: 'RAW-MISSING'};
  const d = document.createElement('div'); d.innerHTML = c;
  let ev = 0, st = 0, de = 0; const det = [], unk = [];
  for (const img of d.querySelectorAll('img')) {
    const src = img.getAttribute('src') || '', base = (src.split('/').pop() || '').split('?')[0], fig = img.closest('figure');
    const cl = fig ? fig.className : '', cap = fig && fig.querySelector('figcaption') ? fig.querySelector('figcaption').textContent : '';
    let k, w;
    if (RE.evC.test(cl)) [k, w] = ['ev', 'class']; else if (RE.evN.test(base)) [k, w] = ['ev', 'name'];
    else if (RE.stock.test(src)) [k, w] = ['stock', 'stock']; else if (RE.gen.test(base)) [k, w] = ['deco', 'gen'];
    else if (RE.cap.test(cap)) [k, w] = ['ev', 'cap']; else if (RE.pub.test(base)) [k, w] = ['ev', 'pub'];
    else if (RE.alt.test(img.alt)) [k, w] = ['ev', 'alt']; else { [k, w] = ['deco', 'UNKNOWN']; unk.push(base); }
    k === 'ev' ? ev++ : k === 'stock' ? st++ : de++;
    det.push(base.slice(0, 40).replace(/[?&=]/g, '_') + '=' + k + '[' + w + ']');
  }
  de += d.querySelectorAll('video').length;
  const gen = de >= 3 ? 0 : Math.max(0, Math.min(3 - de, 5 - ev - de)), L = c.length;
  const h2 = [...c.matchAll(/<h2[^>]*>([\s\S]*?)<\/h2>/g)].map(x => ({i: x.index, t: x[1].replace(/<[^>]*>/g, '').replace(/[?&=]/g, ' ').slice(0, 40)}));
  const figs = [...c.matchAll(/<figure[\s\S]*?<\/figure>/g)].map(x => Math.round(x.index / L * 100) + '-' + Math.round((x.index + x[0].length) / L * 100));
  return {id: p.id, status: p.status, date: p.date, fm: p.featured_media, slug: p.slug, title: p.title.raw, ev, st, de, gen, unk, det, h2, figs,
    health: 'len' + L + ' blocks' + (c.match(/<!-- wp:/g) || []).length + ' ezToc' + (c.match(/ez-toc/g) || []).length};
});
window._cls.map(c => c.err ? c.id + ' ' + c.err : c.id + ' ' + c.status + ' fm' + c.fm + ' ev' + c.ev + ' st' + c.st + ' de' + c.de + ' gen' + c.gen + ' unk' + c.unk.length + ' ' + c.health
  + (c.gen || c.st ? '\n  ' + c.det.join(' | ') + '\n  h2: ' + c.h2.map(h => Math.round(h.i / c.health.match(/\d+/)[0] * 100) + '% ' + h.t).join(' / ') + '\n  figs: ' + c.figs.join(',') : '')).join('\n')
```

**판정**
- `RAW-MISSING` → 중단(nonce·`context=edit` 문제). rendered 폴백 금지.
- `gen:0` 이고 `st:0` → skip. `gen:0` 이고 `st>0` → 히어로 교체만.
- `unk` 가 있으면 자동 skip 금지 — 그 figure의 캡션·alt를 보고 증빙/데코를 손으로 정한 뒤 gen 재계산, 보고에 남긴다.
- **`ezToc>0` 이면 오염본** → 리비전에서 `ezToc 0` 인 최신본을 찾아 그것을 기준으로 한다(→ ref §3-1 「오염 복구」). `blocks0` 자체는 KoreaPlug Writer가 클래식 HTML로 쓰므로 **정상**이다(2026-11-28 #215 확인: 리비전 모두 blocks 0~1).
- genCount 1~2장이면 우선순위 **슬롯1(도입) → 슬롯3(후반) → 슬롯2(중반)**.

---

## STEP 3. 본문 읽기 → 슬롯 설계

### 3-1. 본문 읽기 (1회 batch)

```javascript
// 1번째 호출 — 나머지는 slice 범위만 바꿔 같은 batch에 이어 붙인다
const p = window._postData.find(x => x.id === POST_ID); window._rawContent = p.content.raw;
const d = document.createElement('div'); d.innerHTML = window._rawContent;
window._txt = d.textContent.replace(/https?:\/\/\S+/g, ' ').replace(/[?&=]/g, '').replace(/\s*\n\s*/g, '\n');
window._txt.length + ' ' + window._txt.slice(0, 950)
```
→ `window._txt.slice(950,1900)` … 을 같은 `browser_batch` 에 6개까지. 대개 1~2배치로 끝난다.

본문에서 뽑을 것: ① **핵심 피사체**(실제 제품명·장소명·한글 표기) ② 외국인이 가장 놀랄 **훅 문장**(슬롯마다 다른 문장) ③ **수치·날짜·요금**(C 슬롯 재료, 본문 그대로) ④ 각 h2 주제.

### 3-2. 슬롯 판정과 삽입 위치 (같은 사고 안에서 끝낸다)

- 위치는 **h2 시작 위치(문자 기준)** 에서 고른다. 목표: 히어로 있는 글 `[0.20, 0.40, 0.60]` 근처, 없는 글 `[0.10, 0.45, 0.72]` 근처. **비율보다 섹션 주제 일치가 우선**(±10%p 허용). FAQ·결론 h2 앞은 피한다. 증빙 figure 구간과 5%p 안쪽으로 붙지 않게 한다.
- 슬롯마다 기록: `window._slotPlan = {hero:'B', 1:'B', 2:'A', 3:'C'}` · 훅 문장 · 피사체.
- 파일명: Flow `koreaplug-{slug}-{n}.webp` · 실사진 `koreaplug-photo-{slug}-{n}.webp` · 모션 `koreaplug-motion-{slug}-{n}.mp4` + `-{n}-poster.webp` (`n` = 1·2·3·hero).

### 3-3. Flow(B) 프롬프트 — 사실감 규칙 (v8.0 통합판)

한 프롬프트 = 아래 6블록을 순서대로 이은 영어 한 단락(1,200~1,700자). 예시 전문은 → ref §3-3 「프롬프트 예시 (v7.1)」.

1. **장소·시각**: 실제 도시·장소 + 밝은 낮(`on a bright, sunny December afternoon`). 야간·흐림은 글 주제가 그 시간대일 때만, 4장 중 최대 1장.
2. **사건 1개**: 훅 문장을 동작으로 — 건네는 순간, 카드를 대는 순간, 가리키며 웃는 순간. "…가 놓여 있다"로 끝나면 버린다. 긴장 동사(막 ~하는, 김이 오르는, 기울어진) 1개 이상.
3. **사람**: 중간 거리 ¾ 측면, 웃거나 대화, `not looking at the camera`. 외국인 방문객 1명(`a foreign visitor`, 국적·인종 묘사 없음). 몸통이 보이는 인물에 `X only` 금지 → `face simply turned away` 형식(→ ref §3-3 ③).
4. **한국 지표 2개 이상(물리 묘사)**: 버스전용차선(파란 도색)·초록 시내버스 / 층층 간판(평평한 색면) / 동 번호 큰 고층 아파트 / 스테인리스 수저·반찬 / 플라스틱 스툴 / 분홍 임산부석 / 단청·기와 / 은행잎. 실재 장소면 **혼동 후보를 정하고 그곳에만 있는 지리 요소**를 넣는다(설악=원경의 동해와 속초; → ref §3-2B ⑤). 국가·지명을 부정문에 쓰지 않는다.
5. **초점 1곳 + 생활 흔적 1개 (v8.0)**: `X is the sharpest thing in the frame, slightly off-centre` + 실제 현장에만 있는 자국 1개 — 유리의 손자국·김 서림, 구겨진 영수증, 가격 스티커, 테이프 붙은 안내문, 바닥의 물기, 약간 비뚤어진 크림 장식. AI 이미지의 '너무 깨끗함'을 깨는 가장 싼 방법이다.
6. **촬영·제외 문장 (그대로 붙인다)**:
```
Bright, airy and inviting mood, gentle natural daylight, fresh true-to-life colours, cheerful everyday atmosphere, casual snapshot taken by a visitor on a recent smartphone, eye-level handheld framing with a very slightly tilted horizon, most of the scene in focus, everyday clutter partly cut off at the edges of the frame, plain unbranded clothing, aprons and packaging with no lettering, any signs and banners small and out of focus, background people naturally out of focus but not smudged or blurred out, every person a distinct individual, complete natural human anatomy with no missing or cropped body parts, no headless figures, no floating clothing, no readable paragraphs, no UI text, no logos, no watermark, no 3d render, no illustration, no cinematic colour grading, no HDR look, no studio lighting, no moody dark tones, no posed model looking at camera, no stock photo look
```
   - 굵게 표시할 v8.0 추가분: `plain unbranded … no lettering` · `signs and banners small and out of focus` · `not smudged or blurred out` · `every person a distinct individual` — 2026-11-28 실측 결함(앞치마의 가짜 브랜드 글자, 초점 안 가짜 한글 현수막, 뭉개진 행인 얼굴) 대응.
   - 금지어: `cinematic`·`hyperrealistic`·`8k`·`masterpiece`·`dramatic/studio lighting`·카메라·렌즈 브랜드·`the only bright accent`. 얕은 심도는 음식·손 접사에서만.

**전송 전 자가 점검 5문항** (하나라도 아니면 고쳐 쓴다)
① 한 문장으로 "무슨 일이 벌어지는가"가 말해지는가 ② 한국 지표를 지우면 다른 나라 사진이 되지 않는가 ③ 다른 나라 여행 기사에 넣으면 어색한가(장소 오인) ④ 여행자가 폰으로 찍었다고 믿겠는가 ⑤ 저기 가서 저렇게 해 보고 싶어지는가.

alt 텍스트(영문 60~100자)도 함께 만든다. 대표이미지는 히어로(없으면 슬롯1).

---

### 3-5. 무료 실사진 — A 슬롯 (v8.0 확대)

**① 허용 라이선스 (사진 개별 페이지에서 확인한 것만)**

| 출처 | 허용 | 금지 |
|---|---|---|
| Wikimedia Commons | CC0 · Public domain · CC BY · CC BY-SA (지역판 `2.0 kr` 포함) | NC · ND · Fair use · 미표기 |
| Openverse (Flickr 등) | `license_type=commercial,modification` 결과 중 CC0·PDM·BY·BY-SA | NC·ND, 출처 페이지에서 라이선스가 바뀐 것 |
| 공공누리 | **제1유형** | 제2~4유형 |
| 그 외 | — | 구글 이미지·블로그·SNS·워터마크·유료 스톡·Unsplash |

**② 검색 — 한 번의 호출에 검색어 3~5개 (영문 장소·제품명 + 한글명 + 브랜드 한글명)**

```javascript
// WP 탭. 검색어는 본문에서 뽑는다 — 예: ['Strawberry Choco Saengcream','투썸플레이스 케이크','strawberry cake Korea']
const Q = ['QUERY1', 'QUERY2', 'QUERY3']; window._wm = []; const out = [];
for (const q of Q) {
  const api = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&generator=search&gsrnamespace=6&gsrlimit=25&gsrsearch='
    + encodeURIComponent(q) + '&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1600';
  const d = await fetch(api).then(r => r.json());
  Object.values((d.query || {}).pages || {}).forEach(p => {
    const ii = p.imageinfo[0], m = ii.extmetadata || {}, v = k => ((m[k] || {}).value || '').replace(/<[^>]*>/g, '').trim();
    const x = {src: 'wm', title: p.title.slice(5), w: ii.width, h: ii.height, thumb: ii.thumburl, page: ii.descriptionurl,
      lic: v('LicenseShortName'), licurl: v('LicenseUrl'), artist: v('Artist').slice(0, 60), date: v('DateTimeOriginal').slice(0, 25)};
    if (x.w >= 1600 && x.w / x.h >= 1.3 && /^(CC0|Public domain|CC BY(-SA)? [\d.]+)/i.test(x.lic) && !window._wm.some(y => y.title === x.title)) window._wm.push(x);
  });
}
window._wm.map((x, i) => i + ' ' + x.title.slice(0, 55).replace(/[?&=]/g, ' ') + ' | ' + x.w + 'x' + x.h + ' | ' + x.lic + ' | ' + x.date.slice(0, 16)).join('\n')
```

- 결과가 0~1건이면 **Openverse** 1회(같은 탭):
```javascript
const q = 'QUERY'; const d = await fetch('https://api.openverse.org/v1/images/?q=' + encodeURIComponent(q) + '&license_type=commercial,modification&aspect_ratio=wide&size=large&page_size=20').then(r => r.json());
(d.results || []).forEach(r => window._wm.push({src: 'ov', title: r.title, w: r.width, h: r.height, thumb: r.url, page: r.foreign_landing_url,
  lic: (r.license || '').toUpperCase() + ' ' + r.license_version, licurl: r.license_url, artist: (r.creator || '').slice(0, 60), date: ''}));
window._wm.filter(x => x.src === 'ov').map((x, i) => i + ' ' + (x.title || '').slice(0, 50).replace(/[?&=]/g, ' ') + ' | ' + x.w + 'x' + x.h + ' | ' + x.lic).join('\n')
```
  - ⚠️ Openverse는 v8.0 신규 경로다. **첫 실행에서 CORS·응답을 확인**하고, 막히면 그 실행은 건너뛰고 보고에 「Openverse CORS 실패」를 남긴다. Openverse 결과는 **`page`(원 출처)를 열어 라이선스를 다시 확인**한 뒤에만 쓴다.
- 공공누리·관광공사 사진은 사진 페이지의 유형 마크가 **제1유형**인지 눈으로 보고, 그 이미지 직접 URL을 새 탭으로 열어 같은 출처에서 크롭한다(→ ref §3-5 ③).

**③ 후보를 눈으로 본다 — 임시 탭 1개 + 1배치**
후보 2~3개의 `thumb` 를 `iiurlwidth=960` 크기로 같은 임시 탭에서 차례로 `navigate` → `screenshot scale 0.6`. (URL 출력이 막히면 `x.thumb.replace(/[?&=]/g,'_')` 로 경로를 보고, 썸네일 경로의 `/1600px-` 를 `/960px-` 로 바꿔 연다.)

**④ 채택 기준**
- 피사체가 본문이 말하는 **바로 그 것**(그 제품·그 장소·그 지점). 같은 이름 다른 장소 금지.
- 시기: 계절·리모델링이 맞을 것. 제품은 **현재도 같은 모양으로 팔리면** 오래된 사진도 허용(예: 2018년 스초생).
- 식별 가능한 얼굴이 크게 나온 사진 금지. 원경 군중은 무방.
- 제품 자체의 로고·포장 글자는 허용(실물이므로). 광고 포스터 단독 촬영은 금지.
- 원본 폭 1600px 이상, 확대 보간 금지.

**⑤ 가공·업로드 (WP 리스너 탭에서 1회)** — 16:10 중앙 크롭 1226×768, 그레인 없음.

```javascript
const K = 0, slot = 'SLOT', slug = 'SLUG', ALT = 'ALT';
const P = window._wm[K];
const LIC = P.lic.replace(/^CC BY-SA 2\.0 kr$/i, 'CC BY-SA 2.0 KR');
const CREDIT = 'Photo: ' + P.artist + ' / <a href="' + P.page + '">' + (P.src === 'wm' ? 'Wikimedia Commons' : 'source') + '</a>, '
  + (P.licurl ? '<a href="' + P.licurl + '">' + LIC + '</a>' : LIC) + ', cropped';
const bmp = await createImageBitmap(await fetch(P.thumb, {mode: 'cors', credentials: 'omit'}).then(r => r.blob()));
const W = 1226, H = 768, r = Math.max(W / bmp.width, H / bmp.height); if (r > 1) throw new Error('too small');
const sw = W / r, sh = H / r, sx = (bmp.width - sw) / 2, sy = (bmp.height - sh) / 2;   // 피사체가 잘리면 sx·sy 조정
const c = document.createElement('canvas'); c.width = W; c.height = H; c.getContext('2d').drawImage(bmp, sx, sy, sw, sh, 0, 0, W, H);
const blob = await new Promise(res => c.toBlob(res, 'image/webp', 0.86));
const name = 'koreaplug-photo-' + slug + '-' + slot + '.webp', fd = new FormData(); fd.append('file', blob, name);
const j = await fetch('/wp-json/wp/v2/media', {method: 'POST', headers: {'X-WP-Nonce': window._nonce}, body: fd}).then(r => r.json());
await fetch('/wp-json/wp/v2/media/' + j.id, {method: 'POST', headers: {'X-WP-Nonce': window._nonce, 'Content-Type': 'application/json'}, body: JSON.stringify({alt_text: ALT, caption: CREDIT})});
window._uploadedIds.push({id: j.id, url: j.source_url, alt: ALT, tag: name}); (window._caps = window._caps || {})[slot] = CREDIT;
'photo ' + slot + ' -> ' + j.id + ' ' + Math.round(blob.size / 1024) + 'KB src' + bmp.width + 'x' + bmp.height
```
- `Photo:` 캡션은 라이선스 의무다. 빠지면 저장 금지(§7 가드 `photoCap`).

---

### 3-6. 모션 그래픽 — C 슬롯

**무엇을**: 본문 표·수치가 말하는 **결론 하나**(가장 싼 것, 마감일, 순서, 이동 시간). 숫자·날짜·요금은 **본문 raw 그대로**, 새 숫자 금지.

**HF 템플릿 경로(우선)** — 요금 비교 `stat_bars`, 절차 `steps_flow`. 클라우드 Bash, `timeout` 600000ms:
```bash
D=/tmp/kp_motion_SLUG && mkdir -p $D && cd $D
(test -d hfkit || git clone -q --depth 1 https://github.com/leejc0404/blog hfkit) && K=hfkit/tools/hf
cat > hfN.json <<'EOF'
{"theme":"kp","title":"…","subtitle":"…","items":[{"label":"…","value":31000,"text":"₩31,000","tone":"neutral"}],
 "highlight":0,"badge":"Cheapest","source":"Source: …, checked YYYY-MM-DD"}
EOF
timeout 300 python3 $K/hf_render.py stat_bars hfN.json koreaplug-motion-SLUG-N.mp4 --size 1226x768 --poster koreaplug-motion-SLUG-N-poster.webp; echo "exit=$?"
ffmpeg -y -loglevel error -ss 3 -i koreaplug-motion-SLUG-N.mp4 -frames:v 1 mid.png; ffmpeg -y -loglevel error -i koreaplug-motion-SLUG-N-poster.webp poster.png
```
- **(v8.0 실측) 글자 길이 한도** — `label` **16자 이하**(브랜드명만, 예: `Paris Baguette`), `subtitle` **40자 이하**, `title` 40자 이하. 넘으면 라벨이 막대·숫자와 겹치고 `Cheapest` 배지가 부제목을 가린다(2026-11-28: 1차 렌더에서 겹침 → 라벨 축약 후 통과).
- `highlight` 는 **0부터 세는 번호**다.
- 값 범위가 크면(예: ₩31,000~₩550,000) 그대로 둔다 — 차이 자체가 메시지다.
- ⛔ `Read` 로 `mid.png`·`poster.png` 2장을 직접 보고(겹침·잘림·오타·숫자 대조) 통과한 뒤에만 `mkdir -p /mnt/user-data/outputs/kp_motion && cp koreaplug-motion-SLUG-N* /mnt/user-data/outputs/kp_motion/`.
- 600KB 초과·종료코드 2·시간 초과면 canvas 경로(→ ref §3-6 ③)로 한 번 만든다. 실패하면 슬롯 생략.

**업로드** — 리스너 탭에서 전용 입력 생성 → `find "kp motion picker"` → `file_upload` → REST:
```javascript
const i = document.createElement('input'); i.type = 'file'; i.multiple = true; i.setAttribute('aria-label', 'kp motion picker');
i.style.cssText = 'position:fixed;top:120px;left:20px;z-index:99999'; document.body.appendChild(i); 'added'
```
- ⛔ `find` 결과에서 **`kp motion picker`** ref만 쓴다. `업로드`(plupload) 입력에 넣으면 즉시 자동 업로드된다.
```javascript
const i = document.querySelector('input[aria-label="kp motion picker"]'), out = [], ALT = 'ALT';
for (const f of i.files) { const fd = new FormData(); fd.append('file', f, f.name);
  const j = await fetch('/wp-json/wp/v2/media', {method: 'POST', headers: {'X-WP-Nonce': window._nonce}, body: fd}).then(r => r.json());
  if (!j.id) { out.push(f.name + ' FAIL'); continue; }
  await fetch('/wp-json/wp/v2/media/' + j.id, {method: 'POST', headers: {'X-WP-Nonce': window._nonce, 'Content-Type': 'application/json'}, body: JSON.stringify({alt_text: ALT})});
  window._uploadedIds.push({id: j.id, url: j.source_url, alt: ALT, tag: f.name}); out.push(f.name.slice(-16) + '->' + j.id); }
i.remove(); window._caps['N'] = 'CAPTION ONE LINE';
const seen = {}, dup = []; window._uploadedIds.forEach(u => { if (seen[u.tag]) dup.push(u.id); else seen[u.tag] = 1; });
out.join(' | ') + ' dup:' + (dup.join(',') || 'none')
```
- 모션 정보는 본문 텍스트·표에도 있어야 한다(접근성·검색).

---

## STEP 5. Flow 생성·채택·캡처 (B 슬롯만)

### 5-1. 설정 확인 (매 실행)

```javascript
const B = l => Array.from(document.querySelectorAll('button')).find(b => (b.getAttribute('aria-label') || '') === l);
const ag = B('Flow 에이전트'), st = B('설정 트리거');
'agent:' + (ag ? ag.getAttribute('aria-pressed') : 'NONE') + ' chip:' + (st ? st.textContent.trim() : 'NONE') + ' vp:' + innerWidth + 'x' + innerHeight
```
- `agent:true` 면 그 버튼을 눌러 끈다(ON이면 프롬프트가 채팅 세션으로 넘어가 전량 실패 → ref §5-1).
- `chip` 이 **`Nano Banana Pro … x2`** 면 통과. 아니면 `설정 트리거` `.click()` → 원본 스크린샷 1장 → 모델 드롭다운에서 **맨 위 `Nano Banana Pro`**, 비율 **16:9**, 장수 **x2**, 모드 **이미지**. 칩 선택 즉시 반영(저장 버튼 없음).
- **(v8.0) 모델 목록**: `Nano Banana Pro / Nano Banana 2 Lite / Nano Banana 2.1`, 기본값 `2.1`(2026-11-28). 패널 하단 **「생성 시 0 크레딧이 사용됩니다」** 를 확인한다. Pro에서 0이 아니면 **그 실행만 `Nano Banana 2.1`** 로 내려가고 보고에 문구를 남긴다. Lite는 쓰지 않는다.
- 패널은 입력창 `.focus()` 로 닫힌다.

### 5-2. 제출 (프롬프트 1개 = batch 1회, 대기 없이 연속)

**그리드는 최신순**이다. 히어로를 **마지막에** 보내면 그리드 0·1번이 히어로, 2·3번이 슬롯1이 된다.

```
browser_batch([
  {javascript_tool: "const ed=document.querySelector('[contenteditable=\"true\"], textarea'); ed.focus(); window._first0 ??= (Array.from(document.querySelectorAll('img')).filter(i=>i.naturalWidth>400)[0]||{}).src; 'focused:'+(document.activeElement===ed)"},
  {computer: type → 프롬프트 전문},
  {computer: key "Return"},
  {computer: wait 4},
  {javascript_tool: "const ed=document.querySelector('[contenteditable=\"true\"], textarea'); 'len:'+(ed.value||ed.textContent).length+' prog:'+(Array.from(document.querySelectorAll('div')).map(d=>d.textContent).filter(t=>/^\\d{1,3}%$/.test(t||'')).join(',')||'NO-PROGRESS-CARD')"}
])
```
- **성공** = `len` 이 0~14(플레이스홀더만) **그리고** 진행률 카드가 2개 늘었다.
- **미전송**(len이 프롬프트 길이) → 텍스트는 그대로 두고 ① `Return` 다시 ② 전송 화살표 좌표 클릭(`aria-label="생성 시작"` 버튼의 rect × 스크린샷폭/innerWidth, 입력바 안이므로 허용) ③ 버튼 `.click()`. 3회 모두 실패면 그 슬롯 skip.
- ⛔ 미전송 상태에서 **다음 프롬프트를 타이핑하지 않는다**(이어붙어 잡탕 프롬프트가 된다). 치환이 필요하면 `ctrl+a` 후 타이핑.
- `len:0` 인데 `NO-PROGRESS-CARD` 면 전송 무효 → 같은 프롬프트로 재제출.
- 좌표 클릭은 **입력바 안에서만**. 그리드 카드 위 클릭 금지.
- 기다리는 동안 **C 모션 렌더(클라우드)와 A 실사진 검색을 한다.**

### 5-3. 완료 대기 + 채택 (1~2회)

```javascript
// 40초 이하로. 진행률 카드가 사라지고 첫 카드가 바뀌면 완료 (그리드 장수는 가상 스크롤이라 20에서 늘지 않는다 — 2026-11-28 실측)
let p = 'x'; for (let t = 0; t < 4; t++) { await new Promise(r => setTimeout(r, 9000));
  p = Array.from(document.querySelectorAll('div')).map(d => d.textContent).filter(t => /^\d{1,3}%$/.test(t || '')).join(',');
  if (!p) break; }
const a = Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 400); a[0].scrollIntoView({block: 'start'});
'prog:' + (p || 'done') + ' changed:' + (a[0].src !== window._first0) + ' n:' + a.length + ' vp:' + innerWidth + 'x' + innerHeight
```
→ 이어서 `screenshot`(scale 없이) 1장. 뷰포트가 넓으면 4장(2프롬프트분)이 한 화면에 들어온다.

**채택 판정 — 2장 중 1장. 아래 「결함 7항목」(v8.0) 중 하나라도 걸리면 그 후보는 탈락**

| # | 결함 | 확인 방법 |
|---|---|---|
| 1 | **신체 결손·복제** — 머리·목·팔이 없음, 손가락 6개, 같은 얼굴이 두 번 | 인물마다 머리→손 순서로 본다 |
| 2 | **가짜 브랜드 글자** — 앞치마·컵·상자·간판에 실제 브랜드를 닮은 문자 (2026-11-28: 직원 앞치마) | 의복·포장·간판의 문자 |
| 3 | **초점 안의 엉터리 한글** — 중경 이상 크게 읽히는 현수막·간판 (2026-11-28: 히어로 현수막) | 화면 1/10 이상 크기의 한글 |
| 4 | **뭉개진·지워진 얼굴** — 행인 얼굴이 흐림 처리된 것처럼 번짐 (2026-11-28 후보 3번) | 배경 인물 얼굴 |
| 5 | **장소 오인** — 다른 나라 사진으로 보임 / Nowhere | "다른 나라 기사에 넣어도 어색하지 않은가" |
| 6 | **실물 오류** — 한국 고유 형태(도어락·지하철·케이크·버스)가 서구형 | 본문 묘사와 대조 |
| 7 | **광고 화보 톤** — 완벽 대칭, 과포화, 매끈한 피부, 무결점 진열 | "폰으로 찍었다고 믿겠는가" |

- 두 장 다 탈락이면 결함을 **물리적으로 막는 문장**을 넣은 수정 프롬프트로 1회만 재생성. 그래도 안 되면 그 슬롯은 A·C로 바꾸거나 생략.
- 세부가 꼭 필요하면 Flow 탭이 아니라 **업로드 후 미리보기(§7.5)** 에서 크게 본다. 미리보기에서 결함이 발견되면 그 1장만 교체하고 舊 미디어는 「삭제 대기」.

### 5-4. 캡처 (1회 호출)

```javascript
const pick = [2, 0], names = ['_img1', '_imgHero'];     // 5-3에서 고른 그리드 번호 (최신순)
const all = Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 400), out = [];
for (let k = 0; k < pick.length; k++) {
  const b0 = await fetch(all[pick[k]].currentSrc || all[pick[k]].src, {mode: 'cors', credentials: 'omit'}).then(r => r.blob());   // include 금지
  const bmp = await createImageBitmap(b0), c = document.createElement('canvas'); c.width = bmp.width - 150; c.height = bmp.height;   // 워터마크는 우측 150px
  const g = c.getContext('2d'); g.drawImage(bmp, 0, 0, c.width, c.height, 0, 0, c.width, c.height);
  const id = g.getImageData(0, 0, c.width, c.height), px = id.data;
  for (let j = 0; j < px.length; j += 4) { const n = (Math.random() - 0.5) * 10; px[j] += n; px[j + 1] += n; px[j + 2] += n; }   // 그레인 ±5
  g.putImageData(id, 0, 0);
  const blob = await new Promise(r => c.toBlob(r, 'image/webp', 0.85));
  window[names[k]] = await new Promise(r => { const rd = new FileReader(); rd.onloadend = () => r(rd.result); rd.readAsDataURL(blob); });
  out.push(names[k] + ' ' + bmp.width + 'x' + bmp.height + '->' + c.width + ' ' + Math.round(blob.size / 1024) + 'KB');
}
out.join(' | ')     // 정상: 1376x768->1226
```
- `1376x768` 이 아니면 엉뚱한 카드다 — `pick` 재확인. 캡처 후에는 Flow 탭 navigate·새로고침 금지(`_img*` 소실).

---

## STEP 6. 업로드 — 리스너 탭 하나에 모은다

1. Flow 탭에서 `window._wpWin = window.open('https://koreaplug.com/wp-admin/media-new.php')` (**`'_blank'` 금지** — MCP 그룹 밖으로 열린다) → `wait 8` → `tabs_context_mcp` 로 새 tabId(**LT**) 확인. (한 batch로 묶는다.)
2. LT에 nonce + 리스너 주입 (1회):
```javascript
const s = Array.from(document.querySelectorAll('script:not([src])')).map(x => x.textContent).join('\n');
const m = s.match(/apiFetch\.createNonceMiddleware\(\s*["']([a-f0-9]+)["']/);
window._nonce = m ? m[1] : null; window._uploadedIds = []; window._upErrors = [];
window.addEventListener('message', async (e) => {
  if (!e.data || !e.data.dataUrl) return; const {dataUrl, filename, altText} = e.data;
  try { const arr = dataUrl.split(','), mime = arr[0].match(/:(.*?);/)[1], bs = atob(arr[1]), u8 = new Uint8Array(bs.length);
    for (let i = 0; i < bs.length; i++) u8[i] = bs.charCodeAt(i);
    const fd = new FormData(); fd.append('file', new Blob([u8], {type: mime}), filename);
    const j = await fetch('/wp-json/wp/v2/media', {method: 'POST', headers: {'X-WP-Nonce': window._nonce}, body: fd}).then(r => r.json());
    if (!j.id) return window._upErrors.push(filename + ' ' + JSON.stringify(j).slice(0, 120));
    await fetch('/wp-json/wp/v2/media/' + j.id, {method: 'POST', headers: {'X-WP-Nonce': window._nonce, 'Content-Type': 'application/json'}, body: JSON.stringify({alt_text: altText})});
    window._uploadedIds.push({id: j.id, url: j.source_url, alt: altText, tag: filename});
  } catch (err) { window._upErrors.push(filename + ' ' + err.message); }
});
'nonce:' + (window._nonce ? 'ok' : 'MISSING') + ' listener ready'
```
3. Flow 탭에서 전송 (1회):
```javascript
const send = (d, f, a) => window._wpWin.postMessage({dataUrl: d, filename: f, altText: a}, 'https://koreaplug.com');
send(window._img1, 'koreaplug-SLUG-1.webp', 'ALT_1');
send(window._imgHero, 'koreaplug-SLUG-hero.webp', 'ALT_HERO');
await new Promise(r => setTimeout(r, 20000)); 'sent'
```
4. **A 실사진(§3-5 ⑤)과 C 모션(§3-6)도 같은 LT에서 올린다** — `_uploadedIds` 가 한 곳에 모여 STEP 7이 그대로 돈다.
5. 확인: `'up:'+_uploadedIds.length+' err:'+_upErrors.length`. `up` 이 모자라고 `err:0` 이면 **미완료**다 — 10초 더 기다린 뒤 재확인, 그래도 모자랄 때만 부족분 재전송. 재전송했다면 중복 tag를 빼고 그 ID를 「삭제 대기」로.

---

## STEP 7. 삽입·검증·저장 (2회 호출)

### 7-1. 삽입 + 스톡 교체 + 가드 (1회)

```javascript
const PID = POST_ID, PLAN = [[1, 0], [2, 1], [3, 2]];   // [슬롯 번호, 그 앞에 넣을 h2 번호] — 쓰는 슬롯만, h2 순서대로
const d = await fetch('/wp-json/wp/v2/posts/' + PID + '?context=edit&_fields=content,featured_media,status,date', {headers: {'X-WP-Nonce': window._nonce}}).then(r => r.json());
const c0 = d.content.raw; window._finalContent = c0; window._curFeatured = d.featured_media; window._origStatus = d.status; window._origDate = d.date;
const md = await fetch('/wp-json/wp/v2/media?include=' + window._uploadedIds.map(u => u.id).join(',') + '&per_page=20&_fields=id,source_url,media_details', {headers: {'X-WP-Nonce': window._nonce}}).then(r => r.json());
window._srcset = {};
md.forEach(m => { const x = m.media_details || {}, set = {}; Object.values(x.sizes || {}).forEach(v => { if (v.mime_type === 'image/webp') set[v.width] = v.source_url; });
  if (x.width) set[x.width] = m.source_url; const ws = Object.keys(set).map(Number).sort((a, b) => a - b).filter(w => w >= 300);
  window._srcset[m.id] = {w: x.width, h: x.height, srcset: ws.map(w => set[w] + ' ' + w + 'w').join(', ')}; });
const IMG = (u, hero, style) => { const s = window._srcset[u.id]; return '<img class="wp-image-' + u.id + '" src="' + u.url + '" srcset="' + s.srcset
  + '" sizes="(max-width: 820px) 100vw, 820px" width="' + s.w + '" height="' + s.h + '" alt="' + u.alt + '"' + (hero ? ' loading="eager" fetchpriority="high"' : ' loading="lazy"')
  + ' decoding="async" style="' + (style || 'width:100%;display:block;height:auto;border-radius:8px;') + '" />'; };
const by = (n, re) => window._uploadedIds.find(u => new RegExp('-' + n + re).test(u.tag));
const SLOT = n => { const cap = (window._caps || {})[n] ? '\n  <figcaption style="font-size:13px;color:#666;margin-top:6px">' + window._caps[n] + '</figcaption>' : '';
  const mp4 = by(n, '\\.mp4$'); if (mp4) { const p = by(n, '-poster\\.webp$');
    return '\n<figure class="kp-motion" style="margin:20px 0">\n  <video src="' + mp4.url + '"' + (p ? ' poster="' + p.url + '"' : '') + ' width="1226" height="768" autoplay muted loop playsinline preload="metadata" aria-label="' + mp4.alt + '" style="width:100%;height:auto;display:block;border-radius:8px;"></video>' + cap + '\n</figure>\n'; }
  const u = by(n, '\\.webp$'); return u ? '\n<figure' + (/koreaplug-photo-/.test(u.tag) ? ' class="kp-photo"' : '') + ' style="margin:20px 0">\n  ' + IMG(u) + cap + '\n</figure>\n' : ''; };
const h2 = [...c0.matchAll(/<h2[^>]*>/g)].map(x => x.index), pts = PLAN.map(([, k]) => h2[k]);
let c = c0; for (let i = PLAN.length - 1; i >= 0; i--) c = c.slice(0, pts[i]) + SLOT(PLAN[i][0]) + c.slice(pts[i]);
const hero = window._uploadedIds.find(u => /-hero\.webp$/.test(u.tag)), body = window._uploadedIds.filter(u => /-\d\.webp$/.test(u.tag) && !/poster/.test(u.tag));
let n = 0; c = c.replace(/<img[^>]*>/g, t => { if (!/unsplash\.com|pexels\.com|pixabay\.com|FEATURED_IMAGE/.test(t)) return t; n++;
  const pk = n === 1 ? hero : body[n - 2]; if (!pk) return t; return IMG(pk, n === 1, (t.match(/style="([^"]*)"/) || [])[1]); });
window._newContent = c; window._stockReplaced = n;
const C = (s, r) => (s.match(r) || []).length, kp = (c.match(/<img[^>]*koreaplug-[^>]*>/g) || []);
const G = {evClass: C(c0, /evidence-capture/g) + '>' + C(c, /evidence-capture/g), evName: C(c0, /\/evidence-/g) + '>' + C(c, /\/evidence-/g),
  ezToc: C(c0, /ez-toc/g) + '>' + C(c, /ez-toc/g), h2: C(c0, /<h2/g) + '>' + C(c, /<h2/g), table: C(c0, /<table/g) + '>' + C(c, /<table/g),
  fig: C(c, /<figure/g) + '/' + C(c, /<\/figure>/g), stock: C(c, /unsplash\.com|FEATURED_IMAGE/g), dupImg: (() => { const s = c.match(/src="[^"]*"/g) || []; return s.length - new Set(s).size; })(),
  noAlt: C(c, /<img(?![^>]*alt=)/g), video: C(c0, /<video/g) + '>' + C(c, /<video/g),
  vidAttr: (c.match(/<video[^>]*>/g) || []).filter(t => !/autoplay/.test(t) || !/muted/.test(t) || !/playsinline/.test(t) || !/poster=/.test(t)).length,
  photoCap: C(c, /class="kp-photo"/g) + '/' + C(c, /<figcaption[^>]*>Photo:/g), noSrcset: kp.filter(t => !/srcset=/.test(t)).length,
  noWH: kp.filter(t => !/width="/.test(t)).length, noLoad: kp.filter(t => !/loading="/.test(t)).length};
'st:' + d.status + ' fm:' + d.featured_media + ' stock:' + n + ' pts:' + pts.map(p => Math.round(p / c0.length * 100) + '%') + ' srcsetN:' + Object.entries(window._srcset).map(([k, v]) => k + '=' + v.srcset.split(',').length) + '\n' + Object.entries(G).map(([k, v]) => k + ':' + v).join(' ')
```

**저장 조건 (하나라도 어긋나면 저장 금지)**: `evClass`·`evName`·`h2`·`table` 좌우 같음 · `ezToc 0>0` · `fig` 짝 일치 · `stock 0` · `dupImg 0` · `noAlt 0` · `vidAttr 0` · `photoCap` 두 수 같음 · `noSrcset`·`noWH`·`noLoad` 0 · `srcsetN` 이미지마다 2 이상(mp4는 1이 정상 — 1이면 몇 초 뒤 재조회).

### 7-2. 저장 + 상태 복구 + 대표이미지 (1회)

```javascript
const PID = POST_ID, H = {'X-WP-Nonce': window._nonce, 'Content-Type': 'application/json'};
const s = await fetch('/wp-json/wp/v2/posts/' + PID, {method: 'POST', headers: H, body: JSON.stringify({content: window._newContent, status: window._origStatus})}).then(r => r.json());
let out = 'save:' + s.id + ' status:' + s.status;
if (s.status !== window._origStatus) out += ' RESTORED:' + (await fetch('/wp-json/wp/v2/posts/' + PID, {method: 'POST', headers: H, body: JSON.stringify({status: window._origStatus})}).then(r => r.json())).status;
const hero = window._uploadedIds.find(u => /-hero\.webp$/.test(u.tag)) || window._uploadedIds.find(u => /-1\.webp$/.test(u.tag));
if (window._curFeatured === 0 && hero) { const f = await fetch('/wp-json/wp/v2/posts/' + PID, {method: 'POST', headers: H, body: JSON.stringify({featured_media: hero.id, status: window._origStatus})}).then(r => r.json());
  out += ' featured:' + (f.featured_media === hero.id ? 'ok ' + hero.id : 'FAIL') + ' st:' + f.status; } else out += ' featured:skip(' + window._curFeatured + ')';
out
```
- 이미 대표이미지가 있는 글은 덮어쓰지 않는다.

---

## STEP 7.5. 미리보기 검증 (1 batch)

임시 탭(위키 확인에 썼던 탭)을 재사용한다.

```
browser_batch([
  {navigate: 'https://koreaplug.com/?p=POST_ID&preview=true', tabId: T},
  {javascript_tool: 「측정」},
  {javascript_tool: 「영상」},
  {computer: screenshot, scale 0.5},                       ← 모션 위치
  {javascript_tool: "document.querySelector('figure.kp-photo')?.scrollIntoView({block:'center'}); await new Promise(r=>setTimeout(r,800)); 'ok'"},
  {computer: screenshot, scale 0.5},
  {javascript_tool: "document.querySelector('img[src*=\"-1.webp\"]')?.scrollIntoView({block:'center'}); await new Promise(r=>setTimeout(r,800)); 'ok'"},
  {computer: screenshot},                                  ← Flow 컷은 원본 크기로 결함 7항목 재검
  {javascript_tool: "window.scrollTo(0,0); await new Promise(r=>setTimeout(r,800)); 'ok'"},
  {computer: screenshot}                                   ← 히어로 + 제목 오버레이
])
```

「측정」 — 자연 스크롤로 lazy 로드를 유도한 **뒤에** 측정한다(`eager` 강제 금지 — srcset 판정이 오염된다):
```javascript
for (let y = 0; y < document.documentElement.scrollHeight; y += 500) { scrollTo(0, y); await new Promise(r => setTimeout(r, 250)); }
await new Promise(r => setTimeout(r, 1500)); scrollTo(0, 0); const H = document.documentElement.scrollHeight;
const A = Array.from(document.querySelectorAll('article img')), g = A.filter(i => /koreaplug-/.test(i.src));
A.filter(i => i.naturalWidth > 300).map(i => i.src.split('/').pop().split('?')[0].slice(0, 36) + ' @' + Math.round((i.getBoundingClientRect().top + scrollY) / H * 100) + '%').join('\n')
 + '\nTOC:' + document.querySelectorAll('.ez-toc-container,#ez-toc-container').length + ' h2:' + document.querySelectorAll('article h2').length
 + ' broken:' + A.filter(i => i.complete && i.naturalWidth === 0).length
 + ' full:' + g.filter(i => !/-\d+x\d+\.webp$/.test(i.currentSrc.split('?')[0])).length + '/' + g.length + ' vis:' + document.visibilityState
```
「영상」:
```javascript
const v = document.querySelector('article video'); if (!v) 'no video'; else { v.scrollIntoView({block: 'center'}); await new Promise(r => setTimeout(r, 3000));
  'rs' + v.readyState + ' t' + v.currentTime.toFixed(1) + ' ' + v.videoWidth + 'x' + v.videoHeight + ' paused:' + v.paused; }
```
- 통과: `TOC:1` · `broken:0` · `full` 은 0/N (히어로가 full이어도 허용) · 영상 `rs≥2 paused:false 1226x768`. 탭이 숨김(`vis:hidden`)이라 `rs0` 이면 → ref §7.5 의 Range 요청으로 서버 응답만 확인.
- 육안: 결함 7항목 재검 · 실사진 `Photo:` 캡션 보임 · 증빙 제자리 · 4장이 "한국 글"로 보이는가 · 글 상태 그대로.

**뒷정리**: 마지막 글이 끝나면 루틴이 연 탭을 모두 닫는다(미리보기 탭은 남겨도 된다).

---

## STEP 7.9. 글이 2편 이상일 때

- STEP 1·2는 한 번에. **STEP 3~7.5는 글 단위 라운드**로 끝까지 마치고 다음 글로 간다(부분 삽입 상태로 넘기지 않는다).
- 라운드마다: Flow 탭 프로젝트 URL 재이동 → `_wpWin` 새로 열기 → 새 LT에 리스너 재주입(nonce 포함) → `_caps`·`_slotPlan` 초기화. 이전 라운드 LT는 마지막에 함께 닫는다.

---

## STEP 8. 보고 + 알림

### 8-A. 중단 보고
중단 지점·사유 · 사용자 조치(URL 포함) · 대상 글 표 · STEP 2 결과 · **완성한 프롬프트 전문·훅 문장·alt·삽입 위치**(다음 실행이 STEP 3을 건너뛸 수 있게) · 건드리지 않은 것(상태·본문·미디어) · 탭 정리 여부.

### 8-B. 완료 보고 (글별 표)
- 글 제목·Post ID·상태(시작→종료, 복구 여부)
- 슬롯 표: 슬롯 · 유형(A/B/C) · media ID · 위치 % · 훅 문장 · 출처(실사진: 저작자·라이선스·페이지 / 모션: 템플릿·용량·검수 / Flow: 채택 번호·결함 7항목 결과)
- STEP 2 분류, 가드 결과 요약, 대표이미지 결과, 스톡 교체 수
- Flow 모델·크레딧 표시(폴백 여부) · Openverse 시도 결과(시도했을 때)
- 「삭제 대기」 미디어, 사용자 판단이 필요한 이미지
- 루틴 결함을 발견했으면 **고칠 조항과 교체용 전문**

### 8-C. 알림
- 이미지를 넣었거나, 중단됐거나, 사용자 판단이 필요하면 `PushNotification` 1회(한글, 첫 문장 = 결과). 대상 글 없음·전부 skip이면 알림하지 않는다.

### 마지막. 실행 기록 한 줄 (모든 경로에서 필수)

```bash
python3 - <<'PY'
import json, os, datetime
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
root = os.path.expanduser("~/mnt/Claude/control_tower/runs"); os.makedirs(root, exist_ok=True)
rec = {"routine": "3. Koreaplug auto image insert", "file": "Schd_KoreaPlug-Image.md", "date": now.strftime("%Y-%m-%d"),
       "start": "{시작 HH:MM}", "end": now.strftime("%H:%M"), "result": "{성공|부분|건너뜀|실패}", "count": 0,
       "summary": "{60자 이내}", "warnings": []}
with open(os.path.join(root, now.strftime("%Y-%m") + ".jsonl"), "a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
PY
```
- `count` = 이미지를 채운 글 수. 기존 줄은 고치지 않는다. 자격증명·URL 쿼리스트링을 넣지 않는다.
