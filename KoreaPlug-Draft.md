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

- [ ] **(Originality Gate)** 이 글에 **이 사이트에만 존재하는 자료**가 최소 1개 있는가? — 직접 만든 비교표·계산표(과정 공개) / 직접 캡처한 화면·양식 / 직접 확인한 현장 가격·정보(확인 날짜 명기) / 직접 촬영한 사진 / 여러 출처를 처음 통합 정리한 표. **공식 홈페이지 링크만 있으면 No.** → No면 업로드 중단
- [ ] **(Fabricated Experience Gate)** 실제로 하지 않은 일을 1인칭(I, My)으로 서술한 문장이 **한 개도 없는가?** — "When I first…", "my group chat…", 지어낸 개인 이력·일화 전부 해당. → No면 해당 문장을 3인칭/2인칭으로 고치기 전까지 업로드 중단

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
