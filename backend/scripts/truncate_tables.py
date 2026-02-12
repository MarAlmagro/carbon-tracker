#!/usr/bin/env python3
"""
Truncate all data rows from database tables.

This script removes all rows from the application tables while preserving
the schema (indexes, policies, triggers, comments, etc.).

Tables are truncated in dependency order (children first) to avoid
foreign key constraint violations.

Usage:
    python -m backend.scripts.truncate_tables
"""

import os
import sys

# Tables in reverse dependency order (children before parents)
TABLES = [
    "activities",
    "emission_factors",
    "users",
]


def truncate_tables():
    """Truncate all rows from application tables."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

    try:
        from infrastructure.config.supabase import get_supabase_client

        client = get_supabase_client()

        for table_name in TABLES:
            # Delete all rows (Supabase client doesn't support TRUNCATE directly)
            # Using delete with a filter that matches all rows
            client.table(table_name).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print(f"  ✓ Truncated: {table_name}")

        print(f"\n✅ Truncated {len(TABLES)} tables")

    except ImportError as e:
        print(f"Import error: {e}")
        print("\nCannot connect to database.")
        print("Ensure SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY are set in backend/.env")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error truncating tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    truncate_tables()
