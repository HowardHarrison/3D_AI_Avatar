import { describe, expect, it } from "vitest";
import {
  FACE_MASK_BASE_PATH,
  FACE_PACK_CROSSFADE_MS,
  facePackRegistry,
  isFacePackExpression,
  resolveFaceMask,
} from "../../../../services/avatar/facial/FacePackRegistry";

describe("FacePackRegistry", () => {
  it("maps every semantic expression to a mask under the face-pack path", () => {
    const names = Object.keys(facePackRegistry);
    expect(names).toEqual(
      expect.arrayContaining(["neutral", "serious", "positive", "concerned", "amused", "curious"]),
    );
    for (const name of names) {
      const spec = resolveFaceMask(name);
      expect(spec.id).toBe(name);
      expect(spec.url).toBe(`${FACE_MASK_BASE_PATH}/${name}.webp`);
      expect(spec.crossfadeMs).toBe(FACE_PACK_CROSSFADE_MS);
    }
  });

  it("rejects unknown expression ids", () => {
    expect(() => resolveFaceMask("angry")).toThrow(/Unknown face-pack/);
    expect(isFacePackExpression("neutral")).toBe(true);
    expect(isFacePackExpression("angry")).toBe(false);
  });
});
