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

## 바꿀 때

- HyperFrames 버전은 `hf_render.py` 의 `HF_VERSION` 한 줄로 고정한다(현재 `0.8.140`). 올리면 `examples/*.json` 6개를 전부 다시 렌더해 눈으로 확인한 뒤 커밋한다
- 엔진(`reel_engine.py`)의 전환 공식(XF·e_io·줌)이 바뀌면 `hf_reel_insert.py` 가 스스로 멈춘다(종료코드 2). 그때는 이 스크립트의 상수를 엔진에 맞춰 고친다
- 템플릿을 고치면 그 템플릿의 예시를 렌더해 0초·중간·마지막 프레임을 확인한다
