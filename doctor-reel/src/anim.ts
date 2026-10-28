import {Easing, interpolate} from 'remotion';

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// After Effects–style ease curves
export const easeOutExpo = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);
export const easeIn = Easing.bezier(0.7, 0, 0.84, 0);

/** 0→1 between two frames with an ease. */
export const prog = (frame: number, from: number, dur: number, ease = easeOutExpo) =>
  interpolate(frame, [from, from + dur], [0, 1], {...clamp, easing: ease});

/** Entrance at `inAt`, exit `outDur` frames before `end`. Returns 0..1 visibility. */
export const inOut = (frame: number, inAt: number, inDur: number, end: number, outDur = 8) =>
  Math.min(prog(frame, inAt, inDur), 1 - prog(frame, end - outDur, outDur, easeIn));

export const sec = (s: number, fps: number) => Math.round(s * fps);
