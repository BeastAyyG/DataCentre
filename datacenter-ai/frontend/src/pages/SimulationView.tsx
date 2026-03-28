import { useEffect, useState, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiCyber } from '@/api/client';

interface SimulationState {
  running: boolean;
  active_scenario_id: string | null;
  active_threat: {
    id: string;
    threat_type: string;
    threat_name: string;
    severity: string;
    phase: string;
    status: string;
    target_device_id: string;
    source_ip: string;
    indicator_count: number;
    confidence: number;
    description: string;
    recommended_action: string;
    started_at: string;
    detected_at: string | null;
  } | null;
  affected_devices: string[];
  attack_phase: string;
  indicators_triggered: Array<{
    indicator_type: string;
    value: number;
    threshold: number;
    triggered: boolean;
    description: string;
    phase: string;
    timestamp: string;
  }>;
  elapsed_sec: number;
}

// Stargate Datacenter Layout - Massive US Data Center
interface Rack {
  id: string;
  name: string;
  zone: string;
  row: number;
  col: number;
  servers: number;
  status: 'healthy' | 'at_risk' | 'critical' | 'attacked' | 'affected' | 'offline';
  temp?: number;
  power?: number;
}

interface CRAC {
  id: string;
  name: string;
  zone: string;
  capacity: string;
  status: 'healthy' | 'at_risk' | 'critical';
}

interface Zone {
  id: string;
  name: string;
  color: string;
}

// Generate Stargate datacenter layout - 8 rows x 12 racks = 96 racks!
const generateStargateDatacenter = (): { racks: Rack[], cracs: CRAC[], zones: Zone[] } => {
  const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
  const racks: Rack[] = [];
  const zones: Zone[] = [
    { id: 'cold-north', name: 'COLD AISLE NORTH', color: '#1e40af' },
    { id: 'hot-south', name: 'HOT AISLE SOUTH', color: '#dc2626' },
    { id: 'core', name: 'CORE NETWORK', color: '#7c3aed' },
    { id: 'edge', name: 'EDGE COMPUTE', color: '#059669' },
  ];
  
  let rackIndex = 0;
  rows.forEach((row, rowIdx) => {
    for (let col = 1; col <= 12; col++) {
      rackIndex++;
      const zone = rowIdx < 2 ? 'edge' : rowIdx > 5 ? 'core' : row === 'A' || row === 'D' || row === 'E' || row === 'H' ? 'cold-north' : 'hot-south';
      racks.push({
        id: `RACK-${row}${col.toString().padStart(2, '0')}`,
        name: `${row}${col.toString().padStart(2, '0')}`,
        zone,
        row: rowIdx,
        col,
        servers: 48, // High-density racks
        status: 'healthy',
        temp: 21 + Math.random() * 5,
        power: 8 + Math.random() * 4,
      });
    }
  });

  const cracs: CRAC[] = [
    { id: 'CRAC-N1', name: 'CRAC N-1', zone: 'cold-north', capacity: '500 Ton', status: 'healthy' },
    { id: 'CRAC-N2', name: 'CRAC N-2', zone: 'cold-north', capacity: '500 Ton', status: 'healthy' },
    { id: 'CRAC-N3', name: 'CRAC N-3', zone: 'cold-north', capacity: '500 Ton', status: 'healthy' },
    { id: 'CRAC-S1', name: 'CRAC S-1', zone: 'hot-south', capacity: '500 Ton', status: 'healthy' },
    { id: 'CRAC-S2', name: 'CRAC S-2', zone: 'hot-south', capacity: '500 Ton', status: 'healthy' },
    { id: 'CRAC-S3', name: 'CRAC S-3', zone: 'hot-south', capacity: '500 Ton', status: 'healthy' },
    { id: 'CRAC-C1', name: 'CRAC C-1', zone: 'core', capacity: '750 Ton', status: 'healthy' },
    { id: 'CRAC-C2', name: 'CRAC C-2', zone: 'core', capacity: '750 Ton', status: 'healthy' },
  ];

  return { racks, cracs, zones };
};

export function SimulationViewPage() {
  const [wsConnected, setWsConnected] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const { data: simState } = useQuery<SimulationState>({
    queryKey: ['simulation-state'],
    queryFn: apiCyber.getSimulationState,
    refetchInterval: 1000,
  });

  // Generate datacenter layout
  const { racks: allRacks, cracs } = generateStargateDatacenter();

  // Connect to WebSocket for real-time updates
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/simulation-sync`;
    
    let ws: WebSocket | null = null;
    let reconnectTimeout: ReturnType<typeof setTimeout>;

    const connect = () => {
      try {
        ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          setWsConnected(true);
          console.log('Simulation sync connected');
        };

        ws.onclose = () => {
          setWsConnected(false);
          reconnectTimeout = setTimeout(connect, 3000);
        };

        ws.onerror = () => {
          ws?.close();
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('Simulation update:', data);
          } catch (e) {
            console.error('Failed to parse simulation message');
          }
        };
      } catch (e) {
        reconnectTimeout = setTimeout(connect, 3000);
      }
    };

    connect();

    return () => {
      if (ws) ws.close();
      clearTimeout(reconnectTimeout);
    };
  }, []);

  // Draw Stargate datacenter visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    const width = canvas.width;
    const height = canvas.height;

    // Clear with dark background
    ctx.fillStyle = '#0a0a0f';
    ctx.fillRect(0, 0, width, height);

    // Draw grid pattern
    ctx.strokeStyle = '#1a1a2e';
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x += 30) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += 30) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Get attack state
    const isAttack = simState?.running && simState?.active_threat;
    const targetId = simState?.active_threat?.target_device_id;
    const phase = simState?.attack_phase || 'none';
    const affectedDevices = simState?.affected_devices || [];
    const indicators = simState?.indicators_triggered || [];

    // Phase colors
    const phaseColors: Record<string, string> = {
      recon: '#3b82f6',      // Blue
      exploit: '#f59e0b',    // Amber
      action: '#f97316',     // Orange
      impact: '#dc2626',     // Red
      none: '#22c55e',       // Green
    };
    const phaseColor = phaseColors[phase] || '#22c55e';

    // Layout calculations - Stargate datacenter
    const padding = 80;
    const rackWidth = Math.min(60, (width - padding * 2) / 14);
    const rackHeight = Math.min(30, (height - padding * 2) / 10);
    const rackGap = 4;
    const rowGap = 8;

    // Draw datacenter zones
    const zoneWidth = width - padding * 2;
    const zoneHeight = height - padding * 2;

    // Core Zone (center)
    ctx.fillStyle = 'rgba(124, 58, 237, 0.1)';
    ctx.fillRect(padding + zoneWidth * 0.25, padding + zoneHeight * 0.3, zoneWidth * 0.5, zoneHeight * 0.4);
    ctx.strokeStyle = '#7c3aed';
    ctx.lineWidth = 2;
    ctx.strokeRect(padding + zoneWidth * 0.25, padding + zoneHeight * 0.3, zoneWidth * 0.5, zoneHeight * 0.4);
    ctx.fillStyle = '#7c3aed';
    ctx.font = 'bold 12px sans-serif';
    ctx.fillText('CORE NETWORK ZONE', padding + zoneWidth * 0.25 + 20, padding + zoneHeight * 0.3 + 20);

    // Edge Zone (top and bottom)
    ctx.fillStyle = 'rgba(5, 150, 105, 0.1)';
    ctx.fillRect(padding, padding, zoneWidth, zoneHeight * 0.2);
    ctx.strokeStyle = '#059669';
    ctx.strokeRect(padding, padding, zoneWidth, zoneHeight * 0.2);
    ctx.fillStyle = '#059669';
    ctx.fillText('EDGE COMPUTE ZONE', padding + 20, padding + 20);

    ctx.fillStyle = 'rgba(5, 150, 105, 0.1)';
    ctx.fillRect(padding, padding + zoneHeight * 0.8, zoneWidth, zoneHeight * 0.2);
    ctx.strokeStyle = '#059669';
    ctx.strokeRect(padding, padding + zoneHeight * 0.8, zoneWidth, zoneHeight * 0.2);
    ctx.fillText('EDGE COMPUTE ZONE', padding + 20, padding + zoneHeight * 0.8 + 20);

    // Cold Aisle (North)
    ctx.fillStyle = 'rgba(59, 130, 246, 0.15)';
    ctx.fillRect(padding + 20, padding + zoneHeight * 0.22, zoneWidth - 40, zoneHeight * 0.06);
    ctx.fillStyle = '#3b82f6';
    ctx.font = 'bold 10px sans-serif';
    ctx.fillText('? COLD AISLE ?', padding + zoneWidth / 2 - 40, padding + zoneHeight * 0.22 + 12);

    // Hot Aisle (South)
    ctx.fillStyle = 'rgba(239, 68, 68, 0.15)';
    ctx.fillRect(padding + 20, padding + zoneHeight * 0.72, zoneWidth - 40, zoneHeight * 0.06);
    ctx.fillStyle = '#ef4444';
    ctx.fillText('? HOT AISLE ?', padding + zoneWidth / 2 - 40, padding + zoneHeight * 0.72 + 12);

    // Draw racks in grid layout (8 rows x 12 cols)
    const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
    const startX = padding + 50;
    const startY = padding + zoneHeight * 0.25;

    rows.forEach((row, rowIdx) => {
      for (let col = 1; col <= 12; col++) {
        const rackId = `RACK-${row}${col.toString().padStart(2, '0')}`;
        const x = startX + (col - 1) * (rackWidth + rackGap);
        const y = startY + rowIdx * (rackHeight + rowGap);

        // Determine rack status
        let status: string = 'healthy';
        if (isAttack && rackId === targetId) {
          status = 'attacked';
        } else if (isAttack && affectedDevices.includes(rackId)) {
          status = 'affected';
        }

        // Rack fill color based on status
        let fillColor = '#1e293b';
        let strokeColor = '#334155';
        let glowColor = null;

        if (status === 'attacked') {
          fillColor = `rgba(220, 38, 38, ${0.3 + Math.sin(Date.now() / 200) * 0.2})`;
          strokeColor = '#dc2626';
          glowColor = 'rgba(220, 38, 38, 0.5)';
        } else if (status === 'affected') {
          fillColor = 'rgba(245, 158, 11, 0.2)';
          strokeColor = '#f59e0b';
          glowColor = 'rgba(245, 158, 11, 0.3)';
        }

        // Draw glow effect for attacked racks
        if (glowColor && isAttack) {
          ctx.shadowColor = glowColor;
          ctx.shadowBlur = 15;
        }

        // Draw rack
        ctx.fillStyle = fillColor;
        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = status === 'attacked' ? 2 : 1;
        ctx.beginPath();
        ctx.roundRect(x, y, rackWidth, rackHeight, 3);
        ctx.fill();
        ctx.stroke();

        ctx.shadowBlur = 0;

        // Draw server units inside rack
        const serverCount = 6;
        const serverHeight = (rackHeight - 8) / serverCount;
        for (let s = 0; s < serverCount; s++) {
          const serverY = y + 4 + s * serverHeight;
          ctx.fillStyle = status === 'attacked' ? '#dc2626' : '#0f172a';
          ctx.fillRect(x + 3, serverY, rackWidth - 6, serverHeight - 1);
        }

        // Draw rack label
        ctx.fillStyle = status === 'attacked' ? '#fca5a5' : '#94a3b8';
        ctx.font = '8px sans-serif';
        ctx.fillText(rackId.slice(-4), x + 3, y + rackHeight - 3);
      }
    });

    // Draw CRAC units on sides
    const cracY = padding + zoneHeight * 0.35;
    cracs.forEach((crac, i) => {
      const x = i < 4 ? padding - 40 : width - padding + 10;
      const y = cracY + (i % 4) * 40;
      
      ctx.fillStyle = '#0e7490';
      ctx.strokeStyle = '#06b6d4';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(x, y, 30, 35, 4);
      ctx.fill();
      ctx.stroke();
      
      ctx.fillStyle = '#f8fafc';
      ctx.font = 'bold 8px sans-serif';
      ctx.fillText(crac.name, x + 2, y + 15);
      ctx.font = '6px sans-serif';
      ctx.fillText(crac.capacity, x + 2, y + 28);
    });

    // Draw attack animation
    if (isAttack && targetId) {
      // Find target rack position
      const targetRow = rows.indexOf(targetId.charAt(6));
      const targetCol = parseInt(targetId.charAt(7) + targetId.charAt(8)) - 1;
      const targetX = startX + targetCol * (rackWidth + rackGap) + rackWidth / 2;
      const targetY = startY + targetRow * (rackHeight + rowGap) + rackHeight / 2;

      // Stargate attack ring effect
      const time = Date.now() / 1000;
      const ringCount = 3;
      
      for (let r = 0; r < ringCount; r++) {
        const ringRadius = 30 + r * 25 + Math.sin(time * 2 + r) * 10;
        const alpha = 0.5 - r * 0.15;
        
        ctx.strokeStyle = `rgba(${r === 0 ? '220, 38, 38' : r === 1 ? '245, 158, 11' : '239, 68, 68'}, ${alpha})`;
        ctx.lineWidth = 3 - r;
        ctx.beginPath();
        ctx.arc(targetX, targetY, ringRadius, 0, Math.PI * 2);
        ctx.stroke();
      }

      // Attack beam to affected devices
      if (affectedDevices.length > 0) {
        ctx.setLineDash([5, 5]);
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 2;
        
        affectedDevices.forEach(devId => {
          if (devId !== targetId) {
            const row = rows.indexOf(devId.charAt(6));
            const col = parseInt(devId.charAt(7) + devId.charAt(8)) - 1;
            const dx = startX + col * (rackWidth + rackGap) + rackWidth / 2;
            const dy = startY + row * (rackHeight + rowGap) + rackHeight / 2;
            
            ctx.beginPath();
            ctx.moveTo(targetX, targetY);
            ctx.lineTo(dx, dy);
            ctx.stroke();
          }
        });
        ctx.setLineDash([]);
      }
    }

    // Draw header bar
    ctx.fillStyle = 'rgba(10, 10, 15, 0.9)';
    ctx.fillRect(0, 0, width, 70);

    // Title
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 24px sans-serif';
    ctx.fillText('STARGATE DATA CENTER', 20, 35);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '12px sans-serif';
    ctx.fillText('United States - Arizona Campus', 20, 55);

    // Stats
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 14px sans-serif';
    ctx.fillText(`${allRacks.length} Racks`, width - 200, 30);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px sans-serif';
    ctx.fillText(`${allRacks.length * 48} Servers`, width - 200, 48);

    // Connection status
    ctx.fillStyle = wsConnected ? '#22c55e' : '#ef4444';
    ctx.beginPath();
    ctx.arc(width - 30, 35, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px sans-serif';
    ctx.fillText(wsConnected ? 'LIVE' : 'OFFLINE', width - 55, 38);

    // Attack info overlay
    if (isAttack && simState?.active_threat) {
      const threat = simState.active_threat;
      
      // Threat banner
      ctx.fillStyle = 'rgba(220, 38, 38, 0.9)';
      ctx.fillRect(width / 2 - 300, 10, 600, 50);
      
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 18px sans-serif';
      ctx.fillText(`?? ${threat.threat_name.toUpperCase()} ATTACK`, width / 2 - 200, 38);
      
      ctx.font = '12px sans-serif';
      ctx.fillText(`TARGET: ${threat.target_device_id}`, width / 2 - 200, 52);
    }

    // Phase indicator
    const phaseLabels: Record<string, string> = {
      recon: '?? RECONNAISSANCE',
      exploit: '? EXPLOITATION',
      action: '?? ACTIVE ATTACK',
      impact: '?? IMPACT',
      none: '? ALL SYSTEMS OPERATIONAL',
    };

    ctx.fillStyle = phaseColor;
    ctx.font = 'bold 32px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(phaseLabels[phase] || '? SECURE', width / 2, height / 2 - 80);

    // Confidence meter
    if (isAttack && simState?.active_threat) {
      const confidence = simState.active_threat.confidence;
      
      ctx.fillStyle = '#1e293b';
      ctx.fillRect(width / 2 - 150, height / 2 - 50, 300, 20);
      
      ctx.fillStyle = `rgb(${confidence > 0.7 ? '220, 38, 38' : confidence > 0.4 ? '245, 158, 11' : '34, 197, 94'})`;
      ctx.fillRect(width / 2 - 150, height / 2 - 50, 300 * confidence, 20);
      
      ctx.strokeStyle = '#475569';
      ctx.strokeRect(width / 2 - 150, height / 2 - 50, 300, 20);
      
      ctx.fillStyle = '#f8fafc';
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText(`AI DETECTION CONFIDENCE: ${(confidence * 100).toFixed(0)}%`, width / 2, height / 2 - 55);
    }

    ctx.textAlign = 'left';

    // Indicators panel
    if (indicators.length > 0) {
      ctx.fillStyle = 'rgba(10, 10, 15, 0.85)';
      ctx.fillRect(10, height - 150, 350, 140);
      ctx.strokeStyle = '#334155';
      ctx.strokeRect(10, height - 150, 350, 140);
      
      ctx.fillStyle = '#f8fafc';
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText('THREAT INDICATORS', 20, height - 130);
      
      ctx.font = '10px sans-serif';
      indicators.slice(-6).forEach((ind, i) => {
        ctx.fillStyle = '#f59e0b';
        ctx.fillText('?', 20, height - 110 + i * 18);
        ctx.fillStyle = '#94a3b8';
        ctx.fillText(`${ind.description}`, 35, height - 110 + i * 18);
      });
    }

    // Elapsed time
    if (isAttack && simState) {
      ctx.fillStyle = '#64748b';
      ctx.font = '14px sans-serif';
      ctx.fillText(`Attack Duration: ${simState.elapsed_sec.toFixed(0)}s`, width - 200, height - 20);
    }

  }, [simState, wsConnected]);

  return (
    <div className="w-screen h-screen bg-slate-950 overflow-hidden">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 h-[70px] bg-slate-900/90 backdrop-blur flex items-center justify-between px-8 z-20 border-b border-slate-700">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-600 via-purple-800 to-slate-900 rounded-lg flex items-center justify-center border-2 border-purple-400">
            <span className="text-white font-bold text-lg">SG</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">STARGATE DATA CENTER</h1>
            <p className="text-xs text-slate-400">US Arizona - Primary Campus | 96 Racks | 4,608 Servers</p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="text-right">
            <p className="text-xs text-slate-400">Total Power</p>
            <p className="text-lg font-bold text-cyan-400">4.2 MW</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-400">Cooling</p>
            <p className="text-lg font-bold text-blue-400">3.8 MW</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-400">PUE</p>
            <p className="text-lg font-bold text-green-400">1.42</p>
          </div>
          
          <div className="flex items-center gap-2 ml-6">
            <div className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-xs text-slate-400">{wsConnected ? 'LIVE FEED' : 'DISCONNECTED'}</span>
          </div>
          
          {simState?.running && (
            <div className="bg-red-600/20 border border-red-500 text-red-400 px-4 py-2 rounded-lg font-bold animate-pulse">
              ?? CYBER ATTACK ACTIVE
            </div>
          )}
        </div>
      </div>

      {/* Canvas visualization */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        style={{ paddingTop: '70px' }}
      />

      {/* Instructions overlay */}
      <div className="absolute bottom-4 right-4 bg-slate-900/90 backdrop-blur rounded-lg p-4 border border-slate-700">
        <p className="text-xs text-slate-400 mb-2">DEMO MODE</p>
        <p className="text-sm text-slate-300">
          {simState?.running 
            ? 'Cyber attack in progress - AI detecting...'
            : 'Waiting for attack simulation to start'}
        </p>
        <p className="text-xs text-slate-500 mt-2">
          Control from Dashboard at /dashboard
        </p>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-slate-900/90 backdrop-blur rounded-lg p-4 border border-slate-700">
        <p className="text-xs text-slate-400 mb-2">RACK STATUS</p>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-slate-700 rounded" />
            <span className="text-slate-400">Healthy</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-red-500/50 rounded animate-pulse" />
            <span className="text-red-400">Attacked</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-amber-500/50 rounded" />
            <span className="text-amber-400">Affected</span>
          </div>
        </div>
      </div>
    </div>
  );
}