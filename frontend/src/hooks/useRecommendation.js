import { useState, useCallback } from 'react';
import { getRecommendation } from '../utils/api';

export function useRecommendation() {
  const [result,  setResult]  = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const recommend = useCallback(async (gameState) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getRecommendation(gameState);
      setResult(data);
      return data;
    } catch (e) {
      setError(e.message || 'Could not reach advisor');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const clear = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { recommend, result, loading, error, clear };
}
