// State shared by the chat and composer modules.

export const chatState = {
  // AbortController for the reply being streamed, or null when idle.
  controller: null,
  // Recent completed turns ({role, content}); sent with each message because the
  // server keeps no conversation state (it runs serverless on Vercel).
  history: []
};

export const isStreaming = () => Boolean(chatState.controller);
