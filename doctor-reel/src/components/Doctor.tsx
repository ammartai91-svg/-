import React from 'react';
import {AbsoluteFill, Freeze, OffthreadVideo, Sequence, staticFile} from 'remotion';
import {content} from '../content';

/** The doctor: her original full-frame shot, or a cut-out placed in the room. Placeholder when no video. */
export const Doctor: React.FC = () => {
  const {doctor, fps} = content;
  const delay = Math.round(doctor.delay * fps);
  const startFrom = Math.round(doctor.startFrom * fps);
  const clipFrames = Math.floor(doctor.clipDuration * fps);
  const full = doctor.mode === 'full';
  const transparent = !full;
  const videoStyle: React.CSSProperties = full
    ? {width: '100%', height: '100%', objectFit: 'cover', display: 'block'}
    : {height: '100%', width: 'auto', display: 'block'};
  const wrap: React.CSSProperties = full
    ? {position: 'absolute', inset: 0, transform: doctor.mirror ? 'scaleX(-1)' : undefined}
    : {
        position: 'absolute',
        left: doctor.x,
        bottom: -doctor.y,
        height: doctor.height,
        transform: doctor.mirror ? 'scaleX(-1)' : undefined,
        // grounding shadow + light wrap so she sits in the room, not on top of it
        filter: 'drop-shadow(24px 30px 40px rgba(60,45,30,0.28)) drop-shadow(0 0 2px rgba(255,248,236,0.6))',
      };
  if (!doctor.src) {
    return (
      <AbsoluteFill>
        <div style={{...wrap, width: 640}}>
          <Placeholder />
        </div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill>
      <div style={wrap}>
        {/* during the hook she holds still on her first frame, then starts talking */}
        {delay > 0 && (
          <Sequence durationInFrames={delay} layout="none">
            <Freeze frame={startFrom}>
              <OffthreadVideo src={staticFile(doctor.src)} muted transparent={transparent} style={videoStyle} />
            </Freeze>
          </Sequence>
        )}
        <Sequence from={delay} durationInFrames={clipFrames} layout="none">
          <OffthreadVideo
            src={staticFile(doctor.src)}
            startFrom={startFrom}
            volume={doctor.volume}
            transparent={transparent}
            style={videoStyle}
          />
        </Sequence>
        {/* after her last word she holds on the final frame under the end card */}
        <Sequence from={delay + clipFrames} layout="none">
          <Freeze frame={startFrom + clipFrames - 1}>
            <OffthreadVideo src={staticFile(doctor.src)} muted transparent={transparent} style={videoStyle} />
          </Freeze>
        </Sequence>
      </div>
    </AbsoluteFill>
  );
};

const Placeholder: React.FC = () => (
  <svg viewBox="0 0 640 1640" style={{height: '100%', width: '100%'}}>
    <defs>
      <linearGradient id="ph" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor="#9FB7BD" />
        <stop offset="1" stopColor="#7E979E" />
      </linearGradient>
    </defs>
    <g fill="url(#ph)" opacity={0.85}>
      <ellipse cx="330" cy="560" rx="88" ry="104" />
      <path d="M300 650 h60 v50 h-60z" />
      <path d="M190 720 Q330 670 470 720 L500 1130 Q330 1160 160 1130 Z" />
      <path d="M170 1100 Q330 1080 520 1120 L540 1240 Q330 1270 150 1240 Z" />
      <path d="M210 1220 h110 l-10 380 h-80z" />
      <path d="M350 1220 h110 l-20 380 h-80z" />
    </g>
    <text
      x="330"
      y="920"
      textAnchor="middle"
      fontFamily="Cairo"
      fontWeight={700}
      fontSize={34}
      fill="#fff"
    >
      فيديو الدكتورة هنا
    </text>
  </svg>
);
