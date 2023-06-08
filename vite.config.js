import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  base: process.env.IS_DEV !== 'true' ? './' : '/',
  plugins: [vue()]
})
