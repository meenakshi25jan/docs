const path = require('path');

const API_PROXY_TARGET =
  process.env.API_PROXY_URL || 'https://ai-english-teacher-api.onrender.com';

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  // Trace from ai-english-teacher/ (works on Render Node + Docker frontend builds).
  outputFileTracingRoot: path.join(__dirname, '..'),
  // Repo root has unrelated .eslintrc (Amplify docs) — don't fail Render builds.
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
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
