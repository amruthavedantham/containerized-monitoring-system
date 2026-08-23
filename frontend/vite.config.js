import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/health': 'http://127.0.0.1:5000',
      '/process': 'http://127.0.0.1:5000',
      '/slow': 'http://127.0.0.1:5000',
      '/error': 'http://127.0.0.1:5000',
      '/metrics': 'http://127.0.0.1:5000',
      '/predict': 'http://127.0.0.1:5001',
      '/ml': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ml/, '')
      }

    }
  }
})
