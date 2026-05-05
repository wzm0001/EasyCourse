export interface APIResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

export interface PageResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface PageRequest {
  page: number;
  page_size: number;
}
