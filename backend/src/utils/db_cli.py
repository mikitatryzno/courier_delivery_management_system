"""Command line interface for database operations."""
import click
import logging
from src.utils.database_manager import DatabaseManager
from src.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Database management CLI."""
    pass

@cli.command()
def info():
    """Show database information."""
    with DatabaseManager() as db_manager:
        if not db_manager.check_connection():
            click.echo("❌ Database connection failed")
            return
        
        info = db_manager.get_database_info()
        if info:
            click.echo("📊 Database Information:")
            click.echo(f"  Type: {info['type']}")
            click.echo(f"  Version: {info['version']}")
            click.echo(f"  Environment: {info['environment']}")
            click.echo(f"  URL: {info['url']}")
            
            counts = db_manager.get_table_counts()
            if counts:
                click.echo("\n📈 Table Counts:")
                for table, count in counts.items():
                    click.echo(f"  {table}: {count}")
        else:
            click.echo("❌ Failed to get database information")

@cli.command()
def create():
    """Create database tables."""
    with DatabaseManager() as db_manager:
        if db_manager.create_tables():
            click.echo("✅ Database tables created successfully")
        else:
            click.echo("❌ Failed to create database tables")

@cli.command()
def drop():
    """Drop database tables."""
    if click.confirm("Are you sure you want to drop all tables?"):
        with DatabaseManager() as db_manager:
            if db_manager.drop_tables():
                click.echo("✅ Database tables dropped successfully")
            else:
                click.echo("❌ Failed to drop database tables")

@cli.command()
def reset():
    """Reset database (drop and recreate tables)."""
    if click.confirm("Are you sure you want to reset the database?"):
        with DatabaseManager() as db_manager:
            if db_manager.reset_database():
                click.echo("✅ Database reset successfully")
            else:
                click.echo("❌ Failed to reset database")

@cli.command()
def seed():
    """Seed database with sample data."""
    with DatabaseManager() as db_manager:
        if not db_manager.check_connection():
            click.echo("❌ Database connection failed")
            return
        
        if db_manager.seed_sample_data():
            click.echo("✅ Sample data seeded successfully")
            click.echo("\n👥 Sample users created:")
            click.echo("  Admin: admin@example.com / admin123")
            click.echo("  Courier: courier@example.com / courier123")
            click.echo("  Sender: sender@example.com / sender123")
            click.echo("  Recipient: recipient@example.com / recipient123")
        else:
            click.echo("❌ Failed to seed sample data")

@cli.command()
def init():
    """Initialize database (create tables and seed data)."""
    with DatabaseManager() as db_manager:
        if not db_manager.check_connection():
            click.echo("❌ Database connection failed")
            return
        
        click.echo("🔧 Creating database tables...")
        if not db_manager.create_tables():
            click.echo("❌ Failed to create database tables")
            return
        
        click.echo("🌱 Seeding sample data...")
        if db_manager.seed_sample_data():
            click.echo("✅ Database initialized successfully")
            click.echo("\n👥 Sample users created:")
            click.echo("  Admin: admin@example.com / admin123")
            click.echo("  Courier: courier@example.com / courier123")
            click.echo("  Sender: sender@example.com / sender123")
            click.echo("  Recipient: recipient@example.com / recipient123")
        else:
            click.echo("❌ Failed to seed sample data")

@cli.command()
def cleanup():
    """Clean up test data."""
    if settings.environment == "production":
        click.echo("❌ Cannot cleanup data in production environment")
        return
    
    if click.confirm("Are you sure you want to cleanup test data?"):
        with DatabaseManager() as db_manager:
            if db_manager.cleanup_test_data():
                click.echo("✅ Test data cleaned up successfully")
            else:
                click.echo("❌ Failed to cleanup test data")

@cli.command()
def check():
    """Check database connection."""
    with DatabaseManager() as db_manager:
        if db_manager.check_connection():
            click.echo("✅ Database connection successful")
        else:
            click.echo("❌ Database connection failed")

if __name__ == "__main__":
    cli()