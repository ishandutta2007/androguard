# Androguard

Androguard 5 is a thin Python app over Rust ecosystem libraries for Android APK analysis.

## Setup

```bash
# from repo root; Rust toolchain required for native extras
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1   # needed on Python 3.14+
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -e '.[full]'   # disasm + decompile + arm + patch
```

Optional extras: `androguard[disasm]`, `[decompile]`, `[arm]`, `[patch]`.

Local sibling crates (dex-parser, dex-decompiler, …) under `../` may be installed with `maturin develop --release` when hacking those libs; prefer `pip install -e '.[full]'` for normal use.

## Architecture

| Layer | Package | Role |
|-------|---------|------|
| Thin app | this repo (`androguard`) | CLI + `Application` façade |
| APK | `apkparser-ag` | ZIP, signatures, manifest hooks |
| DEX | `dexparser-ag` | Classes, methods, fields, strings |
| AXML / ARSC | `axml` | Manifest + resources |
| Disasm | `dex-bytecode` via `[disasm]` | Dalvik disassembly / CFG |
| Decompile | `dex-decompiler` via `[decompile]` | DEX → Java, findrefs, vulns, emulate |
| ARM | `arm_*` via `[arm]` | Native disasm / decompile |
| Patch | `apk-patch` via `[patch]` | Decode / rebuild project tree |

High-level API: `from androguard import Application`.

Do **not** restore the old monolithic Androguard 3/4 decompiler as the default path. Prefer ecosystem bindings.

## CLI cheatsheet

```bash
androguard -i app.apk
androguard -i app.apk --list-classes
androguard -i app.apk --list-methods

# disasm (androguard[disasm])
androguard -i app.apk --disasm --class 'MainActivity' --method 'onCreate'
androguard -i app.apk --disasm --class TestActivity --method onCreate --cfg

# decompile (androguard[decompile])
androguard -i app.apk --decompile-method 'pkg.Class#method'
androguard -i app.apk -d workspace/output/pkg/ --only-package pkg.name
androguard -i app.apk --getclass pkg.Class
androguard -i app.apk --findrefs string --findrefs-value password
androguard -i app.apk --scan-vulns
androguard -i app.apk --emulate 'pkg.Class#method'

# patch (androguard[patch])
androguard -i app.apk --decode-project
```

## Python API

```python
from androguard import Application

app = Application("app.apk")
print(app.apk.get_package(), app.apk.get_main_activity())
print(len(app.class_names), len(app.methods), len(app.strings))

for method in app.iter_methods(class_pattern=r"MainActivity", method_pattern=r"onCreate"):
    print(method.class_name, method.name)

# optional extras
app.decompile_apk_to_dir("workspace/output/pkg/", only_package="pkg.name")
print(app.findrefs("string", "api.example.com"))
print(app.scan_vulns()[:5])
```

Examples: `python -m examples.application_summary`, `examples.decompile`, `examples.run_all`.

## Workspace layout (analysis sessions)

```
workspace/
├── samples/     # input APKs
├── output/      # decompiled Java (per package)
└── reports/     # markdown analysis reports
```

Write reports to `workspace/reports/<package>-<YYYY-MM-DD>.md`.

## Tests

```bash
pytest tests/
# or focused:
pytest tests/test_examples.py tests/test_submodules.py
```

Decompiler quality work lives primarily in the sibling `dex-decompiler` repo (`cargo test --test decompiler_tests …`), not by reinventing Java emission in this Python package.

## Agent & skills

- Agent: `/agent androguard-analyst`
- Skills: `/analyze-apk`, `/decompile-apk`, `/find-refs`, `/scan-vulns`

## Rules

- Prefer `Application` + CLI over reinventing APK/DEX parsing in Python.
- Missing optional extras → clear install hint (`pip install -e '.[decompile]'`), do not silently fall back to broken stubs.
- Do not commit secrets, APK samples with PII, or large `workspace/output/` trees.
- Do not invent APIs; read `androguard/application.py` and `androguard/cli/main.py` when unsure.
- Authorized security analysis only; do not help with malware distribution or unauthorized access.
