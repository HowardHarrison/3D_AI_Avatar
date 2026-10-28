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
/** Explicit wave stage directions or wording in the assistant reply. */
const WAVE = /\b(wave|waves|waving)\b|\*\s*waves?\b/i;
/** Raise / hand-up — must win over "can't/sorry" so refusals-in-text still don't steal the gesture. */
const RAISE =
  /\b(raise|raising|raised|lift|lifting)\b[\s\S]{0,48}\b(hand|arm)s?\b|\b(hand|arm)s?\b[\s\S]{0,32}\b(up|air)\b|\bin the air\b|\*\s*raises?\b/i;
/** Hello / greeting — raise open hand (closest clip to a friendly wave). */
const GREETING =
  /\b(hi there|hello|hey there|good (morning|afternoon|evening)|nice to (see|meet) you|great to see you)\b/i;

/**
 * Default wave/raise = right arm overhead (`openHand`).
 * Explicit left → `pointLeft`. Explicit right (no wave) still uses `emphasize`.
 */
function raiseGesture(text: string): GestureName {
  const left = /\bleft\b/i.test(text);
  const right = /\bright\b/i.test(text);
  const wantsWave = /\b(wave|waves|waving)\b|\*\s*waves?\b/i.test(text);
  if (left && !right) {
    return "pointLeft";
  }
  if (right && !left && !wantsWave) {
    return "emphasize";
  }
  return "openHand";
}

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

  // Hand-up / wave / hello before concern ("can't", "sorry") and before generic "great".
  if (WAVE.test(text) || RAISE.test(text) || GREETING.test(text)) {
    return {
      expression: "positive",
      gesture: raiseGesture(text),
      headMotion: "nod",
    };
  }

  // Tone keywords beat length heuristics (e.g. short "Sorry.").
  if (CONCERN.test(text)) {
    return { expression: "concerned", gesture: "handsTogether", headMotion: "tiltLeft" };
  }

  if (POSITIVE.test(text) || /!\s*$/.test(text)) {
    return { expression: "positive", gesture: "emphasize" };
  }

  if (text.includes("?")) {
    return { expression: "curious", gesture: "openHand", headMotion: "tiltRight" };
  }

  if (SHORT_AFFIRM.test(text) || text.length < 24) {
    return { expression: "amused", headMotion: "nod" };
  }

  if (text.length > 160) {
    return { expression: "serious", gesture: "emphasize" };
  }

  if (text.length > 80) {
    return { expression: "neutral", gesture: "openHand" };
  }

  return { expression: "neutral", gesture: "openHand" };
}
