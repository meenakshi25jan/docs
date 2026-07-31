#!/usr/bin/env node
/**
 * Write build-info.json for post-deploy verification (commit SHA, routes, build id).
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const OUT_PUBLIC = path.join(ROOT, 'public/build-info.json');
const OUT_STANDALONE = path.join(
  ROOT,
  '.next/standalone/frontend/public/build-info.json',
);

function gitSha() {
  const env =
    process.env.RENDER_GIT_COMMIT ||
    process.env.GITHUB_SHA ||
    process.env.COMMIT_SHA;
  if (env) return env.trim();
  try {
    return execSync('git rev-parse HEAD', { cwd: ROOT, encoding: 'utf8' }).trim();
  } catch {
    return 'unknown';
  }
}

function readRoutesFromManifest() {
  const manifestPath = path.join(ROOT, '.next/app-path-routes-manifest.json');
  if (!fs.existsSync(manifestPath)) return [];
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  return Object.values(manifest).sort();
}

function readNextBuildId() {
  const buildIdPath = path.join(ROOT, '.next/BUILD_ID');
  if (fs.existsSync(buildIdPath)) {
    return fs.readFileSync(buildIdPath, 'utf8').trim();
  }
  return null;
}

const info = {
  commit: gitSha(),
  builtAt: new Date().toISOString(),
  nextBuildId: readNextBuildId(),
  nodeVersion: process.version,
  routes: readRoutesFromManifest(),
  service: 'ai-english-teacher-web',
};

function validateBuildInfo(data) {
  const errors = [];
  if (!data.commit || data.commit === 'unknown') {
    errors.push('commit (git SHA or RENDER_GIT_COMMIT)');
  }
  if (!data.builtAt || typeof data.builtAt !== 'string') {
    errors.push('builtAt');
  }
  if (!data.nextBuildId || typeof data.nextBuildId !== 'string') {
    errors.push('nextBuildId (.next/BUILD_ID missing)');
  }
  if (!Array.isArray(data.routes) || data.routes.length === 0) {
    errors.push('routes (empty — manifest missing?)');
  } else if (!data.routes.includes('/grammar-class')) {
    errors.push('routes must include /grammar-class');
  }
  if (!data.service || typeof data.service !== 'string') {
    errors.push('service');
  }
  if (errors.length) {
    console.error('');
    console.error('══════════════════════════════════════════════════════════');
    console.error('write-build-info FAILED — incomplete build metadata');
    for (const e of errors) {
      console.error(`  - ${e}`);
    }
    console.error('Build aborted — fix metadata generation before deploy.');
    console.error('══════════════════════════════════════════════════════════');
    process.exit(1);
  }
}

validateBuildInfo(info);

const json = JSON.stringify(info, null, 2);
fs.mkdirSync(path.dirname(OUT_PUBLIC), { recursive: true });
fs.writeFileSync(OUT_PUBLIC, json);

if (fs.existsSync(path.dirname(OUT_STANDALONE))) {
  fs.writeFileSync(OUT_STANDALONE, json);
}

console.log('write-build-info OK:', info.commit.slice(0, 12), info.nextBuildId || 'no-build-id');
