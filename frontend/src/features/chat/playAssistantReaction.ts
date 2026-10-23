/**
 * Drive the avatar through a short “talking” reaction for a chat reply.
 * TTS comes later; for now we use speaking state + gesture + expression.
 */

import type { AvatarHandle } from "../../types";

const timers = new WeakMap<AvatarHandle, number>();

/**
 * Start speaking cues, then return to idle after a duration based on reply length.
 *
 * @param controller - Semantic avatar API handle.
 * @param reply - Assistant text (used only to size the talk window).
 */
export function playAssistantReaction(controller: AvatarHandle, reply: string): void {
  const previous = timers.get(controller);
  if (previous !== undefined) {
    window.clearTimeout(previous);
  }

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
