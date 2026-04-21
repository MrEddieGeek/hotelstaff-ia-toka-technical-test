import type { FastifyReply, FastifyRequest } from 'fastify';

export interface ForwardOptions {
  targetBase: string;
  targetPath: string;
  forwardAuth?: boolean;
}

export const forward = async (
  request: FastifyRequest,
  reply: FastifyReply,
  opts: ForwardOptions,
): Promise<FastifyReply> => {
  const url = new URL(opts.targetPath, opts.targetBase);
  for (const [key, value] of Object.entries(request.query ?? {})) {
    if (Array.isArray(value)) {
      for (const v of value) url.searchParams.append(key, String(v));
    } else if (value !== undefined) {
      url.searchParams.append(key, String(value));
    }
  }

  const headers: Record<string, string> = {
    'x-request-id': String(request.id),
  };
  const contentType = request.headers['content-type'];
  if (contentType) headers['content-type'] = String(contentType);
  if (opts.forwardAuth !== false && request.headers.authorization) {
    headers.authorization = String(request.headers.authorization);
  }

  const method = request.method.toUpperCase();
  const init: RequestInit = { method, headers };
  if (method !== 'GET' && method !== 'HEAD' && request.body !== undefined) {
    if (headers['content-type']?.includes('application/x-www-form-urlencoded')) {
      init.body = new URLSearchParams(request.body as Record<string, string>).toString();
    } else {
      init.body = JSON.stringify(request.body);
      headers['content-type'] = 'application/json';
    }
  }

  let response: Response;
  try {
    response = await fetch(url, init);
  } catch (err) {
    request.log.error({ err, target: url.toString() }, 'bff.forward.upstream_error');
    return reply.code(502).send({ error: 'upstream_unavailable' });
  }

  const body = await response.text();
  reply.code(response.status);
  const ct = response.headers.get('content-type');
  if (ct) reply.header('content-type', ct);
  return reply.send(body);
};
