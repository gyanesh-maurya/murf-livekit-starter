export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  audioVisualizerType?: 'bar' | 'wave' | 'grid' | 'radial' | 'aura';
  audioVisualizerColor?: `#${string}`;
  audioVisualizerColorDark?: `#${string}`;
  audioVisualizerColorShift?: number;
  audioVisualizerBarCount?: number;
  audioVisualizerGridRowCount?: number;
  audioVisualizerGridColumnCount?: number;
  audioVisualizerRadialBarCount?: number;
  audioVisualizerRadialRadius?: number;
  audioVisualizerWaveLineWidth?: number;

  // agent dispatch configuration
  agentName?: string;

  // LiveKit Cloud Sandbox configuration
  sandboxId?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'DukaanSaathi',
  pageTitle: 'DukaanSaathi Assistant',
  pageDescription: 'Aapka local shop assistant, powered by Murf Falcon and LiveKit',

  supportsChatInput: true,
  supportsVideoInput: false, // Turned off for simple voice-only UI
  supportsScreenShare: false, // Turned off for simple voice-only UI
  isPreConnectBufferEnabled: true,

  logo: '/murf-logo.svg', // Keeping the original logo or we could remove it, but let's keep it to satisfy the Murf requirement visually.
  accent: '#10b981', // Emerald-500
  logoDark: '/murf-logo-dark.svg',
  accentDark: '#34d399', // Emerald-400
  startButtonText: 'Baat Shuru Karein (Start)',

  // optional: audio visualization configuration
  audioVisualizerType: 'bar',
  audioVisualizerColor: '#10b981',
  audioVisualizerColorDark: '#34d399',
  // audioVisualizerColorShift: 0.3,
  // audioVisualizerBarCount: 5,
  // audioVisualizerType: 'radial',
  // audioVisualizerRadialBarCount: 24,
  // audioVisualizerRadialRadius: 100,
  // audioVisualizerType: 'grid',
  // audioVisualizerGridRowCount: 25,
  // audioVisualizerGridColumnCount: 25,
  // audioVisualizerType: 'wave',
  // audioVisualizerWaveLineWidth: 3,
  // audioVisualizerType: 'aura',

  // agent dispatch configuration
  agentName: process.env.AGENT_NAME ?? undefined,

  // LiveKit Cloud Sandbox configuration
  sandboxId: undefined,
};
