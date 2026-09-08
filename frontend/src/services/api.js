const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Parses an unstructured Indian address via the AddressAI FastAPI backend
 * @param {string} address - Raw Indian address
 * @returns {Promise<Object>} - Parsed components, coordinates, confidence score, etc.
 */
export async function parseAddress(address) {
  if (!address || !address.trim()) {
    throw new Error('Please enter a valid address to parse.');
  }

  const endpoint = `${API_BASE_URL}/parse`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15000);

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ address: address.trim() }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server responded with status ${response.status}`);
    }

    return await response.json();
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === 'AbortError') {
      throw new Error('Request timed out. Please check if the backend server is running.');
    }
    throw err;
  }
}

/**
 * Checks backend health status
 */
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
    });
    return response.ok;
  } catch {
    return false;
  }
}
