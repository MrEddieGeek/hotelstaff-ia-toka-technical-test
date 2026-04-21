import { z } from 'zod';

const schema = z.object({
  BFF_PORT: z.coerce.number().default(8080),
  BFF_CORS_ORIGIN: z.string().default('http://localhost:3000'),
  LOG_LEVEL: z.string().default('info'),
  SERVICE_ENV: z.string().default('local'),

  AUTH_SERVICE_URL: z.string().default('http://auth-service:8000'),
  USER_SERVICE_URL: z.string().default('http://user-service:8000'),
  ROLE_SERVICE_URL: z.string().default('http://role-service:8000'),
  AUDIT_SERVICE_URL: z.string().default('http://audit-service:8000'),
  IA_AGENT_URL: z.string().default('http://ia-agent:8000'),

  JWT_PUBLIC_KEY_PATH: z.string().default('/run/secrets/jwt_public.pem'),
  JWT_ALGORITHM: z.string().default('RS256'),
  JWT_ISSUER: z.string().default('hotelstaff-auth'),

  REDIS_URL: z.string().default('redis://redis:6379/0'),

  RATE_LIMIT_MAX: z.coerce.number().default(200),
  RATE_LIMIT_WINDOW: z.string().default('1 minute'),
});

export const config = schema.parse(process.env);
export type Config = z.infer<typeof schema>;
