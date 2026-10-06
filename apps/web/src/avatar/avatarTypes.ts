import type { AvatarController } from "@avatar/shared";

/** Handle exposed to React UI after the GLB runtime has initialized. */
export type AvatarHandle = AvatarController;

/** Load-lifecycle callbacks for Avatar.tsx. */
export interface AvatarLoadHandlers {
  onReady?: (controller: AvatarHandle) => void;
  onError?: (message: string) => void;
  onWarning?: (message: string) => void;
}
