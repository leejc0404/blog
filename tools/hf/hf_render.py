#!/usr/bin/env python3
"""HyperFrames 렌더 래퍼 — blog/tools/hf (v1.0 · 2026-10-08)

템플릿(templates/<이름>/index.html) + 값(JSON) → MP4 / MOV / WebP / PNG.
클라우드 작업 공간(리눅스)과 사용자 PC(윈도우) 어디서든 같은 명령으로 돈다.

    python hf_render.py stat_bars vars.json out.mp4 --poster out-poster.webp
    python hf_render.py stat_bars vars.json out.webp            # 정적 1장(마지막 프레임)
    python hf_render.py reel_scene vars.json clip.mp4 --dur 2.9

옵션
  --size WxH      캔버스 크기 (기본: 템플릿 template.json)
  --dur SEC       길이 (기본: vars.dur → 템플릿 기본값)
  --fps N         프레임 수 (기본: 템플릿 기본값, 보통 30)
  --poster PATH   마지막 프레임을 WebP 로 저장 (블로그 <video poster>)
  --still SEC     OUT 이 .webp/.png 일 때 뽑을 시각 (기본: 마지막 프레임)
  --timeout SEC   렌더 제한 시간 (기본 300)
  --keep          작업 폴더를 지우지 않는다 (디버그)

규칙 (루틴이 기대는 약속 — 바꾸지 않는다)
  · 종료코드 0 = 성공, 2 = 실패. 실패해도 예외를 던지지 않는다.
    호출한 루틴은 2를 받으면 HF 단계만 건너뛰고 기존 경로로 간다.
  · 표준출력 마지막 줄은 항상 JSON 한 줄: {"ok": true|false, ...}
  · HyperFrames 버전은 HF_VERSION 으로 고정한다. 올릴 때는 이 파일만 고치고 템플릿 전부를 다시 시험한다.
  · 외부 CDN 을 쓰지 않는다. GSAP·Pretendard 는 npm 레지스트리에서 받아 ~/.cache/hf-kit 에 둔다
    (클라우드는 jsdelivr·storage.googleapis 가 막혀 있다 — 2026-10-08 실측).
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

HF_VERSION = "0.8.140"
GSAP_VERSION = "3.14.2"
PRETENDARD_VERSION = "1.3.9"
FONT_WEIGHTS = ["Black", "ExtraBold", "Bold", "SemiBold", "Medium"]

KIT = Path(__file__).resolve().parent
CACHE = Path(os.environ.get("HF_KIT_CACHE", str(Path.home() / ".cache" / "hf-kit")))


class Fail(Exception):
    def __init__(self, stage, reason, tail=""):
        super().__init__(reason)
        self.stage, self.reason, self.tail = stage, reason, tail


def _which(name):
    p = shutil.which(name)
    if not p and os.name == "nt":
        p = shutil.which(name + ".cmd") or shutil.which(name + ".exe")
    return p


def _run(cmd, cwd=None, timeout=120, env=None):
    r = subprocess.run(cmd, cwd=cwd, timeout=timeout, env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def _npm_pack(spec, members, dest):
    """npm pack 으로 tgz 를 받아 필요한 파일만 dest 로 꺼낸다."""
    npm = _which("npm")
    if not npm:
        raise Fail("assets", "npm 없음")
    tmp = Path(tempfile.mkdtemp(prefix="hfk_pack_"))
    try:
        code, out = _run([npm, "pack", spec, "--silent", "--pack-destination", str(tmp)], timeout=180)
        tgz = sorted(tmp.glob("*.tgz"))
        if code or not tgz:
            raise Fail("assets", f"npm pack {spec} 실패", out[-600:])
        with tarfile.open(tgz[0]) as tf:
            for m in members:
                f = tf.extractfile(m)
                if f is None:
                    raise Fail("assets", f"{spec} 안에 {m} 없음")
                (dest / Path(m).name).write_bytes(f.read())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def ensure_assets():
    CACHE.mkdir(parents=True, exist_ok=True)
    gsap = CACHE / "gsap.min.js"
    if not gsap.exists() or gsap.stat().st_size < 10000:
        _npm_pack(f"gsap@{GSAP_VERSION}", ["package/dist/gsap.min.js"], CACHE)
    fonts = [CACHE / f"Pretendard-{w}.woff2" for w in FONT_WEIGHTS]
    if not all(f.exists() and f.stat().st_size > 10000 for f in fonts):
        _npm_pack(f"pretendard@{PRETENDARD_VERSION}",
                  [f"package/dist/web/static/woff2/Pretendard-{w}.woff2" for w in FONT_WEIGHTS], CACHE)
    marker = CACHE / f"telemetry_off_{HF_VERSION}"
    if not marker.exists():
        npx = _which("npx")
        if npx:
            try:
                _run([npx, "-y", f"hyperframes@{HF_VERSION}", "telemetry", "disable"], timeout=180)
                marker.write_text("1")
            except Exception:
                pass
    return gsap, fonts


def browser_env():
    env = dict(os.environ)
    env["HYPERFRAMES_SKIP_SKILLS"] = "1"
    env.setdefault("NO_UPDATE_NOTIFIER", "1")
    env.setdefault("PYTHONUTF8", "1")
    if sys.platform.startswith("linux") and not env.get("HYPERFRAMES_BROWSER_PATH"):
        # 클라우드 작업 공간: HyperFrames 가 chrome-headless-shell 을 내려받지 못한다(403).
        # 미리 설치된 Playwright 헤드리스 셸을 쓴다.
        cands = sorted(glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-linux*/headless_shell"))
        cands += sorted(glob.glob(str(Path.home() / ".cache/ms-playwright/chromium_headless_shell-*/chrome-linux*/headless_shell")))
        cands += sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
        if cands:
            env["HYPERFRAMES_BROWSER_PATH"] = cands[-1]
    return env


def probe(path):
    ffprobe = _which("ffprobe")
    if not ffprobe:
        raise Fail("verify", "ffprobe 없음")
    code, out = _run([ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries",
                      "stream=width,height:format=duration", "-of", "json", str(path)], timeout=60)
    if code:
        raise Fail("verify", "ffprobe 실패", out[-400:])
    j = json.loads(out[out.find("{"):])
    s = (j.get("streams") or [{}])[0]
    return int(s.get("width", 0)), int(s.get("height", 0)), float(j.get("format", {}).get("duration", 0))


def grab(video, t, out, quality=88):
    ffmpeg = _which("ffmpeg")
    if not ffmpeg:
        raise Fail("still", "ffmpeg 없음")
    cmd = [ffmpeg, "-y", "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", str(video), "-frames:v", "1"]
    if str(out).lower().endswith(".webp"):
        cmd += ["-c:v", "libwebp", "-quality", str(quality)]
    code, log = _run(cmd + [str(out)], timeout=60)
    if code or not Path(out).exists():
        raise Fail("still", f"프레임 추출 실패 {out}", log[-400:])


def build_project(template, vars_, w, h, dur, fps, work):
    tdir = KIT / "templates" / template
    if not (tdir / "index.html").exists():
        raise Fail("template", f"템플릿 없음: {template}")
    gsap, fonts = ensure_assets()
    common = KIT / "templates" / "_common"
    for p in (common.iterdir() if common.is_dir() else []):
        if p.is_file():
            shutil.copy2(p, work / p.name)
    for p in tdir.iterdir():
        if p.is_file() and p.name != "template.json":
            shutil.copy2(p, work / p.name)
    (work / "vendor").mkdir(exist_ok=True)
    shutil.copy2(gsap, work / "vendor" / "gsap.min.js")
    (work / "fonts").mkdir(exist_ok=True)
    for f in fonts:
        shutil.copy2(f, work / "fonts" / f.name)
    # 값 안의 로컬 이미지 경로(키 이름이 img/image/photo 로 끝나는 것)는 작업 폴더로 복사해 상대경로로 바꾼다
    def _assets(o):
        if isinstance(o, dict):
            for k, v in list(o.items()):
                if isinstance(v, str) and k.lower().endswith(("img", "image", "photo")) and Path(v).is_file():
                    dst = work / "assets" / Path(v).name
                    dst.parent.mkdir(exist_ok=True)
                    shutil.copy2(v, dst)
                    o[k] = "assets/" + dst.name
                else:
                    _assets(v)
        elif isinstance(o, list):
            for v in o:
                _assets(v)
    _assets(vars_)
    v = dict(vars_)
    v.update({"W": w, "H": h, "DUR": dur, "FPS": fps})
    payload = json.dumps(v, ensure_ascii=False).replace("</", "<\\/")
    html = (tdir / "index.html").read_text(encoding="utf-8")
    html = (html.replace("__W__", str(w)).replace("__H__", str(h)).replace("__DUR__", f"{dur:g}")
                .replace("<!--HFV-->", f"<script>window.HFV = {payload};</script>"))
    (work / "index.html").write_text(html, encoding="utf-8")


def render(template, vars_, out, size=None, dur=None, fps=None, poster=None, still=None,
           timeout=300, keep=False):
    """모듈로 불러 쓸 때의 진입점. 성공하면 결과 dict, 실패하면 Fail 예외."""
    t0 = time.time()
    tdir = KIT / "templates" / template
    meta = json.loads((tdir / "template.json").read_text(encoding="utf-8")) if (tdir / "template.json").exists() else {}
    w, h = (size or (meta.get("w", 1080), meta.get("h", 1920)))
    dur = float(dur or vars_.get("dur") or meta.get("dur", 6))
    fps = int(fps or meta.get("fps", 30))
    out = Path(out).resolve()
    ext = out.suffix.lower()
    if ext not in (".mp4", ".mov", ".webp", ".png"):
        raise Fail("args", f"지원하지 않는 출력 형식 {ext}")
    work = Path(tempfile.mkdtemp(prefix="hfk_"))
    try:
        build_project(template, dict(vars_), int(w), int(h), dur, fps, work)
        npx = _which("npx")
        if not npx:
            raise Fail("render", "npx 없음")
        tmp_out = work / ("render.mov" if ext == ".mov" else "render.mp4")
        cmd = [npx, "-y", f"hyperframes@{HF_VERSION}", "render", "-o", str(tmp_out), "--fps", str(fps)]
        if ext == ".mov":
            cmd += ["--format", "mov"]
        try:
            code, log = _run(cmd, cwd=str(work), timeout=timeout, env=browser_env())
        except subprocess.TimeoutExpired:
            raise Fail("render", f"제한 시간 {timeout}초 초과")
        if code or not tmp_out.exists():
            raise Fail("render", "hyperframes render 실패", log[-1200:])
        rw, rh, rd = probe(tmp_out)
        if (rw, rh) != (int(w), int(h)) or abs(rd - dur) > 0.2:
            raise Fail("verify", f"규격 불일치 {rw}x{rh} {rd:.2f}s (기대 {w}x{h} {dur:.2f}s)")
        last = max(dur - 1.0 / fps, 0)
        out.parent.mkdir(parents=True, exist_ok=True)
        if ext in (".mp4", ".mov"):
            shutil.move(str(tmp_out), str(out))
        else:
            grab(tmp_out, last if still is None else float(still), out)
        if poster:
            grab(out if ext in (".mp4", ".mov") else tmp_out, last, Path(poster).resolve(), 85)
        return {"ok": True, "template": template, "out": str(out), "poster": str(poster) if poster else None,
                "w": int(w), "h": int(h), "dur": round(dur, 3), "bytes": out.stat().st_size,
                "secs": round(time.time() - t0, 1), "hf": HF_VERSION}
    finally:
        if keep:
            print(f"작업 폴더 보존: {work}", file=sys.stderr)
        else:
            shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="HyperFrames 템플릿 렌더 (실패 시 종료코드 2)")
    ap.add_argument("template")
    ap.add_argument("vars")
    ap.add_argument("out")
    ap.add_argument("--size")
    ap.add_argument("--dur", type=float)
    ap.add_argument("--fps", type=int)
    ap.add_argument("--poster")
    ap.add_argument("--still", type=float)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    try:
        vars_ = json.loads(Path(a.vars).read_text(encoding="utf-8"))
        size = tuple(int(x) for x in a.size.lower().split("x")) if a.size else None
        res = render(a.template, vars_, a.out, size, a.dur, a.fps, a.poster, a.still, a.timeout, a.keep)
        print(json.dumps(res, ensure_ascii=False))
        sys.exit(0)
    except Fail as e:
        print(json.dumps({"ok": False, "stage": e.stage, "reason": e.reason, "tail": e.tail[-600:]}, ensure_ascii=False))
        sys.exit(2)
    except Exception as e:  # 어떤 오류든 루틴을 멈추지 않는다
        print(json.dumps({"ok": False, "stage": "unexpected", "reason": f"{type(e).__name__}: {e}"}, ensure_ascii=False))
        sys.exit(2)


if __name__ == "__main__":
    main()
