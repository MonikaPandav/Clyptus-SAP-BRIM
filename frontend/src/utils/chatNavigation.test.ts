import { describe, expect, it } from 'vitest';
import { readChatPromptState } from './chatNavigation';

describe('chat prompt navigation', () => {
  it('preserves an explicit submission intent through sign-in', () => {
    expect(readChatPromptState({ submitPrompt: ' How are billable items invoiced in SAP CI? ', unrelated: 'ignored' }))
      .toEqual({ submitPrompt: 'How are billable items invoiced in SAP CI?' });
  });

  it('keeps shared prompts as a prefill rather than an automatic submission', () => {
    expect(readChatPromptState({ prefillPrompt: 'Explain a provider contract.' }))
      .toEqual({ prefillPrompt: 'Explain a provider contract.' });
  });

  it.each([null, undefined, '', 'prompt', 42, {}, { submitPrompt: '  ' }, { submitPrompt: 123 }, { prefillPrompt: false }])(
    'ignores invalid navigation state: %j', (state) => {
      expect(readChatPromptState(state)).toBeUndefined();
    },
  );
});
