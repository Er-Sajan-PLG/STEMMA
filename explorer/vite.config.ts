import { defineConfig } from 'vite';
export default defineConfig({
  root: '.',
  // '/' locally; the Pages workflow sets STEMMA_BASE=/STEMMA/ (project site subpath).
  base: process.env.STEMMA_BASE || '/',
  publicDir: 'public',
  server: {
    host: '0.0.0.0',
    port: 5174,
    allowedHosts: true,
    open: false,
    hmr: { overlay: false }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: true,
    target: 'es2020'
  },
  optimizeDeps: {
    include: ['three', '3d-force-graph']
  }
});
