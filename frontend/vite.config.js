import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: './',   // Electron file:// için göreceli path
  server: {
    proxy: {
      '/predict': 'http://localhost:8000',
      '/health':  'http://localhost:8000',
    },
  },
})
