import { defineConfig } from 'vite';

export default defineConfig({
    server: {
        host: 'localhost',
        port: 5173,
        proxy: {
            '/api': 'http://localhost:5000',
        },
    },
});
