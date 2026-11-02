#!/usr/bin/env bash
# يركّب ملف الأغنية (من المالك) على الماستر الصامت.
# الاستخدام: ./add_song.sh <ملف-الأغنية> [ثانية-البداية-داخل-الأغنية، الافتراضي 0]
set -euo pipefail
SONG="$1"; START="${2:-0}"
cd "$(dirname "$0")"
ffmpeg -y -loglevel error -i ticketzone-reel_9x16_30s_no-audio.mp4 -ss "$START" -i "$SONG" \
  -map 0:v -map 1:a -t 30 -c:v copy \
  -af "afade=t=in:st=0:d=0.3,afade=t=out:st=28.5:d=1.5,loudnorm=I=-14:TP=-1.5:LRA=11" \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart ticketzone-reel_9x16_30s_with-song.mp4
echo "تم: ticketzone-reel_9x16_30s_with-song.mp4"
