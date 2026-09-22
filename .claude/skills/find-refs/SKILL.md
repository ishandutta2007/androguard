---
name: find-refs
description: Find string/type/method/field references in an APK via Androguard ASC findrefs
user_invocable: true
argument: "<apk_path> <kind> <needle>"
agent: androguard-analyst
---

# /find-refs — Cross-reference search

## Input

`$ARGUMENTS`:
1. APK path
2. Kind: `string` | `type` | `method` | `field`
3. Needle (substring / descriptor / name)

Examples:
- `app.apk string password`
- `app.apk type Landroid/app/Activity;`
- `app.apk method onCreate`
- `app.apk field API_KEY`

## CLI

```bash
androguard -i "$1" --findrefs "$2" --findrefs-value "$3"
```

## Python

```python
from androguard import Application
app = Application("app.apk")
print(app.findrefs("string", "https://"))
print(app.findrefs("type", "Lokhttp3/OkHttpClient;"))
```

## Follow-up

For each interesting hit:
1. `--getclass` or `--decompile-method` the declaring class/method
2. Note callers if the findrefs output includes them
3. Record evidence in `workspace/reports/`

If decompiler extra is missing, still try findrefs — it comes from the same `[decompile]` stack; install if needed.
