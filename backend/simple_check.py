#!/usr/bin/env python3
"""
Simple check for primary keys
"""

import asyncio
from dotenv import load_dotenv
load_dotenv()

async def simple_check():
    from prisma import Prisma
    
    client = Prisma()
    await client.connect()
    
    print("🔍 Checking tables for primary keys...")
    
    # Simple query to see what tables exist and their structure
    tables = await client.execute_raw("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        ORDER BY table_name
        LIMIT 20;
    """)
    
    print("Tables found:")
    for table in tables:
        print(f"  - {table['table_name']}")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(simple_check())