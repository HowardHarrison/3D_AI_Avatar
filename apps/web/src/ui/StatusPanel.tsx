/**
 * Runtime status readout. Values are sampled on an interval, not every animation frame.
 */

interface StatusPanelProps {
  loaded: boolean;
  fps: number;
  state: string;
  activeAnimation: string;
  currentExpression: string;
  audioTime: number;
  audioDuration: number;
  message: string | null;
  warnings: string[];
}

export function StatusPanel(props: StatusPanelProps): JSX.Element {
  return (
    <div className="debug-section">
      <h3>Runtime</h3>
      <dl className="status-list">
        <div>
          <dt>FPS</dt>
          <dd>{props.fps.toFixed(0)}</dd>
        </div>
        <div>
          <dt>Avatar loaded</dt>
          <dd>{props.loaded ? "yes" : "no"}</dd>
        </div>
        <div>
          <dt>State</dt>
          <dd>{props.state}</dd>
        </div>
        <div>
          <dt>Active animation</dt>
          <dd>{props.activeAnimation}</dd>
        </div>
        <div>
          <dt>Expression</dt>
          <dd>{props.currentExpression}</dd>
        </div>
        <div>
          <dt>Audio time</dt>
          <dd>
            {props.audioTime.toFixed(2)} / {props.audioDuration.toFixed(2)}
          </dd>
        </div>
      </dl>
      {props.message ? <p className="status-error">{props.message}</p> : null}
      {props.warnings.map((warning) => (
        <p key={warning} className="status-warning">
          {warning}
        </p>
      ))}
    </div>
  );
}
