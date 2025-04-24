# Database Migration Guide

This guide explains how to update your database to support the latest features, including the follower/following functionality.

## Automatic Migrations

The application now includes an automatic migration system that will:

1. Check for missing database columns needed for new features
2. Add these columns if they don't exist
3. Set appropriate default values

These migrations run automatically:
- During application startup
- When using the Docker containers
- When using the development scripts

## Manual Migration

If you need to manually run migrations, you can use the included scripts:

### Docker Environment

If running with Docker:

```bash
docker-compose exec api python /app/src/migrate_profiles.py
```

### Local Development

For local development environments:

```bash
# Make the script executable if needed
chmod +x migrate.sh

# Run the migration script
./migrate.sh
```

Or run the Python migration script directly:

```bash
# Set the PYTHONPATH to the current directory
export PYTHONPATH=$(pwd)

# Run the migration script
python src/migrate_profiles.py
```

## Database Schema Changes

### User Profiles Table

The following columns were added to the `user_profiles` table:

| Column Name | Type | Default | Description |
|-------------|------|---------|-------------|
| follower_count | INTEGER | 0 | Count of users who follow this user |
| following_count | INTEGER | 0 | Count of users this user follows |

### Followers Table

A new `followers` table has been created with the following schema:

| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier for the follow relationship |
| follower_id | UUID | FOREIGN KEY | Reference to the user who is following |
| following_id | UUID | FOREIGN KEY | Reference to the user being followed |
| created_at | TIMESTAMP | | When the follow relationship was created |

A unique constraint ensures a user cannot follow another user more than once.

## Verifying Migrations

To verify that migrations have been applied correctly:

### PostgreSQL:

```sql
\d user_profiles
\d followers
```

### SQLite:

```sql
.schema user_profiles
.schema followers
```

You should see the new columns in the `user_profiles` table and the new `followers` table with the appropriate schema.

## Troubleshooting

If you encounter any issues with migrations:

1. Check the application logs for error messages
2. Ensure database permissions are set correctly
3. Manually run the migration script as detailed above
4. Restart the application after migrations complete

For persistent issues, you can run the following manual migrations:

### PostgreSQL:

```sql
-- Add columns to user_profiles if they don't exist
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS follower_count INTEGER DEFAULT 0;
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS following_count INTEGER DEFAULT 0;

-- Create followers table if it doesn't exist
CREATE TABLE IF NOT EXISTS followers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    follower_id UUID NOT NULL REFERENCES users(id),
    following_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_follower_following UNIQUE (follower_id, following_id)
);
```

### SQLite:

```sql
-- Add columns to user_profiles if they don't exist
-- Note: SQLite doesn't support IF NOT EXISTS for columns
-- First check if columns exist, then add them if needed
PRAGMA table_info(user_profiles);
-- Then run these if needed:
ALTER TABLE user_profiles ADD COLUMN follower_count INTEGER DEFAULT 0;
ALTER TABLE user_profiles ADD COLUMN following_count INTEGER DEFAULT 0;

-- Create followers table if it doesn't exist
CREATE TABLE IF NOT EXISTS followers (
    id TEXT PRIMARY KEY,
    follower_id TEXT NOT NULL REFERENCES users(id),
    following_id TEXT NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (follower_id, following_id)
);
``` 