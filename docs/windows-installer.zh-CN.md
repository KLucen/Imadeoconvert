# Windows 安装包构建与验收

本地继续使用 Anaconda `imadeo-p0`。Inno Setup 6.7.3 下载自官方仓库，校验固定
SHA-256 及 Pyrsys B.V. 的数字签名后，以官方 portable 模式提取到项目 `tools/`。
不创建新的 Python 环境，不注册编译器文件关联或修改系统 PATH。

```powershell
conda activate imadeo-p0
./scripts/setup_inno.ps1
python scripts/build_portable.py --output-dir dist/rc-build
python scripts/smoke_portable.py dist/rc-build/Imadeoconvert-1.18.0-rc.1-windows-x64.zip
python scripts/build_installer.py dist/rc-build/Imadeoconvert-1.18.0-rc.1-windows-x64.zip --output-dir dist/rc-build
python scripts/smoke_installer.py dist/rc-build/Imadeoconvert-1.18.0-rc.1-windows-x64-setup.exe
```

构建前提交所有源码，保证安装脚本与便携包使用同一提交。安装包脚本位于
`installer/Imadeoconvert.iss`，固定 AppId 用于后续原位升级；默认安装到
`%LOCALAPPDATA%\Programs\Imadeoconvert`，仅写当前用户的卸载登记，不要求提权。
卸载仅删除安装器跟踪的文件，不使用递归删除规则清空目录，不删除用户配置。

安装自检先确认当前用户没有既有 Imadeoconvert 安装，在 `test-results/installer/`
下新建带中文和空格的测试路径，静默安装、核对所有负载文件哈希、执行已安装 EXE
的媒体自检、卸载，最后核对卸载登记已移除且用户添加的文件和设置保持不变。
若已有安装，自检会停止；应在其他 Windows 用户或干净机器上执行。

`v1.18.0-rc.1` 是维护者明确要求公开的预览版。该标签记录在发行策略的
`preview_tags` 中，通过 `check_release.py --preview` 校验身份及已登记来源文件；
审查状态仍为 `pending`。稳定版本仍要求对应源码覆盖及审核完成，不将预览发布
解释为审查通过。GitHub 标签构建工作流执行回归、ZIP 自检和安装卸载自检后才
发布；重复运行保留已存在的同名资产。

官方参考：[Inno Setup 下载及签名](https://jrsoftware.org/isdl.php)、
[当前用户安装](https://jrsoftware.org/ishelp/topic_setup_privilegesrequired.htm)、
[安装命令行参数](https://jrsoftware.org/ishelp/topic_setupcmdline.htm)。
