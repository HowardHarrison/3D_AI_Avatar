/**
 * Map assistant reply text to semantic avatar cues (expression / gesture / head).
 * Heuristic only — no LLM planning. Product layers can replace this later.
 */

import type { ExpressionName, GestureName, HeadMotionName } from "../../types/animation";

/** Semantic reaction applied before / during a spoken reply. */
export interface ReplyReaction {
  expression: ExpressionName;
  /** Omit when a head nod alone is enough (very short replies). */
  gesture?: GestureName;
  headMotion?: HeadMotionName;
}

const CONCERN =
  /\b(sorry|unfortunately|can't|cannot|unable|error|problem|issue|worried|afraid|don't know|do not know)\b/i;
const POSITIVE =
  /\b(great|awesome|glad|happy|thanks|thank you|wonderful|excellent|love|pleasure|good news)\b/i;
const SHORT_AFFIRM = /^(ok|okay|yes|yep|sure|alright|got it|sounds good)[.!]?$/i;

/**
 * Choose a lightweight face + body reaction from reply wording.
 *
 * @param reply - Assistant message text (plain language).
 * @returns Semantic names only — never clip or morph indexes.
 */
export function mapReplyReaction(reply: string): ReplyReaction {
  const text = reply.trim();
  if (!text) {
    return { expression: "neutral" };
  }

  // Tone keywords beat length heuristics (e.g. short "Sorry.").
  if (CONCERN.test(text)) {
    return { expression: "concerned", gesture: "handsTogether", headMotion: "tiltLeft" };
  }

  if (POSITIVE.test(text) || /!\s*$/.test(text)) {
    return { expression: "positive", gesture: "emphasize" };
  }

  if (text.includes("?")) {
    return { expression: "serious", gesture: "openHand", headMotion: "tiltRight" };
  }

  if (SHORT_AFFIRM.test(text) || text.length < 24) {
    return { expression: "positive", headMotion: "nod" };
  }

  if (text.length > 160) {
    return { expression: "serious", gesture: "emphasize" };
  }

  if (text.length > 80) {
    return { expression: "neutral", gesture: "openHand" };
  }

  return { expression: "neutral", gesture: "openHand" };
}
