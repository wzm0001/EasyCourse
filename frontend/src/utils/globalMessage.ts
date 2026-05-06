import type { MessageInstance } from 'antd/es/message/interface';

let globalMessage: MessageInstance | null = null;

export const setGlobalMessage = (msg: MessageInstance) => {
  globalMessage = msg;
};

export const getGlobalMessage = (): MessageInstance => {
  if (!globalMessage) {
    console.warn('[globalMessage] message instance not initialized yet');
  }
  return globalMessage!;
};
