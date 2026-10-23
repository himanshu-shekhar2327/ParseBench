import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  optimizeDeps: {
    force: true,
    // Avoid repeatedly reusing the broken optimizer cache.
    noDiscovery: true,
    include: ['react', 'react-dom', 'lucide-react', 'recharts'],
  },
  server: {
    watch: {
      usePolling: true,
    },
  },
})