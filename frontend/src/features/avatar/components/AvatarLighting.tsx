/**
 * Soft three-point lighting for the stylized bust shot. No shadow maps yet.
 */

export function AvatarLighting(): JSX.Element {
  return (
    <>
      <ambientLight intensity={0.55} />
      <directionalLight position={[2.4, 3.2, 2.6]} intensity={0.95} color="#fff8f0" />
      <directionalLight position={[-2.8, 1.8, 1.2]} intensity={0.4} color="#c5d8e8" />
      <directionalLight position={[0.2, 2.4, -2.8]} intensity={0.35} color="#ffffff" />
    </>
  );
}
