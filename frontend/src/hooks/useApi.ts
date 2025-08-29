import { useState } from 'react';

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const execute = async (apiCall: () => Promise<any>) => {
    setLoading(true);
    setError('');
    try {
      const result = await apiCall();
      return result;
    } catch (err: any) {
      setError(err.message || 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { execute, loading, error, setError };
}