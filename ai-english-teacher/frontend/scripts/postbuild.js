#!/usr/bin/env node
/**
 * Postbuild: copy standalone assets, stamp build-info, verify routes.
 * Runs automatically after `npm run build` (local + Render).
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const STANDALONE = path.join(ROOT, '.next/standalone/frontend');

function run(cmd) {
  execSync(cmd, { cwd: ROOT, stdio: 'inherit', shell: true });
}

if (!fs.existsSync(STANDALONE)) {
  console.error('postbuild FAIL: missing standalone output — is output: standalone set?');
  process.exit(1);
}

run('cp -r .next/static .next/standalone/frontend/.next/static');
try {
  run('cp -r public .next/standalone/frontend/public');
} catch {
  // public may be empty
}

require('./write-build-info.js');
require('./verify-build-routes.js');

console.log('postbuild OK');
