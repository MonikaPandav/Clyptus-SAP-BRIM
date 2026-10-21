import type { User, Chat, Message, Citation, WebSource, WebImage, DocumentAttachment, DocumentListResponse, ProcessingProgress } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export const getStoredToken = (): string | null => {
  return localStorage.getItem('sap_assistant_token');
};

export const setStoredToken = (token: string): void => {
  localStorage.setItem('sap_assistant_token', token);
};

export const clearStoredToken = (): void => {
  localStorage.removeItem('sap_assistant_token');
};

const authHeaders = (): Record<string, string> => {
  const token = getStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Auth API
export const apiRegister = async (name: string, email: string, password: string) => {
  const resp = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Registration failed');
  }
  return resp.json();
};

export const apiLogin = async (email: string, password: string) => {
  const resp = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Invalid email or password');
  }
  return resp.json();
};

export const apiAdminLogin = async (email: string, password: string) => {
  const resp = await fetch(`${API_BASE_URL}/auth/admin-login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Invalid administrator email or password');
  }
  return resp.json();
};


export const apiDemoLogin = async () => {
  const resp = await fetch(`${API_BASE_URL}/auth/demo`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Demo login failed');
  }
  return resp.json();
};

export const apiGetMe = async (): Promise<User> => {
  const resp = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: { ...authHeaders() },
  });
  if (!resp.ok) {
    throw new Error('Unauthorized');
  }
  return resp.json();
};

// Chats API
export const apiGetChats = async (search?: string): Promise<Chat[]> => {
  const url = new URL(`${API_BASE_URL}/chats`);
  if (search) url.searchParams.append('search', search);

  const resp = await fetch(url.toString(), {
    headers: { ...authHeaders() },
  });
  if (!resp.ok) throw new Error('Failed to load chats');
  return resp.json();
};

export const apiCreateChat = async (title?: string): Promise<Chat> => {
  const resp = await fetch(`${API_BASE_URL}/chats`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ title: title || 'New SAP Chat' }),
  });
  if (!resp.ok) throw new Error('Failed to create chat');
  return resp.json();
};

export const apiGetChat = async (chatId: string): Promise<Chat & { messages: Message[] }> => {
  const resp = await fetch(`${API_BASE_URL}/chats/${chatId}`, {
    headers: { ...authHeaders() },
  });
  if (!resp.ok) throw new Error('Chat not found');
  return resp.json();
};

export const apiUpdateChat = async (chatId: string, title: string): Promise<Chat> => {
  const resp = await fetch(`${API_BASE_URL}/chats/${chatId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ title }),
  });
  if (!resp.ok) throw new Error('Failed to update chat');
  return resp.json();
};

export const apiDeleteChat = async (chatId: string): Promise<void> => {
  const resp = await fetch(`${API_BASE_URL}/chats/${chatId}`, {
    method: 'DELETE',
    headers: { ...authHeaders() },
  });
  if (!resp.ok) throw new Error('Failed to delete chat');
};

// Messages API
export const apiGetMessages = async (chatId: string): Promise<Message[]> => {
  const resp = await fetch(`${API_BASE_URL}/chats/${chatId}/messages`, {
    headers: { ...authHeaders() },
  });
  if (!resp.ok) throw new Error('Failed to load messages');
  return resp.json();
};

export const apiExtractDocument = async (file: File): Promise<{
  filename: string;
  file_type: string;
  size_bytes: number;
  page_count: number;
  char_count: number;
  preview: string;
  text: string;
  detected_question?: string | null;
  analysis_method?: 'vision' | 'vision+ocr' | 'ocr' | null;
}> => {
  const formData = new FormData();
  formData.append('file', file);
  const headers = authHeaders();
  // Ensure browser sets multipart/form-data boundary automatically
  delete (headers as Record<string, string>)['Content-Type'];

  const resp = await fetch(`${API_BASE_URL}/chats/extract-document`, {
    method: 'POST',
    headers,
    body: formData,
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to extract document (${resp.statusText})`);
  }
  return resp.json();
};

export const apiSendMessage = async (
  chatId: string,
  content: string,
  attachments?: DocumentAttachment[]
): Promise<Message> => {
  const resp = await fetch(`${API_BASE_URL}/chats/${chatId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({
      content,
      attachments: attachments && attachments.length > 0 ? attachments : undefined
    }),
  });
  if (!resp.ok) throw new Error('Failed to send message');
  return resp.json();
};

export const apiSavePartialMessage = async (chatId: string, content: string): Promise<void> => {
  try {
    await fetch(`${API_BASE_URL}/chats/${chatId}/messages/save-partial`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ content }),
    });
  } catch (err) {
    console.error('Failed to save partial message:', err);
  }
};

/** Creates (or refreshes) the public link for one prompt and returns its token. */
export const apiSharePrompt = async (chatId: string, messageId: string): Promise<string> => {
  const resp = await fetch(`${API_BASE_URL}/chats/${chatId}/messages/${messageId}/share`, {
    method: 'POST',
    headers: authHeaders(),
  });
  if (!resp.ok) throw new Error('Could not create share link');
  return (await resp.json()).token;
};

/** Public: no login needed to read a shared prompt. */
export const apiGetSharedPrompt = async (token: string): Promise<{ content: string; created_at: string }> => {
  const resp = await fetch(`${API_BASE_URL}/shared/prompts/${encodeURIComponent(token)}`);
  if (!resp.ok) throw new Error('Shared prompt not found');
  return resp.json();
};

// SSE Streaming
export interface StreamStatus {
  type: 'status';
  stage: 'thinking' | 'retrieval' | 'reranking' | 'grounding' | 'generation' | 'document_analysis' | string;
  message: string;
}

export interface StreamMetadata {
  message_id?: string;
  source_type?: 'knowledge_base' | 'github_repo' | 'web' | 'combined' | 'abstention' | 'insufficient' | 'refusal' | 'error' | 'interrupted' | 'attached_document';
  grounding_score?: number;
  citations?: Citation[];
  web_sources?: WebSource[];
  images?: WebImage[];
  is_in_rag_pipeline?: boolean;
  kb_score?: number;
  web_score?: number;
  winning_score?: number;
  source_scores?: Record<string, number>;
  comparison_audit?: Record<string, unknown>;
  verification_status?: 'verified' | 'partial' | 'unverified' | 'abstention';
  internal_evidence_confidence?: number;
  selected_evidence_quality?: number;
  external_search_used?: boolean;
  follow_up_questions?: string[];
  full_answer?: string;
}

export interface StreamCallbacks {
  onStatus?: (status: StreamStatus) => void;
  onMetadata?: (meta: StreamMetadata) => void;
  onToken?: (token: string) => void;
  onDone?: (meta: StreamMetadata, fullAnswer?: string) => void;
  onError?: (err: any) => void;
  /** Stored id of the prompt that this stream answers. */
  onUserMessage?: (messageId: string) => void;
}

export const apiStreamMessage = (
  chatId: string,
  content: string,
  callbacks: StreamCallbacks,
  signal?: AbortSignal,
  attachments?: DocumentAttachment[]
): Promise<void> =>
  streamSSE(
    `${API_BASE_URL}/chats/${chatId}/messages?stream=true`,
    { content, attachments: attachments && attachments.length > 0 ? attachments : undefined },
    callbacks,
    signal
  );

/** Replaces a stored prompt, drops every later message, and streams the new answer. */
export const apiEditMessageStream = (
  chatId: string,
  messageId: string,
  content: string,
  callbacks: StreamCallbacks,
  signal?: AbortSignal
): Promise<void> =>
  streamSSE(`${API_BASE_URL}/chats/${chatId}/messages/${messageId}/edit`, { content }, callbacks, signal);

const streamSSE = async (
  url: string,
  body: Record<string, unknown>,
  callbacks: StreamCallbacks,
  signal?: AbortSignal
): Promise<void> => {
  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify(body),
      signal,
    });

    if (!resp.ok) {
      throw new Error(`Failed to stream message: ${resp.statusText}`);
    }

    const reader = resp.body?.getReader();
    if (!reader) throw new Error('ReadableStream not supported');

    const decoder = new TextDecoder();
    let buffer = '';
    let isCompleted = false;
    let finalReceivedAnswer: string | undefined = undefined;
    let lastDoneMeta: StreamMetadata = {};

    const finishStream = (meta?: StreamMetadata, fullAnswer?: string) => {
      if (!isCompleted) {
        isCompleted = true;
        const effectiveMeta = meta || lastDoneMeta;
        callbacks.onDone?.(effectiveMeta, fullAnswer || finalReceivedAnswer);
      }
    };

    const processBlock = (block: string) => {
      const trimmed = block.trim();
      if (!trimmed) return;

      const lines = trimmed.split('\n');
      for (const line of lines) {
        const trimmedLine = line.trim();
        if (trimmedLine.startsWith('data:')) {
          const rawData = trimmedLine.slice(5).trim();
          if (!rawData) continue;

          try {
            const parsed = JSON.parse(rawData);

            if (parsed.type === 'status') {
              callbacks.onStatus?.(parsed as StreamStatus);
            } else if (parsed.type === 'token') {
              const tokenContent = parsed.content ?? parsed.token ?? '';
              if (tokenContent) {
                callbacks.onToken?.(tokenContent);
              }
            } else if (parsed.type === 'done') {
              lastDoneMeta = parsed;
              const ans = parsed.answer || parsed.full_answer;
              if (ans) {
                finalReceivedAnswer = ans;
              }
              finishStream(parsed, ans);
            } else if (parsed.type === 'error') {
              callbacks.onError?.(new Error(parsed.message || 'Generation error occurred'));
            } else if (parsed.type === 'user_message') {
              callbacks.onUserMessage?.(parsed.message_id);
            } else if (parsed.citations !== undefined || parsed.message_id !== undefined) {
              lastDoneMeta = { ...lastDoneMeta, ...parsed };
              callbacks.onMetadata?.(parsed);
            }
          } catch (e) {
            console.error('SSE JSON parse error:', e, rawData);
          }
        }
      }
    };

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        if (buffer.trim()) {
          processBlock(buffer);
          buffer = '';
        }
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const normalized = buffer.replace(/\r\n/g, '\n');
      const blocks = normalized.split('\n\n');
      buffer = blocks.pop() || '';

      for (const block of blocks) {
        processBlock(block);
      }
    }

    finishStream();
  } catch (err: any) {
    if (signal?.aborted || err?.name === 'AbortError') {
      console.log('Streaming aborted by user.');
      return;
    }
    callbacks.onError?.(err);
  }
};

// ==========================================
// Document Management & Processing API
// ==========================================

export const apiGetDocuments = async (params?: {
  status?: string;
  search?: string;
  page?: number;
  page_size?: number;
}): Promise<DocumentListResponse> => {
  const url = new URL(`${API_BASE_URL}/documents`);
  if (params?.status && params.status !== 'all') {
    url.searchParams.append('status', params.status);
  }
  if (params?.search) {
    url.searchParams.append('search', params.search);
  }
  if (params?.page) {
    url.searchParams.append('page', params.page.toString());
  }
  if (params?.page_size) {
    url.searchParams.append('page_size', params.page_size.toString());
  }

  const resp = await fetch(url.toString(), {
    headers: { ...authHeaders() },
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch knowledge base documents');
  }
  return resp.json();
};

export const apiGetDocumentDetails = async (documentId: string): Promise<any> => {
  const resp = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    headers: { ...authHeaders() },
  });
  if (!resp.ok) {
    throw new Error('Failed to fetch document details');
  }
  return resp.json();
};

export const apiUploadDocuments = async (files: File[]): Promise<{
  status: string;
  registered_count: number;
  documents: any[];
  errors: any[];
}> => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const resp = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    headers: { ...authHeaders() },
    body: formData,
  });

  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to upload documents');
  }
  return resp.json();
};

export const apiProcessAllDocuments = async (force: boolean = false): Promise<{
  status: string;
  message: string;
}> => {
  const resp = await fetch(`${API_BASE_URL}/documents/process-all`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ force }),
  });

  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to trigger batch document processing');
  }
  return resp.json();
};

export const apiProcessIndividualDocument = async (
  documentId: string,
  force: boolean = true
): Promise<{ status: string; message: string }> => {
  const resp = await fetch(`${API_BASE_URL}/documents/${documentId}/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ force }),
  });

  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to process document');
  }
  return resp.json();
};

export const apiGetProcessingStatus = async (): Promise<ProcessingProgress> => {
  const resp = await fetch(`${API_BASE_URL}/documents/processing-status`, {
    headers: { ...authHeaders() },
  });
  if (!resp.ok) {
    throw new Error('Failed to fetch processing status');
  }
  return resp.json();
};

export const apiDeleteDocument = async (documentId: string): Promise<{
  success: boolean;
  deleted_document_id: string;
  deleted_filename: string;
  deleted_chunks: number;
  file_deleted_from_disk: boolean;
  vector_database_status: string;
}> => {
  const resp = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: 'DELETE',
    headers: { ...authHeaders() },
  });

  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to delete document');
  }
  return resp.json();
};

export const connectProcessingStream = (
  onProgress: (progress: ProcessingProgress) => void,
  onError?: (error: any) => void
): (() => void) => {
  const token = getStoredToken();
  const url = token
    ? `${API_BASE_URL}/documents/processing-stream?token=${encodeURIComponent(token)}`
    : `${API_BASE_URL}/documents/processing-stream`;
  const eventSource = new EventSource(url);

  eventSource.onmessage = (event) => {
    try {
      if (event.data && event.data.trim()) {
        const data = JSON.parse(event.data);
        onProgress(data);
      }
    } catch (err) {
      console.error('Error parsing processing stream event:', err);
    }
  };

  eventSource.onerror = (err) => {
    onError?.(err);
  };

  return () => {
    eventSource.close();
  };
};

export const apiGetRAGInspectionDocuments = async (): Promise<any> => {
  const resp = await fetch(`${API_BASE_URL}/rag-inspect/documents`, {
    headers: { ...authHeaders() },
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch knowledge base inspection status');
  }
  return resp.json();
};

export const apiTestSimilaritySearch = async (
  query: string,
  top_k: number = 10,
  include_web_search: boolean = false
): Promise<any> => {
  const resp = await fetch(`${API_BASE_URL}/rag-inspect/similarity-search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ query, top_k, include_web_search }),
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to run similarity search inspection');
  }
  return resp.json();
};

export const apiTriggerIngest = async (): Promise<any> => {
  const resp = await fetch(`${API_BASE_URL}/admin/documents/ingest`, {
    method: 'POST',
    headers: { ...authHeaders() },
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to trigger document ingestion');
  }
  return resp.json();
};


