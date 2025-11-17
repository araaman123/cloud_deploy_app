"""Database initialization and migration scripts."""

import asyncpg
import logging

logger = logging.getLogger(__name__)


async def create_database(dsn: str):
    """Create database if it doesn't exist."""
    # Connect to default postgres database
    default_dsn = dsn.rsplit('/', 1)[0] + '/postgres'
    
    try:
        conn = await asyncpg.connect(default_dsn)
        
        # Get database name from DSN
        db_name = dsn.split('/')[-1]
        
        # Create database
        await conn.execute(f'CREATE DATABASE {db_name}')
        logger.info(f"Database {db_name} created")
        
        await conn.close()
    except asyncpg.DuplicateDatabaseError:
        logger.info("Database already exists")
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise


async def run_migrations(dsn: str):
    """Run database migrations."""
    conn = await asyncpg.connect(dsn)
    
    try:
        # Create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                github_id INTEGER UNIQUE,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                avatar_url TEXT,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create applications table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                name TEXT NOT NULL,
                description TEXT,
                github_repo_url TEXT NOT NULL,
                github_branch TEXT DEFAULT 'main',
                app_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                port INTEGER DEFAULT 8000,
                namespace TEXT UNIQUE NOT NULL,
                domain TEXT UNIQUE,
                tls_enabled BOOLEAN DEFAULT TRUE,
                cpu_limit TEXT DEFAULT '1000m',
                memory_limit TEXT DEFAULT '512Mi',
                replicas INTEGER DEFAULT 1,
                image_uri TEXT,
                image_tag TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                deployed_at TIMESTAMP
            )
        """)
        
        # Create deployments table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS deployments (
                id TEXT PRIMARY KEY,
                app_id TEXT NOT NULL REFERENCES applications(id),
                status TEXT DEFAULT 'pending',
                commit_hash TEXT,
                commit_message TEXT,
                image_uri TEXT,
                started_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP,
                error_message TEXT
            )
        """)
        
        # Create logs table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id TEXT PRIMARY KEY,
                app_id TEXT NOT NULL REFERENCES applications(id),
                deployment_id TEXT REFERENCES deployments(id),
                level TEXT DEFAULT 'INFO',
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create metrics table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id TEXT PRIMARY KEY,
                app_id TEXT NOT NULL REFERENCES applications(id),
                metric_name TEXT NOT NULL,
                metric_value TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create api_keys table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id),
                key_hash TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW(),
                expires_at TIMESTAMP
            )
        """)
        
        logger.info("Database migrations completed")
        
    finally:
        await conn.close()


async def seed_database(dsn: str):
    """Seed database with sample data."""
    conn = await asyncpg.connect(dsn)
    
    try:
        # Check if already seeded
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        
        if user_count == 0:
            # Add sample user
            await conn.execute("""
                INSERT INTO users (id, github_id, username, email, role)
                VALUES ('user_1', 12345, 'demo-user', 'demo@example.com', 'user')
            """)
            
            logger.info("Database seeded with sample data")
        
    finally:
        await conn.close()
