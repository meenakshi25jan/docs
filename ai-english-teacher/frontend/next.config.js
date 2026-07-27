const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Monorepo: trace files from repo root so all app routes ship in production.
  outputFileTracingRoot: path.join(__dirname, '../..'),
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  },
};

module.exports = nextConfig;
