/**
 * Holds the AvatarController once the GLB runtime is ready.
 */

import { useCallback, useState } from "react";
import type { AvatarHandle } from "../types";

export function useAvatar(): {
  controller: AvatarHandle | null;
  setController: (controller: AvatarHandle | null) => void;
} {
  const [controller, setControllerState] = useState<AvatarHandle | null>(null);
  const setController = useCallback((next: AvatarHandle | null) => {
    setControllerState(next);
  }, []);
  return { controller, setController };
}
