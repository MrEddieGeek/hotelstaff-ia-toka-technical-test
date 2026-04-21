import Fastify, { type FastifyInstance } from 'fastify';
import cors from '@fastify/cors';

import { config } from './config.js';
import { healthRoutes } from './routes/health.js';

export const buildApp = async (): Promise<FastifyInstance> => {
  const app = Fastify({
    logger: {
      level: config.LOG_LEVEL,
      formatters: {
        level: (label) => ({ level: label }),
      },
      base: { service: 'bff', env: config.SERVICE_ENV },
      timestamp: () => `,"time":"${new Date().toISOString()}"`,
    },
    genReqId: (req) => (req.headers['x-request-id'] as string) ?? crypto.randomUUID(),
    requestIdHeader: 'x-request-id',
  });

  app.addHook('onSend', async (request, reply) => {
    reply.header('x-request-id', request.id);
  });

  await app.register(cors, {
    origin: config.BFF_CORS_ORIGIN,
    credentials: true,
  });

  await app.register(healthRoutes, { prefix: '/health' });

  return app;
};
