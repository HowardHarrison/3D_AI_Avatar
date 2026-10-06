/**
 * Debug-panel bindings for local audio on the avatar runtime.
 */

import { avatarConfig } from "../avatar/avatarConfig";
import { AvatarRuntime } from "../avatar/AvatarRuntime";
import type { AvatarHandle } from "../avatar/avatarTypes";

function asRuntime(controller: AvatarHandle | null): AvatarRuntime | null {
  return controller instanceof AvatarRuntime ? controller : null;
}

export function useAudio(controller: AvatarHandle | null): {
  loadTestAudio: () => Promise<void>;
  play: () => void;
  pause: () => void;
  stop: () => void;
} {
  const runtime = asRuntime(controller);
  return {
    loadTestAudio: async (): Promise<void> => {
      await runtime?.audio.load(avatarConfig.audioUrl);
    },
    play: (): void => {
      runtime?.audio.play();
    },
    pause: (): void => {
      runtime?.audio.pause();
    },
    stop: (): void => {
      runtime?.audio.stop();
    },
  };
}
