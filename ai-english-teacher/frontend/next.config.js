const path = require('path');

const API_PROXY_TARGET =
  process.env.API_PROXY_URL || 'https://ai-english-teacher-api.onrender.com';

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  // Monorepo: trace files from repo root so all app routes ship in production.
  outputFileTracingRoot: path.join(__dirname, '../..'),
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '/api/v1',
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${API_PROXY_TARGET}/api/v1/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
