/**
 * Crossfades face-pack mask textures onto a FaceCard plane under AvatarFace.
 * Semantic expression names only — callers use FacePackRegistry for URLs.
 */

import {
  DoubleSide,
  Mesh,
  MeshBasicMaterial,
  Object3D,
  PlaneGeometry,
  SRGBColorSpace,
  Texture,
  TextureLoader,
} from "three";
import type { ExpressionName } from "../../../types/animation";
import { logger } from "../../../utils/logger";
import { facePackRegistry, MOUTH_OPEN_MASK_URL } from "./FacePackRegistry";
import type { FaceMaskSpec } from "./facialTypes";

export class FaceMaskLayer {
  private readonly loader = new TextureLoader();
  private readonly textures = new Map<ExpressionName, Texture>();
  private cardRoot: Object3D | null = null;
  private layerA: Mesh | null = null;
  private layerB: Mesh | null = null;
  private matA: MeshBasicMaterial | null = null;
  private matB: MeshBasicMaterial | null = null;
  private mouthMesh: Mesh | null = null;
  private mouthMat: MeshBasicMaterial | null = null;
  private mouthTex: Texture | null = null;
  private showingA = true;
  private fadeElapsed = 0;
  private fadeDuration = 0.2;
  private fading = false;
  private current: ExpressionName = "neutral";

  /**
   * Create FaceCard planes on the character ``Head`` and hide duplicate drawn features.
   * Sized for the cohesive stylized head (not a giant Mixamo cover plate).
   */
  bind(faceRoot: Object3D): void {
    this.disposeCard();
    const socket =
      faceRoot.getObjectByName("Head") ??
      faceRoot.getObjectByName("AvatarFace") ??
      faceRoot;
    this.hideDrawnFeatures(socket);

    const geo = new PlaneGeometry(0.3, 0.34);
    // depthTest off: coplanar transparent cards z-fight / flicker when the head nods.
    this.matA = new MeshBasicMaterial({
      transparent: true,
      opacity: 1,
      depthWrite: false,
      depthTest: false,
      side: DoubleSide,
    });
    this.matB = new MeshBasicMaterial({
      transparent: true,
      opacity: 0,
      depthWrite: false,
      depthTest: false,
      side: DoubleSide,
    });
    this.layerA = new Mesh(geo, this.matA);
    this.layerB = new Mesh(geo.clone(), this.matB);
    this.layerA.name = "FaceCardA";
    this.layerB.name = "FaceCardB";
    this.layerA.renderOrder = 10;
    this.layerB.renderOrder = 11;

    this.mouthMat = new MeshBasicMaterial({
      transparent: true,
      opacity: 0,
      depthWrite: false,
      depthTest: false,
      side: DoubleSide,
    });
    this.mouthMesh = new Mesh(geo.clone(), this.mouthMat);
    this.mouthMesh.name = "FaceCardMouth";
    // In front of expression layers so speech covers closed lips.
    this.mouthMesh.position.z = 0.008;
    this.mouthMesh.renderOrder = 12;

    this.cardRoot = new Object3D();
    this.cardRoot.name = "FaceCard";
    // Front of stylized Head mesh (local +Z); oval mask sits on the peach head.
    this.cardRoot.position.set(0, 0.01, 0.175);
    this.cardRoot.add(this.layerA, this.layerB, this.mouthMesh);
    socket.add(this.cardRoot);
    this.showingA = true;
    this.fading = false;
  }

  /** Preload all face-pack textures. Safe to call once after bind. */
  async preload(): Promise<void> {
    const entries = Object.values(facePackRegistry);
    await Promise.all([
      ...entries.map((spec) => this.loadOne(spec)),
      this.loadMouthOpen(),
    ]);
    this.applyImmediate("neutral");
  }

  /**
   * Drive speech mouth overlay opacity (0 = closed, 1 = fully open).
   * Used when face-pack masks carry emotion and morphs are absent.
   */
  setMouthOpen(value: number): void {
    if (!this.mouthMat) {
      return;
    }
    this.mouthMat.opacity = Math.min(1, Math.max(0, value));
  }

  /**
   * Start a crossfade to the mask for ``name``.
   */
  setExpression(name: ExpressionName, crossfadeMs: number): void {
    if (name === this.current && !this.fading) {
      return;
    }
    this.current = name;
    this.fadeDuration = Math.max(0.05, crossfadeMs / 1000);
    this.fadeElapsed = 0;

    const tex = this.textures.get(name);
    if (!tex || !this.matA || !this.matB || !this.layerA || !this.layerB) {
      return;
    }

    const incoming = this.showingA ? this.matB : this.matA;
    const outgoing = this.showingA ? this.matA : this.matB;
    incoming.map = tex;
    incoming.needsUpdate = true;
    incoming.opacity = 0;
    outgoing.opacity = 1;
    this.fading = true;
  }

  /** Advance crossfade. Call from AvatarRuntime.update. */
  update(delta: number): void {
    if (!this.fading || !this.matA || !this.matB) {
      return;
    }
    this.fadeElapsed += delta;
    const t = Math.min(1, this.fadeElapsed / this.fadeDuration);
    const incoming = this.showingA ? this.matB : this.matA;
    const outgoing = this.showingA ? this.matA : this.matB;
    incoming.opacity = t;
    outgoing.opacity = 1 - t;
    if (t >= 1) {
      outgoing.opacity = 0;
      incoming.opacity = 1;
      this.showingA = !this.showingA;
      this.fading = false;
    }
  }

  getCurrent(): ExpressionName {
    return this.current;
  }

  dispose(): void {
    this.disposeCard();
    for (const tex of this.textures.values()) {
      tex.dispose();
    }
    this.textures.clear();
  }

  private applyImmediate(name: ExpressionName): void {
    const tex = this.textures.get(name);
    if (!tex || !this.matA || !this.matB) {
      return;
    }
    this.matA.map = tex;
    this.matA.opacity = 1;
    this.matA.needsUpdate = true;
    this.matB.opacity = 0;
    this.showingA = true;
    this.fading = false;
    this.current = name;
  }

  private async loadOne(spec: FaceMaskSpec): Promise<void> {
    try {
      const texture = await this.loader.loadAsync(spec.url);
      texture.colorSpace = SRGBColorSpace;
      this.textures.set(spec.id, texture);
    } catch {
      // Fallback to PNG if webp missing.
      const pngUrl = spec.url.replace(/\.webp$/i, ".png");
      try {
        const texture = await this.loader.loadAsync(pngUrl);
        texture.colorSpace = SRGBColorSpace;
        this.textures.set(spec.id, texture);
      } catch {
        logger.warn(`Face mask failed to load: ${spec.url}`);
      }
    }
  }

  private async loadMouthOpen(): Promise<void> {
    const apply = (texture: Texture): void => {
      texture.colorSpace = SRGBColorSpace;
      this.mouthTex?.dispose();
      this.mouthTex = texture;
      if (this.mouthMat) {
        this.mouthMat.map = texture;
        this.mouthMat.needsUpdate = true;
      }
    };
    try {
      apply(await this.loader.loadAsync(MOUTH_OPEN_MASK_URL));
    } catch {
      const pngUrl = MOUTH_OPEN_MASK_URL.replace(/\.webp$/i, ".png");
      try {
        apply(await this.loader.loadAsync(pngUrl));
      } catch {
        logger.warn(`Mouth open mask failed to load: ${MOUTH_OPEN_MASK_URL}`);
      }
    }
  }

  private hideDrawnFeatures(socket: Object3D): void {
    for (const name of ["LeftEye", "RightEye", "Nose", "Mouth"]) {
      const obj = socket.getObjectByName(name);
      if (obj) {
        obj.visible = false;
      }
    }
  }

  private disposeCard(): void {
    if (this.cardRoot?.parent) {
      this.cardRoot.parent.remove(this.cardRoot);
    }
    this.matA?.dispose();
    this.matB?.dispose();
    this.mouthMat?.dispose();
    this.mouthTex?.dispose();
    this.layerA?.geometry.dispose();
    this.layerB?.geometry.dispose();
    this.mouthMesh?.geometry.dispose();
    this.cardRoot = null;
    this.layerA = null;
    this.layerB = null;
    this.mouthMesh = null;
    this.matA = null;
    this.matB = null;
    this.mouthMat = null;
    this.mouthTex = null;
  }
}
