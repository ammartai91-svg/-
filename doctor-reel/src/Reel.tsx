import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {clamp, sec} from './anim';
import {content, totalSeconds} from './content';
import {Doctor} from './components/Doctor';
import {Grade} from './components/Grade';
import {GlassSweep, Progress} from './components/Graphics';
import {Room} from './components/Room';
import {camera, flashFilter, HookScene, OutroScene, PointScene} from './components/Scenes';
import {interpolate} from 'remotion';

const {fps} = content;

/** Every sound effect, placed automatically from the timings in content.ts. */
const sfxCues = (): {at: number; name: string; vol?: number}[] => {
  const cues: {at: number; name: string; vol?: number}[] = [];
  const h = sec(content.hook.start, fps);
  cues.push({at: h, name: 'impact', vol: 0.8}, {at: h + 6, name: 'whoosh'}, {at: h + 18, name: 'pop', vol: 0.7});
  for (const p of content.points) {
    const at = sec(p.start, fps);
    cues.push({at: at - 8, name: 'whoosh-reverse', vol: 0.7});
    if (p.flash) cues.push({at: at - 1, name: 'glitch', vol: 0.9});
    cues.push({at, name: 'impact', vol: 0.55});
    cues.push({at: at + 4, name: 'shimmer', vol: 0.45});
    cues.push({at: at + 8, name: 'whoosh'});
    cues.push({at: at + 20, name: 'pop', vol: 0.7});
    if (p.search) {
      cues.push({at: at + 40, name: 'pop', vol: 0.5});
      cues.push({at: at + 50, name: 'typing', vol: 0.8});
      cues.push({at: at + 50 + Math.round(p.search.length * 1.6) + 4, name: 'whoosh-soft', vol: 0.6});
    }
  }
  const o = sec(content.outro.start, fps);
  cues.push({at: o - 36, name: 'riser', vol: 0.6}, {at: o, name: 'whoosh'}, {at: o + 12, name: 'ding', vol: 0.7});
  return cues.filter((c) => c.at >= 0);
};

const Sound: React.FC = () => {
  const {audio, doctor} = content;
  const total = sec(totalSeconds, fps);
  const bedVol = doctor.src ? audio.musicVolumeUnderVoice : audio.musicVolumeAlone;
  return (
    <>
      <Audio
        src={staticFile(audio.music)}
        volume={(f) =>
          // full level over the hook, ducked while she talks
          interpolate(f, [sec(doctor.delay, fps) - 12, sec(doctor.delay, fps)], [audio.musicVolumeAlone, bedVol], clamp) *
          interpolate(f, [0, 10, total - 30, total], [0, 1, 1, 0], clamp) *
          // lift the music when the end card lands
          interpolate(f, [sec(content.outro.start, fps), sec(content.outro.start, fps) + 10], [1, 1.6], clamp)
        }
      />
      {audio.sfx &&
        sfxCues().map((c, i) => (
          <Sequence key={i} from={c.at} layout="none">
            <Audio src={staticFile(`sfx/${c.name}.wav`)} volume={audio.sfxVolume * (c.vol ?? 1)} />
          </Sequence>
        ))}
    </>
  );
};

/** All motion graphics — also rendered alone with alpha for After Effects / Premiere. */
export const GraphicsLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const active = content.points.findIndex(
    (p) => frame >= sec(p.start, fps) && frame < sec(p.start + p.duration, fps),
  );
  const firstAt = sec(content.points[0]?.start ?? 0, fps);
  const outroAt = sec(content.outro.start, fps);
  const progVis = interpolate(frame, [firstAt, firstAt + 10, outroAt - 8, outroAt], [0, 1, 1, 0], clamp);
  return (
    <AbsoluteFill>
      <HookScene />
      {content.points.map((p, i) => (
        <PointScene key={i} p={p} />
      ))}
      <Progress count={content.points.length} active={Math.max(0, active)} visible={progVis} />
      {content.points.map((p, i) => (
        <GlassSweep key={i} at={sec(p.start, fps)} />
      ))}
      <OutroScene />
    </AbsoluteFill>
  );
};

export const Reel: React.FC = () => {
  const frame = useCurrentFrame();
  const cam = camera(frame);
  return (
    <AbsoluteFill style={{background: '#F4F1EC', filter: flashFilter(frame)}}>
      <AbsoluteFill style={{filter: 'contrast(1.09) saturate(1.08)'}}>
        <AbsoluteFill style={{transform: `translateX(${cam.x}px) scale(${cam.scale})`, transformOrigin: '540px 760px'}}>
          {content.room.enabled && <Room />}
          <Doctor />
        </AbsoluteFill>
        <GraphicsLayer />
      </AbsoluteFill>
      <Grade />
      <Sound />
    </AbsoluteFill>
  );
};

export const OverlayOnly: React.FC = () => (
  <AbsoluteFill>
    <GraphicsLayer />
  </AbsoluteFill>
);
