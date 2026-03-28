import { Badge } from '@/components/ui/Badge';

interface Device {
  id: string;
  name: string;
  type: string;
  status: string;
  current_risk_score: number;
}

interface ThreatMapProps {
  devices: Device[];
  simState?: {
    running: boolean;
    active_threat: {
      threat_type: string;
      target_device_id: string;
      phase: string;
      severity: string;
    } | null;
    affected_devices: string[];
  };
}

export function ThreatMap({ devices, simState }: ThreatMapProps) {
  const threatActive = Boolean(simState?.running && simState.active_threat);

  const getDeviceStatus = (device: Device) => {
    if (!simState?.running) return device.status || 'healthy';
    if (simState.active_threat?.target_device_id === device.id) {
      return 'attacked';
    }
    if (simState.affected_devices?.includes(device.id)) {
      return 'affected';
    }
    return device.status || 'healthy';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'attacked':
        return 'border-cyber-attack bg-cyber-attack/20 pulse-threat neon-edge-critical';
      case 'affected':
        return 'border-cyber-500 bg-cyber-500/15 animate-pulse-fast neon-edge';
      case 'critical':
        return 'border-red-500 bg-red-500/20';
      case 'at_risk':
        return 'border-amber-500 bg-amber-500/10';
      default:
        return 'border-obsidian-600 bg-obsidian-800/60';
    }
  };

  const racks = devices.filter(d => d.type === 'rack');
  const cracs = devices.filter(d => d.type === 'crac');
  const pdus = devices.filter(d => d.type === 'pdu');

  return (
    <div className="relative h-[420px] bg-obsidian-950 rounded-[2px] overflow-hidden border border-obsidian-700 neon-edge">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_18%,rgba(12,165,242,0.18),transparent_42%),radial-gradient(circle_at_84%_80%,rgba(139,92,246,0.16),transparent_45%)] pointer-events-none" />
      <div className="absolute inset-y-0 -left-1/2 w-[60%] bg-gradient-to-r from-transparent via-cyan-300/18 to-transparent pointer-events-none animate-flow-scan" />

      {/* Grid background */}
      <div className="absolute inset-0 opacity-25">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#334155" strokeWidth="0.6" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      {/* Zone labels */}
      <div className="absolute top-2 left-4 text-[11px] text-cyan-300 font-semibold tracking-[0.14em] uppercase">Cold Aisle</div>
      <div className="absolute bottom-2 left-4 text-[11px] text-red-300 font-semibold tracking-[0.14em] uppercase">Hot Aisle</div>

      {/* Racks */}
      <div className="absolute top-12 left-8 flex gap-4 z-10">
        {racks.map((rack, i) => {
          const status = getDeviceStatus(rack);
          return (
            <div
              key={rack.id}
              className={`w-20 h-36 rounded-[2px] border-2 ${getStatusColor(status)} transition-all duration-300`}
              style={{ animationDelay: `${i * 0.1}s` }}
            >
              <div className="p-2 h-full flex flex-col">
                <div className="text-center mb-2">
                  <p className="text-xs font-bold text-white">{rack.name}</p>
                </div>
                {/* Server slots */}
                <div className="flex-1 grid grid-rows-4 gap-1">
                  {[1, 2, 3, 4].map(slot => (
                    <div
                      key={slot}
                      className={`rounded ${
                        status === 'attacked' ? 'bg-cyber-attack/65 animate-pulse-fast' :
                        status === 'affected' ? 'bg-cyber-500/40' :
                        'bg-obsidian-700'
                      }`}
                    />
                  ))}
                </div>
                {/* Status indicator */}
                <div className="mt-auto pt-1 text-center">
                  <Badge 
                    variant={status === 'attacked' ? 'critical' : 
                             status === 'affected' ? 'at_risk' :
                             status === 'critical' ? 'critical' :
                             status === 'at_risk' ? 'at_risk' : 'healthy'}
                  >
                    {status}
                  </Badge>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* CRACs */}
      <div className="absolute right-8 top-12 flex flex-col gap-4 z-10">
        {cracs.map((crac) => {
          const status = getDeviceStatus(crac);
          return (
            <div
              key={crac.id}
              className={`w-16 h-24 rounded-[2px] border-2 ${getStatusColor(status)}`}
            >
              <div className="p-2 h-full flex flex-col items-center justify-center">
                <p className="text-xs font-bold text-white">{crac.name}</p>
                <div className="mt-2 w-8 h-8 bg-cyan-500/30 rounded flex items-center justify-center">
                  <span className="text-cyan-400">❄</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* PDUs */}
      <div className="absolute left-2 top-12 flex flex-col gap-4 z-10">
        {pdus.map((pdu) => {
          const status = getDeviceStatus(pdu);
          return (
            <div
              key={pdu.id}
              className={`w-8 h-32 rounded-[2px] border-2 ${getStatusColor(status)}`}
            >
              <div className="p-1 h-full flex flex-col items-center justify-center">
                <p className="text-[8px] font-bold text-white" style={{ writingMode: 'vertical-rl' }}>
                  {pdu.name}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Attack animation overlay */}
      {threatActive && (
        <div className="absolute inset-0 pointer-events-none">
          <div
            className="absolute w-12 h-12 bg-cyber-attack/30 border border-cyber-attack rounded-full"
            style={{ left: '50%', top: '50%', transform: 'translate(-50%, -50%)' }}
          />
          <div
            className="absolute w-20 h-20 border border-cyber-attack rounded-full animate-ping opacity-35"
            style={{ left: '50%', top: '50%', transform: 'translate(-50%, -50%)', animationDuration: '1.8s' }}
          />
          <div
            className="absolute w-20 h-20 border border-cyber-attack rounded-full animate-ping opacity-30"
            style={{ left: '50%', top: '50%', transform: 'translate(-50%, -50%)', animationDuration: '2.4s', animationDelay: '0.35s' }}
          />
          <div
            className="absolute w-20 h-20 border border-cyber-attack rounded-full animate-ping opacity-20"
            style={{ left: '50%', top: '50%', transform: 'translate(-50%, -50%)', animationDuration: '3.1s', animationDelay: '0.7s' }}
          />
        </div>
      )}
    </div>
  );
}
