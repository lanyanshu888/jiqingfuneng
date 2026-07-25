import { http } from '@kit.NetworkKit';
import { ApiError } from './ApiError';

export interface TokenProvider {
  getToken(): Promise<string>;
}

class RequestHeader {
  'Content-Type': string = 'application/json';
  Accept: string = 'application/json';
  Authorization?: string;
}

export class ApiClient {
  private readonly baseUrl: string;
  private readonly tokenProvider: TokenProvider;

  constructor(baseUrl: string, tokenProvider: TokenProvider) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.tokenProvider = tokenProvider;
  }

  get<T>(path: string): Promise<T> {
    return this.request<T>(path);
  }

  post<T>(path: string, body: object): Promise<T> {
    return this.request<T>(path, body);
  }

  private async request<T>(path: string, body?: object): Promise<T> {
    const token = await this.tokenProvider.getToken();
    const request = http.createHttp();
    const header = new RequestHeader();
    if (token.length > 0) {
      header.Authorization = `Token ${token}`;
    }

    const options: http.HttpRequestOptions = {
      method: body === undefined ? http.RequestMethod.GET : http.RequestMethod.POST,
      header: header,
      readTimeout: 30000,
      connectTimeout: 15000,
      expectDataType: http.HttpDataType.STRING
    };
    if (body !== undefined) {
      options.extraData = JSON.stringify(body);
    }

    try {
      const response = await request.request(`${this.baseUrl}${path}`, options);
      return this.parseResponse<T>(response);
    } catch (error) {
      throw new ApiError(0, `网络请求失败：${this.baseUrl}${path}`);
    } finally {
      request.destroy();
    }
  }

  private parseResponse<T>(response: http.HttpResponse): T {
    const statusCode = Number(response.responseCode);
    const raw = response.result as string;
    if (statusCode < 200 || statusCode >= 300) {
      throw new ApiError(statusCode, this.readErrorMessage(raw, statusCode));
    }
    if (raw.length === 0) {
      return null as T;
    }
    return JSON.parse(raw) as T;
  }

  private readErrorMessage(raw: string, statusCode: number): string {
    if (raw.length === 0) {
      return `接口请求失败：${statusCode}`;
    }
    return raw;
  }
}
