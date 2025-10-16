/**
 * Mock HTTP server for testing
 */

import { MockAPIResponses } from './mockApiResponses';

export class MockHTTPClient {
  private baseUrl: string;
  private apiKey: string;
  public requests: Array<{ method: string; url: string; data?: any }> = [];

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async get(url: string, options?: any): Promise<any> {
    this.requests.push({ method: 'GET', url, data: options });

    // Mock responses based on URL
    if (url.includes('/tasks/')) {
      if (url.includes('/status')) {
        return { status: 'completed', progress: 100 };
      }
      if (url.includes('/result')) {
        return MockAPIResponses.taskResult();
      }
      return MockAPIResponses.taskDetails();
    }

    if (url.includes('/tasks')) {
      // Check if pagination parameters are present
      if (options?.params?.page || options?.params?.pageSize) {
        return MockAPIResponses.paginatedTasksList();
      }
      return MockAPIResponses.tasksList();
    }

    if (url.includes('/steps/')) {
      if (url.includes('/logs')) {
        return { logs: ['Log line 1', 'Log line 2'] };
      }
      if (url.includes('/output')) {
        return { output: 'Step output data' };
      }
      return MockAPIResponses.stepDetails();
    }

    if (url.includes('/steps')) {
      // Check if pagination parameters are present
      if (options?.params?.page || options?.params?.pageSize) {
        return MockAPIResponses.paginatedStepsList();
      }
      return MockAPIResponses.stepsList();
    }

    if (url.includes('/models')) {
      return MockAPIResponses.modelsList();
    }

    if (url.includes('/history')) {
      // Check if pagination parameters are present
      if (options?.params?.page || options?.params?.pageSize) {
        return MockAPIResponses.paginatedHistoryList();
      }
      return MockAPIResponses.historyList();
    }

    if (url.includes('/agents')) {
      // Check if pagination parameters are present
      if (options?.params?.page || options?.params?.pageSize) {
        return MockAPIResponses.paginatedAgentsList();
      }
      return MockAPIResponses.paginatedAgentsList(); // Default to paginated for agents
    }

    if (url.includes('/health')) {
      return { status: 'healthy' };
    }

    return {};
  }

  async post(url: string, data?: any, options?: any): Promise<any> {
    this.requests.push({ method: 'POST', url, data });

    // Mock responses based on URL
    if (url.includes('/agents/chat')) {
      return MockAPIResponses.chatAgentResponse();
    }

    if (url.includes('/agents/plan')) {
      return MockAPIResponses.planAgentResponse();
    }

    if (url.includes('/agents/code')) {
      return MockAPIResponses.codeAgentResponse();
    }

    if (url.includes('/agents/test')) {
      return MockAPIResponses.testAgentResponse();
    }

    if (url.includes('/agents/git')) {
      return MockAPIResponses.gitAgentResponse();
    }

    if (url.includes('/agents/docs')) {
      return MockAPIResponses.docsAgentResponse();
    }

    if (url.includes('/tasks')) {
      if (url.includes('/cancel')) {
        return MockAPIResponses.taskCancelled();
      }
      return MockAPIResponses.taskCreated();
    }

    if (url.includes('/steps')) {
      if (url.includes('/cancel')) {
        return MockAPIResponses.stepCancelled();
      }
      if (url.includes('/retry')) {
        return MockAPIResponses.stepCreated();
      }
      return MockAPIResponses.stepCreated();
    }

    return {};
  }

  async* postStream(url: string, data?: any, options?: any): AsyncGenerator<any> {
    this.requests.push({ method: 'POST_STREAM', url, data });

    // Mock streaming responses
    if (url.includes('/agents/chat') || url.includes('/agents/code')) {
      const chunks = MockAPIResponses.chatAgentStream();
      for (const chunk of chunks) {
        yield chunk;
      }
    } else if (url.includes('/workflow')) {
      const chunks = MockAPIResponses.agenticWorkflowStream();
      for (const chunk of chunks) {
        yield chunk;
      }
    }
  }

  async patch(url: string, data?: any, options?: any): Promise<any> {
    this.requests.push({ method: 'PATCH', url, data });

    if (url.includes('/tasks/')) {
      return MockAPIResponses.taskUpdated();
    }

    if (url.includes('/steps/')) {
      return MockAPIResponses.stepUpdated();
    }

    return {};
  }

  async delete(url: string, options?: any): Promise<any> {
    this.requests.push({ method: 'DELETE', url });

    return { success: true };
  }

  reset() {
    this.requests = [];
  }

  getLastRequest() {
    return this.requests[this.requests.length - 1];
  }
}

export class MockResponse {
  status: number;
  data: any;
  headers: Record<string, string>;

  constructor(status: number, data: any, headers: Record<string, string> = {}) {
    this.status = status;
    this.data = data;
    this.headers = headers;
  }

  json() {
    return Promise.resolve(this.data);
  }

  text() {
    return Promise.resolve(JSON.stringify(this.data));
  }
}

export class MockStreamResponse {
  private chunks: any[];
  private index: number = 0;

  constructor(chunks: any[]) {
    this.chunks = chunks;
  }

  async* [Symbol.asyncIterator]() {
    for (const chunk of this.chunks) {
      yield { data: JSON.stringify(chunk) };
    }
  }
}

