/**
 * Drive the avatar through a spoken reply: map cues → TTS → talk/idle.
 */

import { resolveAudioUrl, synthesizeSpeech } from "../../api/tts";
import { environment } from "../../constants/environment";
import { logger } from "../../utils/logger";
import type { AvatarHandle } from "../../types";
import { mapReplyReaction, type ReplyReaction } from "./mapReplyReaction";

const timers = new WeakMap<AvatarHandle, number>();

/**
 * Apply semantic face / gesture / head cues from a mapped reaction.
 *
 * @param controller - Semantic avatar API handle.
 * @param reaction - Result of {@link mapReplyReaction}.
 */
export function applyReplyReaction(
  controller: AvatarHandle,
  reaction: ReplyReaction,
): void {
  controller.setGaze("camera");
  controller.setExpression(reaction.expression);
  if (reaction.headMotion) {
    controller.setHeadMotion(reaction.headMotion);
  }
  if (reaction.gesture) {
    controller.playGesture(reaction.gesture);
  }
}

/**
 * Speak the assistant reply (TTS when available; timed mime reaction as fallback).
 * Picks expression/gesture from reply text via {@link mapReplyReaction}.
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
  const reaction = mapReplyReaction(reply);

  try {
    const { audioUrl } = await synthesizeSpeech(reply, apiBaseUrl);
    const playUrl = resolveAudioUrl(audioUrl, apiBaseUrl);
    // Apply after TTS is ready so the gesture lands with speech, not during the wait.
    applyReplyReaction(controller, reaction);
    await controller.speakFromUrl(playUrl);
  } catch (error) {
    logger.warn("TTS unavailable; using timed talk reaction.", error);
    playTimedFallback(controller, reply, reaction);
  }
}

function clearTimedFallback(controller: AvatarHandle): void {
  const previous = timers.get(controller);
  if (previous !== undefined) {
    window.clearTimeout(previous);
    timers.delete(controller);
  }
}

function playTimedFallback(
  controller: AvatarHandle,
  reply: string,
  reaction: ReplyReaction,
): void {
  clearTimedFallback(controller);
  controller.startSpeaking();
  applyReplyReaction(controller, reaction);

  const durationMs = Math.min(8000, Math.max(2200, reply.length * 45));
  const handle = window.setTimeout(() => {
    controller.stopSpeaking();
    controller.setExpression("neutral");
    timers.delete(controller);
  }, durationMs);
  timers.set(controller, handle);
}
