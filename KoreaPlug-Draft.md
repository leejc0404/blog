# 📋 KoreaPlug Draft 지침 (Cowork wordpress_draft용)

## 📌 이 문서의 용도

`wordpress_draft` (Cowork 예정됨 루틴)이 WP 배포·SEO 보정 시 참조하는 **배포 전용 지침**입니다.

- **포함**: **5-0(지침서 무결성 검증·조항 자기보완)** → 5-2(TOC 강제 스크립트) → 5-3(블록 구조·820px·키워드 입력 체크) → **5-4(⛔ 발행 차단 관문)** → **5-4B(캡처 품질·마크업)** → 5-4C(피드백) → 5-5(Schema) → Phase 6(완료 처리) → 오류표 → Phase 7(카테고리 매핑)
- **번호 안내**: 번호는 ✏️ Writer 지침의 Phase 체계를 이어받은 것. Phase 0~5-1은 Writer 지침 담당이라 이 문서에 없음(의도된 결번, 오타 아님). ⚠️ Writer 지침의 '5-3(Focus Keyword 배치 자가검수)'과 이 문서의 '5-3(블록 구조·820px 체크)'은 **서로 다른 문서의 별개 항목**임에 주의.
- **v10.5 변경(2026-08-17)**: **「⛔ 본문 삽입 금지 자료」 조항 신설.** 구글 자동완성·SERP 순위·검색량 등 **SEO 리서치 산출물을 본문에 넣는 것을 금지**한다. 1급 자료 인정 목록에서 "구글 자동완성 제안 개수 실측"을 제거하고, ② 관문의 허용 예시도 공공기관 조회 사례로 교체했다. 2026-08-16 회차에서 두 글에 자동완성 캡처가 실린 것이 사용자 검토에서 반려된 것이 근거다. 5-4B에도 금지 목록을 연동했다.
- **v10.4 변경(2026-08-16)**: **「5-0 지침서 무결성 검증 및 조항 자기보완 규약」을 신설**했다. 2026-08-16 실행에서 Draft 루틴이 이 문서를 조회했는데 **v10.2 시점의 캐시된 구버전**이 반환돼, 실제로 존재하는 5-4·5-4B를 "없다"고 오판하고 허위 상충을 보고한 사고가 근거다. 앞으로 조항이 안 보이면 ①캐시버스터 재조회 ②브라우저 2차 확인 ③본문 자가검증을 거친 뒤에만 결번으로 확정하고, 결번이 확정되면 **루틴이 조항을 직접 작성해 이 문서에 써 넣고 배포를 계속 진행**한다.
- **v10.3 변경(2026-08-08)**: `wordpress_draft` 루틴 v10.23이 참조하던 **「5-4 ⛔ 발행 차단 관문」·「5-4B 캡처 품질·마크업 규칙」을 정식 조항으로 신설**했다. 두 조항이 없어 루틴이 2026-08-07·08 이틀 연속 인라인 폴백으로 판정하고 상충을 기록해 온 문제를 해소한다. 기존 「5-4 피드백 체크리스트」는 **5-4C**로 번호를 옮겼다(내용 변경 없음).
  아울러 실측으로 확인된 오류 2건을 반영했다 — ① Rank Math는 `wp.data.dispatch('rank-math')` 로 저장되지 않는다(5-3·오류표 정정), ② REST `meta` 로도 저장되지 않는다(UI 입력만 유효).
- **v10.2 변경(정리)**: 舊 Phase 4(배포 JS) 삭제에 따른 잔존 참조 수정('Phase 4 스크립트 실행 후' → 'freeform 블록 삽입 후'). Writer v10.5 홀짝 트랙제 도입과 무관하게 이 문서의 절차는 동일 — 기본 정보 표의 Track 행(S/L)은 Draft 루틴이 계속 무시한다.

---

## 5-0. 지침서 무결성 검증 및 조항 자기보완 규약 (v10.4 신설)

> **배경 (2026-08-16 실측)**: Draft 루틴이 STEP 0에서 이 지침서를 조회했는데 **v10.2 시점의 캐시된 구버전**이 반환됐다. GitHub `main` 에는 v10.3(2026-08-08)부터 5-4·5-4B가 들어 있었는데도, 루틴은 "조항이 없다"고 판정해 [부록 A] 인라인 폴백으로 관문을 판정하고 지침서-루틴 상충을 보고했다. 같은 URL에 캐시버스터를 붙여 브라우저에서 재조회하니 조항이 정상적으로 존재했다(13,761자, v10.3).
> 즉 **"조항이 안 보인다"는 관측에는 서로 다른 두 원인**이 있다 — ⓐ 조회 경로가 낡은 사본을 준 것, ⓑ 조항이 실제로 없는 것. 이 둘을 구분하지 않으면 한쪽에서는 허위 상충 보고가 매일 쌓이고, 다른 쪽에서는 진짜 결번이 영원히 방치된다.

### 5-0-A. 조회 무결성 3단 검증 (루틴 STEP 0이 수행)

조항이 안 보이면 **아래를 다 밟기 전에는 "없다"고 판정하지 않는다.**

1. **캐시버스터 재조회** — 같은 raw URL 뒤에 `?cb={epoch_ms}` 를 붙여 1회 더 받는다. 중간 캐시가 무효화된다.
2. **브라우저 2차 확인** — 그래도 안 보이면 Claude in Chrome 에서 `fetch(rawURL + '?cb=' + Date.now())` 로 받는다. 샌드박스 fetch 도구와 브라우저는 캐시 계층이 다르다.
3. **본문 자가검증** — 받은 문서에서 아래를 실제 문자열로 확인하고 결과를 로그에 남긴다.
   - `5-4. ⛔ 발행 차단 관문` 존재 여부
   - `5-4B. 캡처 품질·마크업 규칙` 존재 여부
   - 문서 문자 수와 최신 개정 이력 줄(`**v10.x 변경`)

세 단계 중 **어느 하나라도 조항을 찾으면 그것이 진짜 지침서**다. 캐시본으로 이미 판정을 시작했더라도 되돌려 다시 판정한다. 이 경우는 **상충이 아니므로 상충으로 보고하지 않는다** — 조회 캐시 사고로 기록한다.

### 5-0-B. 조항 자기보완 (Self-Authoring) — 3단 검증 후에도 없을 때만

5-0-A를 전부 통과했는데도 조항이 없으면, 루틴은 **멈추지 않고 그 조항을 직접 작성해 넣은 뒤 draft를 계속 진행한다.**

1. **작성** — 결번 조항의 초안을 쓴다. 근거는 이 순서로만 삼는다: ⓐ 루틴 문서의 [부록 A] 인라인 폴백 기준 → ⓑ 같은 계열 지침서의 대응 조항(`0and1Life-Draft.md`) → ⓒ 최근 7일 반려 로그·실행 로그의 실측 사실. **셋 중 아무 근거도 없는 내용은 쓰지 않는다.**
2. **반영 위치** — `C:\Users\win\Documents\Claude\blog\KoreaPlug-Draft.md` 에 **직접 써 넣는다.** 조항 제목에 `(자동 신설 {YYYY-MM-DD}, 루틴 작성)` 을 반드시 표기한다.
3. **추가만 허용** — 기존 조항을 삭제하거나 번호를 바꾸지 않는다.
4. **커밋·푸시 금지** — git commit·push 는 사용자가 직접 한다. 루틴은 파일 수정까지만 한다.
5. **즉시 적용** — 신설한 조항을 그 회차의 판정 기준으로 바로 적용해 draft 를 계속한다. 조항이 없다는 이유로 배포를 중단하지 않는다.
6. **보고** — STEP 7 알림과 Notion 실행 로그에 `조항 자동 신설 {조항번호}` 를 표기하고, **신설 조항 전문을 로그에 그대로 남긴다.** 사용자가 읽고 승인·수정할 대상이기 때문이다.

### 5-0-C. 금지

- 3단 검증 없이 "조항 없음"으로 판정하는 것
- 근거 없이 조항 내용을 지어내는 것 (5-0-B 1의 ⓐⓑⓒ 밖의 창작)
- 기존 조항의 **삭제·번호 변경** — 자기보완은 **추가만** 허용한다
- 루틴이 git commit·push 를 수행하는 것
- 캐시 사고를 "지침서-루틴 상충"으로 보고하는 것

---

## 5-2. TOC 인식 강제 및 재분석 트리거 스크립트

**freeform 블록 삽입 후**(舊 Phase 4 — 현재는 wordpress_draft 루틴 STEP 6이 수행), 아래 스크립트를 이어서 실행한다:

```javascript
const { dispatch, select } = wp.data;
if (window.rankMath && window.rankMath.assessor) {
  window.rankMath.assessor.hasTOCPlugin = true;
  console.log('✅ hasTOCPlugin = true 강제 설정');
} else {
  console.warn('⚠️ rankMath.assessor 없음 — 잠시 후 다시 시도');
}
const blocks = select('core/editor').getBlocks();
const freeformBlock = blocks.find(b => b.name === 'core/freeform');
if (freeformBlock) {
  const originalContent = freeformBlock.attributes.content;
  dispatch('core/editor').updateBlockAttributes(freeformBlock.clientId, { content: originalContent + ' ' });
  setTimeout(() => {
    dispatch('core/editor').updateBlockAttributes(freeformBlock.clientId, { content: originalContent });
    console.log('✅ 재분석 트리거 완료 → Rank Math 패널에서 점수 확인 (목표: 81/100)');
  }, 800);
} else {
  console.error('❌ freeform 블록을 찾을 수 없음 — 콘텐츠 업로드 먼저 실행');
}
setTimeout(() => {
  wp.data.dispatch('core/editor').savePost().then(() => {
    console.log('✅ 임시저장 완료');
  });
}, 2000);
```

> ⚠️ 이 스크립트에서 쓰는 `dispatch('core/editor')` 는 **블록 조작용**이라 정상 동작한다. **`dispatch('rank-math')` 는 다르다** — 5-3의 경고를 반드시 읽을 것.

**TOC 블록이 `isValid:false` 로 뜰 때** (마커를 손으로 써 넣은 경우 발생):

```javascript
const b = wp.data.select('core/editor').getBlocks()[0];
if (b.name === 'rank-math/toc-block' && !b.isValid) {
  wp.data.dispatch('core/block-editor').replaceBlock(b.clientId, wp.blocks.createBlock('rank-math/toc-block'));
}
```

정상 직렬화 형태는 자기완결형이다: `<!-- wp:rank-math/toc-block {"headings":[],"listStyle":"ul"} /-->`

---

## 5-3. SEO 블록 구조 / 820px 무결성 체크 (Astra 보정)

**🟢 추가 SEO (블록 구조)**

- [ ] `rank-math/toc-block` 블록 존재 (1번 블록)
- [ ] `core/freeform` 블록으로 HTML 삽입 (2번 블록)
- [ ] 두 블록 모두 `isValid: true` 인가? (`false` 면 5-2 하단 복구 스크립트 실행)
- [ ] `hasTOCPlugin = true` 강제 설정 완료
- [ ] 재분석 트리거 실행 완료

**🟢 820px 컨테이너 무결성**

- [ ] 모든 콘텐츠가 `max-width:820px; padding:0 16px 40px; box-sizing:border-box;` 래퍼 안에 위치하는가?
- [ ] HTML 내 이미지가 plain `<figure>/<img>` 태그로 삽입되었으며 `<!-- wp:image -->` 마커가 없는가?
- [ ] freeform 블록 외부에 별도 Gutenberg 이미지 블록(`alignwide`)이 추가되지 않았는가?
- [ ] 외부 래퍼 div의 horizontal padding이 `0 16px` 이상으로 설정되어 모바일에서 텍스트가 화면 끝에 붙지 않는가?

**🟢 키워드 입력 (v10.3 전면 개정 — 이전 지시가 틀렸다)**

⛔ **`wp.data.dispatch('rank-math').updateKeywords(...)` 를 쓰지 않는다.**
에러 없이 성공한 것처럼 보이지만 **postmeta에 저장되지 않는다**(2026-07-24 실측). 새로고침하면 사라진다.

⛔ **REST API의 `meta` 로도 저장되지 않는다.**
`rank_math_focus_keyword` / `rank_math_title` / `rank_math_description` 은 `show_in_rest` 에 등록돼 있지 않다(2026-08-08 실측). curl·fetch 어느 쪽으로도 불가능하다.

✅ **유일하게 유효한 방법은 사이드바 UI 직접 입력이다.**

- [ ] Rank Math 포커스 키워드 필드에 Notion 기본 정보 표의 **Focus Keyword + Sub Keywords 전부**를 입력했는가? (Focus가 첫 번째, 총 5개 권장)

**입력 절차 — 태그 누적 버그 대응 (2026-08-08 실측)**

⚠️ **Enter를 눌러도 입력창의 텍스트가 지워지지 않는다.** 그대로 다음 키워드를 타이핑하면 앞 문자열에 이어붙어 `why do kdramas blur thingswhy do kdramas blur knives` 같은 쓰레기 태그가 생긴다.

1. 첫 키워드: 입력창 클릭 → Focus Keyword 타이핑 → Enter
2. 나머지는 **1개씩** 처리한다. 각 회차마다:
   - 입력창을 **triple_click** 한다 (잔여 텍스트를 선택 상태로 만든다 — 단순 클릭으로는 지워지지 않는다)
   - 키워드 타이핑 → Enter
   - **즉시 검증**: `wp.data.select('rank-math').getKeywords()`
3. ⚠️ **좌표가 밀린다.** 태그가 하나 늘 때마다 입력창이 약 26px 아래로 내려간다. 좌표를 예측해서 triple_click 하면 **입력창이 아니라 기존 태그를 덮어써 버린다**(2026-08-08에 키워드 1개가 이렇게 소실됨). 한 번에 묶지 말고 **1개 입력 → 1회 검증 → 스크린샷으로 위치 재확인**을 반복한다.
4. 잘못된 태그는 왼쪽 `×` 로 제거한다. 여러 개면 **아래에서 위 순서로** 지운다.

- [ ] 저장 후 **새로고침하고 나서** 검증: `wp.data.select('rank-math').getKeywords()` 항목이 5개인가? (저장 직후 값은 믿지 않는다 — 반드시 새로고침 후 확인)

> 배경: 2026-07-09 점검에서 Draft 루틴이 Focus만 입력하고 Writer가 Notion 표에 기록한 Sub Keywords를 버리는 문제 확인. 사용자가 매번 수동으로 채워오고 있었음 — 반드시 그대로 복사할 것.

**🟢 스니펫(SEO 타이틀·메타 설명)**

- [ ] 타이틀이 **580px 이내**인가? (영문 기준 약 57자. Notion SEO_TITLE이 60자를 넘으면 의미를 해치지 않는 관사·수식어 1개를 빼서 맞추고, 글 제목 자체는 Notion 원문을 유지한다)
- [ ] 메타 설명이 **150자 이내**이고 Focus Keyword를 포함하는가?
- [ ] ⚠️ Ctrl+A 후 타이핑해도 **이전 텍스트의 첫 글자 1개가 남는 사례가 반복 확인됨**(예: `aWhy do Koreans…`). 타이핑 직후 확대해 육안 확인하고, 잔여 문자가 있으면 필드 클릭 → Ctrl+Home → Delete로 제거한다.

**🟢 최종 확인**

- [ ] Rank Math 패널 점수: **78/100 이상**
- [ ] 임시저장(Draft) 상태 확인
- [ ] Notion 페이지 점수 업데이트

---

## 5-4. ⛔ 발행 차단 관문 (Publication Gate)

> **판정 시점**: WordPress 업로드(POST) **직전**. **Rank Math 점수와 무관**하다 — 90점이어도 관문에서 막히면 발행하지 않는다.
> **판정 주체**: `wordpress_draft` 루틴. 세 항목 **전부** 통과해야 업로드한다.

### ① 1급 원본 자료 — 최소 1개

이 글에만 있는 **직접 만든 근거**가 최소 하나 있어야 한다.

**인정되는 것**

- 공개 화면을 직접 조작해서 얻은 결과 캡처 (정부·공공기관 조회 화면, 예약 시스템, 지도 검색 결과 등)
- 직접 센 수치 (특정 조건의 항목 수 카운트, 현장에서 센 개수·가격 등) — ⛔ **SEO 리서치 산출물은 제외한다. 아래 「본문 삽입 금지 자료」 참조.**
- 직접 계산·산출한 값 (경일 계산으로 산출한 삼복 날짜 등)
- 1차 기록 (법령 조문 원문, 공고문, 기관 발표 원본)

**인정되지 않는 것**

- 다른 매체의 수치를 옮겨 만든 비교표
- 공식 통계를 다시 정리한 표
- 위키·블로그·포럼 내용의 요약
- "일반적으로 알려진" 사실의 나열
- ⛔ **SEO 리서치 산출물 전부** — 아래 별도 조항 참조

#### ⛔ 본문 삽입 금지 자료 (v10.5 신설 2026-08-17)

**필자의 키워드 리서치 과정은 독자가 볼 이유가 없다.** 아래는 주제 선정·수요 검증에는 계속 쓰되, **완성 글 본문에는 표·캡처·문장 어떤 형태로도 넣지 않는다.**

- 구글 **자동완성** 제안 목록·순위·개수 (캡처 및 실측표 모두)
- SERP 순위, 경쟁글 개수, 검색량·난이도 지표
- 키워드 툴 화면, Search Console·GA 화면
- "구글에 무엇을 치는지" 를 소재로 삼은 섹션·H2 전반

> **배경 (2026-08-17)**: 2026-08-16 회차에서 루틴이 `gwangjang-market-tourist-trap`·`korean-delivery-apps-for-foreigners` 두 글에 자동완성 캡처와 실측표를 관문 ① 충족 근거로 넣었다. 사용자 검토에서 **"검색해서 키워드 잡는 걸 왜 독자에게 보여주냐"** 로 반려돼 두 글에서 모두 제거했다(#134는 H2 섹션 통째, #135는 삽입 블록 전체).
> 원인은 舊 172행이 "구글 자동완성 제안 개수 실측"을 1급 자료로 **명시 인정**하고, 舊 ② 관문의 허용 예시가 `"I queried Google's autocomplete endpoint…"` 였던 것이다. 두 줄 다 이 개정에서 정리했다.
> ⚠️ **Writer 지침 4종은 수정하지 않았다** — 그쪽의 자동완성 언급 50여 곳은 전부 주제 선정·수요 검증용이고 본문 삽입을 지시하지 않는다. 문제는 이 문서의 두 줄에 국한된다.

**대신 무엇을 넣는가**: 독자가 그 글을 읽는 이유와 직접 연결되는 공개 화면 — 정부·공공기관 조회 결과, 요금·운영시간 안내, 공식 지원 목록, 법령 조문, 예약 시스템 화면. **"독자가 이 캡처를 보고 행동을 바꾸는가?"** 가 판정 질문이다. 아니오면 넣지 않는다.

**표기 의무**: 1급 자료에는 **출처·확인일**을 병기한다. 실측표에는 측정 방법(엔드포인트, 파라미터, 측정일)을 캡션으로 남긴다.

**조달 주체 판정**

- Notion 기본 정보 표의 `1급 자료 (나)` 에 **Writer가 이미 수행한 실측**이 적혀 있으면 → 그것으로 ①이 충족된다. 루틴이 새 캡처를 만들지 않는다.
- `1급 자료 조달 계획: 루틴가능 {화면·경로}` 가 명시돼 있으면 → **캡처 실행 주체는 루틴이다.** 5-4B에 따라 직접 캡처·삽입해 관문을 스스로 충족시킨다.
- 로그인·결제·개인정보 입력이 필요한 화면은 캡처하지 않는다 → 다른 1급 자료로 대체하거나 반려.
- ⛔ **(v10.4 신설 2026-08-09) 앱전용 화면은 범위 밖이다.** 이 루틴은 **브라우저만 조작**한다. 모바일 앱 안에서만 보이는 화면은 로그인 여부와 무관하게 캡처할 수 없다. **판정 질문: "이 자료가 웹 브라우저에서 보이는가?"** 아니오면 캡처를 시도하지 말고 즉시 반려한다 (자매 블로그 0and1Life #80, 2026-08-09 실측 — 시도 자체가 회차를 낭비시켰다).
  - **반려 전 1회 확인**: 같은 서비스의 **웹 버전·공식 페이지**가 있으면 그 화면으로 대체 가능한지 본다. 대체되면 `루틴가능`으로 전환해 진행한다.
  - 반려 시 사유 코드는 `1급-앱전용`으로 적어 사용자 조달 대기임을 명확히 한다.

### ② 가짜 경험 0건

**하지 않은 일을 1인칭으로 쓰지 않는다.**

- ❌ "I visited the office last week and the staff told me…" (방문한 적 없음)
- ❌ "When I tried the machine, it rejected my card." (시도한 적 없음)
- ✅ "On 8 August 2026 I checked the Korea Heritage Service admission page and the Tuesday closure was listed for every palace." (**실제로 수행한 조회**이므로 허용)
- ⚠️ "On 8 August 2026 I queried Google's autocomplete endpoint…" — 문장 자체는 사실이라 ② 관문은 통과하지만, **① 관문의 「본문 삽입 금지 자료」에 걸려 본문에 쓸 수 없다.** 리서치 기록은 Notion에만 남긴다.
- ✅ "Visitors report that the machine rejects foreign cards." (관찰·인용으로 서술)

실제로 수행한 조작·측정·계산의 1인칭은 **허용된다.** 판단 기준은 문장의 인칭이 아니라 **그 행위를 실제로 했는가**이다.

### ③ 이미지 출처

- 모든 `<img>` 는 **koreaplug.com 자체 업로드** 또는 **images.unsplash.com** 에서 온 것이어야 한다.
- 타 사이트 핫링크 **0건**. (pexels·pixabay·기관 사이트 직접 링크 포함 금지)
- unsplash CDN ID는 `^[0-9]{10,13}-[0-9a-f]{12}$` 형식이어야 한다. 공유링크의 짧은 슬러그 ID는 CDN에서 404가 난다.
- ⚠️ 샌드박스 curl로는 unsplash 접근이 막혀 있다(코드 000). ID 정규식이 맞으면 통과로 보고, **최종 확인은 프론트엔드 프리뷰에서 `naturalWidth > 0`** 으로 한다.

### ⛔ 불통과 시 처리

1. 업로드와 SEO 설정을 건너뛴다. Notion "draft 일자"는 **공란 유지**(다음 실행의 복구 로직이 이어받는다).
2. 발행 반려 로그(`https://www.notion.so/3adbfe4a2ae18167880ecbe3c73b90cc`)에 행을 추가한다:

   `| {날짜} | {슬러그} | {사유 코드} | {무엇을} | {어디에} | {왜} | {어떻게} | {루틴 또는 사용자} | 대기 |`

3. ⚠️ **"1급 자료 없음"만 적는 보고는 무효다.** 무엇을·어디에·왜·어떻게·누가를 모두 채운다. 다음 실행이 그 지시만 보고 자료를 조달할 수 있어야 한다.
4. 같은 슬러그의 '대기' 행이 이미 있으면 중복 추가하지 않는다.

---

## 5-4B. 캡처 품질·마크업 규칙

> 관문 ①을 캡처로 충족할 때 적용한다. 캡처 없이 실측표·계산으로 충족하는 글에는 해당 없음.

### ⛔ 찍기 전에 — 삽입 금지 대상인지 먼저 본다 (v10.5)

캡처 버튼을 누르기 전에 5-4 ①의 **「⛔ 본문 삽입 금지 자료」** 를 확인한다. 아래는 **품질과 무관하게 본문에 넣을 수 없다.**

- 구글 자동완성 화면·제안 목록
- 검색 결과(SERP) 화면, 경쟁글 목록
- 키워드 툴, Search Console, GA 화면

**판정 질문 한 줄: "독자가 이 캡처를 보고 행동을 바꾸는가?"** 아니오면 찍지 않는다. 잘 찍은 자동완성 캡처도 반려 대상이다.

### 캡처 품질

- **결과·표·조문 영역만 크롭**한다. 브라우저 헤더, 스크롤바, 마우스 커서, 쿠키 배너·팝업 잔재가 들어가면 다시 찍는다.
- 크롭은 `computer` 도구의 **`zoom` 액션 + `region`** 으로 한다. `screenshot` 액션은 region을 무시하고 전체 화면을 찍는다.
- 판독 가능한 해상도를 유지한다(표의 글자가 읽혀야 한다).
- **로그인·결제·개인정보 입력이 필요한 화면은 캡처하지 않는다.**
- 개인정보(이름, 연락처, 계정 ID)가 화면에 있으면 크롭으로 제외한다.

### 파일

- 형식 **webp**, 품질 0.88 내외
- 파일명 **`evidence-{SLUG}-{n}.webp`** (n은 1부터)
- `alt_text` 에 Focus Keyword를 포함한 설명을 넣는다
- ⚠️ 브라우저 canvas 크롭 경로를 쓰면 원본 전체 스크린샷이 미디어 라이브러리에 남는다. 잔여 파일 ID를 완료 로그에 기록하고 **삭제는 사용자 확인 후** 진행한다.

### 본문 마크업

```html
<figure class="evidence-capture" style="margin:24px 0;">
  <img src="{source_url}" alt="{Focus Keyword 포함 설명}" style="width:100%;height:auto;border:1px solid #ddd;border-radius:8px;display:block;">
  <figcaption style="font-size:0.85rem;color:#666;margin-top:8px;">
    {출처 기관} — {화면명} · Captured {YYYY-MM-DD}
  </figcaption>
</figure>
```

- 캡션은 **영문 표기**로 통일한다.
- 삽입 위치는 **그 자료가 뒷받침하는 문단·표 바로 아래**다. 글 맨 아래에 몰아넣지 않는다.
- `<!-- wp:image -->` 마커를 쓰지 않는다. plain `<figure>/<img>` 로만 넣는다(820px 래퍼를 벗어난다).

### 확인

업로드 후 `/?p={WP_POST_ID}&preview=true` 에서 `figure.evidence-capture img` 의 `naturalWidth > 0` 을 확인하고 스크린샷으로 육안 검증한다.

---

## 5-4C. 피드백 체크리스트

> (v10.3에서 舊 5-4 → 5-4C로 번호 이동. 내용 변경 없음)

- [ ] (Native Speech Check) 미국인 친구에게 자연스럽게 말할 수 있는가? → **Yes여야 함.**
- [ ] (Authenticity Check) 한국인이 읽었을 때 로컬 문화를 왜곡하지 않았는가? → **Yes여야 함.**
- [ ] (Curiosity Gap Check) 도입부 읽고 "왓? 진짜?" 호기심으로 스크롤을 내릴 수밖에 없는가? → **Yes여야 함.**
- [ ] (Zero-Translation Check) 관공서/사전식 한국어 직역 용어가 단 한 단어도 없는가? → **Yes여야 함.**
- [ ] 글이 한국으로 여행 오는 외국인에게 유용한 팁을 주는가?
- [ ] 제목에 클릭을 부르는 호기심 갭(질문/의외성)이 있는가?
- [ ] "미국인이 이 제목 문장을 구글에 그대로 칠까?"에 Yes라고 답할 수 있는가?

---

## 5-5. Rank Math Schema 마크업 설정

> 구글 로봇에게 콘텐츠 성격을 명확히 전달해 리치 카드(Rich Snippet) 형태로 노출. CTR 2~3배 향상.

**설정 방법:** WordPress 편집기 → 우측 Rank Math SEO 패널 → [Schema] 탭 클릭 → 글 유형에 맞는 Schema 선택 후 저장

| 글 유형 | 권장 Schema |
|---|---|
| 한국 여행·문화 가이드 | Article 또는 TouristAttraction |
| 카페·식당·장소 소개 | LocalBusiness |
| 음식·식재료 소개 | Article (또는 Recipe) |
| Q&A 포함 글 | Article + FAQ 섹션 추가 |
| 비교·순위 글 | Article |

---

## Phase 6: 완료 후 처리

**6-1. Notion 업데이트**

배포 완료 후 해당 Notion 페이지 기본 정보 표 업데이트:

- 상태: `배포완료 (Draft)`
- WordPress Post ID: [확인된 ID 입력]
- Rank Math 점수: [실제 점수]
- 배포일: [오늘 날짜]

⚠️ 메인 테이블의 **"draft 일자"는 SEO 설정까지 전부 성공했을 때만** 채운다. 중간에 실패했으면 공란으로 남겨야 다음 실행이 미완성 draft를 복구할 수 있다.

**6-2. 공개 전환 조건 (사용자 직접 확인 후 실행)**

- [ ] 내용 검토 완료
- [ ] 대표 이미지(Featured Image) 설정 완료
- [ ] 카테고리/태그 확인

> ⚠️ AI는 절대로 공개(Publish)를 직접 실행하지 않는다.

**6-3. 들어오는 내부 링크 (배포 시 자동 — STEP 6 성공 시 필수)**

주제가 인접한 **기존 발행 글 2개**에서 신규 글로 링크를 건다.

- **내부 링크를 이미 받고 있는 글을 우선** 고른다. 고아 글에서 걸면 효과가 없다.
- 후보 검색: `GET /wp-json/wp/v2/posts?search={키워드}&status=publish&_fields=id,slug,title`
- `Related reading` 섹션이 있으면 그 마지막 `</ul>` 직전에 `<li>` 를 추가한다. 삽입 전 `lastIndexOf('Related reading') < lastIndexOf('<ul')` 로 엉뚱한 리스트를 피한다.
- **섹션이 없으면 신설한다** (현행 글 대부분이 이 상태). `<!-- FOOTER CTA -->` 바로 앞에 삽입:

```html
  <!-- RELATED READING -->
  <h3 style="font-size:1.15rem;font-weight:700;margin:32px 0 10px;color:#1a1a1a;">Related reading</h3>
  <ul style="margin:0 0 24px;padding-left:20px;">
    <li><a href="/{신규슬러그}/">{신규 SEO_TITLE}</a></li>
  </ul>
```

- `<ul>/<li>` 여닫이 개수를 검증하고 저장한 뒤, 재조회로 링크가 들어갔는지 확인한다.
- ⚠️ **슬러그 실재 확인**: koreaplug.com은 존재하지 않는 슬러그에도 HTTP 200 + "Page Not Found"(소프트404)를 반환한다. 상태코드로 판단하지 말고 **REST 조회 결과(id 존재)** 로 확인한다.

**6-4. 배포 후 수동 링크 빌딩**

- Reddit: r/korea, r/koreatravel — 정보성 포스팅에 링크 자연 삽입
- Quora: `site:quora.com "korea [주제 키워드]"` 검색 후 답변 말미에 참고 출처로 링크
- 목표: 첫 2주 내 Reddit 1~2개, Quora 2~3개

**6-5. 프론트엔드 최종 검증 (완료 보고 전 필수)**

`/?p={WP_POST_ID}&preview=true` 에서 한 번에 확인한다:

```javascript
JSON.stringify({
  imgs: [...document.querySelectorAll('img')].map(i => i.naturalWidth),
  wrapper: Math.round(document.querySelector('[id$="-report"]')?.getBoundingClientRect().width),
  h2: document.querySelectorAll('h2').length,
  internalLinks: [...document.querySelectorAll('a[href^="/"]')].map(a => a.getAttribute('href'))
})
```

기준: 모든 이미지 `naturalWidth > 0` / 래퍼 폭 820 / H2 존재 / 내부 링크 2개 이상. 미달 항목은 완료 로그에 기록한다.

---

## 🔧 자주 발생하는 오류 & 해결법

| 오류 | 원인 | 해결법 |
|---|---|---|
| Rank Math 점수 60~74 | `core/code` 블록 사용 | `core/freeform` 블록으로 교체 |
| **SEO 설정이 새로고침 후 사라짐** | `wp.data.dispatch('rank-math')` 또는 REST `meta` 사용 | **둘 다 저장되지 않는다.** 사이드바 UI 직접 입력만 유효 (5-3 참조) |
| 키워드가 이어붙어 입력됨 | Enter 후 입력창에 잔여 텍스트가 남음 | 각 키워드 입력 전 **triple_click** 으로 잔여 텍스트 선택 후 타이핑 |
| 키워드 입력 중 기존 태그 소실 | 태그가 늘며 밀린 좌표에 triple_click | 1개 입력 → `getKeywords()` 검증 → 스크린샷으로 위치 재확인 반복 |
| 스니펫 필드 앞에 글자 1개 남음 | Ctrl+A 후 타이핑 시 첫 글자 잔존 | 필드 클릭 → Ctrl+Home → Delete |
| SEO 타이틀 580px 초과 | Notion SEO_TITLE이 60자 초과 | 관사·수식어 1개 제거해 57자 내외로 축소 (글 제목은 원문 유지) |
| 내부 링크 외부 인식 | 절대경로 `https://koreaplug.com/` 사용 | `/slug/` 상대경로로 변경 |
| TOC 인식 안 됨 (79점) | `hasTOCPlugin = false` | `window.rankMath.assessor.hasTOCPlugin = true` 강제 설정 |
| **TOC 블록 `isValid:false`** | 블록 마커를 손으로 작성 | `wp.blocks.createBlock('rank-math/toc-block')` 로 재생성 (5-2 하단) |
| TOC 프론트엔드 미표시 | rank-math/toc-block 렌더링 실패 | `core/html` 블록으로 수동 목차 삽입 |
| Keyword 밀도 경고 | 2.2% 초과 | 본문에서 Focus Keyword 2~3회 삭제 |
| `await` 오류 | Console에서 직접 실행 | `.then()` 콜백으로 변환 |
| 이미지가 820px 초과 | alignwide 블록 또는 wp:image 마커 | plain `<figure><img>` HTML로 교체 |
| 모바일 텍스트 화면 끝에 붙음 | 래퍼 horizontal padding 없음 | `padding:0 16px 40px; box-sizing:border-box;` 수정 |
| **Astra 설정 미반영** | 사이드바 클릭 누락 | REST `meta` 로 지정 후 **새로고침해서 재검증**. Astra meta는 `show_in_rest` 등록돼 있어 이 방식이 유효하다(Rank Math와 반대) |
| CTR 0% (1페이지인데 클릭 없음) | 직역체·설명형 제목 | 미국인 실제 검색어 + 호기심 후크로 재작성 (Phase 2-2 참조) |
| 제목 배경 이미지 흰색 | WP Customizer ::before 오버레이 | `외모 > 사용자 정의하기 > 추가 CSS`에서 `::before background`를 `rgba(0,0,0,0.35)`로 변경 |
| 관문 불통과 | 5-4 ①②③ 중 미충족 | 반려 로그 행 추가 + draft 일자 공란 + 다음 글로 진행 |
| 조항이 지침서에 안 보임 | 캐시된 구버전 또는 진짜 결번 | 5-0-A 3단 검증 → 찾으면 그 기준 사용(상충 아님), 결번 확정 시 5-0-B로 조항 신설 후 계속 진행 |
| 지침서 개정 이력이 루틴이 아는 버전보다 낮음 | 중간 캐시가 옛 사본 반환 | `?cb={epoch_ms}` 새로 붙여 재조회 + 브라우저 재확인. 캐시로 확인되면 상충 보고 금지 |

---

## Phase 7: 카테고리 매핑 (Cowork 참조용)

| 카테고리 | 이모지 | Notion Page ID | WP Category ID |
|---|---|---|---|
| Food & Drink | 🍜 | `33ebfe4a2ae18136b1a9df45458cb1be` | 3 |
| Korean Culture | 🎭 | `33ebfe4a2ae1815ba5e1d58b1bf9a44c` | 4 |
| Travel & Transport | 🚌 | `34fbfe4a2ae18031b3fbcc874496498e` | 5 |
| Lifestyle & Living | 🏠 | `33ebfe4a2ae18133a438ed9274c1dfb1` | 18 |
