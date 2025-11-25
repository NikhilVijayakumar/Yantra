# Virtual Environment Usage for Yantra Development

## Issue
Installation was happening to user-level packages instead of virtual environment.

## Solution

### Always Activate Virtual Environment First

**PowerShell:**
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Verify activation (should show venv path)
$env:VIRTUAL_ENV

# Now install/run commands
pip install -e .
python -m nikhil.yantra --help
```

**Bash/Linux:**
```bash
# Activate venv
source venv/bin/activate

# Verify
echo $VIRTUAL_ENV

# Install/run
pip install -e .
python -m nikhil.yantra --help
```

### How to Tell If Virtual Environment is Active

**PowerShell:**
```powershell
if (Test-Path env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual env active: $env:VIRTUAL_ENV"
} else {
    Write-Host "❌ No virtual environment active"
}
```

**Prompt Indicator:**
```
(venv) $ ~/PycharmProjects/Yantra>  # ✅ Active (note the (venv) prefix)
$ ~/PycharmProjects/Yantra>         # ❌ Not active
```

### Installation Path Check

**User-level (Wrong for dev):**
```
c:\users\nikhi\appdata\roaming\python\python312\site-packages
```

**Virtual environment (Correct):**
```
/path/to/Yantra/venv/lib/site-packages
```

## Workflow for Development

### 1. One-Time Setup
```powershell
# Create venv (if not exists)
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Install in editable mode
pip install -e .
```

### 2. Daily Workflow
```powershell
# Always activate first
.\venv\Scripts\Activate.ps1

# Then work normally
python scripts/something.py
python -m nikhil.yantra
pytest
git commit
```

### 3. Deactivate When Done
```powershell
deactivate
```

## VS Code Integration

### Auto-Activate in VS Code

1.  **Select Python Interpreter:**
    -   `Ctrl+Shift+P` → "Python: Select Interpreter"
    -   Choose `.\venv\Scripts\python.exe`

2.  **VS Code will auto-activate venv in terminals**

3.  **Verify in new terminal:**
    ```bash
    # Should see (venv) prefix
    (venv) $ ~/PycharmProjects/Yantra>
    ```

## Pre-commit Hooks

Pre-commit hooks use the active environment:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
       - id: code-quality
        name: Code Quality Check
        entry: python -m nikhil.yantra  # Uses venv's yantra
        language: system
```

**Important:** Run `pre-commit install` from activated venv:
```powershell
.\venv\Scripts\Activate.ps1
pre-commit install
```

## Common Issues

### Issue: "yantra module not found"
**Cause:** Not in venv or not installed
**Solution:**
```bash
source venv/bin/activate
pip install -e .
python -m nikhil.yantra --version
```

### Issue: "Installing to user packages"
**Cause:** Venv not activated
**Solution:**
```powershell
# Check
$env:VIRTUAL_ENV

# If empty, activate
.\venv\Scripts\Activate.ps1
```

### Issue: "Module not found"
**Cause:** Installed in user packages, running in venv
**Solution:**
```bash
# Reinstall in venv
source venv/bin/activate
pip uninstall yantra
pip install -e .
```

## Best Practices

✅ **Always activate venv before:**
- Installing packages
- Running scripts
- Running commands
- Installing pre-commit

✅ **Add to .gitignore:**
```
venv/
.venv/
*.pyc
__pycache__/
```

✅ **Document in README:**
```markdown
## Development Setup

1. Create virtual environment:
   ```
   python -m venv venv
   ```

2. Activate:
   ```
   .\venv\Scripts\Activate.ps1  # Windows
   source venv/bin/activate     # Linux/Mac
   ```

3. Install:
   ```
   pip install -e .
   ```
```

## PowerShell Profile (Optional)

Add to PowerShell profile for quick activation:

```powershell
# Edit profile
notepad $PROFILE

# Add function
function venv {
    if (Test-Path .\venv\Scripts\Activate.ps1) {
        .\venv\Scripts\Activate.ps1
        Write-Host "✅ Virtual environment activated"
    } else {
        Write-Host "❌ No venv found in current directory"
    }
}

# Save and reload
. $PROFILE

# Now just type 'venv' to activate
```

## Summary

**Problem:** Installed to user packages instead of venv  
**Solution:** Always activate venv first: `source venv/bin/activate`  
**Verification Path:** `/path/to/Yantra/venv/lib/site-packages` ✅  
**Command now works:** `python -m nikhil.yantra --version` ✅
