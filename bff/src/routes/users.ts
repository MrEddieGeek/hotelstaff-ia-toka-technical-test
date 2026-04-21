import type { FastifyPluginAsync } from 'fastify';

import { config } from '../config.js';
import { forward } from '../lib/forward.js';

export const userRoutes: FastifyPluginAsync = async (app) => {
  const base = config.USER_SERVICE_URL;
  app.addHook('preHandler', app.authenticate);

  app.post('/', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/users/' }),
  );
  app.get('/', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/users/' }),
  );
  app.get('/:id', (req, reply) => {
    const { id } = req.params as { id: string };
    return forward(req, reply, { targetBase: base, targetPath: `/users/${id}` });
  });
  app.patch('/:id', (req, reply) => {
    const { id } = req.params as { id: string };
    return forward(req, reply, { targetBase: base, targetPath: `/users/${id}` });
  });
  app.delete('/:id', (req, reply) => {
    const { id } = req.params as { id: string };
    return forward(req, reply, { targetBase: base, targetPath: `/users/${id}` });
  });
};
