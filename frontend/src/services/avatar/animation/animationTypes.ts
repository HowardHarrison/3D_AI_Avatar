import type { PlayAnimationOptions } from "../../../types/animation";

export type { PlayAnimationOptions };

/** Internal clip lookup result used by AnimationController. */
export interface ResolvedClip {
  clipName: string;
  found: boolean;
}
