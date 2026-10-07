#!/usr/bin/env python3
"""릴스 엔진 영상의 장면 1개를 HyperFrames 장면으로 바꿔 끼운다 — blog/tools/hf (v1.0 · 2026-10-08)

0and1life 인스타 릴스 루틴(Schd_0and1Life-Insta STEP 6-HF)이 부른다. 엔진(reel_engine.py)은 그대로 두고,
엔진이 만든 무음 mp4 의 [장면 시작, 장면 끝 + 전환 0.12초] 구간만 HF 화면으로 바꾼다.

    python hf_reel_insert.py --spec reel_spec.json --scene 0 --vars hf_vars.json \
        --video reel-final.mp4 --timeline reel-final_timeline.json --out reel-final-hf.mp4 \
        --stills stills --cover reel-final_cover.jpg --cover-t 1.6 --engine reel_engine.py

지키는 것 (하나라도 어긋나면 종료코드 2 — 루틴은 엔진 영상을 그대로 쓴다)
  ① 길이·프레임 수·규격(1080×1920·30fps)·오디오 트랙이 원본과 같다. 효과음 타임라인을 건드리지 않는다
  ② 그 장면의 효과음 큐(0초 제외)마다 HF 요소가 같은 시각(±0.05초)에 등장하고, 화면이 실제로 변한다
  ③ 장면 전환(가로 스와이프 0.12초 + 펀치 인)은 엔진 공식(e_io, XF=0.12, 줌 1.06)을 그대로 재현해 이어 붙인다
  ④ CTA 장면은 바꾸지 않는다(계정 행 화살표가 엔진 전용)
  ⑤ 엔진 상수가 이 스크립트가 아는 값과 다르면(엔진 개정) 아무것도 하지 않는다
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hf_render  # noqa: E402

W, H, FPS, XF, ZOOM = 1080, 1920, 30, 0.12, 0.06


def e_io(t):
    t = max(0.0, min(1.0, t))
    return 3 * t * t - 2 * t ** 3


def check_engine(path):
    src = Path(path).read_text(encoding="utf-8", errors="replace")
    need = [r"^W, H, FPS = 1080, 1920, 30\s*$", r"^XF = 0\.12\s*$", r"return 3 \* t \* t - 2 \* t \*\* 3",
            r"z = 1\.0 \+ 0\.06 \* \(1 - p\)", r"cv\.paste\(prev, \(-off, 0\)\)", r"cv\.paste\(im, \(W - off, 0\)\)"]
    miss = [n for n in need if not re.search(n, src, re.M)]
    if miss:
        raise hf_render.Fail("engine", "엔진 전환 공식이 바뀌었다 — HF 장면 끼우기 중지", "; ".join(miss))


def ff(cmd, timeout=300):
    code, log = hf_render._run([hf_render._which("ffmpeg") or "ffmpeg"] + cmd, timeout=timeout)
    if code:
        raise hf_render.Fail("ffmpeg", "ffmpeg 실패", log[-800:])


def frames(video, d, f0=None, f1=None):
    d.mkdir(parents=True, exist_ok=True)
    vf = [] if f0 is None else ["-vf", f"select='between(n\\,{f0}\\,{f1})'"]
    ff(["-y", "-v", "error", "-i", str(video)] + vf + ["-vsync", "0", "-start_number", "0", str(d / "%05d.png")])
    return sorted(d.glob("*.png"))


def count_frames(video):
    code, out = hf_render._run([hf_render._which("ffprobe") or "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
                                "-show_entries", "stream=nb_read_frames,width,height,r_frame_rate", "-of", "json", str(video)], timeout=120)
    s = json.loads(out[out.find("{"):])["streams"][0]
    code2, out2 = hf_render._run([hf_render._which("ffprobe") or "ffprobe", "-v", "error", "-select_streams", "a",
                                  "-show_entries", "stream=codec_name", "-of", "csv=p=0", str(video)], timeout=60)
    return int(s["nb_read_frames"]), int(s["width"]), int(s["height"]), s["r_frame_rate"], bool(out2.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--scene", type=int, required=True)
    ap.add_argument("--vars", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--timeline", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--template", default="reel_scene")
    ap.add_argument("--stills")
    ap.add_argument("--cover")
    ap.add_argument("--cover-t", type=float)
    ap.add_argument("--engine")
    ap.add_argument("--timeout", type=int, default=300)
    a = ap.parse_args()
    work = Path(tempfile.mkdtemp(prefix="hfri_"))
    try:
        from PIL import Image, ImageChops, ImageStat

        if a.engine:
            check_engine(a.engine)
        spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
        scenes = spec["scenes"]
        i = a.scene
        if not (0 <= i < len(scenes)):
            raise hf_render.Fail("args", f"장면 번호 범위 밖: {i}")
        sp = scenes[i]
        if sp.get("type") == "cta":
            raise hf_render.Fail("args", "CTA 장면은 HF 로 바꾸지 않는다")
        durs = [float(s["dur"]) for s in scenes]
        start, dur, total = round(sum(durs[:i]), 4), durs[i], round(sum(durs), 4)
        has_next = i < len(scenes) - 1
        tail = XF + 2.0 / FPS if has_next else 0.0

        # ② 효과음 큐 ↔ HF 요소 시각 대조
        tlj = json.loads(Path(a.timeline).read_text(encoding="utf-8"))
        if abs(float(tlj["duration"]) - total) > 0.02:
            raise hf_render.Fail("spec", f"타임라인 길이 {tlj['duration']} ≠ spec 합 {total}")
        cues = sorted({round(c - start, 2) for c, _ in tlj["cues"] if start - 1e-6 <= c < start + dur - 1e-6})
        v = json.loads(Path(a.vars).read_text(encoding="utf-8"))
        beats = {k: (b[0] if isinstance(b, list) else float(b)) for k, b in (sp.get("beats") or {}).items()}
        beats.update(v.get("beats") or {})
        v["beats"] = beats
        v.setdefault("bg", sp.get("bg", "paper"))
        v.setdefault("series", sp.get("series"))
        v.setdefault("foot", sp.get("foot", spec.get("source", "")))
        times = []
        for el in v.get("els", []):
            at = el.get("at", 0)
            if isinstance(at, (int, float)):
                times.append(float(at))
            elif at in beats:
                times.append(float(beats[at]))
            else:
                raise hf_render.Fail("sync", f"요소 시각 '{at}' 를 beats 에서 찾지 못함")
        missing = [c for c in cues if c > 0.001 and not any(abs(c - t) <= 0.051 for t in times)]
        if missing:
            raise hf_render.Fail("sync", f"효과음 큐에 맞는 HF 요소 없음: {missing}")

        # HF 렌더 (다음 장면 전환 구간까지 조금 더 길게)
        clip = work / "hf.mp4"
        hf_render.render(a.template, v, clip, dur=round(dur + tail, 3), timeout=a.timeout)
        B = frames(clip, work / "B")

        # ② 화면이 실제로 변하는가 — 큐 직전 프레임 vs 큐 + 4프레임
        for c in cues:
            if c <= 0.001:
                continue
            k0, k1 = max(int(round(c * FPS)) - 1, 0), min(int(round(c * FPS)) + 4, len(B) - 1)
            d = ImageStat.Stat(ImageChops.difference(Image.open(B[k0]).convert("L").resize((270, 480)),
                                                     Image.open(B[k1]).convert("L").resize((270, 480)))).mean[0]
            if d < 0.6:
                raise hf_render.Fail("sync", f"{c}초 큐에서 화면 변화가 없음(평균 차 {d:.2f})")

        # 엔진 프레임 구간
        f0 = int(round(start * FPS))
        f1 = int(round((start + dur + tail) * FPS)) - 1 if has_next else int(round((start + dur) * FPS)) - 1
        n_total, vw, vh, rate, has_audio = count_frames(a.video)
        f1 = min(f1, n_total - 1)
        A = frames(a.video, work / "A", f0, f1)
        if len(A) != f1 - f0 + 1 or len(B) < len(A):
            raise hf_render.Fail("frames", f"프레임 수 불일치 엔진 {len(A)} / HF {len(B)} / 기대 {f1 - f0 + 1}")

        # ③ 합성
        Cdir = work / "C"
        Cdir.mkdir()
        for k in range(len(A)):
            lt = (f0 + k) / FPS - start
            hfim = Image.open(B[k]).convert("RGB")
            if i > 0 and lt < XF - 1e-9:
                p = e_io(lt / XF)
                z = 1.0 + ZOOM * (1 - p)
                zw, zh = int(W * z), int(H * z)
                hz = hfim.resize((zw, zh), Image.BILINEAR).crop(((zw - W) // 2, (zh - H) // 2, (zw - W) // 2 + W, (zh - H) // 2 + H))
                off = int(W * p)
                im = Image.open(A[k]).convert("RGB")
                if off > 0:
                    im.paste(hz.crop((0, 0, off, H)), (W - off, 0))
            elif lt < dur - 1e-9:
                im = hfim
            else:
                p = e_io((lt - dur) / XF)
                off = int(W * p)
                im = Image.open(A[k]).convert("RGB")
                if off < W:
                    im.paste(hfim.crop((off, 0, W, H)), (0, 0))
            im.save(Cdir / f"{k:05d}.png", compress_level=1)

        out = Path(a.out)
        ff(["-y", "-v", "error", "-i", str(a.video), "-framerate", str(FPS), "-i", str(Cdir / "%05d.png"),
            "-filter_complex", f"[1:v]setpts=PTS+{f0}/{FPS}/TB[ov];[0:v][ov]overlay=eof_action=pass:shortest=0[v]",
            "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-level", "4.1", "-r", str(FPS), "-g", str(FPS * 2), "-c:a", "copy",
            "-movflags", "+faststart", str(out)], timeout=600)

        # ① 규격 대조
        n2, w2, h2, rate2, aud2 = count_frames(out)
        if (n2, w2, h2, rate2, aud2) != (n_total, vw, vh, rate, has_audio):
            raise hf_render.Fail("verify", f"원본과 다름: {n2},{w2}x{h2},{rate2},audio={aud2} vs {n_total},{vw}x{vh},{rate},audio={has_audio}")
        chk = work / "chk.png"
        mid = f0 + min(int(dur * FPS / 2), len(A) - 1)
        ff(["-y", "-v", "error", "-i", str(out), "-vf", f"select='eq(n\\,{mid})'", "-vsync", "0", "-frames:v", "1", str(chk)])
        d = ImageStat.Stat(ImageChops.difference(Image.open(chk).convert("L"), Image.open(Cdir / f"{mid - f0:05d}.png").convert("L"))).mean[0]
        if d > 4.0:
            raise hf_render.Fail("verify", f"합성 위치가 어긋남(중간 프레임 차 {d:.1f})")

        # 스틸·커버는 임시로 먼저 만들고, 모든 검사가 끝난 뒤 한 번에 바꾼다(중간 실패 시 원본 그대로)
        stills_new = []
        if a.stills:
            for tt in sorted({0.0, min(dur - 0.05, 1.6), dur - 0.05}):
                k = min(int(round(tt * FPS)), len(B) - 1)
                stills_new.append((B[k], f"s{i}_{sp['type']}_{tt:.2f}.png"))
        cover_tmp = None
        if a.cover and a.cover_t is not None and start <= a.cover_t < start + dur + tail:
            cover_tmp = work / "cover.jpg"
            ff(["-y", "-v", "error", "-ss", f"{a.cover_t}", "-i", str(out), "-frames:v", "1", "-q:v", "2", str(cover_tmp)])
        if a.stills:
            sd = Path(a.stills)
            sd.mkdir(parents=True, exist_ok=True)
            for old in sd.glob(f"s{i}_*.png"):
                old.unlink()
            for src, name in stills_new:
                shutil.copy2(src, sd / name)
        cover_redone = False
        if cover_tmp is not None:
            shutil.copy2(cover_tmp, a.cover)
            cover_redone = True
        print(json.dumps({"ok": True, "scene": i, "type": sp.get("type"), "start": start, "dur": dur, "frames": len(A),
                          "cues_checked": [c for c in cues if c > 0.001], "cover_redone": cover_redone, "out": str(out)},
                         ensure_ascii=False))
        sys.exit(0)
    except hf_render.Fail as e:
        Path(a.out).unlink(missing_ok=True)          # 실패하면 결과 파일을 남기지 않는다(루틴은 엔진판을 쓴다)
        print(json.dumps({"ok": False, "stage": e.stage, "reason": e.reason, "tail": e.tail[-600:]}, ensure_ascii=False))
        sys.exit(2)
    except Exception as e:
        Path(a.out).unlink(missing_ok=True)
        print(json.dumps({"ok": False, "stage": "unexpected", "reason": f"{type(e).__name__}: {e}"}, ensure_ascii=False))
        sys.exit(2)
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
