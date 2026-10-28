import React from 'react';
import {AbsoluteFill, OffthreadVideo, staticFile} from 'remotion';
import {content} from '../content';

/** The cut-out doctor, seated on the left. Falls back to a placeholder silhouette. */
export const Doctor: React.FC = () => {
  const {doctor, fps} = content;
  const wrap: React.CSSProperties = {
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
        <OffthreadVideo
          src={staticFile(doctor.src)}
          startFrom={Math.round(doctor.startFrom * fps)}
          volume={doctor.volume}
          transparent
          style={{height: '100%', width: 'auto'}}
        />
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
      fontFamily="Tajawal"
      fontWeight={700}
      fontSize={34}
      fill="#fff"
    >
      فيديو الدكتورة هنا
    </text>
  </svg>
);
