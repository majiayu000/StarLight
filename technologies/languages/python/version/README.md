# 在 Win11 把 `py` 默认版本切换到指定 Python（示例：设置为 3.10）

> 本文围绕 Windows 自带的 Python Launcher (`py.exe`)，解释为什么要这么做、每步的作用，以及如何同时管理 `pip` 指向的版本。

---

## 背景与问题来源
- 机器上有两个解释器：官方 3.14（已注册）、uv 下载的 CPython 3.10.19（未注册）。
- `py -V` 早先报 “No suitable Python runtime found”，原因：uv 3.10 未写入注册表，`py.ini` 也未指定默认，launcher 找不到可用默认版本。

## 步骤与动机
1) **枚举现有 Python：** `py -0p`
   - 理由：确认有哪些解释器、标签和路径，避免指向不存在的版本。
2) **验证目标解释器能跑：** `& "...cpython-3.10...\python.exe" -V`
   - 理由：先验证本体可用，再让 launcher 接管。
3) **让 launcher 认识 3.10（写注册表）：**
   ```powershell
   $path = "C:\Users\<你>\AppData\Roaming\uv\python\cpython-3.10.x-windows-x86_64-none"
   New-Item -Path "HKCU:\Software\Python\PythonCore\3.10\InstallPath" -Force | Out-Null
   Set-ItemProperty -Path "HKCU:\Software\Python\PythonCore\3.10\InstallPath" -Name "(default)" -Value $path
   Set-ItemProperty -Path "HKCU:\Software\Python\PythonCore\3.10\InstallPath" -Name "ExecutablePath" -Value "$path\python.exe"
   ```
   - 理由：`py` 发现版本依赖注册表/`py.ini`。未注册的解释器会被忽略，必须登记后才能被 `py -0`/`py -3.10` 识别。
4) **设定默认优先版本（py.ini）：** `%LOCALAPPDATA%\py.ini`
   ```ini
   [defaults]
   python=3.10
   ```
   - 理由：指定首选版本，避免 launcher 继续尝试不存在的默认而报错。
5) **验证：**
   ```powershell
   py -0      # 看到 -V:3.10 * 说明已设为默认
   py -V      # 输出 Python 3.10.x
   py -3.14 -V
   ```
   - 理由：确认“已被识别 + 已设默认”两件事都成立。

## `pip` 指向与切换（现在的状态）
- 目前 `py -m pip --version` → `pip 25.3 ...python 3.10`（走默认 3.10）。
- `py -3.14 -m pip --version` → `pip 25.2 ...python 3.14`。
- 直接敲 `pip --version` → `pip 25.2 ...python 3.14`，路径在 `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\Lib\site-packages\pip`。
- 原因：`pip` 命令解析自 PATH，当前 PATH 里先命中了 3.14 的 `pip.exe`；uv 的 3.10 没有在 PATH 里提供可执行的 `pip.exe`（`Scripts` 目录不存在），所以默认 pip 仍落在 3.14。

### 想让 pip 跟 3.10 走，有两个做法
1) **最稳妥：始终显式用 launcher 调 pip**（避免 PATH 混淆）
   - 安装：`py -3.10 -m pip install <包>`
   - 升级 pip：`py -3.10 -m pip install --upgrade pip`
   - 作用：明确指定解释器，避免“pip 装到了错误版本”的常见坑。
2) **改 PATH 让 `pip` 落到 3.10**（如果你确实需要裸 `pip` 命令）
   - 前提：先为 uv 3.10 生成 `Scripts\pip.exe`（可通过上面的升级 pip 自动生成）。
   - 把 `C:\Users\Administrator\AppData\Roaming\uv\python\cpython-3.10.19-windows-x86_64-none\Scripts` 提前到 PATH，并确保它在 3.14 的 `Scripts` 之前。
   - 理由：PATH 决定裸 `pip` 命令去哪；调整后 `pip` 会指向 3.10。

### 立即可用的校验命令
```powershell
py -m pip --version      # 应看到 python 3.10 路径
py -3.14 -m pip --version
pip --version            # 目前仍指向 3.14，若改 PATH 后应刷新终端再看
```

## 之后想切换默认版本的思路
- 换回 3.14：`py.ini` 写 `python=3.14`；如 3.10 路径无效也要同步清理注册表项。
- 移动/删除 3.10：更新或删除 `HKCU\Software\Python\PythonCore\3.10\InstallPath`，避免 launcher 指向失效路径。
- 特定架构/子版本：可用 `python=3.10-32` 或自定义 tag（如 `V:...`）；但用大版本号即可覆盖常见需求。
