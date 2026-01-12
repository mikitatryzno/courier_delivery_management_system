-- Initialize PostgreSQL database for Courier Delivery System
-- This script runs automatically when the PostgreSQL container starts

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for better performance (will be created by Alembic migrations)
-- This is just a placeholder for any additional database setup