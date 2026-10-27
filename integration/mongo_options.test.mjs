import assert from 'node:assert/strict';
import test from 'node:test';
import { mongoArguments } from './mongo_local.mjs';

test('Windows command excludes unsupported Unix options and retains diagnostics setting', () => {
  assert.deepEqual(mongoArguments('win32'), ['--setParameter', 'diagnosticDataCollectionEnabled=false']);
});
test('Linux command retains its required sandbox socket configuration', () => {
  assert.deepEqual(mongoArguments('linux'), ['--nounixsocket', '--setParameter', 'diagnosticDataCollectionEnabled=false']);
});
test('macOS retains the Unix socket configuration', () => {
  assert.ok(mongoArguments('darwin').includes('--nounixsocket'));
});
