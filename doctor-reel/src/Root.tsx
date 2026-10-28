import '@fontsource/tajawal/400.css';
import '@fontsource/tajawal/500.css';
import '@fontsource/tajawal/700.css';
import '@fontsource/tajawal/800.css';
import '@fontsource/tajawal/900.css';
import React from 'react';
import {Composition, continueRender, delayRender} from 'remotion';
import {content, totalSeconds} from './content';
import {OverlayOnly, Reel} from './Reel';

// Make sure every Tajawal weight is loaded before the first frame is captured.
const fontHandle = delayRender('Loading Tajawal');
Promise.all(
  [400, 500, 700, 800, 900].map((w) => document.fonts.load(`${w} 40px Tajawal`, 'نص عربي')),
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
