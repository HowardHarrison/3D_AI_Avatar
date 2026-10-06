/**
 * News-presenter camera. Numbers come from avatarConfig.
 */

import { PerspectiveCamera } from "@react-three/drei";
import { useLayoutEffect, useRef } from "react";
import type { PerspectiveCamera as ThreePerspectiveCamera } from "three";
import { avatarConfig } from "../../../constants/avatarConfig";

export function AvatarCamera(): JSX.Element {
  const cameraRef = useRef<ThreePerspectiveCamera>(null);
  const { position, target, fov } = avatarConfig.camera;

  useLayoutEffect(() => {
    cameraRef.current?.lookAt(target[0], target[1], target[2]);
  }, [target]);

  return (
    <PerspectiveCamera
      ref={cameraRef}
      makeDefault
      fov={fov}
      position={position}
      near={0.1}
      far={50}
    />
  );
}
