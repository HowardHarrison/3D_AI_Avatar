/**
 * Shared helpers for reading FastAPI-style error payloads.
 */

/**
 * Extract a human-readable message from a failed fetch Response.
 *
 * @param response - Non-OK response.
 * @param fallbackLabel - Prefix used when JSON detail is unavailable.
 */
export async function readErrorDetail(
  response: Response,
  fallbackLabel = "Request failed",
): Promise<string> {
  try {
    const payload: unknown = await response.json();
    if (payload && typeof payload === "object" && "detail" in payload) {
      const detail = (payload as { detail: unknown }).detail;
      if (typeof detail === "string") {
        return detail;
      }
      if (Array.isArray(detail)) {
        return detail.map((item) => JSON.stringify(item)).join("; ");
      }
    }
  } catch {
    // fall through
  }
  return `${fallbackLabel} (${response.status}).`;
}
