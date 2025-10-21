# cli.py

from tools.env_bootstrap import *  

import argparse, sys, traceback
from pathlib import Path

print("CLI: loaded", flush=True)

try:
    from app import app
    print("CLI: imported app", flush=True)
except Exception:
    print("CLI: no app; using dummy", flush=True)
    class DummyApp:
        def invoke(self, state): 
            q = state.get("question") or state.get("prompt") or "(no question)"
            return {"draft": f"# Draft\n\nYou asked: {q}\n\n(DummyApp fallback)"}
    app = DummyApp()

def main():
    p = argparse.ArgumentParser(description="Deep Research CLI")
    p.add_argument("prompt")
    p.add_argument("--depth", choices=["shallow","standard","deep"], default="standard")
    p.add_argument("--out", default="out/draft.md")
    args = p.parse_args()

    print(f"CLI: prompt='{args.prompt}' depth={args.depth}", flush=True)
    print("CLI: invoking app…", flush=True)
    final = app.invoke({"question": args.prompt, "depth": args.depth})
    print(f"CLI: got keys -> {list((final or {}).keys())}", flush=True)

    content = (final or {}).get("draft") or "# Empty draft\n"
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(f"✅ Saved {out.resolve()}", flush=True)

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        print("❌ Unhandled error:", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
