# Harbor CLI on Windows CP936

## Reproduced behavior

On 2026-08-08, `harbor dataset init` from Harbor 0.20.0 was reproduced on a Chinese Windows environment whose output stream used CP936. The command wrote `dataset.toml`, then raised `UnicodeEncodeError` while printing the Unicode checkmark in its success message.

This matters because the filesystem mutation succeeds before the CLI reports failure. Re-running the command can therefore produce a confusing "already exists" state.

## Verified workaround

Set Python's output encoding to UTF-8 for the current PowerShell session:

```powershell
$env:PYTHONIOENCODING = "utf-8"
harbor dataset init org/name --output-dir path/to/dataset
```

The workaround was verified with Harbor 0.20.0: the command returned exit code 0 and created both `dataset.toml` and `README.md`.

To remove the session override:

```powershell
Remove-Item Env:PYTHONIOENCODING
```

## Upstream fix status

A minimal local Harbor patch replaces the six non-ASCII success markers in `src/harbor/cli/init.py` with ASCII text and adds a CP936-backed Rich console regression test. The focused upstream test file passes 46 tests on Python 3.12. The patch is prepared locally; this page does not claim that Harbor has accepted or released it.

See Harbor's official [getting started](https://www.harborframework.com/docs/getting-started) and [dataset](https://www.harborframework.com/docs/datasets) documentation for supported commands.
