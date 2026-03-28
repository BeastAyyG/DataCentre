import { useEffect, useRef, useCallback } from 'react';
import { useSensorStore } from '@/store/useSensorStore';
import { useAlertStore } from '@/store/useAlertStore';
import type { WSMessage } from '@/types';

const HEARTBEAT_INTERVAL_MS = 30_000;

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const updateReading = useSensorStore((s) => s.updateReading);
  const addAlert = useAlertStore((s) => s.addAlert);
  const heartbeatRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const connect = useCallback(() => {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = ${proto}///ws/sensors;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data);
        if (msg.type === 'sensor_update') {
          updateReading(msg.payload);
        } else if (msg.type === 'alert_triggered') {
          addAlert(msg.payload);
        }
      } catch (e) {
        console.error('WS parse error:', e);
      }
    };

    ws.onclose = () => {
      if (heartbeatRef.current) clearInterval(heartbeatRef.current);
      setTimeout(connect, 3000);
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
      ws.close();
    };

    // Heartbeat: send ping every 30s to detect stale connections
    heartbeatRef.current = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('ping');
      }
    }, HEARTBEAT_INTERVAL_MS);
  }, [updateReading, addAlert]);

  useEffect(() => {
    connect();
    return () => {
      if (heartbeatRef.current) clearInterval(heartbeatRef.current);
      wsRef.current?.close();
    };
  }, [connect]);
}
