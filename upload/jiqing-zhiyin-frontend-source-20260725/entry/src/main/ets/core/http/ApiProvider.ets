import { authStore } from '../auth/AuthStore';
import { Environment } from '../config/Environment';
import { ApiClient } from './ApiClient';

export const apiClient = new ApiClient(Environment.API_BASE_URL, authStore);

