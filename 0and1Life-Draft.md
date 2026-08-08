# 📋 0and1Life Draft 지침 (Cowork 0and1life-wordpress-draft용)

## 이 문서의 용도

`0and1life-wordpress-draft` (Cowork 예정됨)이 **매 실행 STEP 0에서 1회 읽고**, SEO 점수 미달 시 보정 근거로 참조하는 지침입니다.

- **포함**: Phase 5-1 저장 순서 규약, 5-2 재분석 트리거, 5-3 블록구조/820px 체크, 5-4 피드백, Phase 6 완료 처리, Phase 7 카테고리 배정, 오류표
- **제외**: Phase 1~4, 콘텐츠 작성 규칙 → ✏️ 0and1Life Writer 지침 참조
- **번호 안내**: 번호는 Writer 지침의 Phase 체계를 이어받은 것 — Phase 0~4는 Writer 담당이라 이 문서에 없음(의도된 결번, 오타 아님). ⚠️ Writer 지침의 'Phase 5-3(SEO 콘텐츠 품질 자가검수)'과 이 문서의 'Phase 5-3(블록 구조·820px 체크)'은 **서로 다른 문서의 별개 항목**임에 주의.

### 개정 이력
- **v1.4 (2026-08-08)** — ⭐ 대폭 개정. ① **Phase 5-1 저장 순서 규약 신설**(자동저장 본문 훼손 사고 규명) ② Phase 5-2 재분석 트리거를 **조건부**로 강등(점수 하향 덮어쓰기 실측) ③ `contentHasShortParagraphs` 구조적 원인 규명 및 **무의미한 문단 쪼개기 금지** ④ **Phase 7 카테고리 배정 규칙 신설**(WP 매핑 실측 정정 + 균형 규칙) ⑤ 오류표 4행 추가
- v1.3 — 舊 Phase 4(배포 JS) 삭제에 따른 잔존 참조 수정. Track 행(S/L)은 Draft 루틴이 무시.

---

## ⛔ Phase 5-1. 저장 순서 규약 (v1.4 신설 — 이 문서에서 가장 중요)

> **배경 (2026-08-08 실측)**: REST로 본문을 올린 뒤 에디터 탭을 열어둔 채 두면, **draft는 Gutenberg 자동저장이 리비전이 아니라 원본 글에 직접 기록**된다. 그 결과 에디터 메모리에 남아 있던 구버전이 REST 결과를 되덮어쓴다. 실측 피해: `<p>` 56개 → 2개, 18,353자 → 17,984자. 2026-08-07 리포트가 "savePost 직후 REST 덮어쓰기"로 진단했던 것의 진짜 원인이며, **탭 정리가 REST 복원보다 먼저**여야 한다.

### 5-1-A. 원칙

1. **에디터 탭이 열려 있는 동안에는 REST로 본문을 쓰지 않는다.**
2. `savePost()` 는 **마지막에 한 번만** 호출한다. 호출할 때마다 TinyMCE 직렬화로 `<p>`·`<br>`가 소실될 수 있다.
3. 본문 REST 수정이 필요하면 **탭 정리 → REST → 검증** 순서를 지킨다.

### 5-1-B. 표준 절차

```
① 에디터에서 GeneratePress 3필드 + Rank Math 설정을 모두 마친다
② savePost() 1회 (여기서 서버측 SEO 점수가 기록된다)
③ 본문 REST 수정이 필요하면:
   ③-1 열린 에디터 탭 전부에서 dirty를 해제한다
        - isEditedPostDirty() 가 true면 savePost() 1회로 해제
        - "Leave site?" 다이얼로그로 navigate가 막히면 억지로 뚫지 말고 이 방법을 쓴다
   ③-2 모든 에디터 탭을 post.php 밖으로 이동시킨다 (예: /wp-admin/upload.php)
   ③-3 그 다음에 REST POST 로 본문을 쓴다
   ③-4 8초 대기 후 GET context=edit 으로 재조회해 검증한다
④ 검증 항목: <p> 개수 · 본문 길이 · ld+json 존재 · evidence figure 존재 · freeform 마커 2개
```

### 5-1-C. 검증 스크립트 (그대로 사용)

```bash
curl -s -u "$CRED" "https://0and1life.com/wp-json/wp/v2/posts/{ID}?context=edit" -o /tmp/p.json
python3 -c "
import json,re
d=json.load(open('/tmp/p.json')); c=d['content']['raw']
print('len',len(c),'| p',len(re.findall(r'<p[ >]',c)),'| ld','application/ld+json' in c,
      '| ev',c.count('evidence-capture'),'| freeform',c.count('wp:freeform'),'| status',d['status'])"
```

`p` 가 기대값보다 크게 작으면(예: 50대 → 한 자릿수) **자동저장에 덮인 것**이다. 5-1-B ③부터 다시 한다.

---

## Phase 5-2. TOC 인식 강제 및 재분석 트리거 (v1.4 — 조건부로 강등)

### ⚠️ v1.4 변경: 재분석 트리거를 기본 동작에서 제외한다

> **배경 (2026-08-08 실측)**: 최초 `savePost()` 시 **서버(PHP)가 계산한 점수는 79점**이었는데, 이후 에디터에서 재분석 트리거를 돌리자 **클라이언트(JS) 점수 76점이 메타를 덮어썼다.** 클라이언트 분석은 `getEditedPostContent()` 를 쓰는데 이 값은 freeform 직렬화 과정에서 `<p>`가 소실된 상태라(59개 → 2개), 서버 분석보다 구조적으로 불리하다.

**규칙:**

- `hasTOCPlugin = true` 강제는 **Rank Math 설정 단계에서 미리** 넣는다(STEP 6d). 이것만으로 TOC 인식은 해결된다 — 2026-08-06·08-08 연속 확인.
- **재분석 트리거는 다음 조건을 모두 만족할 때만 실행한다:**
  1. 저장 후 점수가 81점 미만이고
  2. 실패 항목 중 **본문 수정으로 해소 가능한 것**이 있으며
  3. 그 수정을 실제로 REST에 반영한 뒤일 것
- 위 조건에 해당하지 않으면 **트리거를 돌리지 말고 서버 점수를 그대로 최종값으로 기록한다.** 돌리면 점수만 내려간다.

### 트리거 스크립트 (조건 충족 시에만)

```javascript
const { dispatch, select } = wp.data;
if (window.rankMath && window.rankMath.assessor) window.rankMath.assessor.hasTOCPlugin = true;

const fb = select('core/editor').getBlocks().find(b => b.name === 'core/freeform');
if (fb) {
  const orig = fb.attributes.content;
  dispatch('core/editor').updateBlockAttributes(fb.clientId, { content: orig + ' ' });
  setTimeout(() => {
    dispatch('core/editor').updateBlockAttributes(fb.clientId, { content: orig });
  }, 800);
} else {
  console.error('❌ freeform 블록 없음');
}
```

⚠️ 舊 `wp.data.dispatch('rank-math').updateReduxState({hasTOCPlugin:true})` 는 존재하지 않는 함수(TypeError)이므로 사용 금지.
⚠️ 트리거 실행 후에는 에디터가 dirty 상태가 된다 → **반드시 Phase 5-1-B ③ 절차로 정리**한 뒤 세션을 끝낼 것.

---

## Phase 5-3. 블록 구조 / 820px 무결성 체크 (Cowork 보정용)

**🟢 추가 SEO (블록 구조)**

- [ ] `core/freeform` 블록 **단일**로 HTML 삽입 (`getBlocks()` 결과가 `['core/freeform']` 하나여야 함)
- [ ] `hasTOCPlugin = true` 강제 설정 완료 (STEP 6d에서 선반영)
- [ ] `<!-- TABLE OF CONTENTS -->` 마커가 본문에 존재

**🟢 820px 컨테이너 무결성**

- [ ] 모든 콘텐츠가 `max-width:820px; padding:0 16px 40px; box-sizing:border-box;` 래퍼 안에 위치하는가?
- [ ] HTML 내 이미지가 plain `<figure>/<img>` 태그로 삽입, `<!-- wp:image -->` 마커 없는가?
- [ ] freeform 블록 외부에 별도 Gutenberg 이미지 블록(`alignwide`) 없는가?
- [ ] 래퍼 div의 horizontal padding이 `0 16px` 이상인가?

**🟢 키워드 입력 (누락 금지)**

- [ ] Rank Math 포커스 키워드 필드에 Notion 기본 정보 표의 **Focus Keyword + Sub Keywords 전부**를 쉼표로 연결해 입력했는가? (Focus가 첫 번째, 총 5개 권장)
- [ ] 저장 후 검증: `wp.data.select('rank-math').getKeywords()` 결과에 쉼표 항목이 2개 이상인가?

> 배경: 2026-07-09 점검에서 Draft 루틴이 Focus만 입력하고 Writer가 기록한 Sub Keywords를 버리는 문제 확인(Blog #52).

**🟢 최종 확인**

- [ ] Rank Math 점수 확인 — 목표 81/100, 미달 시 아래 5-3-B 판정
- [ ] 임시저장(Draft) 상태 확인
- [ ] 본문 무결성 재검증 (Phase 5-1-C)
- [ ] Notion 페이지 점수 업데이트

### 5-3-B. 점수 미달 시 — 조치 가능 여부 선판정 (v1.4 신설)

**보정을 시작하기 전에 실패 항목이 조치 가능한지부터 가른다.** 무의미한 보정에 시간을 쓰지 않기 위해서다.

실패 항목은 에디터 콘솔에서 이렇게 뽑는다 (Rank Math 패널을 연 뒤 실행):

```javascript
const p = document.querySelector('.rank-math-sidebar-panel, .interface-complementary-area');
p.querySelectorAll('.rank-math-collapsible-title, .components-button[aria-expanded="false"]')
 .forEach(b => { try { b.click() } catch(e) {} });
await new Promise(r => setTimeout(r, 1500));
JSON.stringify([...p.querySelectorAll('[class*="seo-check-"]')]
  .filter(n => /test-fail/.test(n.className))
  .map(n => (n.className.match(/seo-check-([A-Za-z]+)/) || [])[1]));
```

| 실패 항목 | 판정 | 조치 |
|---|---|---|
| `keywordInPermalink` | ⛔ **구조적 — 조치 불가** | 슬러그 영문 정책. **변경 금지.** 로그에 '사양'으로 기록 |
| `hasContentAI` | ⛔ **PRO 전용 — 조치 불가** | 로그에만 기록 |
| `contentHasShortParagraphs` | ⛔ **구조적 — 조치 불가 (v1.4 규명)** | 아래 참조 |
| `keywordIn10Percent` | ✅ 조치 가능 | 도입 첫 문단 100자 안에 Focus Keyword 배치 |
| `keywordInSubheadings` | ✅ 조치 가능 | H2 1개 이상에 Focus Keyword 포함 |
| `keywordInMetaDescription` | ✅ 조치 가능 | 메타 설명 150자 이내 + Focus Keyword |
| `linksHasInternal` | ✅ 조치 가능 | `/slug/` 상대경로 내부링크 1개 이상 |
| `lengthContent` | ✅ 조치 가능 | 본문 1,500자 이상 |

> ### ⛔ `contentHasShortParagraphs` — 문단을 쪼개도 해소되지 않는다 (2026-08-08 규명)
>
> **실측**: 저장본 raw는 `<p>` 56개·최장 문단 **40어절**로 완전히 정상인데도 이 항목이 실패한다. 원인을 추적하니, Rank Math가 분석하는 대상은 저장본이 아니라 `wp.data.select('core/editor').getEditedPostContent()` 이고, **이 값은 freeform 블록 직렬화 과정에서 `<p>` 태그가 59개 → 2개로 소실된 상태**였다. 즉 Rank Math는 본문 전체를 몇 개의 통짜 덩어리로 보고 있다.
>
> **따라서 본문 문단을 아무리 잘게 쪼개도 이 항목은 통과하지 않는다.** 2026-08-07에 시도한 `<p>` 태그 복원, 2026-08-08에 시도한 FAQ `ld+json` 축약(223어절 → 47어절) 모두 이 항목을 해소하지 못했다.
>
> **규칙**: 이 항목이 실패로 뜨면 **보정을 시도하지 말고** 로그에 "freeform 직렬화 구조적 한계 — 조치 불가"로 기록하고 넘어간다. 서버측 저장 점수에서는 이 항목이 통과하므로(저장본에 `<p>` 56개가 있으므로), **재분석 트리거를 돌리지 않는 것이 점수상 유리하다**(Phase 5-2 참조).

**조치 가능 항목이 하나도 없으면 보정을 생략하고 서버 점수를 그대로 기록한다.**

---

## Phase 5-4. 피드백 체크리스트

- [ ] (공감 검증) 한국 직장인/부업러가 처음 3초에 "나 이거 해당되는데" 반응이 나오는가? → Yes여야 함.
- [ ] (지식 검증) 직접 써보거나 검증된 정보만 담겼는가? → Yes여야 함.
- [ ] (제목 검증) 제목만 보고 답이 금방 보이지 않고 "어떻게?", "진짜?" 궁금한가? → Yes여야 함.
- [ ] (슬러그 검증) 슬러그가 영어로만 작성되었는가? → Yes여야 함.
- [ ] (실용성) 바로 따라할 수 있는 구체적 팁이 3개 이상 있는가? → Yes여야 함.

### ⛔ 발행 차단 관문 (Draft 루틴 STEP [4f]이 이 항목으로 판정)

- [ ] **① 원본자료** — 1급 원본 자료(직접 조작한 화면 캡처·실측 수치) 최소 1개. 계산표·공식 수치 재정리만으로는 불통과
- [ ] **② 가짜경험** — 하지 않은 일의 1인칭 서술 0건. ⚠️ **도입 첫 문단을 특히 주의해 읽는다.** 주어가 생략된 완료형("~끊었습니다. ~요청했더니")은 필자의 실경험으로 읽힌다. Writer 메모에 "0건"이라 적혀 있어도 본문을 직접 읽고 판정한다
- [ ] **③ 이미지출처** — 모든 `<img>`가 자체 업로드(0and1life.com) 또는 images.unsplash.com 또는 `[FEATURED_IMAGE_URL]` 플레이스홀더. 타 사이트 핫링크(gstatic·pstatic 등) 0건

> ⚠️ **소급 적용 원칙 (2026-08-05 사건의 교훈)**: 새 관문을 만들면 **기존 글에도 반드시 소급 적용**한다. `Fabricated Experience Gate`를 신규 글에만 걸어둔 탓에 기존 58편이 방치됐고, 이것이 구글 색인 거부 13편의 유력한 원인으로 지목됐다.

---

## Phase 6. 완료 후 처리

**6-1. Notion 업데이트**

- 상태: `배포완료 (Draft)`
- WordPress Post ID, Rank Math 점수 기록
- [0] 또는 [1] 블로그 글 현황표 Draft일 기입
- ⚠️ Draft일은 **STEP 6 전 과정이 성공했을 때만** 기록한다. GP 미반영·Rank Math 실패·Chrome 로그인 실패 시 공란 유지(다음 실행에서 재시도)

**6-2. 공개 전환 조건 (사용자 직접 확인 후 실행)**

- [ ] 내용 검토 완료
- [ ] 대표 이미지(Featured Image) 설정
- [ ] 카테고리/태그 확인
- [ ] WordPress "발행(Publish)" 클릭

> ⚠️ AI는 절대로 공개(Publish)·예약발행(future)을 직접 실행하지 않는다.

---

## Phase 7. 카테고리 배정 (v1.4 신설)

### 7-1. WP 카테고리 매핑 (2026-08-08 REST 실측 정정)

> ⚠️ **v1.3까지의 매핑표는 실제와 어긋나 있었다.** AI 계열을 18번으로 배정하도록 돼 있었으나, 실제 AI 글 15건은 전부 **26번**에 있고 18번에는 4건뿐이다.

| Notion 서브카테고리 | WP ID | slug | 주간 한도 |
|---|---|---|---|
| 💰 직장인 재테크 | **23** | office-worker-finance | 2 |
| 💼 대기업 직장인 생활 | **29** | corporate-worker-life | 2 |
| 📐 생활 규정·계약 계산 | **30** | time-money-saving *(slug 유지)* | 2 |
| 🔍 생활 비용 비교 | **신설 대기** → 확정 전에는 30 fallback | living-cost-compare | 2 |
| 💍 Wedding | **27** | wedding | 1 |
| 🏠 Life · My Story | **25** | daily-life | — |
| 🤖 AI 정보 | **26** | ai-guide | **0 (동결)** |
| 0. 테크와 효율 | 18 | tech-efficiency | 사용 중단(레거시) |

- 매핑 없는 서브카테고리는 **생성 전에** `GET /wp-json/wp/v2/categories?search={이름}` 으로 동일·유사 카테고리 존재 여부를 먼저 확인한다. 신규 생성은 최후 수단.
- Notion 서브페이지 "Category" 행에 `(WP 29)` 처럼 ID가 명시돼 있으면 **그 값을 그대로 사용**한다.

### 7-2. 카테고리 경계 판정 (한 문장 테스트)

겹치면 **더 좁은 쪽**으로 보낸다.

| 카테고리 | 판정 질문 | 예시 |
|---|---|---|
| 📐 생활 규정·계약 계산 | "누가 얼마를 부담하는가를 조문·약관으로 판정하는가?" (상대방이 있고 다툼이 있다) | PT 환불, 월세 원상복구, 주차 과태료, 택배 파손, 항공 지연 보상 |
| 🔍 생활 비용 비교 | "같은 목적에 선택지가 둘 이상이고 총비용이 갈리는가?" (상대방 없이 내 선택만) | 제습기 전기세, 정수기 렌탈 vs 구매, 인터넷 재약정, 구독 정리 |
| 💰 직장인 재테크 | "국가·금융기관에 내거나 받는 돈인가?" | 세금, 4대보험, 연금, 청약, 지원금 |
| 💼 대기업 직장인 생활 | "고용관계에서 발생하는가?" | 통상임금, 연차, 성과급, 퇴사, 이직 |
| 💍 Wedding | 결혼 준비 전 과정 | 스드메, 보증인원, 축의금 |

⚠️ '웨딩홀 계약금 환불'처럼 겹치는 것은 **웨딩이 아니라 📐 규정·계약 계산**으로 보낸다.

### 7-3. 편중 방지 규칙 v1.0

```
R1. 7일 창 동일 카테고리 상한: 재테크 2 · 대기업 2 · 규정계산 2 · 비용비교 2 · 웨딩 1 · AI 0
R2. 3연속 금지 — 직전 2건이 같은 카테고리면 3번째는 반드시 다른 카테고리
R3. 순환 하한 — 7일 창에 서로 다른 카테고리가 3개 미만이면
    가장 오래 안 쓴 카테고리를 그날 1순위로 강제 검토
R4. 전면 봉쇄 시 — 루틴을 멈추지 말고 여유가 가장 큰 카테고리를 1건 초과 허용하되,
    사유를 실행 로그에 '균형 규칙 예외'로 반드시 기록한다
R5. 형식 로테이션 — 직전 3건이 같은 형식이면 4번째는 다른 형식으로
```

> **배경 (2026-08-08 분석)**: 2026-08-03~08 사이 절약 카테고리가 5건 연속 발행됐다. 원인은 절약 선호가 아니라 **다른 카테고리가 동시에 닫혀 있었기 때문**이다 — 대기업은 '직장 종속성 주 1건' 한도로 4회 연속 제외, 웨딩은 색인 거부에 따른 회피 기조로 6회 연속 제외, AI는 영구 동결, 재테크는 시즌·한도. 한 카테고리에 상한만 추가하면 루틴이 정지하므로, **공급원을 먼저 열고(규정계산/비용비교 분리, 웨딩 회피 해제) 상대 규칙으로 균형**을 잡는다.

### 7-4. 발행량 가드 (F등급 연동)

주간 GSC 리포트의 **F등급 실제 글 비율**(색인 거부된 본문 글 ÷ 색인된 페이지)이 30%를 넘는 구간에서는 신규 발행보다 기존 글 정리가 우선이다.

- 30% 초과 **2주 연속** → Draft 루틴 STEP 7 완료 알림에 `⚠️ F등급 {n}% — 정리 우선 구간` 을 명시한다
- 30% 초과 **3주 연속** → 일일 1편 발행을 **주 3편으로 축소**하는 안을 사용자에게 제시한다

---

## 🔧 자주 발생하는 오류 & 해결법

| 오류 | 원인 | 해결법 |
|---|---|---|
| **본문 `<p>`가 대량 소실 (56 → 2)** | **에디터 탭을 열어둔 채 REST 수정 → draft 자동저장이 원본을 되덮어씀** | **Phase 5-1-B: 탭 정리 → REST → 8초 후 검증** |
| **저장 후 SEO 점수가 오히려 내려감** | **재분석 트리거가 클라이언트 점수(낮음)로 서버 점수(높음)를 덮어씀** | **Phase 5-2: 조치 가능 항목이 없으면 트리거를 돌리지 않는다** |
| **`contentHasShortParagraphs` 가 계속 실패** | **freeform 직렬화에서 `<p>` 소실 — 본문 문제 아님** | **조치 불가로 기록하고 넘어간다. 문단 쪼개기 무의미** |
| **navigate가 "Leave site?"로 막힘** | 에디터 dirty 상태 | `savePost()` 1회로 dirty 해제 후 이동. 억지로 뚫지 말 것 |
| Rank Math 60~74점 | `core/code` 블록 사용 | `core/freeform` 블록으로 교체 |
| TOC 인식 안 됨 (79점) | `hasTOCPlugin = false` | STEP 6d에서 `window.rankMath.assessor.hasTOCPlugin = true` 선반영 |
| 내부 링크 외부 인식 | 절대경로 사용 | `/slug/` 상대경로로 변경 |
| SEO 메타 설정 안 됨 | `editPost({ meta: {} })` | `wp.data.dispatch('rank-math')` 직접 사용 |
| 이미지 컨테이너 이탈 | `wp:image alignwide` 블록 | plain `<figure>/<img>` 태그로 교체 |
| 모바일 텍스트 잘림 | horizontal padding 없음 | `padding:0 16px 40px; box-sizing:border-box` |
| Keyword 밀도 경고 | 2.2% 초과 | 본문에서 keyword 2~3회 삭제 |
| 한국어 슬러그 URL 깨짐 | 한국어 슬러그 | 슬러그는 반드시 영어 |
| `await` 오류 | Console 직접 실행 | `.then()` 콜백으로 변환 |
| 제목 배경 흰색 | WP Customizer `::before` 오버레이 | 추가 CSS에서 `::before background`를 `rgba(0,0,0,0.35)`으로 변경 |
| CTR 0% (1페이지인데 클릭 없음) | 뻔한 설명형 제목 | 호기심 갭+파워워드 포함 제목으로 재작성 |
| TOC 프론트엔드 미표시 | rank-math/toc-block 렌더링 실패 | `core/html` 블록으로 수동 목차 삽입 |
| **행정규칙 별표 캡처 실패** | **별표는 HTML 렌더링 없이 HWP 첨부로만 제공** | **법령(法令) 조문으로 대체. law.go.kr `lawService` iframe은 HTML 인라인 렌더링됨 (8/4·8/6·8/8 3회 검증)** |

---

## Cowork 원라이너 (SEO 보정 기준)

81점 미달 시: **Phase 5-3-B로 조치 가능 여부를 먼저 판정** → 조치 가능 항목이 있을 때만 REST로 HTML 수정 → Phase 5-1-B 순서로 저장·검증 → 재시도 1회. 조치 가능 항목이 없으면 **보정하지 말고** 서버 점수를 그대로 Notion에 기록.
