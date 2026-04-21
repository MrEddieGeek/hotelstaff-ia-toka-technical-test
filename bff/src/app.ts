import Fastify, { type FastifyInstance } from 'fastify';
import cors from '@fastify/cors';
import rateLimit from '@fastify/rate-limit';

import { config } from './config.js';
import { authPlugin } from './plugins/auth.js';
import { healthRoutes } from './routes/health.js';
import { authRoutes } from './routes/auth.js';
import { userRoutes } from './routes/users.js';
import { roleRoutes } from './routes/roles.js';
import { auditRoutes } from './routes/audit.js';
import { agentRoutes } from './routes/agent.js';

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

  await app.register(rateLimit, {
    max: config.RATE_LIMIT_MAX,
    timeWindow: config.RATE_LIMIT_WINDOW,
  });

  await app.register(authPlugin);

  await app.register(healthRoutes, { prefix: '/health' });
  await app.register(authRoutes, { prefix: '/api/auth' });
  await app.register(userRoutes, { prefix: '/api/users' });
  await app.register(roleRoutes, { prefix: '/api' });
  await app.register(auditRoutes, { prefix: '/api/audit' });
  await app.register(agentRoutes, { prefix: '/api/agent' });

  return app;
};
