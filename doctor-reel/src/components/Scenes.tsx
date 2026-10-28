import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {clamp, easeInOut, easeOutExpo, prog, sec} from '../anim';
import {content, Point} from '../content';
import {COL, FONT, GhostNumber, GlowTitle, HexBadge, HighlightBar, SearchBar} from './Graphics';

const {fps, colors: C} = content;

export const HookScene: React.FC = () => {
  const h = content.hook;
  const at = sec(h.start, fps);
  const end = sec(h.start + h.duration, fps);
  return (
    <>
      <GhostNumber text={h.ghost} at={at} end={end} top={240} size={760} />
      <GlowTitle text={h.title} at={at + 6} top={560} size={136} exit={end - 8} />
      <HighlightBar text={h.subtitle} at={at + 18} top={880} exit={end - 8} />
    </>
  );
};

export const PointScene: React.FC<{p: Point}> = ({p}) => {
  const at = sec(p.start, fps);
  const end = sec(p.start + p.duration, fps);
  const lines = p.title.split('\n');
  const longest = Math.max(...lines.map((l) => l.length));
  const titleSize = Math.min(128, COL.width / (longest * 0.5));
  const titleTop = 600;
  const barTop = titleTop + lines.length * titleSize * 1.02 + 34;
  return (
    <>
      <GhostNumber text={p.number} at={at} end={end} top={300} />
      <HexBadge icon={p.icon} at={at + 2} end={end} top={300} />
      <GlowTitle text={p.title} at={at + 8} top={titleTop} exit={end - 8} />
      <HighlightBar text={p.subtitle} at={at + 20} top={barTop} exit={end - 8} />
      {p.search && <SearchBar query={p.search} at={at + 40} end={end} top={barTop + 200} />}
    </>
  );
};

/** End card: teal wave sweeps in from the right with the brand (reference: ÉPOPÉE card). */
export const OutroScene: React.FC = () => {
  const f = useCurrentFrame();
  const o = content.outro;
  const at = sec(o.start, fps);
  const wave = prog(f, at, 22, easeInOut);
  const brand = prog(f, at + 12, 18);
  const tag = prog(f, at + 22, 18);
  const ghost = prog(f, at + 6, 30);
  const x = interpolate(wave, [0, 1], [1100, 0]);
  const tracking = interpolate(tag, [0, 1], [30, 4], clamp);
  return (
    <div style={{position: 'absolute', inset: 0, transform: `translateX(${x}px)`}}>
      <svg viewBox="0 0 1080 1920" width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
        <defs>
          <linearGradient id="wave" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor={C.glow} />
            <stop offset="0.45" stopColor={C.accent} />
            <stop offset="1" stopColor={C.deep} />
          </linearGradient>
        </defs>
        <path d="M560 0 C 420 520, 760 1000, 470 1920 L1080 1920 L1080 0 Z" fill="url(#wave)" opacity={0.96} />
        <path d="M560 0 C 420 520, 760 1000, 470 1920" fill="none" stroke="#fff" strokeOpacity={0.7} strokeWidth={4} />
      </svg>
      <div
        style={{
          position: 'absolute',
          right: 24,
          top: 140,
          writingMode: 'vertical-rl',
          fontFamily: 'Arial Black, sans-serif',
          fontWeight: 900,
          fontSize: 170,
          color: 'transparent',
          WebkitTextStroke: '3px rgba(255,255,255,0.4)',
          transform: `translateY(${(1 - ghost) * 80}px)`,
          opacity: ghost,
          letterSpacing: 6,
        }}
      >
        {o.ghost}
      </div>
      <div
        style={{
          position: 'absolute',
          right: COL.right,
          top: 1170,
          textAlign: 'right',
          direction: 'rtl',
          whiteSpace: 'nowrap',
          fontFamily: FONT,
          fontWeight: 900,
          fontSize: 108,
          color: '#fff',
          opacity: brand,
          filter: `blur(${(1 - brand) * 12}px)`,
          transform: `translateY(${(1 - brand) * 40}px)`,
          textShadow: `0 0 30px ${C.glow}`,
        }}
      >
        {o.brand}
      </div>
      <div
        style={{
          position: 'absolute',
          right: COL.right,
          top: 1320,
          whiteSpace: 'nowrap',
          textAlign: 'right',
          direction: 'rtl',
          fontFamily: FONT,
          fontWeight: 500,
          fontSize: 50,
          color: '#E9FBFF',
          opacity: tag,
          letterSpacing: tracking,
          clipPath: `inset(0 0 0 ${(1 - tag) * 100}%)`,
        }}
      >
        {o.tagline}
      </div>
    </div>
  );
};

/** Two-frame colour inversion (reference: the negative-flash cut). */
export const flashFilter = (frame: number) => {
  for (const p of content.points) {
    if (!p.flash) continue;
    const at = sec(p.start, fps);
    if (frame >= at - 1 && frame <= at + 1) return 'invert(1) hue-rotate(180deg) saturate(1.4)';
  }
  return undefined;
};

/** Virtual camera: punch-in per point + a slow push, like AE scale keyframes. */
export const cameraScale = (frame: number) => {
  const current = [...content.points].reverse().find((p) => frame >= sec(p.start, fps));
  const base = current?.zoom ?? 1;
  const segStart = current ? sec(current.start, fps) : 0;
  const push = interpolate(frame - segStart, [0, 200], [0, 0.03], clamp);
  const outroAt = sec(content.outro.start, fps);
  const pull = prog(frame, outroAt, 22, easeInOut);
  return (base + push) * (1 - pull) + 1 * pull;
};

export {easeOutExpo};
