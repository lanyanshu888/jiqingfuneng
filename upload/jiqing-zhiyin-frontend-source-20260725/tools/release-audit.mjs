import { existsSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const checks = [];

function read(path) {
  return readFileSync(join(root, path), 'utf8');
}

function add(name, pass, detail) {
  checks.push({ name, pass, detail });
}

const env = read('entry/src/main/ets/core/config/Environment.ets');
add('Mock mode disabled', /MOCK_MODE:\s*boolean\s*=\s*false/.test(env), 'Release must set Environment.MOCK_MODE=false.');
add('API URL configured', !env.includes('api.jiqing.invalid'), 'Release must use a stable HTTPS backend.');
add('Release debug flag disabled', /DEBUG:\s*boolean\s*=\s*false/.test(env), 'Release must set Environment.DEBUG=false.');

const apiClient = read('entry/src/main/ets/core/http/ApiClient.ets');
add('Real ApiClient implemented', apiClient.includes('@kit.NetworkKit') && !apiClient.includes('真实接口未启用'), 'ApiClient must use Network Kit for real requests.');

const authStore = read('entry/src/main/ets/core/auth/AuthStore.ets');
add('Secure token storage implemented', authStore.includes('Asset') || authStore.includes('@kit.AssetStoreKit'), 'Token must be stored with Asset Store Kit.');

const cacheStore = read('entry/src/main/ets/core/cache/CacheStore.ets');
add('Persistent cache implemented', cacheStore.includes('preferences') || cacheStore.includes('relationalStore') || cacheStore.includes('@kit.ArkData'), 'Offline cache must persist across restarts.');

const reminder = read('entry/src/main/ets/core/notification/ReminderService.ets');
add('Notification service implemented', reminder.includes('@kit.NotificationKit'), 'ReminderService must use Notification Kit.');

const formService = read('entry/src/main/ets/core/form/GrowthFormService.ets');
add('Form service implemented', formService.includes('@kit.FormKit'), 'GrowthFormService must update real home-screen cards.');

const buildProfile = read('build-profile.json5');
add('Signing configured', !/"signingConfigs"\s*:\s*\[\s*\]/.test(buildProfile), 'Release requires signingConfigs or a documented competition exception.');

add('Backend guide exists', existsSync(join(root, 'docs/backend-integration.md')), 'Backend integration guide is required.');
add('Release checklist exists', existsSync(join(root, 'docs/release-checklist.md')), 'Release checklist is required.');

let failed = 0;
for (const check of checks) {
  const marker = check.pass ? 'PASS' : 'FAIL';
  console.log(`${marker} ${check.name} - ${check.detail}`);
  if (!check.pass) {
    failed += 1;
  }
}

if (failed > 0) {
  console.error(`Release audit failed: ${failed} item(s) need work.`);
  process.exit(1);
}

console.log('Release audit passed.');

