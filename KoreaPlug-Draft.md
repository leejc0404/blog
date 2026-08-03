# 📋 KoreaPlug Draft 지침 (Cowork wordpress_draft용)

## 📌 이 문서의 용도

`wordpress_draft` (Cowork 예정됨 루틴)이 WP 배포·SEO 보정 시 참조하는 **배포 전용 지침**입니다.

- **포함**: 5-2(TOC 강제 스크립트) → 5-3(블록 구조·820px·키워드 입력 체크) → **5-4(⛔ 발행 차단 관문)** → **5-4B(캡처 품질·마크업 규칙)** → 5-4C(피드백 체크리스트) → 5-5(Schema) → Phase 6(완료 처리) → 오류표 → Phase 7(카테고리 매핑)
- **번호 안내**: 번호는 ✏️ Writer 지침의 Phase 체계를 이어받은 것. Phase 0~5-1은 Writer 지침 담당이라 이 문서에 없음(의도된 결번, 오타 아님). ⚠️ Writer 지침의 '5-3(Focus Keyword 배치 자가검수)'과 이 문서의 '5-3(블록 구조·820px 체크)'은 **서로 다른 문서의 별개 항목**임에 주의.
- **v10.2 변경(정리)**: 舊 Phase 4(배포 JS) 삭제에 따른 잔존 참조 수정('Phase 4 스크립트 실행 후' → 'freeform 블록 삽입 후'). Writer v10.5 홀짝 트랙제 도입과 무관하게 이 문서의 절차는 동일 — 기본 정보 표의 Track 행(S/L)은 Draft 루틴이 계속 무시한다.
- **v10.23 변경(2026-08-03, 이번 개정)**: **⛔ 발행 차단 관문을 정식 조항(5-4)으로 신설**하고, 기존 피드백 체크리스트는 5-4C로 이동. 그동안 루틴 파일에만 존재해 지침서와 3일 연속 상충하던 관문·캡처 규칙을 이 문서(SSOT)로 승격했다. 이제 루틴은 판정 기준을 이 문서에서만 읽는다.

---

## 5-2. TOC 인식 강제 및 재분석 트리거 스크립트

**freeform 블록 삽입 후**(舊 Phase 4 — 현재는 wordpress_draft 루틴 STEP 6이 수행), 아래 스크립트를 이어서 실행한다:

```javascript
const { dispatch, select } = wp.data;
if (window.rankMath && window.rankMath.assessor) {
  window.rankMath.assessor.hasTOCPlugin = true;
  console.log('hasTOCPlugin = true 강제 설정');
} else {
  console.warn('rankMath.assessor 없음 — 잠시 후 다시 시도');
}
const blocks = select('core/editor').getBlocks();
const freeformBlock = blocks.find(b => b.name === 'core/freeform');
if (freeformBlock) {
  const originalContent = freeformBlock.attributes.content;
  dispatch('core/editor').updateBlockAttributes(freeformBlock.clientId, { content: originalContent + ' ' });
  setTimeout(() => {
    dispatch('core/editor').updateBlockAttributes(freeformBlock.clientId, { content: originalContent });
    console.log('재분석 트리거 완료 → Rank Math 패널에서 점수 확인');
  }, 800);
} else {
  console.error('freeform 블록을 찾을 수 없음');
}
setTimeout(() => {
  wp.data.dispatch('core/editor').savePost().then(() => {
    console.log('임시저장 완료');
  });
}, 2000);
```

---

## 5-3. SEO 블록 구조 / 820px 무결성 체크 (Astra 보정)

**🟢 추가 SEO (블록 구조)**

- [ ] `rank-math/toc-block` 블록 존재 (1번 블록)
- [ ] `core/freeform` 블록으로 HTML 삽입 (2번 블록)
- [ ] `hasTOCPlugin = true` 강제 설정 완료
- [ ] 재분석 트리거 실행 완료

**🟢 820px 컨테이너 무결성**

- [ ] 모든 콘텐츠가 `max-width:820px; padding:0 16px 40px; box-sizing:border-box;` 래퍼 안에 위치하는가?
- [ ] HTML 내 이미지가 plain `<figure>/<img>` 태그로 삽입되었으며 `<!-- wp:image -->` 마커가 없는가?
- [ ] freeform 블록 외부에 별도 Gutenberg 이미지 블록(`alignwide`)이 추가되지 않았는가?
- [ ] 외부 래퍼 div의 horizontal padding이 `0 16px` 이상으로 설정되어 모바일에서 텍스트가 화면 끝에 붙지 않는가?

**🟢 키워드 입력 (v10.4 추가 — 누락 금지)**

- [ ] Rank Math 포커스 키워드 필드에 Notion 기본 정보 표의 **Focus Keyword + Sub Keywords 전부**를 입력했는가? (Focus가 첫 번째, 총 5개 권장)

> ⚠️ **v10.23 정정 — 입력 방식**: `wp.data.dispatch('rank-math').updateKeywords(...)` 방식은 **에러 없이 성공한 것처럼 보이지만 postmeta에 저장되지 않는다**(2026-07-24 danggeun-market-korea 실측: dispatch 후 Ctrl+S까지 했는데 새로고침하면 빈 값). **JS dispatch는 사용 금지**하고, Rank Math 패널의 포커스 키워드 입력창에 **UI로 직접 타이핑 → Enter**를 항목 수만큼 반복한다.

- [ ] **저장 후 새로고침 검증**: 편집 URL로 다시 navigate → Rank Math 패널을 열어 키워드 칩이 실제로 남아 있는가? (`wp.data.select('rank-math').getKeywords()` 결과에 쉼표 항목이 2개 이상) 새로고침 후 비어 있으면 저장 미반영이므로 재입력. 재시도 후에도 비면 오류 로그에 "SEO 설정 미반영" 명시 — "완료"로 보고 금지.

> 배경: 2026-07-09 점검에서 Draft 루틴이 Focus만 입력하고 Writer가 Notion 표에 기록한 Sub Keywords를 버리는 문제 확인. 사용자가 매번 수동으로 채워오고 있었음 — 반드시 그대로 복사할 것.

**🟢 최종 확인**

- [ ] Rank Math 패널 점수: **78/100 이상**
- [ ] 임시저장(Draft) 상태 확인
- [ ] Notion 페이지 점수 업데이트

---

## 5-4. ⛔ 발행 차단 관문 (Publication Gate) — v10.23 신설

> **이건 체크리스트가 아니라 업로드 전제 조건이다.** SEO 점수가 90점이어도 관문을 통과하지 못한 글은 WordPress에 올리지 않는다. 반대로 관문만 통과하면 SEO 점수는 보정으로 끌어올릴 수 있다.
>
> **왜 이걸 두는가**: 우리 글의 유일한 방어선은 "1페이지 경쟁글이 갖고 있지 않은 것"이다. 문법 설명·공식 안내 재정리는 누구나 30분이면 쓴다. 우리가 이기는 지점은 *직접 조회해서 세어본 숫자*, *직접 찍은 화면*, *직접 확인한 예외*다. 관문은 그 자산이 실제로 글 안에 들어갔는지를 업로드 직전에 한 번 더 강제하는 장치다.

**판정 대상**: Notion 서브페이지의 HTML 전문 + 기본 정보 표
**판정 시점**: WordPress 업로드(POST) **직전**. 통과 전에는 업로드를 시작하지 않는다.

### ① 원본자료 (Primary Source)

1급 원본 자료가 **본문에 최소 1개** 들어가 있어야 한다.

**1급으로 인정되는 것**

- 직접 조작한 공개 화면의 캡처 (조회 조건을 입력하고 얻은 결과 화면, 법령 조문 화면, 통계 조회·정렬 결과, 공식 계산기 입력 결과)
- 직접 센 수치 (예: 공개 연설문 4건 81문장의 종결어미 전수 카운트 98.8%)
- 실제 영수증·요금표·현장 사진 등 1차 기록

**1급으로 인정되지 않는 것**

- 비교표·통합표·요약표만 있는 경우
- 공식 수치를 그대로 옮겨 적은 재정리
- 경쟁글에도 있는 일반 안내 문구
- AI가 생성한 일러스트·장식 이미지 (데코는 데코일 뿐 증빙이 아니다)

**「1급 자료 조달 계획: 루틴가능」이 명시된 경우**

기본 정보 표에 `1급 자료 조달 계획: 루틴가능 {화면·경로}`가 적혀 있으면, **캡처의 실행 주체는 Draft 루틴**이다. 브라우저를 가진 쪽이 루틴이기 때문이다. 절차:

1. 해당 공개 페이지(로그인 불필요)로 이동
2. 5-4B의 캡처 품질 규칙에 따라 필요한 영역만 캡처
3. WP 미디어에 업로드
4. 본문의 지정된 위치에 5-4B의 표준 마크업으로 삽입
5. 삽입 후 프론트엔드에서 실제로 렌더링되는지 1회 육안 확인

로그인·결제·개인정보 입력이 필요한 화면은 루틴이 캡처하지 않는다 → 그 항목은 조달 불가로 보고 다른 1급 자료로 대체하거나 반려 처리.

### ② 가짜경험 (No Fabricated Experience)

하지 않은 일을 1인칭으로 쓴 문장이 **0건**이어야 한다.

- 금지: 지어낸 개인 일화, 가본 적 없는 장소의 체험담, 실재하지 않는 지인·단톡방 인용 ("When I first…", "my group chat…", "my Korean friend told me…" 류)
- 허용: **실제로 수행한 작업**의 1인칭 서술. 예) "I pulled four official speech transcripts and counted every sentence ending" — 실제로 수집·카운트했고 그 근거 화면이 본문에 있으므로 통과.
- 판정 기준은 인칭이 아니라 **근거의 실재 여부**다. 1인칭 문장이 있으면 "이 문장을 뒷받침하는 자료가 본문 어딘가에 있는가"를 확인한다. 없으면 문장을 3인칭 사실 서술로 고치거나 삭제한다.

### ③ 이미지출처 (Image Provenance)

모든 `<img>`의 src가 아래 둘 중 하나여야 한다.

- `koreaplug.com` (자체 업로드)
- `images.unsplash.com` (CDN 직링, photo ID가 `^[0-9]{10,13}-[0-9a-f]{12}$` 형식)

타 사이트 핫링크(gstatic, pstatic, 언론사 이미지 서버 등) **0건**. Unsplash 공유링크의 짧은 슬러그 ID는 CDN에서 404가 나므로 사용 금지 — 정규식에 맞지 않는 ID는 폐기하고 검색 결과의 다른 이미지를 쓴다. URL을 교체했으면 실제로 로드되는지 1회 확인한다.

### 불통과 시 처리

①~③ 중 하나라도 불통과 → **업로드를 건너뛰고 draft 일자는 공란 유지**(다음 실행이 다시 후보로 집도록). 그리고 발행 반려 로그(https://www.notion.so/3adbfe4a2ae18167880ecbe3c73b90cc)에 행 1개를 추가한다.

```
| {TODAY} | {SLUG} | {사유 코드} | {무엇을} | {어디에} | {왜} | {어떻게} | {루틴 또는 사용자} | 대기 |
```

⚠️ **"1급 자료 없음"만 적는 보고는 무효다.** 다음 회차가 그 로그만 보고 바로 실행할 수 있어야 한다 — *무엇을* 찍어야 하는지, *어디에서*(URL·화면명), *왜* 그게 1급인지, *어떻게*(조회 조건·입력값), 그리고 *누가* 해야 하는지 5항목을 반드시 채운다. 같은 슬러그의 '대기' 행이 이미 있으면 중복 추가하지 않는다.

---

## 5-4B. 캡처 품질·마크업 규칙 (v10.23 승격)

> 배경: 2026-08-01 "캡처가 어색하다" 피드백. KOSIS 표 캡처는 깔끔했는데 국립국어원 조문 캡처는 사이트 헤더·스크롤바가 함께 잡혀 어색했다. 증빙 이미지는 **자료 카드**로 보여야지 스크린샷 덩어리로 보이면 신뢰도가 오히려 깎인다.

**🟢 캡처 규칙**

- 전체 화면·전체 페이지 캡처 **금지**. 결과·표·조문 영역만 region을 지정해 잘라 찍는다. 사이트 헤더·글로벌 메뉴·배너가 프레임에 들어가면 실패.
- 프레임에 **스크롤바·마우스 커서·드래그 핸들·쿠키 배너·팝업 잔재**가 보이면 재캡처. 우측 스크롤바는 region 우측 경계를 콘텐츠 폭 기준 약 20px 안쪽으로 잡아 배제한다.
- 표·조문처럼 사각형으로 떨어지는 콘텐츠는 그 사각형에 딱 맞춰 자른다. 문장 중간·행 중간에서 잘리거나 좌우 여백이 비대칭이면 재캡처.
- 조문류는 해당 조항 블록만(조 제목 줄 포함) 잡는다. 목록 화면은 **본문에서 언급한 항목이 전부 보이는 범위**까지 포함한다(예: 4건을 셌다면 그 4건이 한 프레임에 보여야 함).
- 캡처 후 반드시 이미지를 육안 확인한 뒤 업로드한다.

**🟢 파일명**

```
evidence-{SLUG}-{n}.webp
```

⚠️ Image 루틴이 **증빙**과 **생성 이미지**를 구분하는 근거다. 파일명 prefix와 아래 `class="evidence-capture"` 둘 다 반드시 지킨다.

**🟢 삽입 마크업 표준**

```html
<figure class="evidence-capture" style="margin:26px 0; border:1px solid #e2e8f0; border-radius:12px; padding:10px; background:#fafafa;">
  <img style="width:100%;display:block;height:auto;border-radius:8px;" src="{URL}" alt="{Focus Keyword 포함 설명}" />
  <figcaption style="font-size:13px; color:#64748b; margin-top:8px;">{출처 기관 — 화면명 · Captured YYYY-MM-DD}</figcaption>
</figure>
```

- `alt`에는 Focus Keyword를 자연스럽게 포함시킨다(SEO 체크 6번 항목과 연동).
- `figcaption`은 영문 독자 기준으로 쓴다. 예: `Korea.kr Policy Briefing — Speech archive list · Captured 2026-08-03`
- 삽입 위치는 **그 자료가 뒷받침하는 문단·표 바로 아래**. 글 맨 끝에 몰아넣지 않는다.

**🟢 삽입 후 확인**

- [ ] 프론트엔드 프리뷰에서 이미지가 실제로 로드되는가 (naturalWidth > 0)
- [ ] 820px 래퍼 안에 들어가 화면 밖으로 삐져나오지 않는가
- [ ] 캡션의 기관명·화면명·날짜가 실제 캡처 대상과 일치하는가

---

## 5-4C. 피드백 체크리스트 (기존 5-4)

- [ ] (Native Speech Check) 미국인 친구에게 자연스럽게 말할 수 있는가? → **Yes여야 함.**
- [ ] (Authenticity Check) 한국인이 읽었을 때 로컬 문화를 왜곡하지 않았는가? → **Yes여야 함.**
- [ ] (Curiosity Gap Check) 도입부 읽고 "왓? 진짜?" 호기심으로 스크롤을 내릴 수밖에 없는가? → **Yes여야 함.**
- [ ] (Zero-Translation Check) 관공서/사전식 한국어 직역 용어가 단 한 단어도 없는가? → **Yes여야 함.**
- [ ] 글이 한국으로 여행 오는 외국인에게 유용한 팁을 주는가?
- [ ] 제목에 클릭을 부르는 호기심 갭(질문/의외성)이 있는가?
- [ ] "미국인이 이 제목 문장을 구글에 그대로 칠까?"에 Yes라고 답할 수 있는가?

> 이 체크리스트는 **품질 권고**다. 불통과해도 배포는 막지 않되, 미달 항목을 Notion 로그에 남긴다. 배포를 막는 건 5-4 관문뿐이다.

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
- **1급 자료 캡처(실행 완료)**: 업로드한 evidence 파일명 + 삽입 위치 (v10.23 추가 — 다음 회차가 중복 캡처하지 않도록)

⚠️ **draft 일자 기록 시점**: 배포 전 과정(Astra 반영 + Rank Math 새로고침 재검증)이 성공했을 때만 기록한다. 중간에 실패했으면 공란으로 남겨야 다음 실행이 그 글을 다시 후보로 집어 미완성 draft 복구 로직을 태울 수 있다.

**6-2. 공개 전환 조건 (사용자 직접 확인 후 실행)**

- [ ] 내용 검토 완료
- [ ] 대표 이미지(Featured Image) 설정 완료
- [ ] 카테고리/태그 확인

> ⚠️ AI는 절대로 공개(Publish)를 직접 실행하지 않는다.

**6-3. 들어오는 내부 링크 (v10.19)**

발행 목록에서 이번 글과 주제가 인접한 기존 글 2개를 골라 신규 글 링크를 추가한다. **이미 내부 링크를 받고 있는 글을 우선**한다 — 고아 글에서 걸면 전달되는 신호가 없다. 저장 전 `<ul>`/`<li>` 여닫이 짝을 검증하고, 실패해도 발행 자체는 유지한다(반려 아님).

⚠️ **슬러그 실재 확인**: koreaplug.com은 존재하지 않는 슬러그에도 HTTP 200 + "Page Not Found"(소프트404)를 반환한다. 상태코드로 판단하지 말고 REST 조회 결과(id 존재) 또는 title 문자열로 확인한다.

**6-4. 배포 후 수동 링크 빌딩**

- Reddit: r/korea, r/koreatravel — 정보성 포스팅에 링크 자연 삽입
- Quora: `site:quora.com "korea [주제 키워드]"` 검색 후 답변 말미에 참고 출처로 링크
- 목표: 첫 2주 내 Reddit 1~2개, Quora 2~3개

---

## 🔧 자주 발생하는 오류 & 해결법

| 오류 | 원인 | 해결법 |
|---|---|---|
| Rank Math 점수 60~74 | `core/code` 블록 사용 | `core/freeform` 블록으로 교체 |
| SEO 설정이 새로고침 후 사라짐 | `wp.data.dispatch('rank-math')` JS 방식 | **JS dispatch 금지** — Rank Math 패널에 UI로 직접 입력 후 새로고침 재검증 |
| SEO 메타 설정 안 됨 | `editPost({ meta: {} })` 방식 | Rank Math 패널 UI 입력 (5-3 참조) |
| 스니펫 설명 앞에 잔여 문자 1개 | Ctrl+A 후 타이핑 시 첫 글자 잔존 | 필드 클릭 → Home → Delete로 제거 후 **스크린샷 육안 확인** |
| Astra 레이아웃 미반영 | 사이드바 클릭 누락 | REST로 postmeta 직접 지정 후 새로고침 검증 (`ast-site-content-layout` / `site-content-style` / `ast-banner-title-visibility`) |
| 내부 링크 외부 인식 | 절대경로 `https://koreaplug.com/` 사용 | `/slug/` 상대경로로 변경 |
| TOC 인식 안 됨 (79점) | `hasTOCPlugin = false` | `window.rankMath.assessor.hasTOCPlugin = true` 강제 설정 |
| TOC 프론트엔드 미표시 | rank-math/toc-block 렌더링 실패 | `core/html` 블록으로 수동 목차 삽입 |
| Keyword 밀도 경고 | 2.2% 초과 | 본문에서 Focus Keyword 2~3회 삭제 |
| 이미지가 820px 초과 | alignwide 블록 또는 wp:image 마커 | plain `<figure><img>` HTML로 교체 |
| 모바일 텍스트 화면 끝에 붙음 | 래퍼 horizontal padding 없음 | `padding:0 16px 40px; box-sizing:border-box;` 수정 |
| 캡처에 헤더·스크롤바가 같이 찍힘 | 전체 화면 캡처 | 5-4B 규칙대로 region 지정 후 재캡처 |
| 증빙 이미지가 데코처럼 보임 | figure 마크업 누락 | `class="evidence-capture"` + figcaption 표준 마크업 적용 |
| 내부 링크 슬러그 불일치 | Writer 단계에서 미검증 | 소프트404 주의 — REST 조회 또는 title 문자열로 실재 확인 |
| CTR 0% (1페이지인데 클릭 없음) | 직역체·설명형 제목 | 미국인 실제 검색어 + 호기심 후크로 재작성 |
| 제목 배경 이미지 흰색 | WP Customizer ::before 오버레이 | `외모 > 사용자 정의하기 > 추가 CSS`에서 `::before background`를 `rgba(0,0,0,0.35)`로 변경 |

---

## Phase 7: 카테고리 매핑 (Cowork 참조용)

| 카테고리 | 이모지 | Notion Page ID | WP Category ID |
|---|---|---|---|
| Food & Drink | 🍜 | `33ebfe4a2ae18136b1a9df45458cb1be` | 3 |
| Korean Culture | 🎭 | `33ebfe4a2ae1815ba5e1d58b1bf9a44c` | 4 |
| Travel & Transport | 🚌 | `34fbfe4a2ae18031b3fbcc874496498e` | 5 |
| Lifestyle & Living | 🏠 | `33ebfe4a2ae18133a438ed9274c1dfb1` | 18 |
