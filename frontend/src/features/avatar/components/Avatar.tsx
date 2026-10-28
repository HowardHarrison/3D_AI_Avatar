/**
 * Feature loader: cohesive stylized GLB → AvatarRuntime + face-pack masks; tick via useFrame.
 * Debug UI must not import this file or AvatarRuntime.
 */

import { useFrame } from "@react-three/fiber";
import { useEffect, useRef, useState } from "react";
import { AnimationClip, Group } from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { avatarConfig } from "../../../constants/avatarConfig";
import { environment } from "../../../constants/environment";
import type { AvatarLoadHandlers } from "../types";
import { AvatarRuntime } from "../../../services/avatar/AvatarRuntime";
import { validateAvatarConfig } from "../../../services/avatar/validateAvatarConfig";
import { logger } from "../../../utils/logger";

function loadGltf(loader: GLTFLoader, url: string): Promise<{ scene: Group; animations: AnimationClip[] }> {
  return new Promise((resolve, reject) => {
    loader.load(
      url,
      (gltf) => {
        resolve({
          scene: gltf.scene as Group,
          animations: gltf.animations as AnimationClip[],
        });
      },
      undefined,
      () => reject(new Error(`Failed to load ${url}`)),
    );
  });
}

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

    const bodyUrl = environment.avatarModelUrl || avatarConfig.modelUrl;
    const loader = new GLTFLoader();
    let cancelled = false;

    void (async () => {
      try {
        const body = await loadGltf(loader, bodyUrl);
        if (cancelled) {
          return;
        }
        const runtime = new AvatarRuntime(body.scene, body.animations);
        // Masks on the same Head as the stylized body — no separate giant face.glb.
        runtime.bindFacePack();
        if (cancelled) {
          runtime.dispose();
          return;
        }
        runtimeRef.current = runtime;
        setRoot(body.scene);
        onReady?.(runtime);
        runtime.getStatus().warnings.forEach((warning) => onWarning?.(warning));
      } catch {
        if (cancelled) {
          return;
        }
        logger.error("Failed to load avatar.");
        onError?.("Failed to load avatar.");
      }
    })();

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
