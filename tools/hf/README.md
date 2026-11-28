# tools/hf — HyperFrames 장면 키트 (v1.0 · 2026-10-08)

HTML 템플릿에 값(JSON)만 넣어 MP4·WebP를 만든다. 루틴은 이 키트를 **선택 단계**로만 쓴다.
**HF 단계가 실패하면 그 단계만 건너뛰고 기존 경로로 간다.** 기존 엔진·스크립트(`reel_engine.py`·`shorts_maker.py`·AIPick `scripts\`)는 이 키트를 모르고, 바뀌지 않는다.

## 파일

| 파일 | 하는 일 |
|---|---|
| `hf_render.py` | 템플릿 + 값 → mp4 / mov / webp / png. 실패 시 종료코드 **2** + JSON 한 줄 |
| `hf_reel_insert.py` | 인스타 릴스: 엔진 영상의 장면 1개를 HF 장면으로 바꿔 끼움(길이·전환·효과음 싱크 보존 검사 포함) |
| `templates/_common/` | 공통 폰트·도우미 (Pretendard·GSAP는 npm에서 받아 `~/.cache/hf-kit` 에 둔다 — CDN 안 씀) |
| `templates/<이름>/` | 템플릿 6종 (아래) |
| `examples/*.json` | 템플릿별 시험 값 — 2026-10-08 클라우드에서 전부 렌더 통과 |

## 템플릿

| 이름 | 크기·길이 기본 | 누가 쓰나 | 핵심 값 |
|---|---|---|---|
| `reel_scene` | 1080×1920 · 엔진 장면 길이 | 인스타 릴스(Schd_0and1Life-Insta STEP 6-HF) | `els[{kind, at, …}]` — head·big·card·sticker·bar·circle·burst·spark·meme·zoom·flash |
| `stat_bars` | 1280×720 · 7.4초(마지막 2초 정지) | 0and1life·KoreaPlug 이미지 루틴 설명컷(막대 비교) | `title` `items[{label,value,text,tone}]` `highlight` `badge` `source` `theme: ol·kp` |
| `steps_flow` | 1280×720 · 7.4초 | 이미지 루틴 설명컷(단계 흐름·절차) | `title` `steps[{label,sub}]` `warn` `warn_text` `source` `theme` |
| `review_bars` | 1080×1920 · 15초 | AIPick 클립(네이버 클립 수동 업로드용) | `group` `n_text` `quote` `quote_hl` `product` `pros` `cons` `picks` `disclosure` |
| `info_card` | 1080×1920 · 6초 | KoreaPlug 쇼츠 B-roll(가격·조건 카드) | `kicker` `title` `rows[{label,value,sub}]` `highlight` `note` `source` |
| `hangul_build` | 1080×1920 · 6초 | KoreaPlug 쇼츠 B-roll(한글 읽기) | `word` `roman` `meaning` `hint` `kicker` |

공통 규칙: 숫자·문구는 **원문 그대로** 값에 넣는다(템플릿은 새 숫자를 만들지 않는다). 블로그 테마(`ol`·`kp`)는 숫자 올라가기 효과를 기본으로 끈다 — 최종 프레임(포스터)은 언제나 값의 `text` 그대로다.

## 명령

```bash
# 클라우드 작업 공간 (루틴이 쓰는 곳). 키트는 GitHub 공개 저장소에서 받는다
git clone --depth 1 https://github.com/leejc0404/blog /tmp/blogkit && K=/tmp/blogkit/tools/hf
python3 $K/hf_render.py stat_bars vars.json out.mp4 --poster out-poster.webp          # 0and1life 1280×720
python3 $K/hf_render.py stat_bars vars.json out.mp4 --size 1226x768 --poster p.webp   # KoreaPlug
python3 $K/hf_render.py steps_flow vars.json still.webp                               # 정적 1장(마지막 프레임)
python3 $K/hf_render.py review_bars vars.json clip.mp4
python3 $K/hf_reel_insert.py --spec reel_spec.json --scene 0 --vars hf_vars.json --video reel-final.mp4 \
  --timeline reel-final_timeline.json --out reel-final-hf.mp4 --stills stills --cover reel-final_cover.jpg --cover-t 1.6 --engine reel_engine.py
```

- 첫 실행은 npm에서 HyperFrames·GSAP·Pretendard를 받느라 1~2분 더 걸린다. 렌더 자체는 7초 1280×720 약 14초, 15초 세로 약 40초(클라우드 실측)
- 클라우드에서는 HyperFrames가 크롬을 내려받지 못해(403) `/opt/pw-browsers` 의 헤드리스 셸을 자동으로 쓴다
- PC(윈도우)에서도 같은 명령이 돈다(`py -3.12 hf_render.py …`). Node 22 이상·ffmpeg가 PATH에 있어야 한다

## 인스타 릴스 v4.1 (2026-11-22) — OpenMontage 경로와의 관계

- 8번 릴스 루틴(`Schd_0and1Life-Insta` v4.1)의 기본 렌더는 이 키트가 아니라 **OpenMontage `hyperframes_compose`**(HyperFrames `0.9.80` 고정)다. 이 키트는 두 가지로만 쓴다: ① `hf_render.build_project` — 회차마다 새로 지은 `om_index.html` 에 GSAP·Pretendard·사진·값(`window.HFV`)을 넣어 작업 공간을 만든다(템플릿 폴더 `templates/F{nn}_om_*` 는 클라우드에서만 잠깐 생긴다 — 커밋하지 않는다) ② OpenMontage 가 실패했을 때 F27c 포맷으로 `hf_render.py` 대체 렌더.
- OpenMontage 검사(`hyperframes lint`)는 `@font-face` 선언이 없는 글꼴 이름을 오류로 본다. `_common/common.css` 의 `"Noto Sans CJK KR"` 대체 글꼴은 다른 루틴(3·4·9번)을 위해 그대로 두고, 릴스 루틴이 작업 공간 사본에서만 뺀다.
- 이 키트의 `HF_VERSION`(0.8.140)과 OpenMontage 경로의 판(0.9.80)은 따로 관리한다. 2026-11-22 F27c 회차를 0.9.80 으로 다시 렌더해 화면이 같음을 확인했다.

## 바꿀 때

- HyperFrames 버전은 `hf_render.py` 의 `HF_VERSION` 한 줄로 고정한다(현재 `0.8.140`). 올리면 `examples/*.json` 6개를 전부 다시 렌더해 눈으로 확인한 뒤 커밋한다
- 엔진(`reel_engine.py`)의 전환 공식(XF·e_io·줌)이 바뀌면 `hf_reel_insert.py` 가 스스로 멈춘다(종료코드 2). 그때는 이 스크립트의 상수를 엔진에 맞춰 고친다
- 템플릿을 고치면 그 템플릿의 예시를 렌더해 0초·중간·마지막 프레임을 확인한다

## 변경 기록

- **2026-11-29 · `steps_flow`·`stat_bars` 배치 (스킬 패스 D — `{CR}\skills\ROUTINE-SKILLS.md`)**: 실제 설명컷 3장(WP 미디어 2833·2835·2851)에서 내용이 위 70%에 몰리고 출처 위가 높이의 약 20% 비던 것, 두 줄 제목 카드만 번호 동그라미가 올라가 줄이 어긋나던 것을 고쳤다. ① `steps_flow` — 카드 안 위쪽 맞춤(번호 줄 정렬, 높이 차 19~30px → 1px) · 번호 동그라미 `flex-shrink:0`(두 줄 카드에서 납작해지지 않게) · 카드 묶음을 머리말과 출처 사이 세로 가운데로 ② `stat_bars` — **가로 컷만**: 행 높이 상한 150→190px(행이 적으면 막대가 굵어짐, 75→94px) · 남는 공간을 위아래로 나눔 · 첫 행 강조 꼬리표는 위에 자리. 세로(W<H)는 예전과 픽셀 단위로 같음. 색·글자 크기·숫자·움직임은 그대로. 확인: 예시 4개(ol·kp) + 첫 행 강조 + 세로 1080×1920 + 실제 컷 3장, 0.05·1.4·3.0초·마지막 프레임.
