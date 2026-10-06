/**
 * Validate avatar configuration used at runtime initialization.
 */

export interface AvatarConfigInput {
  modelUrl: string;
  camera: {
    position: [number, number, number];
    target: [number, number, number];
    fov: number;
  };
  performance: {
    pixelRatioMax: number;
  };
}

export class AvatarConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AvatarConfigError";
  }
}

/**
 * Ensure camera, performance, and model URL values are usable.
 * @throws AvatarConfigError when a value is missing or out of range.
 */
export function validateAvatarConfig(config: AvatarConfigInput): AvatarConfigInput {
  if (!config.modelUrl || typeof config.modelUrl !== "string") {
    throw new AvatarConfigError("modelUrl is required.");
  }
  if (config.camera.fov <= 0 || config.camera.fov >= 120) {
    throw new AvatarConfigError("camera.fov must be between 0 and 120.");
  }
  if (config.performance.pixelRatioMax < 0.5 || config.performance.pixelRatioMax > 3) {
    throw new AvatarConfigError("pixelRatioMax must be between 0.5 and 3.");
  }
  if (config.camera.position.length !== 3 || config.camera.target.length !== 3) {
    throw new AvatarConfigError("camera position and target must be xyz triples.");
  }
  return config;
}
