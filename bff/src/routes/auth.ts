import type { FastifyPluginAsync } from 'fastify';

import { config } from '../config.js';
import { forward } from '../lib/forward.js';

export const authRoutes: FastifyPluginAsync = async (app) => {
  const base = config.AUTH_SERVICE_URL;

  app.post('/register', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/auth/register' }),
  );
  app.post('/login', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/auth/login' }),
  );
  app.post('/token', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/auth/token' }),
  );
  app.post('/refresh', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/auth/refresh' }),
  );

  app.get(
    '/me',
    { preHandler: app.authenticate },
    (req, reply) => forward(req, reply, { targetBase: base, targetPath: '/auth/me' }),
  );
};
