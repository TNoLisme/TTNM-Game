import { defineConfig } from 'vite';

export default defineConfig({
    server: {
        host: 'localhost',
        port: 5173,
        proxy: {
            '/api': 'http://localhost:5000',
            '/games': {
                target: "http://127.0.0.1:8000",
                changeOrigin: true,
                secure: false,
            },
        },
    },
});
