// Basic API tests — run with: node tests/api.test.js
const http = require('http');

const API = process.env.API_URL || 'http://localhost:5000';
let passed = 0, failed = 0;

async function request(path, opts = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, API);
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: opts.method || 'GET',
      headers: { 'Content-Type': 'application/json', ...opts.headers },
    };
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(data) }); }
        catch { resolve({ status: res.statusCode, body: data }); }
      });
    });
    req.on('error', reject);
    if (opts.body) req.write(JSON.stringify(opts.body));
    req.end();
  });
}

function assert(name, condition) {
  if (condition) { console.log(`  ✅ PASS: ${name}`); passed++; }
  else { console.log(`  ❌ FAIL: ${name}`); failed++; }
}

async function runTests() {
  console.log('\n🧪 Running API Tests...\n');

  // Test 1: Health check
  try {
    const res = await request('/api/health');
    assert('Health endpoint returns 200', res.status === 200);
    assert('Health status is ok', res.body.status === 'ok');
  } catch (e) { assert('Health endpoint reachable', false); }

  // Test 2: Get donations (should return array)
  try {
    const res = await request('/api/donations');
    assert('GET /api/donations returns 200', res.status === 200);
    assert('Donations is an array', Array.isArray(res.body));
  } catch (e) { assert('Donations endpoint reachable', false); }

  // Test 3: Create and delete a donation
  try {
    const create = await request('/api/donations', {
      method: 'POST',
      body: { donor_name: 'Test Donor', amount: 100, method: 'Cash', reference: 'Umair', notes: 'test' }
    });
    assert('POST /api/donations returns 201', create.status === 201);
    assert('Created donation has id', !!create.body.id);

    const del = await request(`/api/donations/${create.body.id}`, { method: 'DELETE' });
    assert('DELETE /api/donations returns 200', del.status === 200);
  } catch (e) { assert('Create/Delete donation flow', false); }

  // Test 4: Get settings
  try {
    const res = await request('/api/settings');
    assert('GET /api/settings returns 200', res.status === 200);
    assert('Settings is an array', Array.isArray(res.body));
  } catch (e) { assert('Settings endpoint reachable', false); }

  // Test 5: Get expenses
  try {
    const res = await request('/api/expenses');
    assert('GET /api/expenses returns 200', res.status === 200);
    assert('Expenses is an array', Array.isArray(res.body));
  } catch (e) { assert('Expenses endpoint reachable', false); }

  console.log(`\n📊 Results: ${passed} passed, ${failed} failed out of ${passed + failed}\n`);
  process.exit(failed > 0 ? 1 : 0);
}

runTests();
