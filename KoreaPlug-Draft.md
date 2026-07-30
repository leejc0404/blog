# 📋 KoreaPlug Draft 지침 (Cowork wordpress_draft용)

## 📌 이 문서의 용도

`wordpress_draft` (Cowork 예정됨 루틴)이 WP 배포·SEO 보정 시 참조하는 **배포 전용 지침**입니다.

- **포함**: 5-2(TOC 강제 스크립트) → 5-3(블록 구조·820px·키워드 입력 체크) → 5-4(피드백) → 5-5(Schema) → Phase 6(완료 처리) → 오류표 → Phase 7(카테고리 매핑)
- **번호 안내**: 번호는 ✏️ Writer 지침의 Phase 체계를 이어받은 것. Phase 0~5-1은 Writer 지침 담당이라 이 문서에 없음(의도된 결번, 오타 아님). ⚠️ Writer 지침의 '5-3(Focus Keyword 배치 자가검수)'과 이 문서의 '5-3(블록 구조·820px 체크)'은 **서로 다른 문서의 별개 항목**임에 주의.
- **v10.2 변경(정리)**: 舊 Phase 4(배포 JS) 삭제에 따른 잔존 참조 수정('Phase 4 스크립트 실행 후' → 'freeform 블록 삽입 후'). Writer v10.5 홀짝 트랙제 도입과 무관하게 이 문서의 절차는 동일 — 기본 정보 표의 Track 행(S/L)은 Draft 루틴이 계속 무시한다.

---

## 5-2. TOC 인식 강제 및 재분석 트리거 스크립트

**freeform 블록 삽입 후**(舊 Phase 4 — 현재는 wordpress_draft 루틴 STEP 6d가 수행), 아래 스크립트를 이어서 실행한다:

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
  console.error('❌ freeform 블록을 찾을 수 없음 — Phase 4 먼저 실행');
}
setTimeout(() => {
  wp.data.dispatch('core/editor').savePost().then(() => {
    console.log('✅ 임시저장 완료');
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

- [ ] Rank Math 포커스 키워드 필드에 Notion 기본 정보 표의 **Focus Keyword + Sub Keywords 전부**를 쉼표로 연결해 입력했는가? (Focus가 첫 번째, 총 5개 권장)

```javascript
// 예: Notion 표의 Sub Keywords "A / B / C / D"를 그대로 복사해 쉼표 연결
wp.data.dispatch('rank-math').updateKeywords('korea business registration,korea business registration for foreigners,how to register a business in korea,hometax business registration');
```

- [ ] 저장 후 검증: `wp.data.select('rank-math').getKeywords()` 결과에 쉼표 항목이 2개 이상인가? (1개뿐이면 Sub Keywords 누락 — 재입력)

> 배경: 2026-07-09 점검에서 Draft 루틴이 Focus만 입력하고 Writer가 Notion 표에 기록한 Sub Keywords를 버리는 문제 확인. 사용자가 매번 수동으로 채워오고 있었음 — 반드시 그대로 복사할 것.

**🟢 최종 확인**

- [ ] Rank Math 패널 점수: **78/100 이상**
- [ ] 임시저장(Draft) 상태 확인
- [ ] Notion 페이지 점수 업데이트

---

## 5-4. 피드백 체크리스트

> ⛔ **(v10.17 신설) 발행 차단 관문 — 아래 2개는 하나라도 No면 워드프레스 업로드를 중단하고 Writer 단계로 반려한다.** 나머지 항목보다 우선 판정한다.

- [ ] **(Originality Gate — v10.18)** 이 글에 **1급 원본 자료**가 최소 1개 있는가? 판정 질문: "검색만 할 줄 아는 사람이 30분 안에 이 자료를 똑같이 만들 수 있는가?" → **예이면 No.** 1급 = 직접 측정한 시간·비용, 실제 견적·영수증, 직접 방문 확인(날짜 명기), 직접 촬영 사진, 직접 조작한 화면 캡처, 직접 돌린 테스트 결과. 비교표·통합표·계산 예시는 2급이라 **단독으로는 통과 불가** → No면 업로드 중단
- [ ] **(Fabricated Experience Gate)** 실제로 하지 않은 일을 1인칭(I, My)으로 서술한 문장이 **한 개도 없는가?** — "When I first…", "my group chat…", 지어낸 개인 이력·일화 전부 해당. → No면 해당 문장을 3인칭/2인칭으로 고치기 전까지 업로드 중단

- [ ] **(이미지 출처 관문 — v10.20)** 본문 이미지가 전부 **자체 업로드 파일 또는 라이선스 소스(Unsplash 등)**인가? `gstatic.com`·`pstatic.net`·`phinf.naver.net` 등 타 사이트 핫링크가 **한 건도 없는가?** → No면 해당 이미지를 제거하거나 직접 촬영본으로 교체하기 전까지 업로드 중단
- [ ] **(들어오는 링크 관문 — v10.19)** 이 글을 가리키는 내부 링크를 **기존 글 2개에 추가했는가?** 출처는 주제가 인접하면서 이미 내부 링크를 받고 있는 글로 고른다(고아 글에서 걸면 무효). → No면 링크를 추가한 뒤 완료 처리한다

> 📋 **(v10.21 신설) 관문 불통과 시 리포트 형식 — 아래 4개를 반드시 채워서 사용자에게 알린다.** "1급 자료 없음"만 적는 보고는 무효 처리한다. 사용자가 무엇을·어디에·왜 넣어야 하는지 모르면 그 글은 그대로 방치되고, 자동화가 멈춘 것과 같아진다.
>
> 1. **무엇을** — 필요한 1급 자료를 구체적으로 지목한다. (예: "홈택스 → 연말정산 미리보기 → 신용카드 소득공제 계산 결과 화면 캡처")
> 2. **어디에** — 삽입 위치를 H2 섹션 이름으로 지정한다. (예: "3장 '카드 사용액 황금 비율' 문단 바로 아래")
> 3. **왜** — 그 자료가 본문의 어떤 주장을 뒷받침하는지 한 줄로 쓴다. (예: "체크카드 전환 시점 주장에 현재 근거가 없음")
> 4. **어떻게** — 사용자가 직접 구하는 최단 경로를 사이트·메뉴·앱 이름까지 적는다. 촬영이 필요하면 무엇을 찍어야 하는지 명시한다.
>
> ⚠️ **1급 자료는 이미지에 한정되지 않는다.** 직접 측정한 소요 시간, 실제 지불한 금액, 실제로 받은 조건처럼 **본문 텍스트로 들어가는 것도 1급**이다. 이미지가 꼭 필요한 경우에만 이미지를 요구하고, 텍스트로 충분하면 텍스트로 요청한다.

> 🚧 **(v10.22) 반려 시 로그 기록 — 보고만 하고 끝내지 않는다.** 위 관문에 걸려 업로드를 중단했으면, 발행 반려 로그(https://www.notion.so/3adbfe4a2ae18167880ecbe3c73b90cc)의 표에 **행 1개를 반드시 추가한다.** 날짜 / 슬러그 / 사유 코드(`원본자료없음`·`가짜경험`·`이미지출처`·`들어오는링크`) / 무엇을 / 어디에 / 왜 / 어떻게 / 조달 주체(`루틴`·`사용자`) / 상태(`대기`)를 채운다.
>
> 이 기록이 없으면 writer는 다음 날에도 같은 방식으로 글을 쓰고, Draft는 같은 사유로 다시 반려한다. **두 단계는 서로 다른 실행이라 로그를 거치지 않으면 피드백이 전달되지 않는다.** 기록은 보고의 부속이 아니라 관문 처리의 일부다.

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

**6-2. 공개 전환 조건 (사용자 직접 확인 후 실행)**

- [ ] 내용 검토 완료
- [ ] 대표 이미지(Featured Image) 설정 완료
- [ ] 카테고리/태그 확인

> ⚠️ AI는 절대로 공개(Publish)를 직접 실행하지 않는다.

**6-3. 배포 후 수동 링크 빌딩**

- Reddit: r/korea, r/koreatravel — 정보성 포스팅에 링크 자연 삽입
- Quora: `site:quora.com "korea [주제 키워드]"` 검색 후 답변 말미에 참고 출처로 링크
- 목표: 첫 2주 내 Reddit 1~2개, Quora 2~3개

---

## 🔧 자주 발생하는 오류 & 해결법

| 오류 | 원인 | 해결법 |
|---|---|---|
| Rank Math 점수 60~74 | `core/code` 블록 사용 | `core/freeform` 블록으로 교체 |
| SEO 메타 설정 안 됨 | `editPost({ meta: {} })` 방식 | `wp.data.dispatch('rank-math')` 직접 사용 |
| 내부 링크 외부 인식 | 절대경로 `https://koreaplug.com/` 사용 | `/slug/` 상대경로로 변경 |
| TOC 인식 안 됨 (79점) | `hasTOCPlugin = false` | `window.rankMath.assessor.hasTOCPlugin = true` 강제 설정 |
| TOC 프론트엔드 미표시 | rank-math/toc-block 렌더링 실패 | `core/html` 블록으로 수동 목차 삽입 |
| Keyword 밀도 경고 | 2.2% 초과 | 본문에서 Focus Keyword 2~3회 삭제 |
| `await` 오류 | Console에서 직접 실행 | `.then()` 콜백으로 변환 |
| 이미지가 820px 초과 | alignwide 블록 또는 wp:image 마커 | plain `<figure><img>` HTML로 교체 |
| 모바일 텍스트 화면 끝에 붙음 | 래퍼 horizontal padding 없음 | `padding:0 16px 40px; box-sizing:border-box;` 수정 |
| CTR 0% (1페이지인데 클릭 없음) | 직역체·설명형 제목 | 미국인 실제 검색어 + 호기심 후크로 재작성 (Phase 2-2 참조) |
| 제목 배경 이미지 흰색 | WP Customizer ::before 오버레이 | `외모 > 사용자 정의하기 > 추가 CSS`에서 `::before background`를 `rgba(0,0,0,0.35)`로 변경 |

---

## Phase 7: 카테고리 매핑 (Cowork 참조용)

| 카테고리 | 이모지 | Notion Page ID | WP Category ID |
|---|---|---|---|
| Food & Drink | 🍜 | `33ebfe4a2ae18136b1a9df45458cb1be` | 3 |
| Korean Culture | 🎭 | `33ebfe4a2ae1815ba5e1d58b1bf9a44c` | 4 |
| Travel & Transport | 🚌 | `34fbfe4a2ae18031b3fbcc874496498e` | 5 |
| Lifestyle & Living | 🏠 | `33ebfe4a2ae18133a438ed9274c1dfb1` | 18 |
