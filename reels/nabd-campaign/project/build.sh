#!/usr/bin/env bash
# يرندر الإعلان من config.json → nabd.mp4   (يحتاج: node + playwright + ffmpeg + python3/numpy)
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
rm -rf "$DIR/frames"
python3 "$DIR/ad_audio.py" "$DIR"
PAGE=ad.html node "$DIR/render.js" "$DIR" full
ffmpeg -loglevel error -y -framerate 30 -i "$DIR/frames/f%05d.jpg" -i "$DIR/ad_mix.wav" \
  -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k -shortest "$DIR/nabd.mp4"
echo "done → $DIR/nabd.mp4"
