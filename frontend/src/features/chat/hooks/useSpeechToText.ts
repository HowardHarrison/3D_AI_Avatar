/**
 * Mic → transcript via the browser Web Speech API.
 * Continuous listening until the user stops; transcript accumulates.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import {
  getSpeechRecognitionConstructor,
  speechErrorMessage,
  type BrowserSpeechRecognition,
} from "../speechRecognition";

export interface UseSpeechToTextOptions {
  /** Full accumulated transcript (finals + current interim) for the draft field. */
  onTranscript: (text: string) => void;
  /** BCP-47 language tag for recognition. */
  lang?: string;
}

export interface UseSpeechToTextResult {
  supported: boolean;
  listening: boolean;
  error: string | null;
  start: () => void;
  /** Stop listening and return the accumulated transcript. */
  stop: () => string;
  toggle: () => string | void;
}

/**
 * Toggle microphone listening; keeps going until ``stop`` (not a short utterance).
 */
export function useSpeechToText(options: UseSpeechToTextOptions): UseSpeechToTextResult {
  const { onTranscript, lang = "en-US" } = options;
  const supported = getSpeechRecognitionConstructor() !== null;
  const [listening, setListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<BrowserSpeechRecognition | null>(null);
  const onTranscriptRef = useRef(onTranscript);
  onTranscriptRef.current = onTranscript;
  /** When true, restart recognition if the browser ends the session early. */
  const wantListenRef = useRef(false);
  const finalBufferRef = useRef("");
  const interimRef = useRef("");

  const emitTranscript = useCallback(() => {
    const combined = `${finalBufferRef.current}${interimRef.current}`.replace(/\s+/g, " ").trim();
    onTranscriptRef.current(combined);
  }, []);

  const stop = useCallback((): string => {
    wantListenRef.current = false;
    const recognition = recognitionRef.current;
    if (recognition) {
      recognition.onresult = null;
      recognition.onerror = null;
      recognition.onend = null;
      try {
        recognition.stop();
      } catch {
        // already stopped
      }
      recognitionRef.current = null;
    }
    setListening(false);
    const text = `${finalBufferRef.current}${interimRef.current}`.replace(/\s+/g, " ").trim();
    interimRef.current = "";
    return text;
  }, []);

  const start = useCallback(() => {
    const Ctor = getSpeechRecognitionConstructor();
    if (!Ctor) {
      setError("Speech recognition is not supported in this browser. Use Chrome or Edge.");
      return;
    }

    stop();
    setError(null);
    finalBufferRef.current = "";
    interimRef.current = "";
    wantListenRef.current = true;
    onTranscriptRef.current("");

    const recognition = new Ctor();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = lang;

    recognition.onresult = (event) => {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const piece = event.results[i][0]?.transcript ?? "";
        if (event.results[i].isFinal) {
          finalBufferRef.current += piece;
        } else {
          interim += piece;
        }
      }
      interimRef.current = interim;
      emitTranscript();
    };

    recognition.onerror = (event) => {
      if (event.error === "aborted") {
        return;
      }
      // "no-speech" during a long pause: keep listening if the user still wants to talk.
      if (event.error === "no-speech" && wantListenRef.current) {
        return;
      }
      const message = speechErrorMessage(event.error);
      if (message) {
        setError(message);
      }
      if (event.error === "not-allowed" || event.error === "service-not-allowed") {
        wantListenRef.current = false;
        setListening(false);
        recognitionRef.current = null;
      }
    };

    recognition.onend = () => {
      if (wantListenRef.current) {
        // Chrome often ends continuous sessions; restart until the user hits Stop.
        try {
          recognition.start();
          setListening(true);
          return;
        } catch {
          wantListenRef.current = false;
        }
      }
      setListening(false);
      recognitionRef.current = null;
    };

    recognitionRef.current = recognition;
    try {
      recognition.start();
      setListening(true);
    } catch {
      setError("Could not start the microphone.");
      wantListenRef.current = false;
      recognitionRef.current = null;
      setListening(false);
    }
  }, [emitTranscript, lang, stop]);

  const toggle = useCallback((): string | void => {
    if (listening) {
      return stop();
    }
    start();
  }, [listening, start, stop]);

  useEffect(() => () => {
    wantListenRef.current = false;
    stop();
  }, [stop]);

  return { supported, listening, error, start, stop, toggle };
}
