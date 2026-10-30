// All services run as children of one test process on disposable data.
import { MongoMemoryServer } from 'mongodb-memory-server';
import { MongoClient } from 'mongodb';
import { spawn } from 'node:child_process';
import { randomBytes } from 'node:crypto';

const password = randomBytes(24).toString('hex');
const name = 'integration_stage2_' + randomBytes(6).toString('hex');
const server = await MongoMemoryServer.create({
  binary: { version: '8.0.17' },
  instance: { ip: '127.0.0.1', args: ['--nounixsocket', '--setParameter', 'diagnosticDataCollectionEnabled=false'] },
  auth: { enable: true, customRootName: 'test-root', customRootPwd: password },
});
try {
  const root = await MongoClient.connect(server.getUri('admin'), { auth: { username: 'test-root', password }, authSource: 'admin' });
  await root.db(name).command({ createUser: 'test-app', pwd: password, roles: [{ role: 'readWrite', db: name }] });
  await root.close();
  const parsed = new URL(server.getUri(name));
  parsed.username = 'test-app'; parsed.password = password;
  parsed.searchParams.set('authSource', name);
  const child = spawn(process.env.STAGE2_PYTHON || 'python3', ['integration/production_smoke.py'], {
    env: { ...process.env, STAGE2_MONGO_URI: parsed.toString() }, stdio: 'inherit',
  });
  const code = await new Promise((resolve, reject) => { child.on('error', reject); child.on('exit', resolve); });
  if (code !== 0) process.exitCode = 1;
} finally {
  await server.stop();
}
