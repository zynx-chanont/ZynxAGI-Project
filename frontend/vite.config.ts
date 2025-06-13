import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '')
  
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
