/**
 * Default framing + horizontal-first OrbitControls (drag yaw 360°, scroll zoom).
 * Numbers come from avatarConfig.
 */

import { OrbitControls, PerspectiveCamera } from "@react-three/drei";
import { avatarConfig } from "../../../constants/avatarConfig";

export function AvatarCamera(): JSX.Element {
  const { position, target, fov, orbit } = avatarConfig.camera;

  return (
    <>
      <PerspectiveCamera makeDefault fov={fov} position={position} near={0.1} far={50} />
      <OrbitControls
        makeDefault
        target={target}
        enablePan={false}
        enableZoom
        enableRotate
        minDistance={orbit.minDistance}
        maxDistance={orbit.maxDistance}
        minPolarAngle={orbit.minPolarAngle}
        maxPolarAngle={orbit.maxPolarAngle}
        enableDamping
        dampingFactor={0.08}
      />
    </>
  );
}
