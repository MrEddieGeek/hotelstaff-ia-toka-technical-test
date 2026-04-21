import type { FastifyPluginAsync } from 'fastify';

import { config } from '../config.js';
import { forward } from '../lib/forward.js';

export const agentRoutes: FastifyPluginAsync = async (app) => {
  const base = config.IA_AGENT_URL;
  app.addHook('preHandler', app.authenticate);

  app.post('/ask', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/agent/ask' }),
  );
  app.post('/index', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/agent/index' }),
  );
  app.post('/index/bulk', (req, reply) =>
    forward(req, reply, { targetBase: base, targetPath: '/agent/index/bulk' }),
  );
};
