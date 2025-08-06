/**
 * Sentinel-AI JavaScript SDK
 * Easy-to-use client for intelligent AI routing.
 */

class ProviderType {
  static OPENAI = 'openai';
  static ANTHROPIC = 'anthropic';
  static GROQ = 'groq';
  static AUTO = 'auto';
}

class ChatMessage {
  constructor(role, content) {
    this.role = role;
    this.content = content;
  }
}

class ChatResponse {
  constructor(data) {
    this.content = data.content;
    this.provider = data.provider;
    this.model = data.model || 'unknown';
    this.cost = data.cost || 0.0;
    this.tokensUsed = data.tokens_used;
    this.cacheHit = data.cache_hit || false;
  }
}

class SentinelAIClient {
  /**
   * Sentinel-AI JavaScript client for intelligent AI routing.
   * 
   * @param {string} apiKey - Your API key
   * @param {string} baseUrl - Base URL for the API
   * @param {number} timeout - Request timeout in seconds
   */
  constructor(apiKey, baseUrl = 'http://localhost:8000', timeout = 30000) {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.timeout = timeout;
  }

  /**
   * Send a chat completion request through intelligent routing.
   * 
   * @param {ChatMessage[]} messages - List of chat messages
   * @param {string} provider - AI provider to use (or 'auto' for intelligent selection)
   * @param {Object} options - Additional options
   * @returns {Promise<ChatResponse>} Chat response with metadata
   */
  async chat(messages, provider = ProviderType.AUTO, options = {}) {
    const payload = {
      messages: messages.map(msg => ({
        role: msg.role,
        content: msg.content
      })),
      provider: provider,
      requirements: { ...options }
    };

    const response = await this._makeRequest('/v1/ai/chat', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    return new ChatResponse(response);
  }

  /**
   * Send a simple completion request.
   * 
   * @param {string} prompt - The prompt to complete
   * @param {string} provider - AI provider to use
   * @param {Object} options - Additional options
   * @returns {Promise<ChatResponse>} Chat response with metadata
   */
  async complete(prompt, provider = ProviderType.AUTO, options = {}) {
    const messages = [new ChatMessage('user', prompt)];
    return await this.chat(messages, provider, options);
  }

  /**
   * Get routing metrics and statistics.
   * 
   * @returns {Promise<Object>} Dictionary with various metrics
   */
  async getMetrics() {
    return await this._makeRequest('/v1/ai/metrics', {
      method: 'GET'
    });
  }

  /**
   * Make an HTTP request to the API.
   * 
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Request options
   * @returns {Promise<Object>} Response data
   * @private
   */
  async _makeRequest(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const requestOptions = {
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        ...options.headers
      },
      timeout: this.timeout,
      ...options
    };

    try {
      const response = await fetch(url, requestOptions);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} - ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    }
  }
}

// Convenience functions
function createClient(apiKey, baseUrl = 'http://localhost:8000') {
  return new SentinelAIClient(apiKey, baseUrl);
}

async function chatCompletion(apiKey, messages, baseUrl = 'http://localhost:8000', options = {}) {
  const client = new SentinelAIClient(apiKey, baseUrl);
  return await client.chat(messages, ProviderType.AUTO, options);
}

async function textCompletion(apiKey, prompt, baseUrl = 'http://localhost:8000', options = {}) {
  const client = new SentinelAIClient(apiKey, baseUrl);
  return await client.complete(prompt, ProviderType.AUTO, options);
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
  // CommonJS
  module.exports = {
    SentinelAIClient,
    ProviderType,
    ChatMessage,
    ChatResponse,
    createClient,
    chatCompletion,
    textCompletion
  };
} else if (typeof define === 'function' && define.amd) {
  // AMD
  define(function() {
    return {
      SentinelAIClient,
      ProviderType,
      ChatMessage,
      ChatResponse,
      createClient,
      chatCompletion,
      textCompletion
    };
  });
} else if (typeof window !== 'undefined') {
  // Browser
  window.SentinelAI = {
    SentinelAIClient,
    ProviderType,
    ChatMessage,
    ChatResponse,
    createClient,
    chatCompletion,
    textCompletion
  };
}

// Example usage
if (typeof window !== 'undefined') {
  // Browser example
  window.SentinelAIExample = async function() {
    const apiKey = 'your-api-key';
    const client = new SentinelAIClient(apiKey);

    try {
      // Chat completion
      const messages = [
        new ChatMessage('user', 'Hello, how are you?')
      ];
      const response = await client.chat(messages);
      console.log('Response:', response.content);
      console.log('Provider:', response.provider);
      console.log('Cost:', response.cost);

      // Simple completion
      const completion = await client.complete('Explain quantum computing in simple terms');
      console.log('Completion:', completion.content);

      // Get metrics
      const metrics = await client.getMetrics();
      console.log('Metrics:', metrics);
    } catch (error) {
      console.error('Error:', error);
    }
  };
}