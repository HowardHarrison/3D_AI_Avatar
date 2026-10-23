/**
 * Browser Web Speech API helpers (Chrome / Edge). No backend STT in this step.
 */

export interface BrowserSpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: BrowserSpeechRecognitionEvent) => void) | null;
  onerror: ((event: BrowserSpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
}

export interface BrowserSpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: {
    length: number;
    [index: number]: {
      isFinal: boolean;
      length: number;
      [index: number]: { transcript: string };
    };
  };
}

export interface BrowserSpeechRecognitionErrorEvent extends Event {
  error: string;
  message?: string;
}

type SpeechRecognitionConstructor = new () => BrowserSpeechRecognition;

/**
 * Resolve the browser SpeechRecognition constructor, if available.
 */
export function getSpeechRecognitionConstructor(): SpeechRecognitionConstructor | null {
  const w = window as Window & {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

/**
 * Map Web Speech error codes to short UI messages.
 */
export function speechErrorMessage(code: string): string {
  switch (code) {
    case "not-allowed":
    case "service-not-allowed":
      return "Microphone permission denied. Allow mic access and try again.";
    case "no-speech":
      return "No speech detected. Try again.";
    case "audio-capture":
      return "No microphone found.";
    case "network":
      return "Speech recognition network error.";
    case "aborted":
      return "";
    default:
      return `Speech recognition error (${code}).`;
  }
}
