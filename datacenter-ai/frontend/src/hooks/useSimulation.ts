import { useMutation } from '@tanstack/react-query';
import { apiSimulation } from '@/api/client';
import { useSimulationStore } from '@/store/useSimulationStore';

export function useSimulation() {
  const setResult = useSimulationStore((s) => s.setResult);
  const setRunning = useSimulationStore((s) => s.setRunning);

  return useMutation({
    mutationFn: apiSimulation.whatIf,
    onMutate: () => setRunning(true),
    onSuccess: (data) => {
      setResult(data);
      setRunning(false);
    },
    onError: () => setRunning(false),
  });
}
