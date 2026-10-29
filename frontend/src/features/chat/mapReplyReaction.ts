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
/** Explicit wave stage directions or wording. */
const WAVE = /\b(wave|waves|waving)\b|\*\s*waves?\b/i;
/** Raise / hand-up — must win over "can't/sorry". */
const RAISE =
  /\b(raise|raising|raised|lift|lifting)\b[\s\S]{0,48}\b(hand|arm)s?\b|\b(hand|arm)s?\b[\s\S]{0,32}\b(up|air)\b|\bin the air\b|\*\s*raises?\b/i;
const GREETING =
  /\b(hi there|hello|hey there|good (morning|afternoon|evening)|nice to (see|meet) you|great to see you)\b/i;
const BOTH_HANDS =
  /\bboth\s+(hands?|arms?)\b|\b(hands?|arms?)\s+both\b|\b(two|2)\s+(hands|arms)\b/i;

/**
 * Prefer side / both cues from the user message, then the assistant reply.
 */
function raiseGesture(intentText: string): GestureName {
  if (BOTH_HANDS.test(intentText)) {
    return "bothHands";
  }
  const left = /\bleft\b/i.test(intentText);
  const right = /\bright\b/i.test(intentText);
  const wantsWave = WAVE.test(intentText);
  if (left && !right && !wantsWave) {
    return "raiseHandLeft";
  }
  if (left && !right) {
    return "pointLeft";
  }
  if (right && !left && !wantsWave) {
    return "raiseHand";
  }
  if (right && !left) {
    return "wave";
  }
  return "wave";
}

/**
 * Choose a lightweight face + body reaction from reply wording.
 *
 * @param reply - Assistant message text (plain language).
 * @param userText - Optional user utterance so “left / both hands” still win if the model omits them.
 * @returns Semantic names only — never clip or morph indexes.
 */
export function mapReplyReaction(reply: string, userText = ""): ReplyReaction {
  const text = reply.trim();
  const user = userText.trim();
  // User intent first so “raise your left hand” works even if the reply only says “*waves*”.
  const intent = user ? `${user}\n${text}` : text;

  if (!text && !user) {
    return { expression: "neutral" };
  }

  const wantsRaise =
    WAVE.test(text) ||
    WAVE.test(user) ||
    RAISE.test(text) ||
    RAISE.test(user) ||
    GREETING.test(text);

  if (wantsRaise) {
    return {
      expression: "positive",
      gesture: raiseGesture(intent),
      headMotion: "nod",
    };
  }

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
