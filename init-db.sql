-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS public;

-- Grant permissions
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public; 