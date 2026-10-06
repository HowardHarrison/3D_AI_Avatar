/**
 * R3F canvas: studio, camera, lights, and avatar model.
 * Mixer logic lives in services/avatar, not here.
 */

import { Canvas } from "@react-three/fiber";
import { avatarConfig } from "../../../constants/avatarConfig";
import { studioConfig } from "../../../constants/studioConfig";
import type { AvatarLoadHandlers } from "../types";
import { Avatar } from "./Avatar";
import { AvatarCamera } from "./AvatarCamera";
import { AvatarLighting } from "./AvatarLighting";
import { Studio } from "./Studio";

interface AvatarSceneProps extends AvatarLoadHandlers {
  className?: string;
}

export function AvatarScene(props: AvatarSceneProps): JSX.Element {
  const { className, ...handlers } = props;
  return (
    <div className={className}>
      <Canvas
        dpr={[1, avatarConfig.performance.pixelRatioMax]}
        gl={{ antialias: true, powerPreference: "high-performance" }}
        style={{ width: "100%", height: "100%" }}
      >
        <color attach="background" args={[studioConfig.background]} />
        <AvatarCamera />
        <AvatarLighting />
        <Studio />
        <Avatar {...handlers} />
      </Canvas>
    </div>
  );
}
