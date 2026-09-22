---
name: decompile-apk
description: Decompile an APK (or one class/method) to Java with Androguard dex-decompiler bindings
user_invocable: true
argument: "<apk_path> [package_or_Class#method]"
agent: androguard-analyst
---

# /decompile-apk — Decompile with Androguard

## Input

`$ARGUMENTS`:
1. APK path (required)
2. Optional: Java package (`com.example.app`) **or** `Class#method` selector

## Ensure decompiler

```bash
python -c "from androguard.core.decompiler import ensure_loaded; ensure_loaded()"
```

On failure: `export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 && pip install -e '.[decompile]'`.

## Whole package → directory

```bash
PKG="${2:-}"   # package filter if provided
OUT="workspace/output/${PKG:-decompiled}"
mkdir -p "$OUT"
androguard -i "$1" -d "$OUT/" ${PKG:+--only-package "$PKG"}
```

## One class

```bash
androguard -i "$1" --getclass "$2"
```

## One method

```bash
androguard -i "$1" --decompile-method "$2"
# or write file:
androguard -i "$1" --decompile-method "$2" -o workspace/output/method.java
```

## Python

```python
from androguard import Application
app = Application("app.apk")
app.decompile_apk_to_dir("workspace/output/pkg/", only_package="com.example")
print(app.getclass("com.example.MainActivity")[:2000])
print(app.decompile_method_selector("com.example.MainActivity#onCreate"))
```

## Notes

- Prefer `--only-package` to avoid dumping entire AndroidX trees.
- Use `--exclude android.` / `androidx.` when decompiling broadly.
- Quality issues in Java emission are fixed in sibling `dex-decompiler`, not by pasting jadx output into this repo.
