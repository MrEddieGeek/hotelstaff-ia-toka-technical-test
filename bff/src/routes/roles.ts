import type { FastifyPluginAsync } from 'fastify';

import { config } from '../config.js';
import { forward } from '../lib/forward.js';

export const roleRoutes: FastifyPluginAsync = async (app) => {
  const base = config.ROLE_SERVICE_URL;
  app.addHook('preHandler', app.authenticate);

  app.post('/roles', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/roles/' }),
  );
  app.get('/roles', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/roles/' }),
  );
  app.post('/assignments', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/assignments/' }),
  );
  app.delete('/assignments', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/assignments/' }),
  );
  app.get('/users/:userId/roles', (req, reply) => {
    const { userId } = req.params as { userId: string };
    return forward(req, reply, { targetBase: base, targetPath: `/users/${userId}/roles` });
  });
};
