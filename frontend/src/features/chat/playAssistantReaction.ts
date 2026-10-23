/**
 * Drive the avatar through a spoken reply: TTS → AudioController → talk/idle.
 */

import { resolveAudioUrl, synthesizeSpeech } from "../../api/tts";
import { environment } from "../../constants/environment";
import { logger } from "../../utils/logger";
import type { AvatarHandle } from "../../types";

const timers = new WeakMap<AvatarHandle, number>();

/**
 * Speak the assistant reply (TTS when available; timed mime reaction as fallback).
 *
 * @param controller - Semantic avatar API handle.
 * @param reply - Assistant text to speak.
 * @param apiBaseUrl - Backend origin (empty = Vite proxy / same origin).
 */
export async function playAssistantReaction(
  controller: AvatarHandle,
  reply: string,
  apiBaseUrl: string = environment.apiBaseUrl,
): Promise<void> {
  clearTimedFallback(controller);

  try {
    const { audioUrl } = await synthesizeSpeech(reply, apiBaseUrl);
    const playUrl = resolveAudioUrl(audioUrl, apiBaseUrl);
    await controller.speakFromUrl(playUrl);
  } catch (error) {
    logger.warn("TTS unavailable; using timed talk reaction.", error);
    playTimedFallback(controller, reply);
  }
}

function clearTimedFallback(controller: AvatarHandle): void {
  const previous = timers.get(controller);
  if (previous !== undefined) {
    window.clearTimeout(previous);
    timers.delete(controller);
  }
}

function playTimedFallback(controller: AvatarHandle, reply: string): void {
  clearTimedFallback(controller);
  controller.startSpeaking();
  controller.setGaze("camera");
  controller.setExpression("positive");
  controller.playGesture("openHand");

  const durationMs = Math.min(8000, Math.max(2200, reply.length * 45));
  const handle = window.setTimeout(() => {
    controller.stopSpeaking();
    controller.setExpression("neutral");
    timers.delete(controller);
  }, durationMs);
  timers.set(controller, handle);
}
