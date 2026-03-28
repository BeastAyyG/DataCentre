import { create } from 'zustand';
import type { WorkOrder } from '@/types';

interface WorkOrderStore {
  workOrders: WorkOrder[];
  setWorkOrders: (orders: WorkOrder[]) => void;
  addWorkOrder: (wo: WorkOrder) => void;
  updateWorkOrder: (wo: WorkOrder) => void;
}

export const useWorkOrderStore = create<WorkOrderStore>((set) => ({
  workOrders: [],
  setWorkOrders: (workOrders) => set({ workOrders }),
  addWorkOrder: (wo) => set((s) => ({ workOrders: [wo, ...s.workOrders] })),
  updateWorkOrder: (wo) =>
    set((s) => ({
      workOrders: s.workOrders.map((w) => (w.id === wo.id ? wo : w)),
    })),
}));
