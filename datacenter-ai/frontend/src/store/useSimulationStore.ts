import { create } from 'zustand';
import type { SimulationResult } from '@/types';

interface SimulationStore {
  result: SimulationResult | null;
  isRunning: boolean;
  setResult: (result: SimulationResult | null) => void;
  setRunning: (running: boolean) => void;
}

export const useSimulationStore = create<SimulationStore>((set) => ({
  result: null,
  isRunning: false,
  setResult: (result) => set({ result }),
  setRunning: (isRunning) => set({ isRunning }),
}));
