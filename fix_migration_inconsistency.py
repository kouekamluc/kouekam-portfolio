"""
Fix migration inconsistency where socialaccount migrations are applied 
out of order or before their dependencies.

This script checks migration history and fixes inconsistencies by:
1. Checking if any socialaccount migrations are marked as applied
2. Checking if sites.0001_initial is marked as applied
3. Fixing inconsistencies by either faking missing migrations or removing
   incorrectly ordered migration entries as appropriate.
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
                socialaccount_0001_exists = cursor.fetchone()[0]
                
                # Check if ANY socialaccount migrations are recorded
                cursor.execute("""
                    SELECT COUNT(*) FROM django_migrations 
                    WHERE app = 'socialaccount';
                """)
                socialaccount_migration_count = cursor.fetchone()[0]
                
                # Check if socialaccount_socialapp table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'socialaccount_socialapp'
                    );
                """)
                socialaccount_table_exists = cursor.fetchone()[0]
                
                # Check if migration 0004 is recorded
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM django_migrations 
                        WHERE app = 'socialaccount' 
                        AND name = '0004_app_provider_id_settings'
                    );
                """)
                socialaccount_0004_exists = cursor.fetchone()[0]
                
                # Check if provider_id column exists (added by migration 0004)
                provider_id_exists = False
                if socialaccount_table_exists:
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = 'socialaccount_socialapp'
                            AND column_name = 'provider_id'
                        );
                    """)
                    provider_id_exists = cursor.fetchone()[0]
                
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
                socialaccount_0001_exists = cursor.fetchone()[0] > 0
                
                # Check if ANY socialaccount migrations are recorded
                cursor.execute("""
                    SELECT COUNT(*) FROM django_migrations 
                    WHERE app = 'socialaccount';
                """)
                socialaccount_migration_count = cursor.fetchone()[0]
                
                # Check if socialaccount_socialapp table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='socialaccount_socialapp';
                """)
                socialaccount_table_exists = cursor.fetchone() is not None
                
                # Check if migration 0004 is recorded
                cursor.execute("""
                    SELECT COUNT(*) FROM django_migrations 
                    WHERE app = 'socialaccount' AND name = '0004_app_provider_id_settings';
                """)
                socialaccount_0004_exists = cursor.fetchone()[0] > 0
                
                # Check if provider_id column exists (added by migration 0004)
                provider_id_exists = False
                if socialaccount_table_exists:
                    cursor.execute("PRAGMA table_info(socialaccount_socialapp);")
                    columns = [row[1] for row in cursor.fetchall()]
                    provider_id_exists = 'provider_id' in columns
            else:
                print(f"Unsupported database engine: {db_engine}")
                return False
            
            print(f"Site table exists: {site_table_exists}")
            print(f"Sites migration recorded: {sites_migration_exists}")
            print(f"Socialaccount migrations recorded: {socialaccount_migration_count} (0001_initial: {socialaccount_0001_exists})")
            
            # Case 0: provider_id column exists but migration 0004 is not recorded
            # This happens when migration 0004 was partially applied
            if provider_id_exists and not socialaccount_0004_exists and socialaccount_table_exists:
                print("\n⚠️  Migration inconsistency detected!")
                print("   provider_id column exists but migration 0004 is not recorded.")
                print("   Fixing by faking migration 0004...")
                try:
                    call_command('migrate', 'socialaccount', '0004_app_provider_id_settings', '--fake', verbosity=1)
                    print("✓ Successfully faked socialaccount.0004_app_provider_id_settings migration")
                    return True
                except Exception as e:
                    print(f"✗ Error faking migration 0004: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            # Case 1: Socialaccount tables exist but no migrations are recorded
            # This happens when we removed migration entries but tables still exist
            if socialaccount_table_exists and socialaccount_migration_count == 0:
                print("\n⚠️  Migration inconsistency detected!")
                print("   Socialaccount tables exist but no migrations are recorded.")
                print("   Fixing by faking socialaccount migrations...")
                
                try:
                    # Fake the initial migration (and all subsequent ones will be handled by migrate)
                    call_command('migrate', 'socialaccount', '--fake-initial', verbosity=1)
                    print("✓ Successfully faked socialaccount migrations")
                    return True
                except Exception as e:
                    print(f"✗ Error faking socialaccount migrations: {e}")
                    print("   Will try to fake initial migration only...")
                    try:
                        call_command('migrate', 'socialaccount', '0001_initial', '--fake', verbosity=1)
                        print("✓ Successfully faked socialaccount.0001_initial migration")
                        return True
                    except Exception as e2:
                        print(f"✗ Error faking socialaccount.0001_initial: {e2}")
                        import traceback
                        traceback.print_exc()
                        return False
            
            # Case 2: Any socialaccount migrations are applied but socialaccount.0001_initial is not
            # This includes cases like 0002_token_max_lengths before 0001_initial
            elif socialaccount_migration_count > 0 and not socialaccount_0001_exists:
                print("\n⚠️  Migration inconsistency detected!")
                print(f"   {socialaccount_migration_count} socialaccount migration(s) are marked as applied,")
                print("   but socialaccount.0001_initial is not marked.")
                
                if socialaccount_table_exists:
                    # Tables exist, so we should fake the 0001_initial migration
                    print("   Socialaccount tables exist. Fixing by faking socialaccount.0001_initial migration...")
                    try:
                        call_command('migrate', 'socialaccount', '0001_initial', '--fake', verbosity=1)
                        print("✓ Successfully faked socialaccount.0001_initial migration")
                        return True
                    except Exception as e:
                        print(f"✗ Error faking socialaccount.0001_initial migration: {e}")
                        import traceback
                        traceback.print_exc()
                        return False
                else:
                    # Tables don't exist, so we can safely remove the migration entries
                    print("   Removing all socialaccount migration entries to fix dependency order...")
                    try:
                        with transaction.atomic():
                            # Remove ALL socialaccount migration entries
                            cursor.execute("""
                                DELETE FROM django_migrations 
                                WHERE app = 'socialaccount';
                            """)
                            deleted = cursor.rowcount
                            
                            if deleted > 0:
                                print(f"✓ Successfully removed {deleted} socialaccount migration entry/entries")
                                print("  (Migrations will run in correct order on next migrate)")
                                return True
                            else:
                                print("⚠ Warning: No socialaccount migration entries found")
                                return True
                    except Exception as e:
                        print(f"✗ Error removing socialaccount migration entries: {e}")
                        import traceback
                        traceback.print_exc()
                        return False
            
            # Case 3: socialaccount.0001_initial is applied but sites.0001_initial is not
            elif socialaccount_0001_exists and not sites_migration_exists:
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
                    
                    # Remove ALL socialaccount migration entries (in case there are later ones too)
                    try:
                        with transaction.atomic():
                            # Remove ALL socialaccount migration entries
                            cursor.execute("""
                                DELETE FROM django_migrations 
                                WHERE app = 'socialaccount';
                            """)
                            deleted = cursor.rowcount
                            
                            if deleted > 0:
                                print(f"✓ Successfully removed {deleted} socialaccount migration entry/entries")
                                print("  (Migrations will run in correct order on next migrate)")
                                return True
                            else:
                                print("⚠ Warning: No socialaccount migration entries found")
                                return True
                    except Exception as e:
                        print(f"✗ Error removing socialaccount migration entry: {e}")
                        import traceback
                        traceback.print_exc()
                        return False
            
            # Case 4: Sites tables exist but migration is not recorded
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
            
            # Case 5: Everything is consistent
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
