import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import fp from 'fastify-plugin';
import { createRemoteJWKSet, jwtVerify, type JWTPayload } from 'jose';

import { config } from '../config.js';

declare module 'fastify' {
  interface FastifyInstance {
    authenticate: (request: FastifyRequest, reply: FastifyReply) => Promise<void>;
  }
  interface FastifyRequest {
    user?: JWTPayload;
  }
}

export const authPlugin = fp(async (app: FastifyInstance) => {
  const jwksUrl = new URL('/.well-known/jwks.json', config.AUTH_SERVICE_URL);
  const JWKS = createRemoteJWKSet(jwksUrl, { cacheMaxAge: 10 * 60 * 1000 });

  app.decorate('authenticate', async (request: FastifyRequest, reply: FastifyReply) => {
    const header = request.headers.authorization;
    if (!header || !header.startsWith('Bearer ')) {
      return reply.code(401).send({ error: 'missing_token' });
    }
    const token = header.slice('Bearer '.length);
    try {
      const { payload } = await jwtVerify(token, JWKS, {
        issuer: config.JWT_ISSUER,
        algorithms: [config.JWT_ALGORITHM],
      });
      request.user = payload;
    } catch (err) {
      request.log.warn({ err }, 'bff.auth.invalid_token');
      return reply.code(401).send({ error: 'invalid_token' });
    }
  });
});
