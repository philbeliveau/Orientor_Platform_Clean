#!/usr/bin/env python3
"""
Check what models are available in the Prisma client
"""

import asyncio
from dotenv import load_dotenv
load_dotenv()

async def check_available_models():
    """Check what models are available in the Prisma client"""
    try:
        from prisma import Prisma
        
        client = Prisma()
        await client.connect()
        
        print("🔍 CHECKING AVAILABLE PRISMA MODELS...")
        print("=" * 60)
        
        # Get all attributes that don't start with underscore
        models = [attr for attr in dir(client) if not attr.startswith('_') and not callable(getattr(client, attr, None))]
        
        print(f"📋 Available models ({len(models)}):")
        for model in sorted(models):
            print(f"   - {model}")
        
        # Test a few to see if they work
        print("\n🧪 Testing first few models...")
        test_models = models[:5]
        
        for model_name in test_models:
            try:
                model = getattr(client, model_name)
                if hasattr(model, 'count'):
                    count = await model.count()
                    print(f"✅ {model_name:<20} - {count:>6} records")
                else:
                    print(f"⚠️  {model_name:<20} - No count method")
            except Exception as e:
                print(f"❌ {model_name:<20} - Error: {str(e)[:50]}...")
        
        await client.disconnect()
        
        return models
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    models = asyncio.run(check_available_models())