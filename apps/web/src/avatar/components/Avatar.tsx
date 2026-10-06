/**
 * Loads presenter.glb, constructs AvatarRuntime, and advances it on the render loop.
 */

import { useFrame } from "@react-three/fiber";
import { useEffect, useRef, useState } from "react";
import { AnimationClip, Group } from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { environment } from "../../config/environment";
import { logger } from "../../logging/logger";
import { AvatarRuntime } from "../AvatarRuntime";
import { avatarConfig } from "../avatarConfig";
import type { AvatarLoadHandlers } from "../avatarTypes";
import { validateAvatarConfig } from "../validateAvatarConfig";

export function Avatar(props: AvatarLoadHandlers): JSX.Element | null {
  const { onReady, onError, onWarning } = props;
  const [root, setRoot] = useState<Group | null>(null);
  const runtimeRef = useRef<AvatarRuntime | null>(null);

  useEffect(() => {
    try {
      validateAvatarConfig({
        modelUrl: environment.avatarModelUrl || avatarConfig.modelUrl,
        camera: avatarConfig.camera,
        performance: avatarConfig.performance,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Invalid configuration.";
      logger.error(message);
      onError?.(message);
      return;
    }

    const url = environment.avatarModelUrl || avatarConfig.modelUrl;
    const loader = new GLTFLoader();
    let cancelled = false;

    loader.load(
      url,
      (gltf) => {
        if (cancelled) {
          return;
        }
        const scene = gltf.scene as Group;
        const clips = gltf.animations as AnimationClip[];
        const runtime = new AvatarRuntime(scene, clips);
        runtimeRef.current = runtime;
        setRoot(scene);
        onReady?.(runtime);
        runtime.getStatus().warnings.forEach((warning) => onWarning?.(warning));
      },
      undefined,
      () => {
        if (cancelled) {
          return;
        }
        logger.error("Failed to load avatar.");
        onError?.("Failed to load avatar.");
      },
    );

    return () => {
      cancelled = true;
      runtimeRef.current?.dispose();
      runtimeRef.current = null;
    };
  }, [onError, onReady, onWarning]);

  useFrame((_, delta) => {
    runtimeRef.current?.update(delta);
  });

  if (!root) {
    return null;
  }

  return <primitive object={root} />;
}
