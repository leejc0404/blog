# Schd_NaverClip — (15번 aipick · 16번 kids) 9번·12번 글의 상품 → 네이버 클립(쇼핑 커넥트) 제작·업로드 루틴 (Cowork 예약 작업용, v1.0 2026-11-28)

> 🖥️ **실행 환경 공통** — 이 블록이 문서 안의 경로·셸 전제보다 우선한다.
> - **연결 폴더 루트 `CR`** = `get_device_info.connectedFolders` 첫 항목(현재 `C:\Users\USER\Documents\Claude`). 문서의 `{CR}`·`$HOME/mnt/Claude` 는 모두 이 폴더. 사용자 이름을 경로에 박아 쓰지 않는다.
> - **셸 모드**(`mcp__remote-devices__device_bash` 있음): PC 파일 읽기·쓰기는 PC 셸, 렌더·음성·OpenMontage·Playwright·누끼는 **클라우드 Bash**(`~/clip_work`). PC 파일은 `device_stage_files` 로 가져오고, 결과는 `/mnt/user-data/outputs/clip-{날짜}-{src}/`(회차마다 새 이름 — 출력 폴더를 지우는 명령은 쓰지 않는다)에 두었다가 `device_commit_files` 로 PC 에 쓴다. 한글 경로 파일은 PC 셸로 영문 이름 폴더에 먼저 복사한 뒤 스테이징한다(11/28 실측: 한글 폴더 직접 스테이징 실패).
> - **브리지 모드**(셸 없음): 목록 = `device_list_dir` · 읽기 = `device_stage_files` · 쓰기 = `device_commit_files`.
> - 클라우드에서 막히는 곳(11/28 실측): `huggingface.co` · `generativelanguage.googleapis.com` · 일부 기관 사이트. `rembg` 모델(GitHub)·npm·pip·Edge 음성은 된다.
> - 폴더 접근 요청은 하지 않는다. 사람이 없는 시간에 실행된다 — 승인이 필요한 호출을 불필요하게 하지 않는다.

**이 루틴이 하는 일**: 9번(aipick-weekly)·12번(kidspick-weekly)이 만든 **리뷰 분석 글의 상품**으로 20~30초 세로 영상을 만들어, **네이버 클립에 쇼핑 커넥트 상품을 붙여 올린다.** 목표는 하나 — **첫 1.5초에 멈추게 하고, 끝에서 상품 버튼을 누르게** 하는 것.

**사용자 지시(2026-11-28, 이 루틴의 출발점)**
- "네이버 클립용 새로운 15번 루틴을 만들어서 돌리자."
- "네이버 클립들을 보고 강한 후킹으로 끌고 오고 거기서 바로 구매를 할 수 있게끔 구성."
- "리뷰에 대한 얘기는 너무 '리뷰리뷰'하지 말고, 그 리뷰에서 나온 내용만큼 그 아이템을 구매하고자 하는 소비자의 욕구를 만족시킬 만한 것으로 표현."
- "실제 이미지를 영상에서 움직이듯이 모션그래픽을 (prompt-motion.com 을 참고해) 다양하게 구현."
- 3D(three.js)는 "어색하다" → **2D 모션그래픽만** 쓴다.
- 음성은 Edge `ko-KR-SunHiNeural` +42%("A가 제일 낫네").
- 소재: 9번 + 12번 둘 다 · 업로드: 브라우저로 대신 올림(게시는 사용자 확인) · 시각: 9번 글 05:00, 12번 글 05:30.

**절대 지키는 것**
- **공개 게시는 하지 않는다.** 업로드 화면에 `비공개`(나만 보기) 설정이 있으면 비공개로 끝까지 올리고, 없으면 **게시 버튼 직전에서 멈춘다**. 공개 전환·게시는 사용자가 이 세션에서 "올려"라고 할 때만(사용자 지침 ②).
- 9번·12번의 파일(`naver_blog\`, `kids_blog\`)·큐·블로그 글·크리에이터샵은 **읽기만** 한다.
- 삭제(PC 파일·클립·네이버 콘텐츠)는 하지 않는다. 필요해 보이면 알림으로 묻는다(사용자 지침 ①).
- 좋아요·팔로우·댓글·DM 금지(레퍼런스 스캔은 읽기 전용).
- 자격증명 값 출력 금지 · git 커밋 금지 · 사용자 폴더에 백업 사본을 만들지 않는다.

---

## 실행 자산

| 무엇 | 어디 | 비고 |
|---|---|---|
| 소재(9번) | `{CR}\naver_blog\out\{YYYYMMDD}_{n}_{주제}\` | `발행정보.txt`·`원고.txt`·`models.json`·`analysis.json`·`findings.json`·`tips.json`·`photos\`(m1~m3 · `_g1~g4`)·`photos\gallery.json`·`data\links.json` |
| 소재(12번) | `{CR}\kids_blog\out\{YYYYMMDD}_{n}_{주제}\` | 같은 구성 + `facts_allow.json`·`price_counts.json` |
| 작업 폴더(PC) | `{CR}\naver_clip\{YYYY-MM-DD}_{src}_{영문 slug}\` | `src` = `aipick` 또는 `kids` |
| 원장 | `{CR}\naver_clip\ledger.json` | `{clips: {"{src}:{소재 폴더 이름}:{모델 key}": {date, status, technique[], hook, title, upload{…}}}}` 없으면 만든다 |
| 레퍼런스 | `{CR}\naver_clip\refs\{YYYY-Www}.md` | STEP W |
| 내레이션 | 아래 STEP 4 `tts.py` | Edge SunHi +42%, 낱말 시각 기록 |
| 렌더 | OpenMontage `hyperframes_compose`(커밋 `2e003e65fa99a0f329478a2c1cdcf26bc481933a`, HyperFrames `0.9.80`) + HF 키트(`leejc0404/blog` `tools/hf`) | 8번 루틴과 같은 준비 코드(STEP 5 ①) |
| 효과음·믹스·싱크 | `{CR}\instagram\relay\build_reel_sfx_v2.py` · `{CR}\instagram\2026-11-28\base-rate-hike-loan-interest\mix.py`·`verify_hf_sync.py` | 스테이징해서 복사 |
| 견본 회차 | `{CR}\instagram\2026-11-28\neck-warmer-review-4005\v2_2d\` | 2D 점판 → 막대(`om_index.html`·`build_hf_vars.py`) — 구조 참고용. **이 루틴의 구성(STEP 3)은 견본보다 구매 중심이다** |

설정값: `DUR = 20~30초` · `FPS = 30` · `SIZE = 1080×1920` · `VOICE = Edge ko-KR-SunHiNeural +42%, 문장 간격 0.16초` · `BGM = 없음` · `PRODUCT_PER_CLIP = 1` · `TECHNIQUES = 회차마다 3~4개, 직전 3회차와 시그니처 기법 겹치지 않음` · `UPLOAD = 비공개 업로드 또는 게시 직전 정지`

---

## STEP W. 주간 레퍼런스 — 네이버 클립 쇼핑 영상 보기 (월요일 aipick 회차에서만 · 읽기 전용)
1. 브라우저(내장 브라우저 우선, 없으면 Claude in Chrome)로 네이버 모바일 웹에서 이 회차 상품군·`발행정보.txt` 의 검색 태그로 클립을 찾아 **쇼핑 스티커·상품 태그가 붙은 클립 6~10개**를 연다.
2. 클립마다 기록(`refs\{YYYY-Www}.md`): 첫 1.5초 화면·첫 문장(훅 유형 — STEP 3 표의 코드) · 제품이 처음 보이는 시각 · 컷 수·길이 · 실물 사진/영상을 어떻게 움직였나 · 자막 방식 · 가격·혜택 표기 · 끝 CTA 문구·스티커 위치 · 좋아요·댓글 수(보이면) · "차용할 것(형식) / 복제하지 않을 것".
3. 끝에 **이번 주에 써 볼 훅 2개·기법 2개**를 적는다 — STEP 3 이 이 줄을 우선 후보로 쓴다.
4. 화면에서는 페이지 이동·스크롤만. 영상·이미지·문구를 복제하지 않는다(형식만). 열었던 탭은 닫는다. 30초 넘게 안 열리면 그 주는 건너뛴다.

## STEP 0. 준비
1. 실행 시각(KST)으로 **소재 원천**을 정한다: 05:00 회차 = `aipick`(`naver_blog\out`, **15번**), 05:30 회차 = `kids`(`kids_blog\out`, **16번**). 예약 본문이 원천을 적었으면 그것을 따른다. 아래 알림·실행 기록의 `{N}` 은 aipick = 15, kids = 16.
2. PC 셸: `mkdir -p "$HOME/mnt/Claude/naver_clip/refs"`, `ledger.json` 이 없으면 `{"clips":{}}` 로 만든다.
3. 클라우드: `mkdir -p ~/clip_work`, `pip install -q edge-tts "rembg[cpu]" --break-system-packages`(이미 있으면 건너뜀).

## STEP 1. 소재 고르기
1. 원천 폴더에서 **완성된 글**만 후보로 본다: `발행정보.txt`·`점검.md`·`models.json`·`analysis.json`·`photos\` 가 모두 있고, `점검.md` 에 ❌ 줄이 없는 폴더. 9번·12번이 아직 쓰는 중인 폴더(마지막 수정 20분 이내)는 건너뛴다.
2. 최근 14일 안의 폴더를 최신 순으로 보며, 그 글의 **1위 상품**(원고의 "왜 ○○가 1위일까요" 블록 · 없으면 `analysis.json` 에서 따뜻함·만족 등 핵심 라벨 수가 가장 큰 모델)이 ledger 에 없는 첫 글을 고른다. 1위가 이미 있으면 그 글의 2위 → 3위. 모두 있으면 다음 글.
3. 14일 안에 남은 게 없으면 60일 안으로 넓힌다. 그래도 없으면 "소재 없음" → STEP 9 알림 없이 실행 기록만 남기고 끝.
4. ⛔ 시즌이 지난 상품(원고·제목에 지난 날짜·행사가 결론인 글)은 건너뛴다.
5. 고른 상품의 `models.json` 항목(이름·short·가격·커넥트 링크 `link`·커미션)과 `analysis.json`·`findings.json`·`tips.json`·`원고.txt` 를 PC 셸에서 `{CR}\naver_clip\{작업 폴더}\src\` 로 복사(영문 이름: `post.txt`·`post.html`)하고 사진(`photos\{key}*.jpg`)도 같이 복사한 뒤 스테이징한다.

## STEP 2. 사고 싶은 이유 뽑기 (리뷰를 '욕구'로 번역)
`concepts.md` 맨 위에 적는다.
1. **누가 · 언제 · 무엇이 불편한가**(장면 1개): `findings.json` 의 `who`·상황 라벨과 원고의 "이런 분께 맞아요"에서. 예: "찬바람에 목·귀가 시린 출근길" · "스키장 리프트 위".
2. **이 상품이 주는 느낌 3개**(구매 욕구의 언어): `analysis.json` 의 만족 라벨 상위·`findings.json` 예시 문장·`tips.json` 에서 **구매자가 실제로 느낀 것**을 감각어로 바꾼다. 예: 라벨 "따뜻함 39.8%" + 예시 "기모가 부드러워서 얼굴이 따뜻하게 감싸져요" → "기모가 얼굴을 폭 감싸요". 예시 "귀가 눌리지 않아서" → "귀가 안 눌려요".
3. **믿을 근거 1개**(한 번만): 숫자 하나 — "써 본 1,405명이 따뜻하다고" 처럼. `리뷰 N개 분석`·`라벨`·`%`·`표본` 같은 분석 말은 화면·음성에 쓰지 않는다(**'리뷰리뷰' 금지**). 근거 숫자는 영상에 1~2번까지.
4. **가격·혜택**: `models.json.price_won`(기준일 `발행정보.txt`/원고의 날짜) — 화면에 "○월 ○일 기준"을 작게. 실제로 있는 쿠폰·할인만(원고·상품 데이터에 있을 때). 가짜 한정·마감 금지.
5. **걸리는 점 1개(선택)**: 원고 꿀팁 블록의 단점(예: 안경 김 서림)을 팁으로 바꿔 말할 수 있으면 — 신뢰를 준다. 단점을 숨기지도, 과장하지도 않는다.
6. ⛔ 글·데이터에 없는 효능·수치·후기 문장 지어내기 금지. 리뷰 원문을 길게 인용하지 않는다(짧은 감각어로 바꿔 말한다). 의료·안전 효능 단정 금지.

## STEP 3. 대본·구성 (20~30초 · 한 상품)

**구성 (순서 고정)**

| 박 | 시간 | 하는 일 | 화면 |
|---|---|---|---|
| ① 훅 | 0~2초 | 불편·욕구를 찌르는 한 문장(14자 안팎) | 실물 상품이 0프레임부터 크게 + 0.3초 안에 사건(아래 기법) + 굵은 한 줄 |
| ② 해결 장면 | 2~7초 | "이걸 쓰면 이렇게 된다" — 감각 1번 | 상품이 문제 장면을 막는 그림(바람 화살표가 튕겨 나감·차가운 색이 따뜻한 색으로) |
| ③ 사고 싶은 이유 | 7~18초 | 느낌 2~3개 + 근거 숫자 1개 | 실물 사진의 그 부분을 짚으며(핫스팟·줌) 한 줄씩 |
| ④ 누구에게 | 18~23초 | "○○ 하는 분이면 이거" (+ 걸리는 점 팁 선택) | 상황 아이콘·사진 컷 |
| ⑤ 가격·버튼 | 마지막 3~6초 | 가격(기준일) + "아래 상품 버튼에서 바로 볼 수 있어요" | 가격표가 떨어져 꽂힘 + 버튼 자리를 가리키는 화살표·펄스 + `광고` 표시 |

**훅 공식(회차마다 하나 — 직전 2회차와 다르게, STEP W 우선 후보 먼저)**

| 코드 | 공식 | 예 |
|---|---|---|
| `K1` 불편 직격 | 시청자의 지금 불편을 그대로 | "목으로 찬바람 들어오죠?" |
| `K2` 결과 먼저 | 쓰고 난 느낌을 0초에 | "귀까지 뜨끈해요" |
| `K3` 대상 부르기 | 누구 + 약속 | "스키장 가는 분, 이거 하나면 돼요" |
| `K4` 갈아타기 | 익숙한 대안 대신 | "목도리 말고 이거예요" |
| `K5` 숫자 한 방 | 근거 숫자 하나 | "1,405명이 따뜻하다고 한 넥워머" |
| `K6` 가격 반전 | 가격 대비 체감 | "1만3천원인데 이 정도예요" (가격은 데이터 그대로) |

**문장 규칙**: 친구에게 말하듯 짧게(한 문장 한 마디, 25자 안팎) · 한 문장에 숫자 하나 · 광고 말("꼭"·"무조건"·"역대급"·"지금 사세요") 금지 — 대신 "바로 볼 수 있어요" · 화면 글자는 그 장면 내레이션의 말로만(숫자·`광고`·버튼 안내 예외) · 숫자는 데이터 표기 그대로(`say` 에만 읽는 말) · 상품명은 `models.json.short` 로.

**대본 시험**: Agent 도구로 새 서브에이전트에게 대본 문장만 주고 "(1) 무슨 상품인지 (2) 사고 싶어졌는지 0~10과 이유 (3) 막힌 말 (4) 첫 문장만 듣고 계속 볼지"를 받는다. (2) ≥ 7 · (3) '모름' 0 · (4) 본다 — 아니면 고쳐 다시(최대 3판, 그래도 안 되면 훅을 다른 공식으로).

## STEP 4. 내레이션·값 (클라우드)
1. `script.json` = `[{"key":"S1","lines":[{"text":"화면·자막","say":"읽기용(선택)"}]},…]` (S1~S5 = 박 ①~⑤).
2. `tts.py`(아래 그대로) → `python3 tts.py`. 합계 30초를 넘으면 ③의 문장 하나를 뺀다. 20초보다 짧으면 ③에 느낌 하나를 더한다.
```python
# Edge ko-KR-SunHiNeural +42%, 문장마다 따로 만들어 0.16초 간격 · 낱말 시각 → timing.json[k].words
import json, asyncio, os, subprocess, edge_tts
os.makedirs('tts', exist_ok=True)
S = json.load(open('script.json')); P = os.environ.get('HTTPS_PROXY'); GAP = 0.16; out = {}
async def one(txt, f):
    c = edge_tts.Communicate(txt, 'ko-KR-SunHiNeural', rate='+42%', proxy=P, boundary='WordBoundary'); last = 0; wb = []
    with open(f, 'wb') as o:
        async for ch in c.stream():
            if ch['type'] == 'audio': o.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                a = ch['offset'] / 1e7; b = (ch['offset'] + ch['duration']) / 1e7; wb.append([a, b]); last = b
    return last, wb
def words_for(disp, wb, t0, d):
    dw = disp.split()
    if wb and len(wb) == len(dw): return [[round(t0 + a, 3), round(t0 + b, 3), w] for (a, b), w in zip(wb, dw)]
    tot = sum(len(w) for w in dw) or 1; acc = 0; r = []
    for w in dw:
        a = t0 + d * acc / tot; acc += len(w); r.append([round(a, 3), round(t0 + d * acc / tot, 3), w])
    return r
async def main():
    for sc in S:
        k = sc['key']; t = 0; parts = []; subs = []; words = []
        for i, l in enumerate(sc['lines']):
            f = f'tts/{k}_{i}.mp3'; end, wb = await one(l.get('say', l['text']), f)
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f, '-t', str(end + 0.05), '-ar', '24000', '-ac', '1', f'tts/{k}_{i}.wav'], check=True)
            d = end + 0.05; subs.append([round(t, 2), round(t + d + GAP, 2), l['text']])
            words += [w + [i] for w in words_for(l['text'], wb, t, end)]; parts.append(f'tts/{k}_{i}.wav'); t += d + GAP
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono', '-t', str(GAP), 'tts/gap.wav'], check=True)
        with open('tts/list.txt', 'w') as lst:
            for f in parts: lst.write(f"file '{os.path.basename(f)}'\nfile 'gap.wav'\n")
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'tts/list.txt', '-c:a', 'libmp3lame', '-q:a', '3', f'tts/{k}.mp3'], check=True)
        out[k] = dict(dur=round(t, 2), subs=subs, words=words)
asyncio.run(main()); json.dump(out, open('tts/timing.json', 'w'), ensure_ascii=False, indent=1)
print({k: v['dur'] for k, v in out.items()}, round(sum(v['dur'] for v in out.values()), 2))
```
3. `build_hf_vars.py` — 견본(`neck-warmer-review-4005\v2_2d\build_hf_vars.py`)처럼 `ev`(모든 사건 시각 — 문장 시작 기준, 그림은 말보다 0~0.3초 먼저) · `txt`(화면 글자) · `subs` · `words` · `scenes` · `photo`(이미지 경로 키는 `…img` 로 끝나게 — 키트가 복사) 를 `hf_vars.json` 에, 효과음 큐(반드시 `ev` 값에서만)를 `reel-final_timeline.json` 에 쓴다. 효과음: 사건 `click`·`tick`·`stamp`, 장면 경계 `whoosh`, 가격 착지 `thud`, 버튼 `chime`.
4. **실물 이미지 준비**: 상품 사진 중 **제품이 주인공인 컷**(사람 얼굴이 주인공이면 쓰지 않는다 — 얼굴이 가려진 착용 컷은 잘라서 제품 부분만) 2~4장. `rembg`(u2net)로 누끼 → `img\p{n}_cut.png`, 착용 컷은 `img\p{n}.jpg`. 격자 미리보기로 짚을 부분(기모·귀 덮개·지퍼 등)의 좌표를 재서 `photo.spots = [[x, y, "그 부분 이름"]]`.

## STEP 5. 화면 짓기 — 2D 모션그래픽 (OpenMontage HyperFrames)
① **준비**(회차 처음 1회 — 클라우드, 8번 루틴 STEP 6-OM ① 과 같다):
```bash
mkdir -p ~/clip_work && cd ~/clip_work
[ -f package.json ] || echo '{"name":"clip-work","private":true}' > package.json
npm i -s hyperframes@0.9.80 >/dev/null 2>&1
[ -d om/.venv ] || (rm -rf om && mkdir om && cd om && git init -q && git remote add origin https://github.com/OpenMontageInc/OpenMontage.git \
  && git fetch -q --depth 1 origin 2e003e65fa99a0f329478a2c1cdcf26bc481933a && git checkout -q FETCH_HEAD \
  && python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt)
cd ~/clip_work && rm -rf hfkit && git clone -q --depth 1 https://github.com/leejc0404/blog hfkit
# om_render.py · snap.js 는 8번 루틴(Schd_0and1Life-Insta.md v5.0 STEP 6-OM ①·STEP 5-OM ⑤)의 코드를 그대로 ~/clip_work 에 만든다
```
② **먼저 읽는다**: `om/skills/core/hyperframes.md`(Gotchas·Anti-patterns) · `om/.agents/skills/hyperframes-core/SKILL.md` · `om/.agents/skills/hyperframes-animation/blueprints-index.md` 와 고른 기법에 맞는 청사진·규칙 2~4개.

③ **기법 고르기 — 실물 사진을 움직이는 2D 모션 라이브러리** (prompt-motion.com 갤러리의 갈래 — Kinetic type · Product UI · Photos · Phone · Charts · Shapes · Particles — 의 **제작 어휘만** 빌린다. 원 영상·프롬프트 원문은 쓰지 않는다)

| 코드 | 기법 | 실물 사진을 어떻게 | 어울리는 박 | 기반 규칙 |
|---|---|---|---|---|
| `T1` 누끼 팝 + 그림자 | 누끼 상품이 0프레임부터 크게, 0.3초에 살짝 들리며(스프링) 바닥 그림자가 번짐 | ① | `spring-pop-entrance` |
| `T2` 2.5D 패럴랙스 | 누끼(앞)·배경 색면(뒤)·장식 선(중간)을 다른 속도로 움직여 깊이 | ①② | `viewport-change` |
| `T3` 핫스팟 짚기 | 사진 속 실제 부분(`photo.spots`)에 고리가 그려지고 선이 뻗어 감각어 라벨이 붙음 | ③ | `svg-path-draw`·`coordinate-target-zoom` |
| `T4` 줌 스루 | 카메라가 핫스팟으로 밀고 들어가 질감(기모·니트)을 가득 채움 → 다음 장면으로 빠짐 | ③ | `coordinate-target-zoom`·`multi-phase-camera` |
| `T5` 변화 와이프 | 차가운 색(전) → 따뜻한 색(후)으로 대각선 와이프, 그 위에 상품 | ② | `scale-swap-transition` |
| `T6` 막는 그림 | 바람·물방울 화살표가 날아오다 상품에 닿아 튕겨 나감(닿으면 반응) | ② | `reactive-displacement` |
| `T7` 키네틱 한 줄 | 감각어가 낱말 단위로 꽝꽝(크기 위계), 읽는 동안 정지 | ①③ | `kinetic-beat-slam` |
| `T8` 폰 화면 | 폰 틀 안에서 상품 페이지 같은 일반 카드가 스크롤되다 가격·버튼에서 멈춤(실존 앱 UI 흉내 금지 — 일반 카드) | ⑤ | `3d-page-scroll`(평면) |
| `T9` 가격표 드롭 | 가격 태그가 떨어져 상품에 꽂히고(스프링) 기준일이 작게 붙음 | ⑤ | `spring-pop-entrance` |
| `T10` 상황 컷 스택 | 착용·사용 사진 2~3장이 카드처럼 겹쳐 넘어감(스와이프) | ④ | `split-tilt-cards`(평면) |
| `T11` 근거 점판 | 점(1개 = n명)이 모여 숫자가 됨 — 근거 숫자 1번만 | ③ | `stat-bars-and-fills` |
| `T12` 입자 | 눈송이·김·반짝이 같은 입자가 장면 성격을 말함(장식 아님 — 상품의 쓰임과 연결될 때만) | ①② | `sine-wave-loop`(유한 반복) |
| `T13` 버튼 포인터 | 마지막에 화면 아래 상품 버튼 자리를 큰 화살표가 가리키며 2번 맥박 | ⑤ | `press-release-spring` |

- 회차마다 **3~4개**(⑤의 `T9` 또는 `T8` + `T13` 은 늘 포함), 그중 하나를 **시그니처**로 정한다. 직전 3회차와 시그니처가 겹치지 않게(ledger `technique`). STEP W 의 이번 주 후보를 먼저 본다.
- 공통 문법: 시그니처 장면을 먼저 설계하고 나머지가 그쪽으로 모이게 · 샷마다 카메라 움직임 1개(push-in·pull-out·pan·hold) · 등장 `expo.out`/`power3.out`, 착지·누름은 스프링 · 닿으면 반응 · 주인공에만 빛·그림자 · 발광은 한 곳 · 같은 전환 연속 금지 · 2초 넘게 그대로인 화면 금지 · 그림이 말보다 0~0.3초 먼저.
- **금지**: 3D 장면(사용자 "어색하다") · 모든 요소에 발광 · 이유 없이 도는 물체 · 리뷰 표·라벨·% 그래프 나열 · 실존 앱·쇼핑 화면 흉내 · 브랜드 로고를 따로 그리기(제품 사진에 원래 있는 것은 그대로).

④ **`om_index.html`** — 견본 회차(`v2_2d\om_index.html`)의 뼈대(`<!--HFV-->`·`vendor/gsap.min.js`·`common.css`·`common.js`·`#root[data-composition-id="main"]`·`#stage`·`__W__ __H__ __DUR__`·끝에 `window.__timelines["main"] = tl; tl.seek(0);`)를 따르고:
- 시각은 `V.ev` 에서만, 글자는 `V.txt` 에서만(따옴표 안 한글·숫자 금지 — 기호 `✔ → ↓` 는 됨), 속성 트윈·`tl.set` 만(콜백·`Math.random`·무한 반복 금지, 난수는 `HF.rng`).
- **클립 화면 가림(잠정 — 첫 업로드 캡처로 고친다)**: 글자는 x 80~900 · y 300~1440. 아래 y 1480~1920(제목·설명·상품 스티커)과 오른쪽 x 920~1080·y 900~1700(버튼)에는 글자를 두지 않는다. 자막 상자는 아래 끝 y 1440(`bottom: 480px`). 버튼 화살표(`T13`)는 아래쪽 스티커 자리(y 1500~1700, x 80~500)를 가리킨다.
- **`광고` 표시**: 0프레임부터 끝까지 오른쪽 위(y 300 안팎) 작은 알약 `광고`.
- **낱말 강조 자막**: 8번 루틴 v5.0 STEP 5-OM ③ 의 자막 코드를 그대로(위치만 `bottom: 480px`).
- 첫 화면: 상품 이름이 아니라 **훅 문장이 가장 큰 글자**(최대 144px) + 실물 상품(화면 폭 60% 이상) + 0.3초 안 사건. 상품명은 ②에서 처음 작게.

⑤ **작업 공간 → 샷 점검 → 검사 → 렌더**:
```bash
cd ~/clip_work/{slug}
NEWF="C{nn}_{기법이름}"; T=~/clip_work/hfkit/tools/hf/templates/$NEWF; mkdir -p "$T" && cp om_index.html "$T/index.html" && echo '{"w":1080,"h":1920,"dur":30,"fps":30}' > "$T/template.json"
rm -rf om_ws && mkdir om_ws && NEWF=$NEWF python3 - <<'PY'
import json, os, sys; from pathlib import Path
sys.path.insert(0, os.path.expanduser("~/clip_work/hfkit/tools/hf")); import hf_render
V = json.load(open("hf_vars.json"))
hf_render.build_project(os.environ["NEWF"], V, 1080, 1920, V["dur"], 30, Path("om_ws"))
p = Path("om_ws/common.css"); p.write_text(p.read_text().replace(', "Noto Sans CJK KR"', ""))
PY
NODE_PATH=$(npm root -g) node ~/clip_work/snap.js om_ws /tmp/shot 0 0.6 {샷마다 시각…}      # 한 장으로 붙여 Read — 잘림·겹침·빈 화면·pageerror
~/clip_work/om/.venv/bin/python ~/clip_work/om_render.py om_ws reel-hf.mp4 check          # 오류 0
timeout 560 ~/clip_work/om/.venv/bin/python ~/clip_work/om_render.py om_ws reel-hf.mp4
python3 build_reel_sfx_v2.py reel-final_timeline.json sfx.wav && python3 mix.py && python3 verify_hf_sync.py   # 종료코드 0
```
- 검사 `errors` 는 고친다(`content_overlap` 은 퇴장을 0.2초 당기기·위치 이동). `verify_hf_sync.py` 의 정지 큐는 그 시각 사건을 크게.

## STEP 6. 검수
1. **규격**: 1080×1920 · 30fps · yuv420p · 20~30초 · AAC 2ch.
2. **숫자·사실 대조**: 화면·자막·설명의 모든 숫자·가격·감각어의 근거가 `analysis.json`·`findings.json`·`tips.json`·`models.json`·`post.txt` 에 있는지 스크립트+눈으로. 없으면 고친다.
3. **대표 프레임**(박마다 처음·가운데·끝) 한 장 → `Read`: 가림 구역에 글자 없음 · 실물 상품이 박마다 보임 · `광고` 표시 · 버튼 화살표.
4. **처음 보는 사람 시험**(새 서브에이전트, 판마다 새로): 실제 재생 시각대로 12~16장(자막 조각마다 가운데 1장 + 0.0·1.0·1.5초) + 안내("이 장면들 외에 아무것도 보지 마세요" · "아래 자막 = 내레이션") → (0) 무슨 상품인지 (a) 왜 사고 싶어지는지(또는 왜 아닌지) (b) 끝나고 상품 버튼을 누르겠는가 0~10·이유 (c) 막힌 말·장면('모름'/'짐작') (e) 0.0·1.0·1.5초만 보고 넘기겠는가 (g) 광고처럼 거슬리는 곳·말투.
   - **통과**: (0) 맞음 · (a) STEP 2 의 느낌 중 하나 이상을 자기 말로 · (b) ≥ 7 · (c) '모름' 0 · (e) 안 넘긴다 · (g) "속이는 느낌" 없음.
   - 실패면 지적을 한 번에 고쳐 다시 렌더·시험(최대 4판). 4판에도 안 되면 훅 공식·시그니처 기법을 바꿔 1판부터. 그래도 안 되면 `status: "retry"` 로 남기고 알림 — 다음 같은 원천 회차가 새 소재보다 먼저 이어서 고친다.

## STEP 7. 저장 (PC)
- `{CR}\naver_clip\{작업 폴더}\` 에: `reel-final.mp4` · `cover.jpg`(첫 화면 사건·훅·상품이 다 보이는 시각) · `stills.jpg` · `script.json` · `hf_vars.json` · `build_hf_vars.py` · `om_index.html` · `concepts.md`(사고 싶은 이유·훅·기법·시그니처·시험 판별 기록) · `upload.json`(아래) · `src\`.
- `upload.json`:
```json
{"title": "{30자 안팎 — 효익이 드러나는 상품 말 + 상황, 예: 귀까지 덮는 겨울 넥워머, 찬바람 막는 법}",
 "description": "광고 · 쇼핑 커넥트 활동으로 판매 시 수수료를 받을 수 있어요\n{사고 싶은 이유 2줄}\n{가격} ({기준일} 기준)\n{걸리는 점 팁 1줄(선택)}",
 "hashtags": ["{주제어}", "{상품군}", "{상황}", "{발행정보.txt 태그 중 2개}"],
 "product": {"name": "{models.json.name}", "short": "{short}", "connect_link": "{link}", "connect_pid": "{connect_pid}", "price_won": 0},
 "visibility_wanted": "private_first"}
```
  설명 첫 줄은 항상 광고·수수료 고지. 해시태그 3~5개.
- ledger: `clips["{src}:{폴더}:{key}"] = {date, status: "ready", hook, technique: [...], signature, title, blind: "{점수·판}"}`.

## STEP 8. 업로드 — 브라우저로, 공개 게시는 하지 않는다
1. 브라우저(내장 브라우저 우선, 없으면 Claude in Chrome — 네이버에 로그인된 쪽)로 **네이버 클립 크리에이터 PC 웹**을 연다. 첫 회차는 네이버 검색으로 공식 주소를 찾아 `upload.json` 옆 `clip_web.txt` 에 적어 두고 다음부터 그 주소를 쓴다. 로그인돼 있지 않으면 로그인하지 않고(자격증명 입력 금지) 멈춘 뒤 알림.
2. 영상 파일 선택에는 파일 업로드 도구를 쓴다(내장 브라우저에서 파일을 넣을 수 없으면 Claude in Chrome 의 `file_upload`). 제목·설명·해시태그는 `upload.json` 그대로.
3. **쇼핑 커넥트 상품 붙이기**: 업로드 화면에 상품 연결(쇼핑 커넥트·상품 스티커) 메뉴가 있으면 `connect_pid`/상품명으로 찾아 1개만 붙인다. PC 웹에 그 메뉴가 없으면 붙이지 않고 알림에 "앱에서 상품 스티커를 붙여 주세요"를 적는다.
4. **공개 범위**: `비공개`·`나만 보기` 가 있으면 그것으로 **끝까지 업로드**(사용자 지침 ② — 가능하면 비공개 먼저) → `upload.status = "private_uploaded"`, 클립 주소 기록. 공개 범위 선택이 없으면 **게시 버튼을 누르지 않고** 입력한 상태에서 멈춘다 → `upload.status = "ready_to_post"`(창은 닫지 않는다 — 다음 세션이 다시 채우므로 남겨도 무방).
5. ⛔ 공개 게시·공개 전환은 사용자가 이 세션에서 직접 지시할 때만(그때는 같은 화면에서 공개로 바꾸고, 결과 주소를 ledger 에).
6. 업로드 중 화면이 예상과 다르거나 2번 실패하면 멈추고 알림(영상·업로드 정보는 PC 폴더에 있음).

## STEP 9. 알림 (PushNotification 1회 · 한글)
- 완료: `🎬 {N}. 네이버 클립 {날짜} {src} — {short} {길이}초 · {비공개 업로드 완료|게시 직전 대기} · 확인 후 "올려"라고 답하면 공개합니다` + 줄: `🪝 훅: {코드} "{첫 문장}"` · `✨ 기법: {T 코드들}(시그니처 {T})` · `🧪 시험: 버튼 {b}/10 · {판}판` · `🛒 상품 스티커: {붙임|앱에서 붙여 주세요}` · `📁 {작업 폴더}`.
- 소재 없음: 알림 보내지 않는다(실행 기록만).
- 실패: `⏸️ {N}. 네이버 클립 {날짜} {src} — {단계}에서 멈춤: {사유 한 줄}`.

## STEP 10. 성과 (매주 월요일 aipick 회차에서만)
- 공개된 클립(ledger `status: "posted"`)의 조회·좋아요를 클립 크리에이터 화면에서 읽기만 해서 ledger `stats[날짜]` 에 적고, 14번(쇼핑 커넥트 실적 수집)의 상품별 클릭·판매 기록(`{CR}\…` 14번 문서가 적는 파일)이 있으면 같은 상품의 클립 공개일 전후를 나란히 적는다. 훅 공식·시그니처 기법별 평균을 `refs\{YYYY-Www}.md` 끝에 표로 — 3편 이상 쌓인 것 중 가장 나쁜 조합은 다음 주에 쓰지 않는다.

---

## 🚨 오류 처리

| 상황 | 조치 |
|---|---|
| PC 미연결 | 아무것도 바꾸지 않고 실패 알림 |
| 소재 없음 | 실행 기록만(알림 없음) |
| Edge 음성 실패 | 1회 재시도 → 실패 알림, `retry` |
| OpenMontage 준비·렌더 실패 | 1회 재시도 → 키트 기본 렌더(`hf_render.py`, 같은 작업 공간 템플릿) → 실패면 `retry` |
| 싱크·시험 불통과 | STEP 6 대로 고쳐 다시(통과 전에는 업로드하지 않는다) |
| 네이버 로그인 안 됨·화면 다름 | 업로드 단계에서 멈추고 알림(로그인·자격증명 입력 금지) |
| 상품 스티커 메뉴 없음 | 붙이지 않고 알림에 적음 |
| 9번·12번이 아직 쓰는 중 | 그 폴더 건너뜀 |

## ⚠️ 전제조건 (사용자 몫)

| 항목 | 상태 |
|---|---|
| 이 문서 `{CR}\blog\Schd_NaverClip.md` 저장 | ⬜ |
| 예약 작업 2개: `15. 네이버 클립 — aipick`(매일 05:00) · `16. 네이버 클립 — kids`(매일 05:30) — 같은 이 문서를 쓴다 | ✅ 2026-11-28 등록 · 두 작업에 '이 컴퓨터 필요' 켜기 ⬜ |
| 네이버 클립 채널(aipick·kidspick 계정) · 쇼핑 커넥트 크리에이터 연결 | ⬜ 확인 필요 — 어느 네이버 계정으로 올릴지 |
| 브라우저(내장 또는 Chrome)에 그 계정 로그인 | ⬜ |
| 첫 업로드 뒤 폰 화면 캡처 1장(가림 구역 확정) | ⬜ |
| 상품 사진 사용(판매자 상세 사진) 가능 여부 — 쇼핑 커넥트 이용 조건 | ⬜ 확인 권장 |

## 원라이너
원천 정하기(0) → 완성된 글의 1위 상품 중 아직 클립이 없는 것(1) → 리뷰를 사고 싶은 이유로 번역(2) → 훅 공식·5박 대본·대본 시험(3) → Edge 음성 + 낱말 시각(4) → 실물 사진 누끼·핫스팟 → 2D 기법 3~4개(시그니처 1)로 회차 화면 → 샷 점검·검사·렌더·싱크(5) → 규격·사실 대조·처음 보는 사람 시험(버튼 ≥ 7)(6) → PC 저장·`upload.json`(7) → 브라우저로 비공개 업로드 또는 게시 직전 정지(8) → 알림(9) → 주 1회 성과(10) → 실행 기록.

---

## 🧾 마지막 STEP — 실행 기록 한 줄 (관제탑용)
어떤 경로로 끝나든 끝내기 직전에 `{CR}\control_tower\runs\YYYY-MM.jsonl` 에 한 줄(없으면 만든다, 기존 줄은 고치지 않는다).
```bash
python3 - <<'PY'
import json, os, datetime
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
root = os.path.expanduser("~/mnt/Claude/control_tower/runs"); os.makedirs(root, exist_ok=True)
rec = {"routine": "{N}. 네이버 클립", "file": "Schd_NaverClip.md", "date": now.strftime("%Y-%m-%d"),
       "start": "{시작 HH:MM}", "end": now.strftime("%H:%M"), "result": "{성공|부분|건너뜀|실패}",
       "count": 0, "summary": "{src} {한 줄 요약}", "warnings": []}
with open(os.path.join(root, now.strftime("%Y-%m") + ".jsonl"), "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
PY
```
