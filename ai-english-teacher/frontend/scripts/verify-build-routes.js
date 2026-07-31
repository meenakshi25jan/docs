#!/usr/bin/env node
/**
 * Fail builds if App Router pages in src/app are missing from manifest + standalone.
 * Discovers expected routes from src/app (all page.tsx files).
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const APP_SRC = path.join(ROOT, 'src/app');
const MANIFEST_PATH = path.join(ROOT, '.next/app-path-routes-manifest.json');
const STANDALONE_APP = path.join(
  ROOT,
  '.next/standalone/frontend/.next/server/app',
);
const STANDALONE_SERVER = path.join(
  ROOT,
  '.next/standalone/frontend/server.js',
);

function fail(msg) {
  console.error('');
  console.error('══════════════════════════════════════════════════════════');
  console.error('verify-build-routes FAILED');
  console.error(msg);
  console.error('Build aborted — fix routes before deploy.');
  console.error('══════════════════════════════════════════════════════════');
  process.exit(1);
}

/**
 * Walk src/app for page.tsx → URL paths.
 */
function discoverRoutesFromSrc() {
  const found = new Set();

  function scan(dir, prefix) {
    if (!fs.existsSync(dir)) return;
    const pageTsx = path.join(dir, 'page.tsx');
    const pageJs = path.join(dir, 'page.js');
    if (fs.existsSync(pageTsx) || fs.existsSync(pageJs)) {
      found.add(prefix === '' ? '/' : prefix);
    }
    for (const name of fs.readdirSync(dir)) {
      const child = path.join(dir, name);
      if (!fs.statSync(child).isDirectory()) continue;
      const childPrefix = prefix === '' ? `/${name}` : `${prefix}/${name}`;
      scan(child, childPrefix);
    }
  }

  scan(APP_SRC, '');
  return [...found].sort();
}

function manifestRoutes(manifest) {
  return new Set(Object.values(manifest));
}

/**
 * Standalone server app artifact for a route path.
 * / → index.html or page/ ; /grammar-class → grammar-class/ or grammar-class.html
 */
function standaloneArtifactsForRoute(routePath) {
  if (routePath === '/') {
    return [
      path.join(STANDALONE_APP, 'index.html'),
      path.join(STANDALONE_APP, 'page'),
    ];
  }
  const slug = routePath.replace(/^\//, '');
  return [
    path.join(STANDALONE_APP, slug),
    path.join(STANDALONE_APP, `${slug}.html`),
  ];
}

function routePresentInStandalone(routePath) {
  return standaloneArtifactsForRoute(routePath).some((p) => fs.existsSync(p));
}

// --- checks ---
if (!fs.existsSync(MANIFEST_PATH)) {
  fail(`missing ${MANIFEST_PATH} — run next build first`);
}

if (!fs.existsSync(STANDALONE_SERVER)) {
  fail(`missing standalone server at ${STANDALONE_SERVER}`);
}

if (!fs.existsSync(STANDALONE_APP)) {
  fail(`missing standalone app dir at ${STANDALONE_APP}`);
}

const expectedRoutes = discoverRoutesFromSrc();
if (expectedRoutes.length === 0) {
  fail(`no routes discovered under ${APP_SRC}`);
}

const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));
const manifestSet = manifestRoutes(manifest);

const missingManifest = expectedRoutes.filter((r) => !manifestSet.has(r));
if (missingManifest.length) {
  fail(
    `routes missing from app-path-routes-manifest.json:\n  ${missingManifest.join('\n  ')}\n` +
      `manifest has: ${[...manifestSet].sort().join(', ')}`
  );
}

const missingStandalone = expectedRoutes.filter((r) => !routePresentInStandalone(r));
if (missingStandalone.length) {
  const details = missingStandalone.map((r) => {
    const tried = standaloneArtifactsForRoute(r).join(', ');
    return `  ${r} (checked: ${tried})`;
  });
  fail(`routes missing from standalone output:\n${details.join('\n')}`);
}

// Critical route — explicit loud check
if (!manifestSet.has('/grammar-class') || !routePresentInStandalone('/grammar-class')) {
  fail('/grammar-class must be in manifest and standalone (stale-build guard)');
}

console.log('verify-build-routes OK');
console.log(`  src/app routes (${expectedRoutes.length}): ${expectedRoutes.join(', ')}`);
console.log(`  manifest: ${MANIFEST_PATH}`);
console.log(`  standalone: ${STANDALONE_SERVER}`);
console.log('  /grammar-class: manifest + standalone present');
