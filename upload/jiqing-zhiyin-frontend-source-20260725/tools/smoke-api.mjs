const baseUrl = mustEnv('JIQING_API_BASE_URL').replace(/\/$/, '');
const username = mustEnv('JIQING_TEST_USERNAME');
const passcode = mustEnv('JIQING_TEST_PASSCODE');

const results = [];

function mustEnv(name) {
  const value = process.env[name];
  if (!value || value.trim().length === 0) {
    console.error(`Missing environment variable: ${name}`);
    process.exit(1);
  }
  return value.trim();
}

async function request(method, path, { token = '', body = undefined } = {}) {
  const headers = { Accept: 'application/json' };
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }
  if (token.length > 0) {
    headers.Authorization = `Token ${token}`;
  }

  const response = await fetch(`${baseUrl}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body)
  });

  const text = await response.text();
  let data = {};
  if (text.length > 0) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { message: 'Response is not JSON' };
    }
  }

  results.push({
    method,
    path,
    status: response.status,
    ok: response.ok
  });

  if (!response.ok) {
    const message = typeof data.message === 'string' ? data.message : `HTTP ${response.status}`;
    throw new Error(`${method} ${path} failed: ${message}`);
  }
  return data;
}

function requireArray(name, value) {
  if (!Array.isArray(value)) {
    throw new Error(`${name} response is not an array`);
  }
}

async function main() {
  const login = await request('POST', '/auth/login/', {
    body: {
      username,
      password: passcode
    }
  });

  if (typeof login.token !== 'string' || login.token.length === 0) {
    throw new Error('Login response missing token');
  }
  const token = login.token;

  await request('GET', '/auth/me/', { token });
  await request('GET', '/profiles/me/', { token });
  await request('GET', '/agent/me/dashboard/', { token });
  await request('GET', '/me/growth/', { token });

  for (const path of ['/policies/', '/opportunities/', '/courses/', '/activities/', '/mentors/']) {
    const data = await request('GET', path, { token });
    if (Array.isArray(data)) {
      requireArray(path, data);
    } else if (data.items !== undefined) {
      requireArray(`${path}.items`, data.items);
    }
  }

  await request('GET', '/assistant/profile-analysis/', { token });
  await request('POST', '/assistant/career-plan/', {
    token,
    body: { goal: '县域数字运营' }
  });
  await request('GET', '/assistant/policy-search/?keyword=%E9%AB%98%E6%A0%A1%E6%AF%95%E4%B8%9A%E7%94%9F&region=%E6%B2%A7%E5%B7%9E&limit=5', { token });
  await request('POST', '/assistant/resource-match/', {
    token,
    body: {
      resourceTypes: ['opportunity', 'course', 'activity', 'mentor'],
      goal: '数字运营',
      limit: 3
    }
  });

  console.log('API smoke test passed.');
  for (const result of results) {
    console.log(`${result.ok ? 'PASS' : 'FAIL'} ${result.status} ${result.method} ${result.path}`);
  }
}

main().catch((error) => {
  console.error(error.message);
  console.error('Completed requests:');
  for (const result of results) {
    console.error(`${result.ok ? 'PASS' : 'FAIL'} ${result.status} ${result.method} ${result.path}`);
  }
  process.exit(1);
});

