/**
 * Application shell. React owns UI lifecycle; the avatar runtime owns the render loop.
 */

import { AppRoutes } from "./routes";

export function App(): JSX.Element {
  return <AppRoutes />;
}
