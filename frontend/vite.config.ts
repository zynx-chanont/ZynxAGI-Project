import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(() => {
  return {
    plugins: [react()],
    // Vite options tailored for large-scale applications
    build: {
      target: 'esnext',
      outDir: 'dist',
      assetsDir: 'assets',
      // Ensure proper handling of environment variables
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
          },
        },
      },
    },
    // Server configuration
    server: {
      port: 5173,
      strictPort: true,
      host: true,
    },
  }
})
