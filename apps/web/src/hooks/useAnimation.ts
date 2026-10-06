/**
 * Semantic animation helpers for UI buttons.
 */

import type { GestureName, HeadMotionName } from "@avatar/shared";
import type { AvatarHandle } from "../avatar/avatarTypes";

export function useAnimation(controller: AvatarHandle | null): {
  playGesture: (name: GestureName) => void;
  playHead: (name: HeadMotionName) => void;
} {
  return {
    playGesture: (name: GestureName): void => {
      controller?.playGesture(name);
    },
    playHead: (name: HeadMotionName): void => {
      controller?.setHeadMotion(name);
    },
  };
}
