"""
Fix migration inconsistency where socialaccount.0001_initial is applied 
before its dependency sites.0001_initial.

This script checks migration history and fixes inconsistencies by:
1. Checking if socialaccount.0001_initial is marked as applied
2. Checking if sites.0001_initial is marked as applied
3. Fixing the inconsistency by either faking sites.0001_initial or removing
   the socialaccount.0001_initial entry as appropriate.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.db import connection, transaction
from django.core.management import call_command
from django.conf import settings

def fix_migration_inconsistency():
    """Fix migration inconsistency between socialaccount and sites apps."""
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
                
                # Check if socialaccount.0001_initial migration is recorded
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM django_migrations 
                        WHERE app = 'socialaccount' 
                        AND name = '0001_initial'
                    );
                """)
                socialaccount_migration_exists = cursor.fetchone()[0]
                
                # Check if socialaccount_socialapp table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'socialaccount_socialapp'
                    );
                """)
                socialaccount_table_exists = cursor.fetchone()[0]
                
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
                
                # Check if socialaccount.0001_initial migration is recorded
                cursor.execute("""
                    SELECT COUNT(*) FROM django_migrations 
                    WHERE app = 'socialaccount' AND name = '0001_initial';
                """)
                socialaccount_migration_exists = cursor.fetchone()[0] > 0
                
                # Check if socialaccount_socialapp table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='socialaccount_socialapp';
                """)
                socialaccount_table_exists = cursor.fetchone() is not None
            else:
                print(f"Unsupported database engine: {db_engine}")
                return False
            
            print(f"Site table exists: {site_table_exists}")
            print(f"Sites migration recorded: {sites_migration_exists}")
            print(f"Socialaccount migration recorded: {socialaccount_migration_exists}")
            
            # Case 1: socialaccount.0001_initial is applied but sites.0001_initial is not
            # This is the error we're seeing
            if socialaccount_migration_exists and not sites_migration_exists:
                print("\n⚠️  Migration inconsistency detected!")
                print("   socialaccount.0001_initial is marked as applied,")
                print("   but its dependency sites.0001_initial is not marked.")
                
                if site_table_exists:
                    # Sites tables exist, so we should fake the sites.0001_initial migration
                    print("\n   Sites tables exist. Fixing by faking sites.0001_initial migration...")
                    try:
                        call_command('migrate', 'sites', '0001_initial', '--fake', verbosity=1)
                        print("✓ Successfully faked sites.0001_initial migration")
                        return True
                    except Exception as e:
                        print(f"✗ Error faking sites migration: {e}")
                        import traceback
                        traceback.print_exc()
                        return False
                else:
                    # Sites tables don't exist, but socialaccount is marked as applied
                    # We cannot fake sites.0001_initial because the table doesn't exist
                    # The safest fix is to remove the socialaccount.0001_initial entry
                    # so migrations can run in the correct order
                    print("\n   Sites tables don't exist, so we cannot fake sites.0001_initial.")
                    print("   Removing socialaccount.0001_initial migration entry")
                    print("   so migrations can run in the correct order...")
                    
                    # Also check if we need to remove any other socialaccount migrations
                    # that depend on sites
                    try:
                        with transaction.atomic():
                            # Remove socialaccount.0001_initial migration entry
                            cursor.execute("""
                                DELETE FROM django_migrations 
                                WHERE app = 'socialaccount' AND name = '0001_initial';
                            """)
                            deleted = cursor.rowcount
                            
                            if deleted > 0:
                                print(f"✓ Successfully removed socialaccount.0001_initial migration entry")
                                print("  (Migrations will run in correct order on next migrate)")
                                return True
                            else:
                                print("⚠ Warning: socialaccount.0001_initial entry not found (may have been removed already)")
                                return True
                    except Exception as e:
                        print(f"✗ Error removing socialaccount migration entry: {e}")
                        import traceback
                        traceback.print_exc()
                        return False
            
            # Case 2: Sites tables exist but migration is not recorded
            elif site_table_exists and not sites_migration_exists:
                print("\n⚠️  Migration inconsistency detected!")
                print("   Sites tables exist but sites.0001_initial migration is not recorded.")
                print("   Fixing by faking sites.0001_initial migration...")
                try:
                    call_command('migrate', 'sites', '0001_initial', '--fake', verbosity=1)
                    print("✓ Successfully faked sites.0001_initial migration")
                    return True
                except Exception as e:
                    print(f"✗ Error faking sites migration: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            # Case 3: Everything is consistent
            elif not site_table_exists and not sites_migration_exists:
                print("✓ Sites tables don't exist yet - will be created by migrations")
                return True
            else:
                print("✓ Migration state is consistent")
                return True
                
    except Exception as e:
        print(f"✗ Error checking migration state: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_migration_inconsistency()
    sys.exit(0 if success else 1)
