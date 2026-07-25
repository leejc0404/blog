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
