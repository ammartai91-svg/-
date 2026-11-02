#!/usr/bin/env bash
# الاستخدام: bash vo/mux.sh path/to/voiceover.mp3 [music.mp3]
# يدمج الفويس (يبدي من 2.0 ث (مضبوط على توقيت المشاهد)) + النبض + موسيقى اختيارية بالفيديو
set -e; cd "$(dirname "$0")/.."
VO="$1"; MUS="$2"
if [ -n "$MUS" ]; then
  ffmpeg -y -i clinic-ad-30s-no-vo.mp4 -i "$VO" -i "$MUS" -filter_complex \
  "[1:a]adelay=2000|2000,volume=1.6[v];[2:a]atrim=0:30,afade=t=out:st=27:d=3,volume=0.18[m];[0:a][v][m]amix=inputs=3:normalize=0,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t 30 clinic-ad-30s-FINAL.mp4
else
  ffmpeg -y -i clinic-ad-30s-no-vo.mp4 -i "$VO" -filter_complex \
  "[1:a]adelay=2000|2000,volume=1.6[v];[0:a][v]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t 30 clinic-ad-30s-FINAL.mp4
fi
echo "✅ clinic-ad-30s-FINAL.mp4"
