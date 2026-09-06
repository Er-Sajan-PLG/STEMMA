import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  root: '.',
  publicDir: 'public',
  server: {
    host: '0.0.0.0',
    port: 5174,
    allowedHosts: true,
    open: false
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
});
