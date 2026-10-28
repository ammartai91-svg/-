import React from 'react';
import {Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {clamp, easeInOut, easeOutExpo, prog} from '../anim';
import {content, IconName} from '../content';
import {Icon} from './Icons';

const C = content.colors;
export const FONT = 'Cairo, sans-serif';

/** Centered text column in the free wall space above the doctor's head. */
export const COL = {right: 90, width: 900};
const W = content.width;

/**
 * Big glowing title. Revealed right→left with a light-sweep edge, like an AE
 * linear wipe + glow. Clip-based so Arabic letters stay connected.
 */
export const GlowTitle: React.FC<{
  text: string;
  at: number;
  size?: number;
  color?: string;
  top: number;
  exit?: number;
}> = ({text, at, size = 128, color = C.primary, top, exit}) => {
  const f = useCurrentFrame();
  if (f < at || (exit !== undefined && f > exit + 8)) return null;
  const p = prog(f, at, 16);
  const out = exit === undefined ? 0 : prog(f, exit, 8, easeInOut);
  // shrink long lines so every title line fits the column on one line
  const longest = Math.max(...text.split('\n').map((l) => l.length));
  const fit = Math.min(size, COL.width / (longest * 0.5));
  const y = interpolate(p, [0, 1], [40, 0]) - out * 30;
  const blur = interpolate(p, [0, 1], [14, 0]) + out * 12;
  const edge = 100 - p * 100; // % hidden from the left
  return (
    <div
      style={{
        position: 'absolute',
        right: COL.right,
        top,
        width: COL.width,
        textAlign: 'center',
        direction: 'rtl',
        fontFamily: FONT,
        fontWeight: 900,
        fontSize: fit,
        lineHeight: 1.02,
        whiteSpace: 'pre',
        color,
        transform: `translateY(${y}px)`,
        filter: `blur(${blur}px)`,
        opacity: 1 - out,
        clipPath: `inset(-40px -40px -40px ${edge}%)`,
        textShadow: `0 0 26px ${C.glow}aa, 0 0 3px ${C.glow}, 0 8px 26px rgba(10,20,40,0.45)`,
      }}
    >
      {text}
      {/* sweep light at the reveal edge */}
      {p > 0.02 && p < 0.97 && (
        <div
          style={{
            position: 'absolute',
            top: -20,
            bottom: -20,
            left: `${edge}%`,
            width: 10,
            background: `linear-gradient(180deg, transparent, #fff, ${C.glow}, transparent)`,
            boxShadow: `0 0 30px 10px ${C.glow}`,
            opacity: 1 - p,
          }}
        />
      )}
    </div>
  );
};

/** Subtitle inside a colour bar that wipes in from the right (reference: highlight box). */
export const HighlightBar: React.FC<{text: string; at: number; top: number; exit?: number; size?: number}> = ({
  text,
  at,
  top,
  exit,
  size = 40,
}) => {
  const f = useCurrentFrame();
  const bar = prog(f, at, 12);
  const txt = prog(f, at + 6, 12);
  const out = exit === undefined ? 0 : prog(f, exit, 8, easeInOut);
  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        top,
        display: 'flex',
        justifyContent: 'center',
        direction: 'rtl',
        opacity: 1 - out,
        transform: `translateY(${-out * 20}px)`,
      }}
    >
     <div style={{position: 'relative', maxWidth: COL.width}}>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: 10,
          background: `linear-gradient(270deg, ${C.accent}, ${C.glow})`,
          boxShadow: `0 10px 30px ${C.accent}55`,
          transform: `scaleX(${bar})`,
          transformOrigin: 'center',
        }}
      />
      <div
        style={{
          position: 'relative',
          padding: '10px 22px 14px',
          fontFamily: FONT,
          fontWeight: 700,
          fontSize: size,
          lineHeight: 1.3,
          color: '#fff',
          textAlign: 'center',
          opacity: txt,
          transform: `translateY(${(1 - txt) * 14}px)`,
        }}
      >
        {text}
      </div>
     </div>
    </div>
  );
};

/** Huge outlined number behind the title (reference: the ghost "100"). */
export const GhostNumber: React.FC<{text: string; at: number; end: number; top: number; size?: number}> = ({
  text,
  at,
  end,
  top,
  size = 560,
}) => {
  const f = useCurrentFrame();
  const p = prog(f, at, 22);
  const out = prog(f, end - 10, 10, easeInOut);
  const drift = interpolate(f, [at, end], [0, -40], clamp);
  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        textAlign: 'center',
        top,
        fontFamily: FONT,
        fontWeight: 900,
        fontSize: size,
        lineHeight: 1,
        letterSpacing: -20,
        color: 'transparent',
        WebkitTextStroke: `4px ${C.primary}`,
        opacity: 0.36 * p * (1 - out),
        transform: `translateY(${(1 - p) * 120 + drift}px) scale(${0.92 + p * 0.08})`,
        clipPath: `inset(${(1 - p) * 100}% 0 0 0)`,
        filter: `drop-shadow(0 0 18px ${C.glow}66)`,
      }}
    >
      {text}
    </div>
  );
};

/** Hexagon outline that draws itself, with a line icon inside (reference: the hex frame). */
export const HexBadge: React.FC<{icon: IconName; at: number; end: number; top: number}> = ({icon, at, end, top}) => {
  const f = useCurrentFrame();
  const draw = prog(f, at, 20, easeInOut);
  const iconDraw = prog(f, at + 8, 20, easeInOut);
  const pop = prog(f, at, 14);
  const out = prog(f, end - 8, 8, easeInOut);
  const spin = interpolate(f, [at, end], [0, 12], clamp);
  const size = 160;
  const hex = Array.from({length: 6})
    .map((_, i) => {
      const a = (Math.PI / 3) * i - Math.PI / 2;
      return `${100 + 92 * Math.cos(a)},${100 + 92 * Math.sin(a)}`;
    })
    .join(' ');
  return (
    <div
      style={{
        position: 'absolute',
        left: (W - size) / 2,
        top,
        width: size,
        height: size,
        opacity: 1 - out,
        transform: `scale(${0.6 + pop * 0.4 + out * 0.2})`,
        filter: `drop-shadow(0 0 14px ${C.glow}aa)`,
      }}
    >
      <svg viewBox="0 0 200 200" width={size} height={size} style={{position: 'absolute', transform: `rotate(${spin}deg)`}}>
        <polygon points={hex} fill="rgba(255,255,255,0.55)" opacity={pop} />
        <polygon
          points={hex}
          fill="none"
          stroke={C.glow}
          strokeWidth={4}
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - draw}
        />
        <polygon
          points={hex}
          fill="none"
          stroke={C.deep}
          strokeWidth={1.5}
          transform="translate(100 100) scale(1.12) translate(-100 -100)"
          pathLength={1}
          strokeDasharray="0.02 0.03"
          strokeDashoffset={-draw * 0.5}
          opacity={draw}
        />
      </svg>
      <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <Icon name={icon} color={C.deep} draw={iconDraw} size={80} />
      </div>
    </div>
  );
};

/** Search pill that types a question, then a magnifier sweeps it (reference: Google bar). */
export const SearchBar: React.FC<{query: string; at: number; end: number; top: number}> = ({query, at, end, top}) => {
  const f = useCurrentFrame();
  const pop = prog(f, at, 14);
  const out = prog(f, end - 8, 8, easeInOut);
  const typeStart = at + 10;
  const chars = Math.floor(interpolate(f, [typeStart, typeStart + query.length * 1.6], [0, query.length], clamp));
  const typed = query.slice(0, chars);
  const cursorOn = Math.floor(f / 8) % 2 === 0 || chars < query.length;
  const lensT = prog(f, typeStart + query.length * 1.6 + 4, 26, easeInOut);
  const lensX = interpolate(lensT, [0, 1], [640, 60]);
  const lensVisible = lensT > 0 && lensT < 1 ? 1 : 0;
  return (
    <div
      style={{
        position: 'absolute',
        left: (W - 820) / 2,
        top,
        width: 820,
        height: 104,
        opacity: pop * (1 - out),
        transform: `translateY(${(1 - pop) * 40}px) scale(${0.9 + pop * 0.1})`,
        transformOrigin: 'center',
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: 52,
          background: 'rgba(255,255,255,0.92)',
          boxShadow: `0 18px 40px rgba(7,84,106,0.18), 0 0 0 2px ${C.glow}66, 0 0 26px ${C.glow}55`,
          display: 'flex',
          alignItems: 'center',
          direction: 'rtl',
          padding: '0 32px',
          gap: 18,
        }}
      >
        <svg viewBox="0 0 40 40" width={40} height={40}>
          <circle cx="17" cy="17" r="11" fill="none" stroke={C.deep} strokeWidth={4} />
          <path d="M25 25 L35 35" stroke={C.deep} strokeWidth={4} strokeLinecap="round" />
        </svg>
        <div style={{fontFamily: FONT, fontWeight: 700, fontSize: 36, color: C.text, whiteSpace: 'nowrap'}}>
          {typed}
          <span style={{opacity: cursorOn ? 1 : 0, color: C.accent, fontWeight: 400}}>|</span>
        </div>
      </div>
      {/* magnifier lens sweeping over the query */}
      <div
        style={{
          position: 'absolute',
          left: lensX,
          top: -18,
          width: 140,
          height: 140,
          borderRadius: '50%',
          border: `6px solid ${C.deep}`,
          background: 'rgba(255,255,255,0.15)',
          backdropFilter: 'blur(0.5px) contrast(1.2)',
          boxShadow: '0 12px 30px rgba(0,0,0,0.2), inset 0 0 20px rgba(255,255,255,0.6)',
          opacity: lensVisible,
          transform: 'scale(1)',
        }}
      >
        <div
          style={{
            position: 'absolute',
            right: -54,
            bottom: -42,
            width: 80,
            height: 16,
            borderRadius: 8,
            background: C.deep,
            transform: 'rotate(40deg)',
          }}
        />
      </div>
    </div>
  );
};

/** Frosted-glass arc that sweeps across between beats (reference: glass circle wipe). */
export const GlassSweep: React.FC<{at: number}> = ({at}) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [at - 8, at + 12], [0, 1], {...clamp, easing: easeInOut});
  if (t <= 0 || t >= 1) return null;
  const x = interpolate(t, [0, 1], [-1500, 1300]);
  const y = interpolate(t, [0, 1], [1900, -500]);
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: 1300,
        height: 1300,
        borderRadius: '50%',
        backdropFilter: 'blur(22px) brightness(1.08)',
        background: 'linear-gradient(135deg, rgba(255,255,255,0.35), rgba(46,214,240,0.10))',
        boxShadow: `inset 0 0 0 3px rgba(255,255,255,0.7), inset 30px 30px 80px rgba(255,255,255,0.35), 0 0 60px ${C.glow}44`,
      }}
    />
  );
};

/** Little 1–4 progress ticks at the top of the text column. */
export const Progress: React.FC<{count: number; active: number; visible: number}> = ({count, active, visible}) => (
  <div
    style={{
      position: 'absolute',
      left: 0,
      right: 0,
      top: 64,
      justifyContent: 'center',
      display: 'flex',
      flexDirection: 'row-reverse',
      gap: 12,
      opacity: visible,
    }}
  >
    {Array.from({length: count}).map((_, i) => (
      <div
        key={i}
        style={{
          width: i === active ? 70 : 26,
          height: 10,
          borderRadius: 5,
          background: i <= active ? C.accent : 'rgba(255,255,255,0.35)',
          boxShadow: i === active ? `0 0 14px ${C.glow}` : undefined,
        }}
      />
    ))}
  </div>
);

/** Campaign heartbeat line (ECG) that draws itself with a glowing head, like the Nabd teaser. */
export const EcgLine: React.FC<{
  at: number;
  end: number;
  top: number;
  width?: number;
  beats?: number;
  left?: number;
  color?: string;
}> = ({at, end, top, width = 900, beats = 2, left, color = C.glow}) => {
  const f = useCurrentFrame();
  if (f < at || f > end) return null;
  const draw = prog(f, at, 26, easeInOut);
  const out = prog(f, end - 8, 8, easeInOut);
  const h = 120;
  const seg = width / beats;
  let d = `M0 ${h / 2}`;
  for (let i = 0; i < beats; i++) {
    const x = i * seg;
    d += ` L${x + seg * 0.3} ${h / 2} L${x + seg * 0.38} ${h * 0.35} L${x + seg * 0.44} ${h / 2}`;
    d += ` L${x + seg * 0.5} ${h / 2} L${x + seg * 0.55} ${h * 0.02} L${x + seg * 0.61} ${h * 0.98}`;
    d += ` L${x + seg * 0.66} ${h / 2} L${x + seg * 0.76} ${h * 0.3} L${x + seg * 0.86} ${h / 2}`;
  }
  d += ` L${width} ${h / 2}`;
  return (
    <svg
      width={width}
      height={h}
      viewBox={`0 0 ${width} ${h}`}
      style={{position: 'absolute', left: left ?? (W - width) / 2, top, opacity: 1 - out, overflow: 'visible'}}
    >
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={5}
        strokeLinejoin="round"
        pathLength={1}
        strokeDasharray={1}
        strokeDashoffset={1 - draw}
        style={{filter: `drop-shadow(0 0 10px ${color}) drop-shadow(0 0 22px ${C.accent}88)`}}
      />
    </svg>
  );
};

/** Small brand bug in the corner while she talks. */
export const LogoBug: React.FC<{from: number; to: number}> = ({from, to}) => {
  const f = useCurrentFrame();
  if (!content.logo) return null;
  const v = Math.min(prog(f, from, 14), 1 - prog(f, to - 10, 10, easeInOut));
  return (
    <Img
      src={staticFile(content.logo)}
      style={{
        position: 'absolute',
        left: 44,
        top: 44,
        width: 118,
        height: 118,
        borderRadius: '50%',
        opacity: v,
        transform: `scale(${0.8 + v * 0.2})`,
        boxShadow: '0 8px 24px rgba(0,0,0,0.25)',
      }}
    />
  );
};

export {easeOutExpo};
