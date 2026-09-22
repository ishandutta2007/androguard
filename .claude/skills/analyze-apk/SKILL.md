---
name: analyze-apk
description: Full static analysis of an Android APK with Androguard — metadata, decompile, findrefs, vulns, markdown report
user_invocable: true
argument: "<apk_path_or_package_hint>"
agent: androguard-analyst
---

# /analyze-apk — Androguard static analysis

## Input

`$ARGUMENTS` — path to an APK (preferred). If only a package name is given, look under `workspace/samples/` for a matching APK or ask for a path.

Set:
- `$APK` — APK path
- `$PKG` — package name from `androguard -i $APK` (or manifest)

## Phase 1 — Recon

```bash
androguard -i "$APK"
unzip -l "$APK" | head -80
unzip -l "$APK" | grep -E '\.so$|classes.*\.dex' | head -40
```

Record package, main activity, DEX count, permissions, signing notes, native libs.

## Phase 2 — Inventory

```bash
androguard -i "$APK" --list-classes | head -200
androguard -i "$APK" --list-methods | head -200
```

Identify the app’s own package prefix for `--only-package`.

## Phase 3 — Decompile (requires `[decompile]`)

```bash
mkdir -p "workspace/output/$PKG"
androguard -i "$APK" -d "workspace/output/$PKG/" --only-package "$PKG"
```

If decompiler missing: `pip install -e '.[decompile]'` (with `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` on 3.14+).

## Phase 4 — Search & vulns

```bash
androguard -i "$APK" --findrefs string --findrefs-value http
androguard -i "$APK" --findrefs string --findrefs-value api
androguard -i "$APK" --scan-vulns
```

Also search decompiled tree for secrets/URLs (`rg` / `grep` on `workspace/output/$PKG`).

## Phase 5 — Deep methods

For suspicious methods:

```bash
androguard -i "$APK" --decompile-method 'fully.qualified.Class#method'
androguard -i "$APK" --disasm --class 'ClassName' --method 'methodName'   # needs [disasm]
```

## Phase 6 — Report

Write `workspace/reports/$PKG-$(date +%Y-%m-%d).md` using the agent report template.

Every finding needs evidence (path or class#method) and impact — not a bare checklist.
