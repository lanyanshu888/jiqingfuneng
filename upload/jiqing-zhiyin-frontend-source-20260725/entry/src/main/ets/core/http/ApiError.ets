export class ApiError extends Error {
  readonly statusCode: number;
  readonly userMessage: string;

  constructor(statusCode: number, userMessage: string) {
    super(userMessage);
    this.statusCode = statusCode;
    this.userMessage = userMessage;
  }

  isUnauthorized(): boolean {
    return this.statusCode === 401;
  }
}

