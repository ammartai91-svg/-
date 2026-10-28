import React from 'react';
import type {IconName} from '../content';

/** Line icons, drawn on with `draw` (0..1) like a stroke-reveal in AE. */
export const Icon: React.FC<{name: IconName; color: string; draw: number; size?: number}> = ({
  name,
  color,
  draw,
  size = 120,
}) => {
  const common = {
    fill: 'none',
    stroke: color,
    strokeWidth: 5,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    pathLength: 1,
    strokeDasharray: 1,
    strokeDashoffset: 1 - draw,
  };
  const paths: Record<IconName, React.ReactNode> = {
    calendar: (
      <>
        <rect x="18" y="26" width="84" height="76" rx="12" {...common} />
        <path d="M18 48 H102 M42 16 V34 M78 16 V34" {...common} />
        <path d="M44 74 L56 86 L80 62" {...common} />
      </>
    ),
    apple: (
      <>
        <path d="M60 38 C40 24 16 34 18 62 C20 92 42 108 60 100 C78 108 100 92 102 62 C104 34 80 24 60 38 Z" {...common} />
        <path d="M60 38 C60 28 64 18 72 12 M62 30 C72 22 86 24 90 30 C80 38 68 36 62 30 Z" {...common} />
      </>
    ),
    pill: (
      <>
        <rect x="22" y="44" width="76" height="34" rx="17" transform="rotate(-35 60 61)" {...common} />
        <path d="M50 46 L70 76" {...common} />
        <path d="M14 106 L106 14" {...common} stroke="#E0475B" />
      </>
    ),
    alert: (
      <>
        <path d="M60 14 L108 100 H12 Z" {...common} />
        <path d="M60 46 V72 M60 86 V88" {...common} />
      </>
    ),
    heart: (
      <>
        <path d="M60 100 C20 74 12 50 24 34 C36 18 54 24 60 38 C66 24 84 18 96 34 C108 50 100 74 60 100 Z" {...common} />
        <path d="M30 62 H48 L54 50 L64 76 L70 62 H90" {...common} />
      </>
    ),
    stethoscope: (
      <>
        <path d="M34 18 V50 C34 66 46 76 58 76 C70 76 82 66 82 50 V18" {...common} />
        <path d="M58 76 V90 C58 102 70 108 82 104 C94 100 96 86 96 78" {...common} />
        <circle cx="96" cy="70" r="9" {...common} />
      </>
    ),
  };
  return (
    <svg viewBox="0 0 120 120" width={size} height={size}>
      {paths[name]}
    </svg>
  );
};
