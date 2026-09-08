const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Parse using either the existing endpoint or the ML-enhanced endpoint.
 * @param {string} address - Raw Indian address
 * @param {'original'|'ml'} method - Endpoint strategy
 */
export async function parseAddress(address, method = 'original') {
  if (!address || !address.trim()) {
    throw new Error('Please enter a valid address to parse.');
  }

  const endpoint = `${API_BASE_URL}/${method === 'ml' ? 'parse_ml' : 'parse'}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), method === 'ml' ? 30000 : 15000);

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
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

/** Convenience wrappers for callers that prefer explicit methods. */
export function parseAddressOriginal(address) {
  return parseAddress(address, 'original');
}

export function parseAddressML(address) {
  return parseAddress(address, 'ml');
}

export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {method: 'GET'});
    return response.ok;
  } catch {
    return false;
  }
}
