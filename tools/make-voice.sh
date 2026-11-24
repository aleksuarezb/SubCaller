#!/bin/bash
# Rebuilds the spoken call clips in voice/ (needs: apt-get install libttspico-utils ffmpeg)
set -e
cd "$(dirname "$0")/.."
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
make() { # make <file> <text>
  pico2wave -l en-GB -w "$TMP/raw.wav" "$2"
  ffmpeg -v error -y -i "$TMP/raw.wav" -af "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,highpass=f=120,acompressor=threshold=-20dB:ratio=4:attack=5:release=80:makeup=2,loudnorm=I=-12:TP=-1:LRA=7,aresample=22050" -ac 1 -c:a libmp3lame -b:a 48k "voice/$1.mp3"
}
make sub "Sub."
for n in $(seq 1 30); do
  make "black-$n" "Black $n."
  make "white-$n" "White $n."
  make "and-$n" "and $n."
done
