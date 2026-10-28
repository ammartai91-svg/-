import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {content} from '../content';

/** Cinematic finish: teal shadows / warm highlights, light leak, vignette, film grain. */
export const Grade: React.FC = () => {
  const frame = useCurrentFrame();
  const g = content.grade;
  const leakX = 700 + Math.sin(frame / 50) * 160;
  const leakY = 120 + Math.cos(frame / 70) * 90;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, rgba(255,196,140,${g.warmHighlights}) 0%, rgba(255,214,170,${g.warmHighlights * 0.4}) 40%, rgba(${g.shadowTint},${g.tealShadows}) 100%)`,
          mixBlendMode: 'soft-light',
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(600px 520px at ${leakX}px ${leakY}px, rgba(255,190,120,${g.lightLeak}), rgba(255,190,120,0))`,
          mixBlendMode: 'screen',
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 75% 65% at 50% 48%, rgba(0,0,0,0) 55%, rgba(5,30,38,${g.vignette}) 100%)`,
        }}
      />
      {g.grain > 0 && (
        <AbsoluteFill style={{opacity: g.grain, mixBlendMode: 'overlay'}}>
          <svg width="100%" height="100%">
            <filter id="grain">
              <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={frame % 12} stitchTiles="stitch" />
              <feColorMatrix type="saturate" values="0" />
            </filter>
            <rect width="100%" height="100%" filter="url(#grain)" />
          </svg>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
