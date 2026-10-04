import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'dev.abene.workouttracker',
  appName: 'Workout Tracker',
  webDir: 'public',
  server: {
    url: 'https://toa-gold.vercel.app',
    cleartext: true
  }
};

export default config;
