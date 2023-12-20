import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
// Export configuration
export default defineConfig({
    base: process.env.IS_DEV !== 'true' ? './' : '/', // Define the base path.
    plugins: [vue()]
})
