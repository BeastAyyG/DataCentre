import '@fontsource/space-grotesk/500.css';
import '@fontsource/space-grotesk/700.css';
import '@fontsource/jetbrains-mono/500.css';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { animate, createTimeline, stagger, utils } from 'animejs';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import * as THREE from 'three';

type TelemetryMetric = {
  label: string;
  value: string;
  unit: string;
  trend: string;
  gauge: number;
};

type ThreatPulse = {
  ts: string;
  rack: string;
  event: string;
};

type StageCard = {
  id: string;
  title: string;
  body: string;
};

type CapabilityCard = {
  id: string;
  title: string;
  body: string;
  kind: 'mission' | 'vision' | 'purpose';
};

const TELEMETRY: TelemetryMetric[] = [
  { label: 'PUE', value: '1.42', unit: '', trend: '-0.03', gauge: 64 },
  { label: 'INLET TEMP', value: '23.8', unit: 'C', trend: '+0.6', gauge: 72 },
  { label: 'COOLING LOAD', value: '18.3', unit: 'kW', trend: '-1.1', gauge: 58 },
  { label: 'ALERT LATENCY', value: '19', unit: 'min', trend: '-4.2', gauge: 44 },
];

const STAGE_CARDS: StageCard[] = [
  {
    id: '01',
    title: 'Detection',
    body: 'IsolationForest and LSTM detect non-normal thermal behavior on RACK-A1 before threshold breach.',
  },
  {
    id: '02',
    title: 'Decision',
    body: 'XGBoost + CatBoost confidence crosses the critical band and generates mitigation guidance.',
  },
  {
    id: '03',
    title: 'Execution',
    body: 'Operator accepts recommendation, work order is created, checklist completed, and audit trail is locked.',
  },
];

const THREAT_FEED: ThreatPulse[] = [
  { ts: '14:02:11', rack: 'R-B3', event: 'Cooling drift detected' },
  { ts: '14:02:20', rack: 'R-B2', event: 'Temp delta rising (+1.4C)' },
  { ts: '14:02:33', rack: 'R-C3', event: 'Risk score crossed 66' },
  { ts: '14:02:44', rack: 'R-B3', event: 'Work order prepared' },
  { ts: '14:03:02', rack: 'R-B3', event: 'Fan setpoint +12%' },
  { ts: '14:03:15', rack: 'R-B3', event: 'Risk score dropped to 43' },
];

const RACK_GRID = [
  ['R-A1', 'R-A2', 'R-A3', 'R-A4', 'R-A5', 'R-A6'],
  ['R-B1', 'R-B2', 'R-B3', 'R-B4', 'R-B5', 'R-B6'],
  ['R-C1', 'R-C2', 'R-C3', 'R-C4', 'R-C5', 'R-C6'],
  ['R-D1', 'R-D2', 'R-D3', 'R-D4', 'R-D5', 'R-D6'],
];

const HOST_SIDE_CAPABILITIES: CapabilityCard[] = [
  {
    id: '01',
    title: 'Real-time Simulator (SensorSimulator)',
    body: 'Continuously simulates rack, CRAC, and PDU physics (temperature, power, airflow) and streams telemetry over WebSockets.',
    kind: 'mission',
  },
  {
    id: '02',
    title: '5-Model ML Ensemble',
    body: 'Isolation Forest, LSTM Autoencoder, XGBoost, CatBoost, and Prophet score risk in parallel to predict thermal anomalies early.',
    kind: 'vision',
  },
  {
    id: '03',
    title: 'Cyber Threat Engine (CyberSimulator)',
    body: 'Simulates intrusions, DDoS, and ransomware scenarios while calculating blast radius and confidence in real time.',
    kind: 'purpose',
  },
  {
    id: '04',
    title: 'Multi-Datacenter Hub',
    body: 'Aggregates facilities into one PostgreSQL-backed control plane so operators can pivot from dc-primary to fleet-wide view.',
    kind: 'mission',
  },
];

const DASHBOARD_SIDE_FEATURES = [
  {
    id: '01',
    title: 'Pane-of-Glass SOC Interface',
    body: 'React connects to the host side over REST APIs and WebSockets so operational context updates instantly.',
  },
  {
    id: '02',
    title: 'Threat Map AttackPulse',
    body: 'When attacks launch, affected devices pulse from scale(1) to scale(1.05) with neon red borders and glow.',
  },
  {
    id: '03',
    title: 'Attack Waves',
    body: 'Radar-style wavefronts radiate across Cold and Hot aisle zones to visualize blast propagation.',
  },
  {
    id: '04',
    title: 'Live KPI Tickers & Gauges',
    body: 'Metric cards and risk gauges animate as payloads stream roughly every 2 seconds, no refresh required.',
  },
  {
    id: '05',
    title: 'Neon Operational Aesthetic',
    body: 'Deep slate #020617 surfaces with Cyber Purple #8b5cf6, Cyan #0ca5f2, and Emerald #22c55e accents.',
  },
];

gsap.registerPlugin(ScrollTrigger);

function DesignationIcon({ kind }: { kind: 'mission' | 'vision' | 'purpose' }) {
  if (kind === 'mission') {
    return (
      <svg viewBox="0 0 64 64" className="w-12 h-12" fill="none" stroke="currentColor" strokeWidth="1.2">
        <rect x="10" y="10" width="44" height="44" rx="2" />
        <path d="M16 32H48" />
        <path d="M32 16V48" />
        <path d="M22 22L42 42" />
      </svg>
    );
  }

  if (kind === 'vision') {
    return (
      <svg viewBox="0 0 64 64" className="w-12 h-12" fill="none" stroke="currentColor" strokeWidth="1.2">
        <circle cx="32" cy="32" r="22" />
        <circle cx="32" cy="32" r="8" />
        <path d="M32 4V18" />
        <path d="M32 46V60" />
        <path d="M4 32H18" />
        <path d="M46 32H60" />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 64 64" className="w-12 h-12" fill="none" stroke="currentColor" strokeWidth="1.2">
      <path d="M14 14H50V50H14z" />
      <path d="M20 43L28 35L34 39L45 24" />
      <path d="M45 24H39" />
      <path d="M45 24V30" />
    </svg>
  );
}

function useThreeBackground(canvasRef: { current: HTMLCanvasElement | null }) {
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const renderer = new THREE.WebGLRenderer({
      canvas,
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance',
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(48, 1, 0.1, 1000);
    camera.position.set(0, 0, 10.8);

    const group = new THREE.Group();
    scene.add(group);

    const pointsGeometry = new THREE.BufferGeometry();
    const pointsCount = 680;
    const positions = new Float32Array(pointsCount * 3);

    for (let i = 0; i < pointsCount; i++) {
      const i3 = i * 3;
      positions[i3] = (Math.random() - 0.5) * 30;
      positions[i3 + 1] = (Math.random() - 0.5) * 16;
      positions[i3 + 2] = (Math.random() - 0.5) * 21;
    }

    pointsGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const pointsMaterial = new THREE.PointsMaterial({
      color: '#f5f5f5',
      size: 0.03,
      transparent: true,
      opacity: 0.35,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });

    const particles = new THREE.Points(pointsGeometry, pointsMaterial);
    group.add(particles);

    const coreGeometry = new THREE.IcosahedronGeometry(3.3, 1);
    const coreMaterial = new THREE.MeshBasicMaterial({
      color: '#d4d4d8',
      wireframe: true,
      transparent: true,
      opacity: 0.28,
    });
    const core = new THREE.Mesh(coreGeometry, coreMaterial);
    group.add(core);

    const rings: THREE.Mesh[] = [];
    for (let i = 0; i < 4; i++) {
      const ringGeo = new THREE.TorusGeometry(2.1 + i * 0.55, 0.028, 24, 120);
      const ringMat = new THREE.MeshBasicMaterial({
        color: i % 2 === 0 ? '#e5e7eb' : '#9ca3af',
        transparent: true,
        opacity: 0.15 - i * 0.02,
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = Math.PI / 2 + i * 0.22;
      ring.rotation.y = i * 0.15;
      rings.push(ring);
      group.add(ring);
    }

    const orbitLines: THREE.Line[] = [];
    for (let i = 0; i < 3; i++) {
      const curve = new THREE.EllipseCurve(0, 0, 1.8 + i * 0.9, 1.2 + i * 0.6);
      const points = curve.getPoints(140).map((p) => new THREE.Vector3(p.x, p.y, 0));
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      const material = new THREE.LineBasicMaterial({
        color: '#f5f5f5',
        transparent: true,
        opacity: 0.1,
      });
      const line = new THREE.LineLoop(geometry, material);
      line.rotation.x = i * 0.48;
      line.rotation.y = i * 0.34;
      orbitLines.push(line);
      group.add(line);
    }

    let raf = 0;
    const clock = new THREE.Clock();

    const resize = () => {
      const parent = canvas.parentElement;
      const width = parent ? parent.clientWidth : window.innerWidth;
      const height = parent ? parent.clientHeight : window.innerHeight;
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };

    resize();
    window.addEventListener('resize', resize);

    const mouse = { x: 0, y: 0 };
    const onMouseMove = (event: MouseEvent) => {
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    };
    window.addEventListener('mousemove', onMouseMove);

    const render = () => {
      const elapsed = clock.getElapsedTime();

      group.rotation.y = elapsed * 0.1 + mouse.x * 0.14;
      group.rotation.x = Math.sin(elapsed * 0.14) * 0.08 + mouse.y * 0.08;

      particles.rotation.y = -elapsed * 0.05;
      particles.rotation.z = elapsed * 0.025;

      core.rotation.x = elapsed * 0.17;
      core.rotation.y = -elapsed * 0.11;

      rings.forEach((ring, idx) => {
        ring.rotation.z += 0.0015 + idx * 0.0004;
      });

      orbitLines.forEach((line, idx) => {
        line.rotation.z = elapsed * (0.08 + idx * 0.03);
      });

      renderer.render(scene, camera);
      raf = window.requestAnimationFrame(render);
    };

    render();

    return () => {
      window.cancelAnimationFrame(raf);
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', onMouseMove);
      pointsGeometry.dispose();
      pointsMaterial.dispose();
      coreGeometry.dispose();
      coreMaterial.dispose();
      rings.forEach((ring) => {
        ring.geometry.dispose();
        (ring.material as THREE.Material).dispose();
      });
      orbitLines.forEach((line) => {
        line.geometry.dispose();
        (line.material as THREE.Material).dispose();
      });
      renderer.dispose();
    };
  }, [canvasRef]);
}

export function LandingPage() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rootRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const [menuOpen, setMenuOpen] = useState(false);
  const [clock, setClock] = useState('');
  const [feedIndex, setFeedIndex] = useState(0);
  const [activeRack, setActiveRack] = useState(THREAT_FEED[0].rack);
  const [phaseIndex, setPhaseIndex] = useState(0);
  const [logoMissing, setLogoMissing] = useState(false);

  const feedKey = useMemo(
    () => `${THREAT_FEED[feedIndex].ts}-${THREAT_FEED[feedIndex].rack}-${feedIndex}`,
    [feedIndex]
  );

  useThreeBackground(canvasRef);

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      const timestamp = now.toLocaleTimeString('en-GB', { hour12: false });
      setClock(`${timestamp} UTC`);
    };

    tick();
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const feedTimer = setInterval(() => {
      setFeedIndex((prev) => {
        const next = (prev + 1) % THREAT_FEED.length;
        setActiveRack(THREAT_FEED[next].rack);
        return next;
      });
    }, 1400);

    const phaseTimer = setInterval(() => {
      setPhaseIndex((prev) => (prev + 1) % STAGE_CARDS.length);
    }, 2100);

    return () => {
      clearInterval(feedTimer);
      clearInterval(phaseTimer);
    };
  }, []);

  useEffect(() => {
    const intro = createTimeline({
      defaults: { ease: 'outExpo' },
    });

    intro
      .add('.js-reveal-nav', {
        opacity: [0, 1],
        y: [-20, 0],
        duration: 700,
      })
      .add(
        '.js-clip-line',
        {
          opacity: [0.2, 1],
          y: [16, 0],
          duration: 760,
          delay: stagger(110),
        },
        '<<+=80'
      )
      .add(
        '.js-reveal-hero',
        {
          opacity: [0, 1],
          y: [34, 0],
          duration: 940,
          delay: stagger(100),
        },
        '<<+=80'
      )
      .add(
        '.js-reveal-side',
        {
          opacity: [0, 1],
          x: [20, 0],
          duration: 740,
          delay: stagger(70),
        },
        '<<+=160'
      )
      .add(
        '.js-reveal-grid > *',
        {
          opacity: [0, 1],
          y: [20, 0],
          duration: 640,
          delay: stagger(65),
        },
        '<<+=120'
      );

    animate('.js-subtle-float', {
      y: [0, -10],
      rotateZ: [0, 0.2],
      duration: 2300,
      ease: 'inOutSine',
      loop: true,
      alternate: true,
      delay: stagger(220, { from: 'center' }),
    });

    animate('.js-signal-dot', {
      scale: [1, 1.5],
      opacity: [0.3, 1],
      duration: 650,
      ease: 'inOutSine',
      loop: true,
      alternate: true,
      delay: stagger(90),
    });

    animate('.js-grid-flicker', {
      opacity: [0.42, 1],
      duration: 950,
      ease: 'inOutSine',
      loop: true,
      alternate: true,
      delay: stagger(55, { grid: [6, 4], from: 'center' }),
    });

    animate('.js-hud-spin', {
      rotate: 360,
      duration: 15000,
      ease: 'linear',
      loop: true,
    });

    const glitchTimer = window.setInterval(() => {
      animate('.js-distort', {
        x: [0, -0.8, 0.8, 0],
        skewX: [0, 2, -1.6, 0],
        opacity: [1, 0.94, 1],
        duration: 180,
        ease: 'inOutSine',
      });
    }, 4200);

    return () => {
      intro.cancel();
      clearInterval(glitchTimer);
      utils.remove('.js-subtle-float');
      utils.remove('.js-signal-dot');
      utils.remove('.js-grid-flicker');
      utils.remove('.js-hud-spin');
      utils.remove('.js-distort');
    };
  }, []);

  useEffect(() => {
    if (!rootRef.current) return;

    const ctx = gsap.context(() => {
      const pinTl = gsap.timeline({
        scrollTrigger: {
          trigger: '.js-pin-stage',
          start: 'top top',
          end: '+=260%',
          scrub: 1.1,
          pin: true,
          anticipatePin: 1,
        },
      });

      pinTl
        .to('.js-stage-intro', { opacity: 0, y: -40, duration: 1 }, 0.32)
        .fromTo('.js-stage-detect', { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 1 }, 0.24)
        .to('.js-stage-detect', { opacity: 0, y: -38, duration: 0.9 }, 0.56)
        .fromTo('.js-stage-action', { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.9 }, 0.62)
        .to('.js-progress-bar', { scaleX: 1, duration: 0.6, transformOrigin: 'left center' }, 0.7)
        .to('.js-background-zoom', { scale: 1.08, duration: 1 }, 0)
        .to('.js-noise-layer', { opacity: 0.28, duration: 1 }, 0.2)
        .to('.js-canvas-layer', { opacity: 0.82, duration: 1 }, 0.1)
        .to('.js-pin-vignette', { opacity: 0.95, duration: 1 }, 0.34);

      gsap.utils.toArray<HTMLElement>('.js-scroll-section').forEach((section) => {
        gsap.fromTo(
          section,
          { opacity: 0.28, y: 56 },
          {
            opacity: 1,
            y: 0,
            duration: 1.2,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: section,
              start: 'top 82%',
              end: 'top 40%',
              scrub: 1,
            },
          }
        );
      });

      gsap.utils.toArray<HTMLElement>('.js-scroll-card').forEach((card, index) => {
        gsap.fromTo(
          card,
          { y: 36, opacity: 0.16 },
          {
            y: 0,
            opacity: 1,
            duration: 0.9,
            ease: 'power2.out',
            delay: index * 0.03,
            scrollTrigger: {
              trigger: card,
              start: 'top 86%',
            },
          }
        );
      });

      gsap.utils.toArray<HTMLElement>('.js-parallax-item').forEach((item, idx) => {
        gsap.fromTo(
          item,
          { y: 0 },
          {
            y: (idx + 1) * -46,
            ease: 'none',
            scrollTrigger: {
              trigger: item,
              start: 'top bottom',
              end: 'bottom top',
              scrub: 1,
            },
          }
        );
      });

      gsap.utils.toArray<HTMLElement>('.js-mask-reveal').forEach((mask) => {
        gsap.fromTo(
          mask,
          { clipPath: 'inset(0 100% 0 0)' },
          {
            clipPath: 'inset(0 0% 0 0)',
            duration: 1.1,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: mask,
              start: 'top 84%',
            },
          }
        );
      });

      gsap.utils.toArray<HTMLElement>('.js-meter-fill').forEach((bar) => {
        gsap.fromTo(
          bar,
          { scaleX: 0, transformOrigin: 'left center' },
          {
            scaleX: 1,
            duration: 1.05,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: bar,
              start: 'top 92%',
            },
          }
        );
      });
    }, rootRef);

    return () => ctx.revert();
  }, []);

  useEffect(() => {
    const hoverTargets = gsap.utils.toArray<HTMLElement>('.js-hover-bulge');
    const disposers: Array<() => void> = [];

    hoverTargets.forEach((target) => {
      gsap.set(target, { transformPerspective: 800, transformOrigin: '50% 60%' });

      const xTo = gsap.quickTo(target, 'x', { duration: 0.22, ease: 'power3.out' });
      const yTo = gsap.quickTo(target, 'y', { duration: 0.22, ease: 'power3.out' });
      const scaleTo = gsap.quickTo(target, 'scale', { duration: 0.3, ease: 'power3.out' });
      const rotateXTo = gsap.quickTo(target, 'rotateX', { duration: 0.3, ease: 'power3.out' });
      const rotateYTo = gsap.quickTo(target, 'rotateY', { duration: 0.3, ease: 'power3.out' });

      const onEnter = () => {
        scaleTo(1.04);
        gsap.to(target, {
          textShadow: '0 0 22px rgba(255,255,255,0.28), 0 4px 14px rgba(0,0,0,0.72)',
          duration: 0.3,
          ease: 'power2.out',
        });
      };

      const onMove = (event: MouseEvent) => {
        const rect = target.getBoundingClientRect();
        const relX = (event.clientX - rect.left) / rect.width - 0.5;
        const relY = (event.clientY - rect.top) / rect.height - 0.5;

        xTo(relX * 8);
        yTo(relY * -7);
        rotateXTo(relY * -5);
        rotateYTo(relX * 6);
      };

      const onLeave = () => {
        xTo(0);
        yTo(0);
        rotateXTo(0);
        rotateYTo(0);
        scaleTo(1);
        gsap.to(target, {
          textShadow: '0 1px 4px rgba(0,0,0,0.92)',
          duration: 0.3,
          ease: 'power2.out',
        });
      };

      target.addEventListener('mouseenter', onEnter);
      target.addEventListener('mousemove', onMove);
      target.addEventListener('mouseleave', onLeave);

      disposers.push(() => {
        target.removeEventListener('mouseenter', onEnter);
        target.removeEventListener('mousemove', onMove);
        target.removeEventListener('mouseleave', onLeave);
      });
    });

    return () => {
      disposers.forEach((dispose) => dispose());
    };
  }, []);

  const scrollToSection = (id: string) => {
    setMenuOpen(false);
    const section = document.getElementById(id);
    if (!section) return;
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div
      ref={rootRef}
      className="relative min-h-screen overflow-x-hidden"
      style={{
        background: '#050606',
        color: '#e8e8e8',
        fontFamily: 'Space Grotesk, sans-serif',
      }}
    >
      <div className="fixed inset-0 pointer-events-none origin-center js-background-zoom">
        <video
          ref={videoRef}
          autoPlay
          loop
          muted
          playsInline
          controls={false}
          disablePictureInPicture
          controlsList="nodownload noplaybackrate noremoteplayback nofullscreen"
          className="absolute inset-0 w-full h-full object-cover opacity-42"
          style={{
            filter: 'blur(1.7px) brightness(0.28) saturate(0.45) contrast(1.1)',
            transform: 'scale(1.045)',
          }}
        >
          <source src="/landing-video.mp4" type="video/mp4" />
        </video>
      </div>

      <canvas
        ref={canvasRef}
        className="fixed inset-0 w-full h-full pointer-events-none opacity-56 js-canvas-layer"
        aria-hidden="true"
      />

      <div className="fixed inset-0 pointer-events-none js-noise-layer">
        <div className="absolute inset-0 bg-gradient-to-b from-black/84 via-black/80 to-black/94" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_78%_15%,rgba(255,255,255,0.12),transparent_30%),radial-gradient(circle_at_8%_85%,rgba(255,255,255,0.08),transparent_42%)]" />
        <div
          className="absolute inset-0 opacity-[0.04] animate-noise"
          style={{
            backgroundImage:
              'repeating-radial-gradient(circle at 0 0, rgba(255,255,255,0.16) 0 1px, transparent 1px 3px), repeating-radial-gradient(circle at 100% 100%, rgba(255,255,255,0.1) 0 1px, transparent 1px 4px)',
            backgroundSize: '180px 180px, 240px 240px',
          }}
        />
      </div>

      <div className="fixed inset-x-0 top-0 h-36 bg-gradient-to-b from-black to-transparent pointer-events-none z-20" />

      <div className="hidden xl:block fixed left-6 top-1/2 -translate-y-1/2 z-40 pointer-events-none js-reveal-nav">
        <div
          className="flex items-center gap-3 text-[11px] uppercase tracking-[0.24em] text-white/58 [writing-mode:vertical-rl] rotate-180"
          style={{ fontFamily: 'JetBrains Mono, monospace' }}
        >
          scroll
          <span className="inline-block w-px h-16 bg-white/24" />
          zone-04
          <span className="inline-flex items-center gap-1 mt-2">
            <i className="w-1.5 h-1.5 rounded-full bg-white/70 js-signal-dot" />
            <i className="w-1.5 h-1.5 rounded-full bg-white/70 js-signal-dot" />
            <i className="w-1.5 h-1.5 rounded-full bg-white/70 js-signal-dot" />
          </span>
        </div>
      </div>

      <header className="fixed top-0 inset-x-0 z-50 border-b border-white/16 backdrop-blur-[2px] js-reveal-nav">
        <nav className="mx-auto max-w-7xl px-6 lg:px-8 py-5 flex items-center justify-between">
          <div className="flex flex-col items-start gap-2">
            <div className="w-12 h-12 border border-white/42 rounded-sm bg-black/45 flex items-center justify-center overflow-hidden js-subtle-float">
              {logoMissing ? (
                <span
                  className="text-[12px] font-semibold tracking-[0.2em] text-white/92"
                  style={{ fontFamily: 'JetBrains Mono, monospace' }}
                >
                  AK
                </span>
              ) : (
                <img
                  src="/image.png"
                  alt="AKAGAMI logo"
                  className="w-full h-full object-contain p-1"
                  onError={() => setLogoMissing(true)}
                />
              )}
            </div>
            <div>
              <p className="text-sm font-semibold tracking-tight text-white">AKAGAMI</p>
              <p className="text-[10px] uppercase tracking-[0.24em] text-white/55" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                Reliability Command
              </p>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-6 text-[12px] uppercase tracking-[0.16em] text-white/74" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            <button onClick={() => scrollToSection('about')} className="hover:text-white transition-colors">About</button>
            <button onClick={() => scrollToSection('host-side')} className="hover:text-white transition-colors">Host Side</button>
            <button onClick={() => scrollToSection('dashboard-side')} className="hover:text-white transition-colors">Dashboard Side</button>
            <button onClick={() => scrollToSection('story')} className="hover:text-white transition-colors">Story</button>
          </div>

          <div className="flex items-center gap-3">
            <span className="hidden sm:inline text-[11px] uppercase tracking-[0.14em] text-white/55" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
              {clock}
            </span>
            <button
              onClick={() => navigate('/overview')}
              className="hidden md:inline px-4 py-2 border border-white/45 rounded-sm text-xs uppercase tracking-[0.14em] text-white hover:bg-white hover:text-black transition-colors"
              style={{ fontFamily: 'JetBrains Mono, monospace' }}
            >
              Launch App
            </button>
            <button
              className="md:hidden px-3 py-2 border border-white/45 text-[11px] uppercase tracking-[0.14em] text-white"
              onClick={() => setMenuOpen((value) => !value)}
              aria-label="Toggle navigation menu"
              style={{ fontFamily: 'JetBrains Mono, monospace' }}
            >
              Menu
            </button>
          </div>
        </nav>
      </header>

      {menuOpen && (
        <div className="md:hidden fixed inset-0 z-[70] bg-black/96 backdrop-blur-sm">
          <div className="h-full px-6 py-8 flex flex-col">
            <div className="flex items-center justify-between pb-6 border-b border-white/15">
              <p className="text-[11px] uppercase tracking-[0.22em] text-white/70" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                Navigation
              </p>
              <button
                onClick={() => setMenuOpen(false)}
                className="text-[11px] uppercase tracking-[0.18em] text-white"
                style={{ fontFamily: 'JetBrains Mono, monospace' }}
              >
                Close
              </button>
            </div>
            <div className="mt-8 flex flex-col gap-5 text-2xl uppercase tracking-tight text-white">
              <button onClick={() => scrollToSection('about')} className="text-left">About</button>
              <button onClick={() => scrollToSection('host-side')} className="text-left">Host Side</button>
              <button onClick={() => scrollToSection('dashboard-side')} className="text-left">Dashboard Side</button>
              <button onClick={() => scrollToSection('story')} className="text-left">Operational Story</button>
              <button onClick={() => navigate('/overview')} className="mt-3 text-left text-white/70">Launch Platform</button>
            </div>
          </div>
        </div>
      )}

      <main className="relative z-10 pt-[84px]">
        <section className="js-pin-stage relative h-[100vh]">
          <div className="absolute inset-0 js-pin-vignette opacity-70 bg-gradient-to-b from-transparent via-black/15 to-black/45 pointer-events-none" />

          <div className="mx-auto max-w-7xl h-full px-6 lg:px-8 pb-12 grid lg:grid-cols-[1.2fr_0.8fr] gap-10 items-center">
            <div className="relative h-[420px] lg:h-[500px]">
              <div className="absolute inset-0 border border-white/16 bg-black/72 backdrop-blur-[2px] js-stage-intro">
                <div className="relative h-full p-8 sm:p-10 lg:p-12 flex flex-col justify-center">
                  <div className="absolute inset-y-6 left-5 right-8 bg-gradient-to-r from-black/70 via-black/36 to-transparent pointer-events-none" />

                  <p className="relative z-10 text-[11px] uppercase tracking-[0.22em] text-white/82 js-reveal-hero js-distort" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                    [ Operational Intelligence for Critical Infrastructure ]
                  </p>

                  <h1 className="relative z-10 mt-8 text-[42px] sm:text-[58px] lg:text-[76px] font-bold uppercase leading-[0.96] tracking-[-0.02em] text-white drop-shadow-[0_1px_4px_rgba(0,0,0,0.92)] js-reveal-hero js-hover-bulge">
                    <span className="block js-clip-line">
                      Keep data centers online.
                    </span>
                    <span className="block text-white/78 js-clip-line">
                      Predict thermal and power risk
                    </span>
                    <span className="block text-white/78 js-clip-line">
                      before outage.
                    </span>
                  </h1>

                  <p className="relative z-10 mt-8 text-lg text-white/90 max-w-3xl leading-relaxed js-reveal-hero">
                    AKAGAMI streams rack telemetry, runs a five-model ensemble, and routes
                    recommendations into operator-approved actions with full audit traceability.
                  </p>

                  <div className="mt-10 flex flex-col sm:flex-row gap-4 js-reveal-hero">
                    <button
                      onClick={() => navigate('/overview')}
                      className="px-7 py-3 border border-white bg-white text-black text-sm uppercase tracking-[0.14em] font-semibold hover:bg-transparent hover:text-white transition-colors"
                      style={{ fontFamily: 'JetBrains Mono, monospace' }}
                    >
                      Enter Control Room
                    </button>
                    <button
                      onClick={() => navigate('/simulation')}
                      className="px-7 py-3 border border-white/45 text-sm uppercase tracking-[0.14em] text-white hover:border-white hover:bg-white/8 transition-colors"
                      style={{ fontFamily: 'JetBrains Mono, monospace' }}
                    >
                      Open Simulation
                    </button>
                  </div>
                </div>
              </div>

              <div className="absolute inset-0 border border-white/20 bg-black/60 backdrop-blur-sm opacity-0 js-stage-detect">
                <div className="h-full p-8 sm:p-10 lg:p-12 flex flex-col justify-center">
                  <p className="text-[11px] uppercase tracking-[0.2em] text-white/62" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                    [ Stage 01 · Detection ]
                  </p>
                  <h2 className="mt-6 text-[34px] sm:text-[44px] lg:text-[56px] uppercase leading-[0.95] tracking-tight text-white js-mask-reveal overflow-hidden">
                    Thermal acceleration detected on
                    <span className="block text-white/62">RACK-B3 18 minutes early.</span>
                  </h2>
                  <p className="mt-6 text-white/74 leading-relaxed max-w-2xl">
                    IsolationForest and LSTM both exceed anomaly thresholds. Forecast residual rises beyond acceptable margin.
                  </p>
                  <div className="mt-8 grid grid-cols-3 gap-3 max-w-xl">
                    {['IF:0.82', 'LSTM:0.76', 'Forecast:+2.8C'].map((token) => (
                      <div
                        key={token}
                        className="border border-white/18 bg-white/8 px-3 py-2 text-[11px] uppercase tracking-[0.14em] text-white/84"
                        style={{ fontFamily: 'JetBrains Mono, monospace' }}
                      >
                        {token}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="absolute inset-0 border border-white/20 bg-black/60 backdrop-blur-sm opacity-0 js-stage-action">
                <div className="h-full p-8 sm:p-10 lg:p-12 flex flex-col justify-center">
                  <p className="text-[11px] uppercase tracking-[0.2em] text-white/62" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                    [ Stage 02 · Decision / Stage 03 · Execution ]
                  </p>
                  <h2 className="mt-6 text-[34px] sm:text-[44px] lg:text-[56px] uppercase leading-[0.95] tracking-tight text-white js-mask-reveal overflow-hidden">
                    Recommendation approved.
                    <span className="block text-white/62">Work order auto-generated in one click.</span>
                  </h2>
                  <p className="mt-6 text-white/74 leading-relaxed max-w-2xl">
                    Suggested adjustment applied to cooling setpoint and fan speed profile. Incident risk score drops from 66 to 43.
                  </p>
                  <div className="mt-8 border border-white/20 bg-white/7 p-3 max-w-xl">
                    <p className="text-[10px] uppercase tracking-[0.16em] text-white/62" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                      mitigation progress
                    </p>
                    <div className="mt-2 h-1.5 bg-white/14 overflow-hidden">
                      <div className="h-full w-full bg-white scale-x-0 js-progress-bar" />
                    </div>
                  </div>
                </div>
              </div>

            </div>

            <aside className="border border-white/18 bg-black/52 backdrop-blur-sm p-5 sm:p-6 js-reveal-side js-parallax-item relative">
              <div className="absolute top-4 right-4 w-14 h-14 text-white/45 js-hud-spin">
                <svg viewBox="0 0 80 80" fill="none" stroke="currentColor" strokeWidth="1.1">
                  <circle cx="40" cy="40" r="32" />
                  <circle cx="40" cy="40" r="18" />
                  <path d="M40 8V20" />
                  <path d="M40 60V72" />
                  <path d="M8 40H20" />
                  <path d="M60 40H72" />
                </svg>
              </div>

              <div className="flex items-center justify-between">
                <p className="text-[11px] uppercase tracking-[0.2em] text-white/66" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                  Live Telemetry
                </p>
                <span className="text-[10px] uppercase tracking-[0.16em] text-white/88 animate-pulse" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                  Stream Active
                </span>
              </div>

              <div className="mt-5 grid grid-cols-2 gap-3">
                {TELEMETRY.map((item) => (
                  <div key={item.label} className="border border-white/15 bg-black/45 p-3 js-reveal-side js-subtle-float">
                    <p className="text-[10px] uppercase tracking-[0.18em] text-white/52" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                      {item.label}
                    </p>
                    <p className="mt-2 text-2xl font-semibold tracking-tight text-white">
                      {item.value}
                      <span className="text-sm text-white/58 ml-1">{item.unit}</span>
                    </p>
                    <div className="mt-2 h-1 bg-white/10 overflow-hidden">
                      <div className="h-full bg-white js-meter-fill" style={{ width: `${item.gauge}%` }} />
                    </div>
                    <p className="mt-1 text-[10px] uppercase tracking-[0.16em] text-white/56" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                      Trend {item.trend}
                    </p>
                  </div>
                ))}
              </div>

              <div className="mt-5 border border-white/15 bg-black/45 p-3 js-reveal-side">
                <div className="flex items-center justify-between">
                  <p className="text-[10px] uppercase tracking-[0.18em] text-white/52" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                    Zone Map Snapshot
                  </p>
                  <span className="text-[10px] uppercase tracking-[0.16em] text-white/82" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                    Rack {activeRack}
                  </span>
                </div>

                <div className="mt-3 grid grid-cols-6 gap-1">
                  {RACK_GRID.flatMap((row, r) =>
                    row.map((rack, c) => {
                      const critical = rack === activeRack;
                      const atRisk = rack === 'R-B2' || rack === 'R-C3';
                      return (
                        <div
                          key={`${r}-${c}`}
                          className={`h-8 border text-[9px] tracking-wide flex items-center justify-center transition-all duration-500 js-grid-flicker ${
                            critical
                              ? 'bg-white/30 border-white text-white shadow-[0_0_18px_rgba(255,255,255,0.24)]'
                              : atRisk
                              ? 'bg-white/14 border-white/55 text-white/88'
                              : 'bg-white/8 border-white/35 text-white/72'
                          }`}
                          style={{ fontFamily: 'JetBrains Mono, monospace' }}
                        >
                          {rack}
                        </div>
                      );
                    })
                  )}
                </div>

                <svg viewBox="0 0 240 70" className="w-full mt-3 h-[54px] border border-white/14 bg-black/48">
                  <path
                    d="M4 50 C 40 42, 68 30, 108 34 C 142 38, 184 22, 236 24"
                    fill="none"
                    stroke="rgba(255,255,255,0.55)"
                    strokeWidth="1.4"
                    strokeDasharray="5 6"
                    className="js-line-pulse"
                  />
                  <path
                    d="M4 58 C 34 54, 62 44, 98 48 C 144 52, 196 35, 236 38"
                    fill="none"
                    stroke="rgba(255,255,255,0.28)"
                    strokeWidth="1.2"
                    strokeDasharray="3 8"
                    className="js-line-pulse"
                  />
                </svg>

                <div className="mt-3 h-[56px] overflow-hidden border border-white/15 bg-black/45 p-2 relative">
                  <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/14 to-transparent animate-scanline pointer-events-none" />
                  <div
                    className="text-[10px] uppercase tracking-[0.14em] text-white/82 animate-feed-slide"
                    key={feedKey}
                    style={{ fontFamily: 'JetBrains Mono, monospace' }}
                  >
                    {THREAT_FEED[feedIndex].ts}  {THREAT_FEED[feedIndex].rack}  {THREAT_FEED[feedIndex].event}
                    <span className="ml-1 inline-block w-1.5 h-3 bg-white/85 align-middle animate-cursor" />
                  </div>
                </div>
              </div>
            </aside>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-6 lg:px-8 pb-20 js-reveal-grid">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-px border border-white/20 bg-white/12">
            {[
              { value: '5', label: 'Models in Ensemble', desc: 'LSTM · XGB · IF · CatBoost · Prophet' },
              { value: '<20m', label: 'Detection Lead Time', desc: 'before threshold alert' },
              { value: '12-18%', label: 'Cooling Savings', desc: 'forecasted annual range' },
              { value: '0-100', label: 'Risk Scoring', desc: 'continuous per-device index' },
            ].map((stat) => (
              <div key={stat.label} className="bg-black/62 p-5 sm:p-6">
                <p className="text-3xl sm:text-4xl font-semibold tracking-tight text-white">{stat.value}</p>
                <p className="mt-2 text-[11px] uppercase tracking-[0.18em] text-white/72" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                  {stat.label}
                </p>
                <p className="mt-2 text-xs text-white/55 leading-relaxed">{stat.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="about" className="mx-auto max-w-7xl px-6 lg:px-8 py-24 border-t border-white/18 js-scroll-section">
          <p className="text-[11px] uppercase tracking-[0.22em] text-white/60 mb-8" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            [ About ]
          </p>
          <div className="grid lg:grid-cols-[1.1fr_1fr] gap-12 items-start">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl uppercase leading-[0.95] tracking-[-0.02em] text-white js-scroll-card js-mask-reveal overflow-hidden">
              We turn data center telemetry into operator decisions.
            </h2>
            <div className="space-y-5 text-white/76 leading-relaxed js-scroll-card">
              <p>
                Most facilities can monitor. Few can act with confidence. We built an operational layer that
                detects drift, quantifies risk, recommends action, and tracks execution.
              </p>
              <p>
                This is not a static dashboard. It is a reliability workflow that keeps teams aligned during
                high-pressure, high-cost events.
              </p>
            </div>
          </div>
        </section>

        <section id="host-side" className="mx-auto max-w-7xl px-6 lg:px-8 py-24 border-t border-white/18 js-scroll-section">
          <p className="text-[11px] uppercase tracking-[0.22em] text-white/60 mb-8" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            [ Host Side ]
          </p>
          <div className="grid lg:grid-cols-[1.05fr_0.95fr] gap-10 items-start">
            <div className="border border-white/20 bg-black/56 p-7 sm:p-9 js-scroll-card">
              <p className="text-xs uppercase tracking-[0.2em] text-white/52" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                The AI Brain & Orchestrator
              </p>
              <h3 className="mt-4 text-4xl sm:text-5xl uppercase tracking-tight leading-[0.95] text-white">
                Central host, continuous simulation, predictive control.
              </h3>
              <p className="mt-6 text-white/74 leading-relaxed max-w-2xl">
                The backend runs on the primary computer and orchestrates real-time physics simulation,
                anomaly inference, cyber scenario execution, and cross-facility aggregation before anything
                reaches the operator interface.
              </p>
              <div className="mt-8 flex flex-wrap gap-3 text-xs uppercase tracking-[0.14em]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                <span className="px-3 py-2 border border-white/28 text-white/84">SensorSimulator</span>
                <span className="px-3 py-2 border border-white/28 text-white/84">5-model ensemble</span>
                <span className="px-3 py-2 border border-white/28 text-white/84">CyberSimulator</span>
                <span className="px-3 py-2 border border-white/28 text-white/84">PostgreSQL hub</span>
                <span className="px-3 py-2 border border-white/28 text-white/84">dc-primary + multi-site</span>
              </div>
            </div>
            <div className="space-y-4 js-scroll-card">
              {HOST_SIDE_CAPABILITIES.map((feature, idx) => (
                <article
                  key={feature.id}
                  className="border border-white/20 bg-black/56 p-5 sm:p-6 min-h-[154px] js-scroll-card"
                  style={{ transform: `translateX(${idx * 2}px)` }}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-xs tracking-[0.24em] text-white/52" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                        [{feature.id}]
                      </p>
                      <h4 className="mt-2 text-lg uppercase tracking-tight text-white">{feature.title}</h4>
                    </div>
                    <div className="text-white/52 js-subtle-float">
                      <DesignationIcon kind={feature.kind} />
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-white/72 leading-relaxed">{feature.body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="dashboard-side" className="mx-auto max-w-7xl px-6 lg:px-8 py-24 border-t border-white/18 js-scroll-section">
          <p className="text-[11px] uppercase tracking-[0.22em] text-white/60 mb-8" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            [ Dashboard Side ]
          </p>
          <div className="grid lg:grid-cols-[1.1fr_1fr] gap-10">
            <div className="border border-white/20 p-7 sm:p-9 bg-black/58 js-scroll-card">
              <p className="text-xs uppercase tracking-[0.2em] text-white/52" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                The Operator's View
              </p>
              <h3 className="mt-4 text-4xl sm:text-5xl uppercase tracking-tight leading-none text-white">
                One pane of glass for SOC-speed decisions.
              </h3>
              <p className="mt-6 text-white/76 max-w-xl leading-relaxed">
                React renders live telemetry from REST APIs and WebSockets into a fluid cybersecurity
                operations interface where attacks, risk, and response status update without page refreshes.
              </p>
              <div className="mt-8 border border-cyan-400/45 bg-slate-950/90 p-4">
                <p className="text-[10px] uppercase tracking-[0.18em] text-cyan-300" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                  visual tokens
                </p>
                <div className="mt-3 flex flex-wrap gap-2 text-[11px] uppercase tracking-[0.14em]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                  <span className="px-2.5 py-1 border border-[#8b5cf6]/70 text-[#8b5cf6]">Cyber Purple #8b5cf6</span>
                  <span className="px-2.5 py-1 border border-[#0ca5f2]/70 text-[#0ca5f2]">Cyan #0ca5f2</span>
                  <span className="px-2.5 py-1 border border-[#22c55e]/70 text-[#22c55e]">Emerald #22c55e</span>
                  <span className="px-2.5 py-1 border border-slate-500 text-slate-300">Surface #020617</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {DASHBOARD_SIDE_FEATURES.map((item, idx) => (
                <article
                  key={item.id}
                  className="border border-white/20 p-5 bg-black/58 js-scroll-card"
                  style={{ transform: `translateX(${idx * 3}px)` }}
                >
                  <p className="text-xs uppercase tracking-[0.18em] text-white/52" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                    {item.id}
                  </p>
                  <h4 className="mt-2 text-lg uppercase text-white">{item.title}</h4>
                  <p className="mt-2 text-sm text-white/72 leading-relaxed">{item.body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="story" className="mx-auto max-w-7xl px-6 lg:px-8 py-24 border-t border-white/18 js-scroll-section">
          <p className="text-[11px] uppercase tracking-[0.22em] text-white/60 mb-8" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            [ Operational Story ]
          </p>

          <div className="mb-8 flex flex-wrap items-center gap-2 text-[11px] uppercase tracking-[0.16em]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            {STAGE_CARDS.map((phase, idx) => (
              <div
                key={phase.id}
                className={`px-3 py-2 border transition-all duration-500 ${
                  idx === phaseIndex
                    ? 'border-white bg-white/18 text-white'
                    : 'border-white/30 text-white/56'
                }`}
              >
                {phase.id} {phase.title}
              </div>
            ))}
          </div>

          <div className="grid lg:grid-cols-[1.1fr_1fr] gap-10">
            <div className="border border-white/20 bg-black/58 p-7 sm:p-9 js-scroll-card">
              <h3 className="text-3xl sm:text-4xl uppercase tracking-tight leading-[0.95] text-white js-mask-reveal overflow-hidden">
                From anomaly to action in one workflow.
              </h3>
              <p className="mt-5 text-white/72 leading-relaxed max-w-2xl">
                During thermal acceleration events, most teams lose time between detection and response.
                Our stack compresses that gap with prioritized alerts, recommended interventions,
                and one-click operator execution.
              </p>
              <button
                onClick={() => navigate('/anomalies')}
                className="mt-8 px-6 py-3 border border-white/45 text-xs uppercase tracking-[0.14em] text-white hover:border-white hover:bg-white/8 transition-colors"
                style={{ fontFamily: 'JetBrains Mono, monospace' }}
              >
                View Live Alert Panel
              </button>
            </div>

            <div className="space-y-4">
              {STAGE_CARDS.map((step, idx) => (
                <div
                  key={step.id}
                  className={`border p-5 transition-all duration-500 js-scroll-card ${
                    idx === phaseIndex
                      ? 'border-white bg-white/14 shadow-[0_0_24px_rgba(255,255,255,0.16)]'
                      : 'border-white/22 bg-black/58'
                  }`}
                >
                  <p className="text-xs uppercase tracking-[0.18em] text-white/52" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                    Step {step.id}
                  </p>
                  <h4 className="mt-2 text-lg uppercase text-white">{step.title}</h4>
                  <p className="mt-2 text-sm text-white/72 leading-relaxed">{step.body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-6 lg:px-8 py-20 border-t border-white/18 js-scroll-section">
          <div className="border border-white/28 bg-black/62 p-8 sm:p-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8 relative overflow-hidden js-scroll-card">
            <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(120deg,transparent_0%,rgba(255,255,255,0.16)_48%,transparent_70%)] animate-sweep" />
            <div>
              <p className="text-[11px] uppercase tracking-[0.22em] text-white/60" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                [ Deploy ]
              </p>
              <h3 className="mt-4 text-3xl sm:text-4xl uppercase leading-[0.95] tracking-tight max-w-2xl text-white">
                Build a reliability command center your operators will trust under pressure.
              </h3>
            </div>
            <button
              onClick={() => navigate('/overview')}
              className="px-7 py-3 border border-white bg-white text-black text-sm uppercase tracking-[0.14em] font-semibold hover:bg-transparent hover:text-white transition-colors"
              style={{ fontFamily: 'JetBrains Mono, monospace' }}
            >
              Launch Platform
            </button>
          </div>
        </section>
      </main>

      <footer className="relative z-10 border-t border-white/18">
        <div className="mx-auto max-w-7xl px-6 lg:px-8 py-7 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <p className="text-xs uppercase tracking-[0.16em] text-white/52" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            © 2026 AKAGAMI
          </p>
          <div className="flex flex-wrap items-center gap-5 text-xs uppercase tracking-[0.14em] text-white/52" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            <button onClick={() => navigate('/dashboard')} className="hover:text-white transition-colors">Threat Dashboard</button>
            <button onClick={() => navigate('/anomalies')} className="hover:text-white transition-colors">AI Alerts</button>
            <button onClick={() => navigate('/actions')} className="hover:text-white transition-colors">Work Orders</button>
          </div>
        </div>
      </footer>

      <style>{`
        video::-webkit-media-controls { display: none !important; }
        video::-webkit-media-controls-enclosure { display: none !important; }
        video::-webkit-media-controls-panel { display: none !important; }
        video::-webkit-media-controls-play-button { display: none !important; }
        video::-webkit-media-controls-start-playback-button { display: none !important; }

        @keyframes scanline {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(185%); }
        }

        @keyframes feedSlide {
          0% { opacity: 0; transform: translateY(8px); }
          100% { opacity: 1; transform: translateY(0); }
        }

        @keyframes sweep {
          0% { transform: translateX(-115%); }
          100% { transform: translateX(115%); }
        }

        @keyframes noiseShift {
          0% { transform: translate(0, 0); }
          25% { transform: translate(-2%, 1.5%); }
          50% { transform: translate(1.5%, -1.2%); }
          75% { transform: translate(-1.4%, -1.8%); }
          100% { transform: translate(0, 0); }
        }

        @keyframes cursor {
          0%, 49% { opacity: 1; }
          50%, 100% { opacity: 0; }
        }

        .animate-scanline {
          animation: scanline 2s linear infinite;
        }

        .animate-feed-slide {
          animation: feedSlide 0.35s ease forwards;
        }

        .animate-sweep {
          animation: sweep 2.65s ease-in-out infinite;
        }

        .animate-noise {
          animation: noiseShift 4.2s steps(8) infinite;
        }

        .animate-cursor {
          animation: cursor 0.9s steps(1) infinite;
        }
      `}</style>
    </div>
  );
}
