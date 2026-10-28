import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {content} from '../content';

/** Bright white room: wall, curved cove, floor, window light, chair and plant. */
export const Room: React.FC = () => {
  const frame = useCurrentFrame();
  const {room} = content;
  if (room.image) {
    return (
      <AbsoluteFill>
        <Img src={staticFile(room.image)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      </AbsoluteFill>
    );
  }
  // Slow drift of the window light so the plate never feels frozen
  const drift = Math.sin(frame / 90) * 14;
  return (
    <AbsoluteFill style={{background: 'linear-gradient(180deg,#F8F6F2 0%,#F1EEE9 55%,#E9E5DE 70%)'}}>
      {/* floor */}
      <div
        style={{
          position: 'absolute',
          left: -100,
          right: -100,
          top: 1330,
          bottom: 0,
          background: 'linear-gradient(180deg,#E6E1D9 0%,#DCD5CA 60%,#D3CBBF 100%)',
        }}
      />
      {/* cove: soft curve where wall meets floor */}
      <div
        style={{
          position: 'absolute',
          left: -200,
          right: -200,
          top: 1250,
          height: 160,
          background: 'linear-gradient(180deg,rgba(0,0,0,0) 0%,rgba(120,105,90,0.10) 70%,rgba(0,0,0,0) 100%)',
          filter: 'blur(18px)',
        }}
      />
      {/* window light shafts on the wall from the right */}
      <div style={{position: 'absolute', inset: 0, filter: 'blur(26px)', opacity: 0.7}}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: 160 + i * 10,
              left: 470 + i * 190 + drift,
              width: 150,
              height: 1150,
              background: 'linear-gradient(180deg,rgba(255,248,236,0.0),rgba(255,246,230,0.95) 30%,rgba(255,244,228,0.75) 80%,rgba(255,244,228,0))',
              transform: 'skewX(-14deg)',
            }}
          />
        ))}
      </div>
      {/* window frame shadow bars */}
      <div style={{position: 'absolute', inset: 0, filter: 'blur(14px)', opacity: 0.16}}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: 180,
              left: 620 + i * 190 + drift,
              width: 26,
              height: 1100,
              background: '#7a6a58',
              transform: 'skewX(-14deg)',
            }}
          />
        ))}
      </div>
      {/* floor light pool */}
      <div
        style={{
          position: 'absolute',
          left: 380 + drift,
          top: 1420,
          width: 760,
          height: 300,
          borderRadius: '50%',
          background: 'radial-gradient(closest-side,rgba(255,248,235,0.75),rgba(255,248,235,0))',
          filter: 'blur(20px)',
        }}
      />
      {room.showPlant && <Plant />}
      {room.showChair && <Chair />}
    </AbsoluteFill>
  );
};

const Plant: React.FC = () => (
  <div style={{position: 'absolute', right: -60, top: 880, width: 360, height: 640, filter: 'blur(5px)', opacity: 0.95}}>
    <svg viewBox="0 0 360 640" width={360} height={640}>
      {Array.from({length: 22}).map((_, i) => {
        const a = -70 + (i * 140) / 21;
        const len = 170 + ((i * 37) % 90);
        const cx = 180 + Math.sin((a * Math.PI) / 180) * len * 0.6;
        const cy = 420 - Math.cos((a * Math.PI) / 180) * len;
        return (
          <ellipse
            key={i}
            cx={cx}
            cy={cy}
            rx={20}
            ry={52}
            fill={i % 3 ? '#6F8E5C' : '#86A672'}
            transform={`rotate(${a} ${cx} ${cy})`}
          />
        );
      })}
      <path d="M180 430 L180 250 M180 430 L120 260 M180 430 L245 270" stroke="#5E6E4C" strokeWidth={5} fill="none" />
      <path d="M95 430 H265 L245 620 H115 Z" fill="#F4F1EC" />
      <path d="M95 430 H265 L262 450 H98 Z" fill="#E3DDD3" />
    </svg>
  </div>
);

/** Modern boucle armchair on the left — the doctor sits here. */
const Chair: React.FC = () => (
  <div style={{position: 'absolute', left: 10, top: 960, width: 640, height: 820}}>
    {/* contact shadow */}
    <div
      style={{
        position: 'absolute',
        left: 40,
        top: 690,
        width: 560,
        height: 120,
        borderRadius: '50%',
        background: 'radial-gradient(closest-side,rgba(70,55,40,0.35),rgba(70,55,40,0))',
        filter: 'blur(8px)',
      }}
    />
    <svg viewBox="0 0 640 820" width={640} height={820}>
      <defs>
        <linearGradient id="chairBody" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#F1EBE2" />
          <stop offset="0.6" stopColor="#E2D9CC" />
          <stop offset="1" stopColor="#CFC4B5" />
        </linearGradient>
        <linearGradient id="chairSeat" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#EFE8DE" />
          <stop offset="1" stopColor="#D8CEC0" />
        </linearGradient>
      </defs>
      {/* back */}
      <path d="M90 120 Q320 40 550 120 L560 560 L80 560 Z" fill="url(#chairBody)" />
      {/* seat */}
      <path d="M70 520 Q320 470 570 520 L580 640 Q320 670 60 640 Z" fill="url(#chairSeat)" />
      {/* arms */}
      <rect x="20" y="360" width="120" height="330" rx="58" fill="url(#chairBody)" />
      <rect x="500" y="360" width="120" height="330" rx="58" fill="url(#chairBody)" />
      {/* legs */}
      <rect x="110" y="680" width="16" height="110" rx="6" fill="#B9A58C" transform="rotate(8 118 735)" />
      <rect x="514" y="680" width="16" height="110" rx="6" fill="#B9A58C" transform="rotate(-8 522 735)" />
    </svg>
  </div>
);
