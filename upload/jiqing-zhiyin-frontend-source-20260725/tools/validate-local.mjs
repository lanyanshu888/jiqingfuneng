import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');

const requiredFiles = [
  'README.md',
  'docs/api-contract.md',
  'docs/backend-integration.md',
  'docs/delivery-status.md',
  'docs/release-checklist.md',
  'entry/src/main/ets/pages/Index.ets',
  'entry/src/main/ets/pages/home/HomePage.ets',
  'entry/src/main/ets/pages/plan/PlanPage.ets',
  'entry/src/main/ets/pages/resource/ResourceCenterPage.ets',
  'entry/src/main/ets/pages/assistant/AssistantPage.ets',
  'entry/src/main/ets/pages/mine/MinePage.ets',
  'entry/src/main/ets/state/AppState.ets',
  'entry/src/main/ets/core/http/ApiClient.ets',
  'entry/src/main/ets/mock/MockFixtures.ets',
  'growthform/src/main/ets/widget/pages/GrowthCard.ets',
  'simulator/index.html',
  'simulator/app.js',
  'simulator/styles.css',
  'tools/build-dev.ps1',
  'tools/collect-evidence.ps1',
  'tools/install-run-dev.ps1',
  'tools/release-audit.mjs',
  'tools/smoke-api.mjs'
];

const secretPatterns = [
  new RegExp('JIQING_' + 'AGENT_' + 'SERVICE_' + 'KEY'),
  new RegExp('binding' + 'Token'),
  new RegExp('Token [A-Za-z0-9]'),
  new RegExp('trycloudflare' + '\\.com'),
  new RegExp("password" + "\\s*[:=]\\s*['\\\"]", 'i')
];

function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    if (['.hvigor', '.idea', '.preview', 'build', 'oh_modules'].includes(name)) {
      return [];
    }
    return statSync(path).isDirectory() ? walk(path) : [path];
  });
}

const missing = requiredFiles.filter((file) => !existsSync(join(root, file)));
if (missing.length > 0) {
  console.error('Missing required files:');
  missing.forEach((file) => console.error(`- ${file}`));
  process.exit(1);
}

const hits = [];
for (const file of walk(root)) {
  if (!/\.(ets|ts|js|json|json5|md|html|css|bat)$/i.test(file)) {
    continue;
  }
  const content = readFileSync(file, 'utf8');
  for (const pattern of secretPatterns) {
    if (pattern.test(content)) {
      hits.push(file);
      break;
    }
  }
}

if (hits.length > 0) {
  console.error('Sensitive pattern hits:');
  hits.forEach((file) => console.error(`- ${file}`));
  process.exit(1);
}

console.log('Local validation passed.');
console.log(`Checked ${requiredFiles.length} required files.`);
