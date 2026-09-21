import { defineConfig } from 'vite';
export default defineConfig({
  root: '.',
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
