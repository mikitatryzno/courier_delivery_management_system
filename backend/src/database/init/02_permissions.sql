-- Set up database permissions
-- Grant necessary permissions to the application user

-- Ensure the user has the right permissions
GRANT CONNECT ON DATABASE courier_delivery TO courier_user;
GRANT USAGE ON SCHEMA public TO courier_user;
GRANT CREATE ON SCHEMA public TO courier_user;

-- Grant permissions on all tables (current and future)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO courier_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO courier_user;

-- Grant permissions on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO courier_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO courier_user;