import type { Message } from '../../types';

/** Optimistic prompts (id "user-…") have no stored row to edit or share until the stream confirms them. */
export const isStoredMessage = (message: Message) => !message.id.startsWith('user-');
