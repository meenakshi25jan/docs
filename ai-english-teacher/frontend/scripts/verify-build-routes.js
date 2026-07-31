#!/usr/bin/env node
/**
 * Fail CI/Render builds if critical App Router routes are missing from the Next output.
 * Checks app-path-routes-manifest.json and standalone server artifacts.
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const REQUIRED_ROUTES = [
  '/',
  '/grammar-class',
  '/conversation',
  '/login',
  '/register',
  '/dashboard/student',
];

function fail(msg) {
  console.error(`verify-build-routes FAIL: ${msg}`);
  process.exit(1);
}

const manifestPath = path.join(ROOT, '.next/app-path-routes-manifest.json');
if (!fs.existsSync(manifestPath)) {
  fail(`missing ${manifestPath} — run npm run build first`);
}

const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const routes = new Set(Object.values(manifest));
const missing = REQUIRED_ROUTES.filter((r) => !routes.has(r));
if (missing.length) {
  fail(`routes absent from app-path-routes-manifest.json: ${missing.join(', ')}`);
}

const standaloneServer = path.join(
  ROOT,
  '.next/standalone/frontend/server.js',
);
if (!fs.existsSync(standaloneServer)) {
  fail(`missing standalone server at ${standaloneServer}`);
}

const standaloneGrammar = path.join(
  ROOT,
  '.next/standalone/frontend/.next/server/app/grammar-class',
);
if (!fs.existsSync(standaloneGrammar)) {
  fail(`missing standalone grammar-class bundle at ${standaloneGrammar}`);
}

console.log('verify-build-routes OK:', REQUIRED_ROUTES.join(', '));
console.log('manifest:', manifestPath);
console.log('standalone:', standaloneServer);
