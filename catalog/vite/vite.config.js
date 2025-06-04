import { defineConfig } from 'vite'
import { resolve } from 'path';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        detail: resolve(__dirname, 'detail.html'),
        list: resolve(__dirname, 'list.html'),
      }
    }
  },  
  optimizeDeps: {
      exclude: ['@neo4j-nvl/layout-workers'],
      include: [
        '@neo4j-nvl/layout-workers > cytoscape',
        '@neo4j-nvl/layout-workers > cytoscape-cose-bilkent',
        '@neo4j-nvl/layout-workers > @neo4j-bloom/dagre',
        '@neo4j-nvl/layout-workers > bin-pack',
        '@neo4j-nvl/layout-workers > graphlib'
      ],
      esbuildOptions: {
        target: 'es2020'
      }
    }
  })