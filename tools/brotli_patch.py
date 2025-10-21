# tools/brotli_patch.py
# Make brotlicffi act as the 'brotli' package for libs that import 'brotli'
try:
    import brotlicffi as _brotli
    import sys
    sys.modules["brotli"] = _brotli
except Exception as e:
    print("⚠️ brotli fallback failed:", repr(e))
