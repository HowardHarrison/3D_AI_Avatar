/**
 * Gesture, expression, and head buttons. They only call the semantic avatar API.
 */

import type { ExpressionName, GestureName, HeadMotionName } from "../../../types/animation";
import type { AvatarHandle } from "../types";

interface AnimationControlsProps {
  controller: AvatarHandle | null;
}

const GESTURES: { id: GestureName; label: string }[] = [
  { id: "openHand", label: "Open Hand" },
  { id: "emphasize", label: "Emphasize" },
  { id: "pointLeft", label: "Point Left" },
  { id: "pointRight", label: "Point Right" },
  { id: "handsTogether", label: "Hands Together" },
];

const EXPRESSIONS: { id: ExpressionName; label: string }[] = [
  { id: "neutral", label: "Neutral" },
  { id: "serious", label: "Serious" },
  { id: "positive", label: "Positive" },
  { id: "concerned", label: "Concerned" },
  { id: "amused", label: "Amused" },
  { id: "curious", label: "Curious" },
];

const HEADS: { id: HeadMotionName; label: string }[] = [
  { id: "nod", label: "Nod" },
  { id: "turnLeft", label: "Turn Left" },
  { id: "turnRight", label: "Turn Right" },
  { id: "tiltLeft", label: "Tilt Left" },
  { id: "tiltRight", label: "Tilt Right" },
];

export function AnimationControls(props: AnimationControlsProps): JSX.Element {
  const { controller } = props;
  const disabled = !controller;

  return (
    <div className="debug-section">
      <h3>Animation</h3>
      <div className="debug-row">
        <button type="button" disabled={disabled} onClick={() => controller?.reset()}>
          Idle
        </button>
        {GESTURES.map((item) => (
          <button
            key={item.id}
            type="button"
            disabled={disabled}
            onClick={() => controller?.playGesture(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>
      <h3>Expression</h3>
      <div className="debug-row">
        {EXPRESSIONS.map((item) => (
          <button
            key={item.id}
            type="button"
            disabled={disabled}
            onClick={() => controller?.setExpression(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>
      <h3>Head</h3>
      <div className="debug-row">
        {HEADS.map((item) => (
          <button
            key={item.id}
            type="button"
            disabled={disabled}
            onClick={() => controller?.setHeadMotion(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
}
