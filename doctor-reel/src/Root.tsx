import '@fontsource/cairo/500.css';
import '@fontsource/cairo/700.css';
import '@fontsource/cairo/800.css';
import '@fontsource/cairo/900.css';
import React from 'react';
import {Composition, continueRender, delayRender} from 'remotion';
import {content, totalSeconds} from './content';
import {OverlayOnly, Reel} from './Reel';

// Make sure every Cairo weight is loaded before the first frame is captured.
const fontHandle = delayRender('Loading Cairo');
Promise.all(
  [500, 700, 800, 900].map((w) => document.fonts.load(`${w} 40px Cairo`, 'نص عربي')),
)
  .then(() => continueRender(fontHandle))
  .catch(() => continueRender(fontHandle));

export const RemotionRoot: React.FC = () => {
  const common = {
    durationInFrames: Math.round(totalSeconds * content.fps),
    fps: content.fps,
    width: content.width,
    height: content.height,
  };
  return (
    <>
      <Composition id="DoctorReel" component={Reel} {...common} />
      <Composition id="DoctorReelOverlay" component={OverlayOnly} {...common} />
    </>
  );
};
