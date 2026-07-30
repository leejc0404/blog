# 📋 0and1Life Draft 지침 (Cowork 0and1life-wordpress-draft용)

## 이 문서의 용도

`0and1life-wordpress-draft` (Cowork 예정됨)이 SEO 점수 미달 시 참조하는 **보정 전용 지침**입니다.

- **포함**: Phase 5-2 TOC 스크립트, 5-3 블록구조/820px 체크, 5-4 피드백, Phase 6 완료 처리, 오류표
- **제외**: Phase 1~4, 5-1, 콘텐츠 작성 규칙 → ✏️ 0and1Life Writer 지침 참조
- **번호 안내**: 번호는 Writer 지침의 Phase 체계를 이어받은 것 — Phase 0~5-1은 Writer 담당이라 이 문서에 없음(의도된 결번, 오타 아님). ⚠️ Writer 지침의 'Phase 5-3(SEO 콘텐츠 품질 자가검수)'과 이 문서의 'Phase 5-3(블록 구조·820px 체크)'은 **서로 다른 문서의 별개 항목**임에 주의.
- **v1.3 변경(정리)**: 舊 Phase 4(배포 JS) 삭제에 따른 잔존 참조 수정('Phase 4 스크립트 실행 후' → 'freeform 블록 삽입 후'). Writer v1.5 홀짝 트랙제 도입과 무관하게 이 문서 절차는 동일 — 기본 정보 표의 Track 행(S/L)은 Draft 루틴이 무시한다.

---

## Phase 5-2. TOC 인식 강제 및 재분석 트리거 스크립트

**freeform 블록 삽입 후**(舊 Phase 4 — 현재는 0and1life-wordpress-draft 루틴 STEP 6c-1이 수행), 아래 스크립트를 이어서 실행한다:

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
  const orig = freeformBlock.attributes.content;
  dispatch('core/editor').updateBlockAttributes(freeformBlock.clientId, { content: orig + ' ' });
  setTimeout(() => {
    dispatch('core/editor').updateBlockAttributes(freeformBlock.clientId, { content: orig });
    console.log('✅ 재분석 트리거 완료 → Rank Math 패널에서 점수 확인 (목표: 81/100)');
  }, 800);
} else {
  console.error('❌ freeform 블록 없음 — Phase 4 먼저 실행');
}

setTimeout(() => {
  wp.data.dispatch('core/editor').savePost().then(() => console.log('✅ 임시저장 완료'));
}, 2000);
```

---

## Phase 5-3. 블록 구조 / 820px 무결성 체크 (Cowork 보정용)

**🟢 추가 SEO (블록 구조)**

- [ ] `rank-math/toc-block` 블록 존재 (1번 블록)
- [ ] `core/freeform` 블록으로 HTML 삽입 (2번 블록)
- [ ] `hasTOCPlugin = true` 강제 설정 완료
- [ ] 재분석 트리거 실행 완료

**🟢 820px 컨테이너 무결성**

- [ ] 모든 콘텐츠가 `max-width:820px; padding:0 16px 40px; box-sizing:border-box;` 래퍼 안에 위치하는가?
- [ ] HTML 내 이미지가 plain `<figure>/<img>` 태그로 삽입, `<!-- wp:image -->` 마커 없는가?
- [ ] freeform 블록 외부에 별도 Gutenberg 이미지 블록(`alignwide`) 없는가?
- [ ] 래퍼 div의 horizontal padding이 `0 16px` 이상인가?

**🟢 키워드 입력 (v1.3 추가 — 누락 금지)**

- [ ] Rank Math 포커스 키워드 필드에 Notion 기본 정보 표의 **Focus Keyword + Sub Keywords 전부**를 쉼표로 연결해 입력했는가? (Focus가 첫 번째, 총 5개 권장)

```javascript
// 예: Notion 표의 Sub Keywords "A / B / C"를 그대로 복사해 쉼표 연결
wp.data.dispatch('rank-math').updateKeywords('AI 여행 계획,AI 여행 계획 앱,AI 여행 계획 추천,AI 여행 계획 무료');
```

- [ ] 저장 후 검증: `wp.data.select('rank-math').getKeywords()` 결과에 쉼표 항목이 2개 이상인가? (1개뿐이면 Sub Keywords 누락 — 재입력)

> 배경: 2026-07-09 점검에서 Draft 루틴이 Focus만 입력하고 Writer가 Notion 표에 기록한 Sub Keywords를 버리는 문제 확인 (Blog #52 사례). 사용자가 매번 수동으로 채워오고 있었음 — 반드시 그대로 복사할 것.

**🟢 최종 확인**

- [ ] Rank Math 점수: **81/100**
- [ ] 임시저장(Draft) 상태 확인
- [ ] Notion 페이지 점수 업데이트

---

## Phase 5-4. 피드백 체크리스트

> ⛔ **(v1.21 신설) 발행 차단 관문 — 아래 2개는 하나라도 No면 워드프레스 업로드를 중단하고 Writer 단계로 반려한다.** 나머지 항목보다 우선 판정한다.

- [ ] **(원본 자료 관문 — v1.22)** 이 글에 **1급 원본 자료**가 최소 1개 있는가? 판정 질문: "검색만 할 줄 아는 사람이 30분 안에 이 자료를 똑같이 만들 수 있는가?" → **예이면 No.** 1급 = 직접 받은 견적·고지서·수수료 명세, 직접 측정한 시간·금액, 직접 조작한 화면 캡처(마스킹), 직접 방문 확인(날짜 명기), 직접 촬영 사진. 계산표·통합표·공식 수치 재정리는 2급이라 **단독으로는 통과 불가** → No면 업로드 중단
- [ ] **(가짜 경험 관문)** 실제로 하지 않은 일을 1인칭(저/제가)으로 서술했거나, 지어낸 개인 이력(나이·연차·직군·결혼 준비 등)을 사실처럼 쓴 문장이 **한 개도 없는가?** → No면 해당 문장을 고치기 전까지 업로드 중단

- [ ] **(이미지 출처 관문 — v1.24)** 본문 이미지가 전부 **자체 업로드 파일 또는 라이선스 소스(Unsplash 등)**인가? `gstatic.com`·`pstatic.net`·`phinf.naver.net` 등 타 사이트 핫링크가 **한 건도 없는가?** → No면 해당 이미지를 제거하거나 직접 촬영본으로 교체하기 전까지 업로드 중단
- [ ] **(들어오는 링크 관문 — v1.23)** 이 글을 가리키는 내부 링크를 **기존 글 2개에 추가했는가?** 출처는 주제가 인접하면서 이미 내부 링크를 받고 있는 글로 고른다(고아 글에서 걸면 무효). → No면 링크를 추가한 뒤 완료 처리한다

> 📋 **(v1.25 신설) 관문 불통과 시 리포트 형식 — 아래 4개를 반드시 채워서 사용자에게 알린다.** "1급 자료 없음"만 적는 보고는 무효 처리한다. 사용자가 무엇을·어디에·왜 넣어야 하는지 모르면 그 글은 그대로 방치되고, 자동화가 멈춘 것과 같아진다.
>
> 1. **무엇을** — 필요한 1급 자료를 구체적으로 지목한다. (예: "홈택스 → 연말정산 미리보기 → 신용카드 소득공제 계산 결과 화면 캡처")
> 2. **어디에** — 삽입 위치를 H2 섹션 이름으로 지정한다. (예: "3장 '카드 사용액 황금 비율' 문단 바로 아래")
> 3. **왜** — 그 자료가 본문의 어떤 주장을 뒷받침하는지 한 줄로 쓴다. (예: "체크카드 전환 시점 주장에 현재 근거가 없음")
> 4. **어떻게** — 사용자가 직접 구하는 최단 경로를 사이트·메뉴·앱 이름까지 적는다. 촬영이 필요하면 무엇을 찍어야 하는지 명시한다.
>
> ⚠️ **1급 자료는 이미지에 한정되지 않는다.** 직접 측정한 소요 시간, 실제 지불한 금액, 실제로 받은 조건처럼 **본문 텍스트로 들어가는 것도 1급**이다. 이미지가 꼭 필요한 경우에만 이미지를 요구하고, 텍스트로 충분하면 텍스트로 요청한다.

> 🚧 **(v1.26) 반려 시 로그 기록 — 보고만 하고 끝내지 않는다.** 위 관문에 걸려 업로드를 중단했으면, 발행 반려 로그(https://www.notion.so/3adbfe4a2ae1817994f0f901de5c8dec)의 표에 **행 1개를 반드시 추가한다.** 날짜 / 슬러그 / 사유 코드(`원본자료없음`·`가짜경험`·`이미지출처`·`들어오는링크`) / 무엇을 / 어디에 / 왜 / 어떻게 / 조달 주체(`루틴`·`사용자`) / 상태(`대기`)를 채운다.
>
> 이 기록이 없으면 writer는 다음 날에도 같은 방식으로 글을 쓰고, Draft는 같은 사유로 다시 반려한다. **두 단계는 서로 다른 실행이라 로그를 거치지 않으면 피드백이 전달되지 않는다.** 기록은 보고의 부속이 아니라 관문 처리의 일부다.

- [ ] (공감 검증) 한국 직장인/부업러가 처음 3초에 "나 이거 해당되는데" 반응이 나오는가? → Yes여야 함.
- [ ] (지식 검증) 직접 써보거나 검증된 정보만 담겼는가? → Yes여야 함.
- [ ] (제목 검증) 제목만 보고 답이 금방 보이지 않고 "어떻게?", "진짜?" 궁금한가? → Yes여야 함.
- [ ] (슬러그 검증) 슬러그가 영어로만 작성되었는가? → Yes여야 함.
- [ ] (실용성) 바로 따라할 수 있는 구체적 팁이 3개 이상 있는가? → Yes여야 함.

---

## Phase 6. 완료 후 처리

**6-1. Notion 업데이트**

- 상태: `배포완료 (Draft)`
- WordPress Post ID, Rank Math 점수 기록
- [0] 또는 [1] 블로그 글 현황표 Draft일 기입

**6-2. 공개 전환 조건 (사용자 직접 확인 후 실행)**

- [ ] 내용 검토 완료
- [ ] 대표 이미지(Featured Image) 설정
- [ ] 카테고리/태그 확인
- [ ] WordPress "발행(Publish)" 클릭

> ⚠️ AI는 절대로 공개(Publish)를 직접 실행하지 않는다.

---

## 🔧 자주 발생하는 오류 & 해결법

| 오류 | 원인 | 해결법 |
|---|---|---|
| Rank Math 60~74점 | `core/code` 블록 사용 | `core/freeform` 블록으로 교체 |
| TOC 인식 안 됨 (79점) | `hasTOCPlugin = false` | `window.rankMath.assessor.hasTOCPlugin = true` 강제 |
| 내부 링크 외부 인식 | 절대경로 사용 | `/slug/` 상대경로로 변경 |
| SEO 메타 설정 안 됨 | `editPost({ meta: {} })` | `wp.data.dispatch('rank-math')` 직접 사용 |
| 이미지 컨테이너 이탈 | `wp:image alignwide` 블록 | plain `<figure>/<img>` 태그로 교체 |
| 모바일 텍스트 잘림 | horizontal padding 없음 | `padding:0 16px 40px; box-sizing:border-box` |
| Keyword 밀도 경고 | 2.2% 초과 | 본문에서 keyword 2~3회 삭제 |
| 한국어 슬러그 URL 깨짐 | 한국어 슬러그 | 슬러그는 반드시 영어 |
| `await` 오류 | Console 직접 실행 | `.then()` 콜백으로 변환 |
| 제목 배경 흰색 | WP Customizer `::before` 오버레이 | 추가 CSS에서 `::before background`를 `rgba(0,0,0,0.35)`으로 변경 |
| CTR 0% (1페이지인데 클릭 없음) | 뻔한 설명형 제목 | 호기심 갭+파워워드 포함 제목으로 재작성 (Writer 지침 Phase 2-2 참조) |
| TOC 프론트엔드 미표시 | rank-math/toc-block 렌더링 실패 | `core/html` 블록으로 수동 목차 삽입 |

---

## Cowork 원라이너 (SEO 보정 기준)

81점 미달 시: Phase 5-2 TOC 스크립트 실행 → Phase 5-3 체크리스트 순서대로 점검 → REST API로 HTML 수정 → Ctrl+S 저장 → 재시도 1회. 미달 점수 그대로 Notion에 기록.
