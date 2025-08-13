#!/usr/bin/env python3
"""
Check which tables have primary keys and which need them
"""

import asyncio
from dotenv import load_dotenv
load_dotenv()

async def check_primary_keys():
    """Check primary key status of all tables"""
    try:
        from prisma import Prisma
        
        client = Prisma()
        await client.connect()
        
        print("🔍 Checking Primary Key Status for All Tables...")
        print("=" * 60)
        
        # Get all tables first
        all_tables_result = await client.execute_raw("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                AND table_name NOT LIKE 'pg_%'
                AND table_name != 'alembic_version'
            ORDER BY table_name;
        """)
        
        # Get tables with primary keys
        pk_tables_result = await client.execute_raw("""
            SELECT DISTINCT t.table_name,
                   string_agg(kcu.column_name, ', ') as primary_key_columns
            FROM information_schema.tables t
            JOIN information_schema.table_constraints tc 
                ON t.table_name = tc.table_name 
                AND tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_schema = 'public'
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE t.table_schema = 'public' 
                AND t.table_type = 'BASE TABLE'
            GROUP BY t.table_name
            ORDER BY t.table_name;
        """)
        
        # Convert to sets for easy comparison
        all_tables = {row['table_name'] for row in all_tables_result}
        pk_tables_info = {row['table_name']: row['primary_key_columns'] for row in pk_tables_result}
        
        result = []
        for table in sorted(all_tables):
            if table in pk_tables_info:
                result.append({
                    'table_name': table,
                    'status': '✅ HAS PK',
                    'primary_key_columns': pk_tables_info[table]
                })
            else:
                result.append({
                    'table_name': table,
                    'status': '❌ NO PK',
                    'primary_key_columns': 'None'
                })
        
        tables_with_pk = []
        tables_without_pk = []
        
        for row in result:
            table_name = row['table_name']
            status = row['status']
            pk_columns = row['primary_key_columns'] or 'None'
            
            print(f"{status:<10} {table_name:<30} PK: {pk_columns}")
            
            if '✅' in status:
                tables_with_pk.append(table_name)
            else:
                tables_without_pk.append(table_name)
        
        print("\n" + "=" * 60)
        print(f"📊 SUMMARY:")
        print(f"✅ Tables WITH primary keys: {len(tables_with_pk)}")
        print(f"❌ Tables WITHOUT primary keys: {len(tables_without_pk)}")
        
        if tables_without_pk:
            print(f"\n🔧 Tables needing primary keys:")
            for table in tables_without_pk:
                print(f"   - {table}")
                
        await client.disconnect()
        
        return tables_without_pk
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    missing_pk_tables = asyncio.run(check_primary_keys())