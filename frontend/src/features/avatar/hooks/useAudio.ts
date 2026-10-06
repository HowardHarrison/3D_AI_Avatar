/**
 * Debug-panel bindings for local audio on the avatar runtime.
 */

import { avatarConfig } from "../../../constants/avatarConfig";
import type { AvatarHandle } from "../types";

export function useAudio(controller: AvatarHandle | null): {
  loadTestAudio: () => Promise<void>;
  play: () => void;
  pause: () => void;
  stop: () => void;
} {
  return {
    loadTestAudio: async (): Promise<void> => {
      await controller?.loadAudio(avatarConfig.audioUrl);
    },
    play: (): void => {
      controller?.playAudio();
    },
    pause: (): void => {
      controller?.pauseAudio();
    },
    stop: (): void => {
      controller?.stopAudio();
    },
  };
}
