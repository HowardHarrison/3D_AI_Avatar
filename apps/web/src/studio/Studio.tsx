/**
 * Default studio look: simple floor and backdrop suitable for a news presenter.
 * Keep geometry cheap for integrated GPUs.
 */

import { studioConfig } from "./studioConfig";

export function Studio(): JSX.Element {
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow={false}>
        <planeGeometry args={[12, 12]} />
        <meshStandardMaterial color={studioConfig.floorColor} roughness={0.9} metalness={0} />
      </mesh>
      <mesh position={[0, 2.2, -2.4]}>
        <planeGeometry args={[10, 6]} />
        <meshStandardMaterial color={studioConfig.backdropColor} roughness={1} metalness={0} />
      </mesh>
    </group>
  );
}
