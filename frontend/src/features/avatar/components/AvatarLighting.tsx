/**
 * Three-point studio lighting. No shadow maps in Phase 1.
 */

export function AvatarLighting(): JSX.Element {
  return (
    <>
      <ambientLight intensity={0.35} />
      <directionalLight position={[2.4, 3.2, 2.6]} intensity={1.15} color="#fff4e8" />
      <directionalLight position={[-2.8, 1.8, 1.2]} intensity={0.35} color="#9eb6ff" />
      <directionalLight position={[0.2, 2.4, -2.8]} intensity={0.45} color="#ffffff" />
    </>
  );
}
