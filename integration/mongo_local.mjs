import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { MongoMemoryServer } from 'mongodb-memory-server';

export function mongoArguments(platform = process.platform) {
  // mongod on Windows does not accept the Unix socket option (exit code 2).
  return [
    ...(platform === 'win32' ? [] : ['--nounixsocket']),
    '--setParameter', 'diagnosticDataCollectionEnabled=false',
  ];
}

export async function startMongo() {
  const disposable = process.env.STN_DISPOSABLE_MONGO === '1';
  const dataRoot = path.resolve('integration-data');
  const dbPath = path.join(dataRoot, 'mongo');
  const logPath = path.join(dataRoot, 'mongo-startup.log');
  // Disposable tests must not write in the user's persistent data tree.
  if (!disposable) fs.mkdirSync(dbPath, { recursive: true });
  const record = message => {
    if (!disposable) fs.appendFileSync(logPath, `${new Date().toISOString()} ${message}\n`);
  };
  const args = mongoArguments();
  record(`Starting local MongoDB 7.0.24; platform=${process.platform}; args=${JSON.stringify(args)}`);
  let server;
  try {
    server = await MongoMemoryServer.create({
      binary: { version: '7.0.24' },
      instance: { ip: '127.0.0.1', port: 27017, portGeneration: false, ...(!disposable ? { dbPath } : {}), args },
    });
  } catch (error) {
    record(error instanceof Error ? error.stack || error.message : String(error));
    console.error('Local MongoDB could not start.');
    console.error(error instanceof Error ? error.message : String(error));
    if (!disposable) console.error(`Startup log: ${logPath}`);
    process.exitCode = 1;
    return;
  }
  record('READY on 127.0.0.1:27017');
  console.log('MongoDB ready on 127.0.0.1:27017. ' + (disposable ? 'Disposable test data.' : 'Local test data retained in integration-data/mongo.'));
  for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, async () => {
    await server.stop({ doCleanup: disposable });
    record('Stopped. Saved test data retained.');
    process.exit(0);
  });
  return server;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) await startMongo();
