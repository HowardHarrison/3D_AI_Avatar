import { describe, expect, it } from "vitest";
import { avatarConfig } from "../../../constants/avatarConfig";
import { validateAvatarConfig } from "../../../services/avatar/validateAvatarConfig";

describe("validateAvatarConfig", () => {
  it("accepts the default avatar configuration", () => {
    const result = validateAvatarConfig({
      modelUrl: avatarConfig.modelUrl,
      camera: avatarConfig.camera,
      performance: avatarConfig.performance,
    });
    expect(result.modelUrl).toBe("/avatars/presenter.glb");
    expect(result.performance.pixelRatioMax).toBe(1.5);
  });

  it("rejects an empty model URL and an illegal FOV", () => {
    expect(() =>
      validateAvatarConfig({
        modelUrl: "",
        camera: avatarConfig.camera,
        performance: avatarConfig.performance,
      }),
    ).toThrow(/modelUrl/);
    expect(() =>
      validateAvatarConfig({
        modelUrl: avatarConfig.modelUrl,
        camera: { ...avatarConfig.camera, fov: 180 },
        performance: avatarConfig.performance,
      }),
    ).toThrow(/fov/);
  });
});
