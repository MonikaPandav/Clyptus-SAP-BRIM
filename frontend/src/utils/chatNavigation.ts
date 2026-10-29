export interface ChatPromptState {
  prefillPrompt?: string;
  submitPrompt?: string;
}

/** Only forward supported prompt intents through the sign-in redirect. */
export function readChatPromptState(value: unknown): ChatPromptState | undefined {
  if (!value || typeof value !== 'object') return undefined;
  const state = value as Record<string, unknown>;
  if (typeof state.submitPrompt === 'string' && state.submitPrompt.trim()) {
    return { submitPrompt: state.submitPrompt.trim() };
  }
  if (typeof state.prefillPrompt === 'string' && state.prefillPrompt.trim()) {
    return { prefillPrompt: state.prefillPrompt.trim() };
  }
  return undefined;
}
