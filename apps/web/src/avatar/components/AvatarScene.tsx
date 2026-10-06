/**
 * React Three Fiber canvas: studio, camera, lights, and avatar.
 */

import { Canvas } from "@react-three/fiber";
import { avatarConfig } from "../avatarConfig";
import type { AvatarLoadHandlers } from "../avatarTypes";
import { Studio } from "../../studio/Studio";
import { studioConfig } from "../../studio/studioConfig";
import { Avatar } from "./Avatar";
import { AvatarCamera } from "./AvatarCamera";
import { AvatarLighting } from "./AvatarLighting";

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
