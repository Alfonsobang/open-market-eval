# Harbor CLI 在中文 Windows CP936 环境下的编码问题

## 已复现现象

2026-08-08，我们在输出流使用 CP936 的中文 Windows 环境中复现了 Harbor 0.20.0 的 `harbor dataset init` 编码问题：命令已经写入 `dataset.toml`，随后在打印成功提示中的 Unicode 对勾时抛出 `UnicodeEncodeError`。

这个问题容易误导使用者，因为文件系统改动已经成功，CLI 却显示失败；此时直接重跑命令又会遇到“文件已存在”。

## 已验证的临时方案

在当前 PowerShell 会话中把 Python 输出编码设为 UTF-8：

```powershell
$env:PYTHONIOENCODING = "utf-8"
harbor dataset init org/name --output-dir path/to/dataset
```

该方案已在 Harbor 0.20.0 上验证：命令退出码为 0，并成功生成 `dataset.toml` 与 `README.md`。

使用结束后可以移除会话级设置：

```powershell
Remove-Item Env:PYTHONIOENCODING
```

## 上游修复状态

本地已经准备了一个最小 Harbor 补丁：将 `src/harbor/cli/init.py` 中六处非 ASCII 成功标记改为 ASCII 文本，并增加绑定 CP936 输出流的 Rich console 回归测试。该补丁在 Python 3.12 下通过了上游 `test_init.py` 的 46 项测试。目前补丁仍处于本地准备状态，本文不声称 Harbor 已接受或发布此修复。

支持的标准命令请参考 Harbor 官方的[快速开始](https://www.harborframework.com/docs/getting-started)与[数据集文档](https://www.harborframework.com/docs/datasets)。
