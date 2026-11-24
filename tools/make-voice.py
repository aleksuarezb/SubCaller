"""Rebuilds the spoken call clips in voice/ with the Kokoro-82M voice "bm_george" (British male).

Needs: pip install kokoro-onnx soundfile, plus ffmpeg.
  MODEL  = Kokoro-82M v1.0 ONNX (q8). Used here: npm package kokoro-q8-shards@1.0.0, parts 0-5 joined,
           sha256 fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478
  VOICES = folder of Kokoro voice .bin files (npm package kokoro-local-runtime@0.1.0, voices/)
Usage: python tools/make-voice.py MODEL VOICES
"""
import os, subprocess, sys, tempfile
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

VOICE, SPEED = 'bm_george', 0.95
model, vdir = sys.argv[1], sys.argv[2]
tmp = tempfile.mkdtemp()
npz = os.path.join(tmp, 'voices.npz')
np.savez(npz, **{VOICE: np.fromfile(os.path.join(vdir, VOICE + '.bin'), dtype=np.float32).reshape(510, 1, 256)})
k = Kokoro(model, npz)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'voice')
os.makedirs(out, exist_ok=True)
AF = ('silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
      'highpass=f=100,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,loudnorm=I=-12:TP=-1:LRA=7,aresample=24000')

def make(name, text):
    audio, sr = k.create(text, voice=VOICE, speed=SPEED, lang='en-gb')
    wav = os.path.join(tmp, 'raw.wav'); sf.write(wav, audio, sr)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-af', AF, '-ac', '1', '-c:a', 'libmp3lame', '-b:a', '64k',
                    os.path.join(out, name + '.mp3')], check=True)

make('sub', 'Sub.')
for n in range(1, 31):
    make(f'black-{n}', f'Black {n}.')
    make(f'white-{n}', f'White {n}.')
    make(f'and-{n}', f'and {n}.')
