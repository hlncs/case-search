import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { API_BASE_URL } from '@utils/constants';

/**
 * API client wrapper using axios
 */
class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * GET request
   */
  async get<T>(url: string, config: AxiosRequestConfig = {}): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  /**
   * POST request
   */
  async post<T>(url: string, data: any, config: AxiosRequestConfig = {}): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  /**
   * PUT request
   */
  async put<T>(url: string, data: any, config: AxiosRequestConfig = {}): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  /**
   * DELETE request
   */
  async delete<T>(url: string, config: AxiosRequestConfig = {}): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }

  /**
   * File upload
   */
  async uploadFile<T>(url: string, file: File): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    return this.post<T>(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }
}

export default new APIClient();
