import { useEffect, useState } from "react";

/**
 * Guarda e sincroniza um estado com o localStorage.
 * Usado enquanto não temos backend (fase 2 trocará por API).
 */
export function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const raw = localStorage.getItem(key);
      return raw ? (JSON.parse(raw) as T) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      /* quota cheia ou modo privado — ignorar */
    }
  }, [key, value]);

  return [value, setValue] as const;
}