#!/usr/bin/env python3
"""
Wine Chat CLI - Command line interface for application management.
"""
import sys
import argparse
from backend.config.env_validator import EnvironmentValidator
from backend.utils.startup import run_startup_sequence

def validate_env(args):
    """Validate environment configuration."""
    print("🔍 Validating environment configuration...\n")
    
    success = EnvironmentValidator.print_validation_report(detailed=args.detailed)
    
    if success:
        print("\n✅ Environment validation passed!")
        return 0
    else:
        print("\n❌ Environment validation failed!")
        print("\nTo fix these issues:")
        print("1. Copy .env.example to .env")
        print("2. Fill in the required values")
        print("3. Run this validation again")
        return 1

def check_startup(args):
    """Run startup checks."""
    print("🚀 Running startup checks...\n")
    
    success = run_startup_sequence(verbose=True)
    
    return 0 if success else 1

def init_db(args):
    """Initialize database."""
    print("🗄️  Initializing database...\n")
    
    try:
        from backend.models.database import init_database
        from backend.utils.startup import StartupManager
        
        # Initialize database tables
        init_database()
        print("✅ Database tables created")
        
        # Create default data
        startup_manager = StartupManager()
        if startup_manager.create_default_data():
            print("✅ Default data created")
        else:
            print("⚠️  Warning: Some default data creation failed")
        
        print("\n🎉 Database initialization complete!")
        return 0
    
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return 1

def generate_migration(args):
    """Generate database migration."""
    print("📝 Generating database migration...\n")
    
    try:
        import subprocess
        import os
        
        # Change to backend directory
        os.chdir('backend')
        
        # Run alembic revision
        cmd = ['alembic', 'revision', '--autogenerate']
        if args.message:
            cmd.extend(['-m', args.message])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migration generated successfully!")
            print(result.stdout)
            return 0
        else:
            print("❌ Migration generation failed!")
            print(result.stderr)
            return 1
    
    except Exception as e:
        print(f"❌ Migration generation failed: {str(e)}")
        return 1

def run_migration(args):
    """Run database migrations."""
    print("🔄 Running database migrations...\n")
    
    try:
        import subprocess
        import os
        
        # Change to backend directory
        os.chdir('backend')
        
        # Run alembic upgrade
        result = subprocess.run(['alembic', 'upgrade', 'head'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migrations applied successfully!")
            print(result.stdout)
            return 0
        else:
            print("❌ Migration failed!")
            print(result.stderr)
            return 1
    
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return 1

def seed_wine_data(args):
    """Seed wine database with sample data."""
    print("🍷 Seeding wine database with sample data...\n")
    
    try:
        from backend.services.wine_data_seeder import wine_data_seeder
        
        # Seed sample wines
        if wine_data_seeder.seed_sample_wines():
            print("✅ Sample wines seeded successfully")
        else:
            print("⚠️  Warning: Wine seeding failed or skipped")
        
        # Seed wine type translations
        if wine_data_seeder.seed_wine_type_translations():
            print("✅ Wine type translations seeded successfully")
        else:
            print("⚠️  Warning: Translation seeding failed or skipped")
        
        print("\n🎉 Wine data seeding complete!")
        return 0
    
    except Exception as e:
        print(f"❌ Wine data seeding failed: {str(e)}")
        return 1

def create_env_file(args):
    """Create .env file from template."""
    import shutil
    import os
    
    if os.path.exists('.env') and not args.force:
        print("❌ .env file already exists. Use --force to overwrite.")
        return 1
    
    try:
        shutil.copy('.env.example', '.env')
        print("✅ Created .env file from template")
        print("📝 Please edit .env file and fill in your configuration values")
        return 0
    
    except Exception as e:
        print(f"❌ Failed to create .env file: {str(e)}")
        return 1

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Wine Chat CLI - Application management tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py validate-env --detailed    # Detailed environment validation
  python cli.py check-startup             # Run startup checks
  python cli.py init-db                   # Initialize database
  python cli.py create-env                # Create .env from template
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate environment command
    validate_parser = subparsers.add_parser('validate-env', help='Validate environment configuration')
    validate_parser.add_argument('--detailed', action='store_true', help='Show detailed validation report')
    validate_parser.set_defaults(func=validate_env)
    
    # Check startup command
    startup_parser = subparsers.add_parser('check-startup', help='Run startup checks')
    startup_parser.set_defaults(func=check_startup)
    
    # Initialize database command
    init_parser = subparsers.add_parser('init-db', help='Initialize database')
    init_parser.set_defaults(func=init_db)
    
    # Generate migration command
    migration_parser = subparsers.add_parser('generate-migration', help='Generate database migration')
    migration_parser.add_argument('-m', '--message', help='Migration message')
    migration_parser.set_defaults(func=generate_migration)
    
    # Run migration command
    migrate_parser = subparsers.add_parser('run-migrations', help='Run database migrations')
    migrate_parser.set_defaults(func=run_migration)
    
    # Seed wine data command
    seed_parser = subparsers.add_parser('seed-wine-data', help='Seed database with sample wine data')
    seed_parser.set_defaults(func=seed_wine_data)
    
    # Create env file command
    env_parser = subparsers.add_parser('create-env', help='Create .env file from template')
    env_parser.add_argument('--force', action='store_true', help='Overwrite existing .env file')
    env_parser.set_defaults(func=create_env_file)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Run the selected command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())