"""
Test nano_banano import to find exact error location
"""
import sys
from pathlib import Path
import traceback

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("Testing nano_banano import step by step...\n")

try:
    print("1. Importing service module...")
    from services.nano_banano import service as nano_module
    print("✅ Success!")
except Exception as e:
    print(f"❌ Failed: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n2. Getting service class...")
    from services.nano_banano.service import NanoBananoService
    print("✅ Success!")
except Exception as e:
    print(f"❌ Failed: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n3. Creating service instance...")
    from core.plugins.core_api import CoreAPI
    core_api = CoreAPI("nano_banano")
    service = NanoBananoService(core_api)
    print("✅ Success!")
    print(f"   Service: {service.info.name}")
except Exception as e:
    print(f"❌ Failed: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All tests passed!")
