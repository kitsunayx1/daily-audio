"""Render a spoken script (plain text, blank-line separated paragraphs) to MP3.

Usage: python3 tools/tts.py script.txt out.mp3 [--model DIR] [--voice am_michael]
Needs: pip install kokoro-onnx soundfile; ffmpeg; model files kokoro.onnx (use the fp32 kokoro-v1.0.onnx; int8 is ~5x slower on CPU) + voices.bin in --model DIR
(download from https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0).
"""
import argparse, re, subprocess, tempfile, os
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

ap = argparse.ArgumentParser()
ap.add_argument("script"); ap.add_argument("out")
ap.add_argument("--model", default=os.path.expanduser("~/.cache/kokoro"))
ap.add_argument("--voice", default="am_michael")
ap.add_argument("--speed", type=float, default=1.05)
ap.add_argument("--title", default="")
a = ap.parse_args()

k = Kokoro(os.path.join(a.model, "kokoro.onnx"), os.path.join(a.model, "voices.bin"))
text = open(a.script, encoding="utf-8").read()
paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
chunks, sr = [], 24000
for i, p in enumerate(paras):
    heading = p.startswith("## ")
    p = p.lstrip("# ").strip()
    s, sr = k.create(p, voice=a.voice, speed=a.speed, lang="en-us")
    chunks.append(s)
    chunks.append(np.zeros(int(sr * (1.2 if heading else 0.5)), dtype=s.dtype))
    print(f"{i+1}/{len(paras)}", flush=True)
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as t:
    sf.write(t.name, np.concatenate(chunks), sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", t.name, "-ac", "1", "-b:a", "64k",
                    "-metadata", f"title={a.title}", "-metadata", "artist=Morning Signal", a.out], check=True)
os.unlink(t.name)
