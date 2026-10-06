import {defineConfig, esmExternalRequirePlugin} from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';


export default defineConfig({
    define: {
        global: 'globalThis',
        'process.env.NODE_ENV': JSON.stringify('production')
    },
    root: 'paragon/src',
    plugins: [react()],
    css: {
        preprocessorOptions: {
            scss: {
                loadPaths: [resolve(import.meta.dirname, 'paragon', 'node_modules')],
                silenceDeprecations: ['import', 'global-builtin'],
            },
        },
    },
    build: {
        lib: {
            formats: ['es'],
            entry: 'index.ts'
        },
        emptyOutDir: true,
        rolldownOptions: {
            output: {
                paths: {react: '../react/index.js'},
            },
            plugins: [
                esmExternalRequirePlugin({
                    external: ['react'],
                }),
            ]
        },
        outDir: '../../../scratch/paragon'
    },
    resolve: {
        alias: {
            '@': resolve(import.meta.dirname, 'src'),
        },
    },
});
