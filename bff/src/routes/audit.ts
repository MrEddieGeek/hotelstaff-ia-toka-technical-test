import type { FastifyPluginAsync } from 'fastify';

import { config } from '../config.js';
import { forward } from '../lib/forward.js';

export const auditRoutes: FastifyPluginAsync = async (app) => {
  const base = config.AUDIT_SERVICE_URL;
  app.addHook('preHandler', app.authenticate);

  app.get('/logs', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/audit' }),
  );
  app.get('/logs/:eventId', (req, reply) => {
    const { eventId } = req.params as { eventId: string };
    return forward(req, reply, { targetBase: base, targetPath: `/audit/${eventId}` });
  });
};
