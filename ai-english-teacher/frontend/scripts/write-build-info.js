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

const json = JSON.stringify(info, null, 2);
fs.mkdirSync(path.dirname(OUT_PUBLIC), { recursive: true });
fs.writeFileSync(OUT_PUBLIC, json);

if (fs.existsSync(path.dirname(OUT_STANDALONE))) {
  fs.writeFileSync(OUT_STANDALONE, json);
}

console.log('write-build-info OK:', info.commit.slice(0, 12), info.nextBuildId || 'no-build-id');
