import { create } from 'zustand';
import type { SensorReading } from '@/types';

interface SensorStore {
  latestReadings: Record<string, SensorReading>;
  updateReading: (reading: SensorReading) => void;
}

export const useSensorStore = create<SensorStore>((set) => ({
  latestReadings: {},
  updateReading: (reading) =>
    set((state) => ({
      latestReadings: {
        ...state.latestReadings,
        [reading.device_id]: reading,
      },
    })),
}));
