/**
 * Presenter page chrome: `main.page` wrapping the scene slot and aside.
 */

import type { ReactNode } from "react";

interface PresenterLayoutProps {
  children: ReactNode;
}

export function PresenterLayout(props: PresenterLayoutProps): JSX.Element {
  return <main className="page">{props.children}</main>;
}
