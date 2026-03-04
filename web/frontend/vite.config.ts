import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // bind to all interfaces so the dev server is reachable from other hosts
    host: true,
    port: 3000
    ,
    proxy: {
      // proxy API calls to the backend during development
      '/api': {
        target: `http://127.0.0.1:${process.env.PORT_BACKEND ?? '5000'}`,
        changeOrigin: true,
        secure: false
      }
    }
  }
})
