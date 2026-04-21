import { buildApp } from './app.js';
import { config } from './config.js';

const start = async (): Promise<void> => {
  const app = await buildApp();
  try {
    await app.listen({ host: '0.0.0.0', port: config.BFF_PORT });
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

void start();
