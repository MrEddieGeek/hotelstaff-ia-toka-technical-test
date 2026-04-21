-- Schemas aislados por servicio. Cada servicio tiene su usuario con permisos
-- mínimos sobre su propio schema (principio de least privilege).

CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS roles;

-- Usuarios por servicio (las contraseñas deben rotarse en producción).
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'auth_service') THEN
        CREATE ROLE auth_service LOGIN PASSWORD 'auth_service_pwd';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'user_service') THEN
        CREATE ROLE user_service LOGIN PASSWORD 'user_service_pwd';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'role_service') THEN
        CREATE ROLE role_service LOGIN PASSWORD 'role_service_pwd';
    END IF;
END$$;

GRANT USAGE, CREATE ON SCHEMA auth TO auth_service;
GRANT USAGE, CREATE ON SCHEMA users TO user_service;
GRANT USAGE, CREATE ON SCHEMA roles TO role_service;

ALTER DEFAULT PRIVILEGES IN SCHEMA auth GRANT ALL ON TABLES TO auth_service;
ALTER DEFAULT PRIVILEGES IN SCHEMA users GRANT ALL ON TABLES TO user_service;
ALTER DEFAULT PRIVILEGES IN SCHEMA roles GRANT ALL ON TABLES TO role_service;
