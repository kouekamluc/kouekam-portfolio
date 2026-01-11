"""
Fix migration inconsistency where socialaccount.0001_initial is applied 
before its dependency sites.0001_initial.

This script checks if sites tables exist and fakes the sites.0001_initial 
migration if needed.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.db import connection
from django.core.management import call_command
from django.conf import settings

def fix_migration_inconsistency():
    """Fix migration inconsistency for sites app."""
    db_engine = settings.DATABASES['default']['ENGINE']
    is_postgres = 'postgresql' in db_engine or 'psycopg' in db_engine
    is_sqlite = 'sqlite' in db_engine
    
    print(f"Database engine: {db_engine}")
    
    try:
        with connection.cursor() as cursor:
            if is_postgres:
                # Check if django_site table exists (PostgreSQL)
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'django_site'
                    );
                """)
                site_table_exists = cursor.fetchone()[0]
                
                # Check if sites.0001_initial migration is recorded
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM django_migrations 
                        WHERE app = 'sites' 
                        AND name = '0001_initial'
                    );
                """)
                sites_migration_exists = cursor.fetchone()[0]
                
            elif is_sqlite:
                # Check if django_site table exists (SQLite)
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='django_site';
                """)
                site_table_exists = cursor.fetchone() is not None
                
                # Check if sites.0001_initial migration is recorded
                cursor.execute("""
                    SELECT COUNT(*) FROM django_migrations 
                    WHERE app = 'sites' AND name = '0001_initial';
                """)
                sites_migration_exists = cursor.fetchone()[0] > 0
            else:
                print(f"Unsupported database engine: {db_engine}")
                return False
            
            print(f"Site table exists: {site_table_exists}")
            print(f"Sites migration recorded: {sites_migration_exists}")
            
            if site_table_exists and not sites_migration_exists:
                print("\n⚠️  Migration inconsistency detected!")
                print("   Sites tables exist but sites.0001_initial migration is not recorded.")
                print("   This can cause 'InconsistentMigrationHistory' errors.")
                print("\n   Fixing by faking sites.0001_initial migration...")
                
                try:
                    call_command('migrate', 'sites', '0001_initial', '--fake', verbosity=1)
                    print("✓ Successfully faked sites.0001_initial migration")
                    return True
                except Exception as e:
                    print(f"✗ Error faking sites migration: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            elif not site_table_exists and not sites_migration_exists:
                print("✓ Sites tables don't exist yet - will be created by migrations")
                return True
            else:
                print("✓ Sites migration state is consistent")
                return True
                
    except Exception as e:
        print(f"✗ Error checking migration state: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_migration_inconsistency()
    sys.exit(0 if success else 1)
