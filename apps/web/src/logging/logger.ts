/**
 * Lightweight logging facade so call sites do not scatter console.* usage.
 */

export type LogLevel = "debug" | "info" | "warn" | "error";

function write(level: LogLevel, message: string, extra?: unknown): void {
  const payload = extra === undefined ? [message] : [message, extra];
  if (level === "debug") {
    console.debug(...payload);
    return;
  }
  if (level === "info") {
    console.info(...payload);
    return;
  }
  if (level === "warn") {
    console.warn(...payload);
    return;
  }
  console.error(...payload);
}

export const logger = {
  debug: (message: string, extra?: unknown): void => write("debug", message, extra),
  info: (message: string, extra?: unknown): void => write("info", message, extra),
  warn: (message: string, extra?: unknown): void => write("warn", message, extra),
  error: (message: string, extra?: unknown): void => write("error", message, extra),
};
