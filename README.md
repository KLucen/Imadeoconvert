# Imadeoconvert

**Windows 本地图片与视频批量转换工具。** 在同一个桌面窗口中转换图片、调整图片尺寸，或将视频导出为 MP4、MKV 和 WebM。媒体处理在本机完成，不上传源文件。

[![Tests](https://github.com/KLucen/Imadeoconvert/actions/workflows/test.yml/badge.svg)](https://github.com/KLucen/Imadeoconvert/actions/workflows/test.yml)
[![Windows](https://img.shields.io/badge/Windows-10%20%2F%2011%20x64-blue)](#运行与安装)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](environment.yml)
[![License](https://img.shields.io/badge/License-GPL--3.0--or--later-green)](LICENSE)

Imadeoconvert is a local desktop image and video converter for Windows, derived from [Formatix](https://github.com/cyber-anderson/Formatix). It adds batch video conversion, cancellation, media information and portable build verification to the original image workflow.

> **当前版本：1.18.0-dev。** 图片与视频功能、便携 ZIP 构建和产物自检已实现。公开二进制发行仍待第三方对应源码材料核对及干净 Windows 验收；当前不宣称已有正式安装包。源码、构建记录和后续发行均以 [本仓库](https://github.com/KLucen/Imadeoconvert) 为准。

## 功能

| 图片 | 视频 |
| --- | --- |
| 批量转换 AVIF、WebP、JPEG、HEIC、PNG、BMP、TIFF、ICO | 导出 MP4 / MKV（H.264 + AAC）和 WebM（VP9 + Opus） |
| 质量、目标文件大小、缩放与裁剪设置 | 画质与编码速度独立设置，最大高度 720p / 1080p 或保持原尺寸 |
| SVG 栅格化、ICC 色彩处理、多尺寸 ICO | 显示时长、分辨率、音视频编码及轨道信息 |
| 文件命名、拖放添加、转换前后图片对比 | 批量进度、速度、预计剩余时间、取消和失败重试 |
| 保留原有图片转换界面与浅色 / 深色主题 | 无音轨视频、移除音频、打开输出目录和系统播放器 |

视频逐个处理，转换在后台运行。默认保留已有输出，重名时添加数字后缀；先写临时文件，成功校验后才提交最终结果。取消或关闭程序时会等待当前子进程退出。视频引擎缺失时，图片模式仍可使用。

原图片界面支持六种语言；新增视频界面提供中文、英文，其余语言使用英文回退。主题切换在重启后生效。

## 运行与安装

主要目标平台为 **Windows 10/11 x64**。从源码运行需要 Python 3.10+；本地开发使用 Anaconda / Conda 环境 `imadeo-p0`，不需要 uv。其他操作系统尚未验收。

### 从源码运行

在 Anaconda Prompt 或已初始化 Conda 的 PowerShell 中执行：

```powershell
git clone https://github.com/KLucen/Imadeoconvert.git
cd Imadeoconvert
conda env create -f environment.yml
conda activate imadeo-p0
python scripts/setup_ffmpeg.py
python imadeo.py
```

如果已经创建过 `imadeo-p0`，直接激活并使用现有环境，不要重复创建。需要同步依赖时执行 `python -m pip install -r requirements-dev.txt`。

`setup_ffmpeg.py` 下载并校验 [引擎清单](tools/ffmpeg-manifest.json) 中固定版本的 FFmpeg / FFprobe，放入项目的 `tools/ffmpeg/`。首次安装依赖和引擎需要联网；转换过程无需联网。程序启动时不会自动下载引擎。

### Windows 便携 ZIP

维护者可按下文构建 ZIP；后续公开包会列在 [Releases](https://github.com/KLucen/Imadeoconvert/releases)。使用便携包时：

1. 完整解压 ZIP 到任意可读取目录。
2. 运行 `Imadeoconvert.exe`，保留旁边的 `_internal`、`tools`、`licenses` 等目录。
3. 选择输出目录后转换；输出目录需要写入权限。

便携包包含 Python 运行时和 FFmpeg / FFprobe，用户无需另装 Python。它是一个完整目录，不能只复制 EXE。当前构建未做代码签名。

## 使用方法

**图片：** 切换到“图片”，添加或拖入文件，选择输出格式、质量、尺寸与输出目录，开始转换。完成后可比较原图与结果。

**视频：** 切换到“视频”，等待引擎检测完成，添加或拖入视频。选择文件可查看媒体信息；设置格式、画质、速度、最大高度及是否移除音频后开始转换。任务失败时打开“详情”查看原因，再使用“重试失败 / 已取消”。双击已完成结果会调用系统播放器。

引擎检测失败时，选择同时包含 `ffmpeg.exe` 和 `ffprobe.exe` 的目录，再点击“重新检测”。源码运行可回退到 PATH 中的引擎；便携版默认只使用自身的捆绑引擎，也允许用户显式指定其他引擎目录。

### 格式支持与限制

| 类别 | 支持范围 |
| --- | --- |
| 图片输入 | JPEG、PNG、WebP、AVIF、HEIC / HEIF、SVG、BMP、TIFF、GIF、ICO |
| 图片输出 | AVIF、WebP、JPEG、HEIC、PNG、BMP、TIFF、ICO |
| 视频界面接受的扩展名 | `.mp4`、`.mov`、`.mkv`、`.avi`、`.webm`、`.m4v`、`.wmv`、`.flv`、`.ts`、`.mts`、`.m2ts` |
| 视频输出 | MP4、MKV、WebM；实际输入能否解码取决于文件内容和 FFmpeg 能力 |

视频当前支持普通 SDR 内容，输出为 8-bit `yuv420p`。HDR / Dolby Vision、透明视频及非 90° 倍数旋转会被拒绝。高位深 SDR 会转换为 8-bit；尺寸只缩小、不放大，并做编码器所需的偶数取整。

仅保留主视频和默认 / 第一条音轨；字幕、章节、附件、封面、额外音视频轨及全局元数据不会保留。暂不提供无损换封装、GPU 编码、HDR 转换、多音轨选择和视频目标文件大小模式。结果的播放能力取决于本机播放器。

### 视频命令行

```powershell
conda activate imadeo-p0
python scripts/convert_video.py "D:\videos\input.mov" --output-dir "D:\converted" --format mp4
python scripts/convert_video.py "D:\videos\a.mp4" "D:\videos\b.mkv" --output-dir "D:\converted" --format webm --quality balanced --speed fast --height 720 --mute
```

命令行输出 JSON 任务事件。Ctrl+C 取消当前批次；默认自动避开重名文件。完整参数和编码策略见 [命令行说明](docs/p1-conversion.zh-CN.md)。

## 设置与网络

设置保存在用户目录的 **`.imadeoconvert_settings.json`**，分为 `general`、`image` 和 `video` 三部分。首次使用新名称时，按以下顺序读取：

1. 新的 `.imadeoconvert_settings.json`。
2. 旧产品的 `.imadeocovert_settings.json`，包含图片和视频设置。
3. 更早的 `.formatix_image_converter_settings.json`，迁移图片和通用设置。

只有前一项不存在时才读取下一项；保存时写入新文件，旧文件保持不变。无效或更新版本的配置会保留并提示错误。关闭“记住设置”会清除磁盘中的图片与视频转换偏好，语言、主题、更新偏好和引擎目录仍保留。

媒体文件不会上传。默认启用的可选更新检查会访问本仓库的 GitHub Releases API；需要完全离线时，可在设置中关闭检查。没有可用 Release 或网络不可用时，更新检查正常返回，不影响转换。

## 开发、测试与打包

```powershell
conda activate imadeo-p0
python -m pip check
$env:IMADEO_REQUIRE_FFMPEG = '1'
python -m pytest -q

# 输出目录可自选；保留旧构建，不覆盖同名 ZIP。
python scripts/build_portable.py --output-dir dist/my-build
python scripts/smoke_portable.py dist/my-build/Imadeoconvert-1.18.0-dev-windows-x64.zip
```

构建使用 [Imadeoconvert.spec](Imadeoconvert.spec)。ZIP 附带 SHA-256、应用源码快照、第三方许可、构建身份和逐文件清单。自检从含中文、空格、括号的路径启动 EXE，清除 Conda/Python 环境变量，并限制 PATH；覆盖图片编码、MP4/MKV/WebM、无音轨输入和取消回收。这种本机隔离测试不能替代干净 Windows 实测。

CI 在 Windows 上运行 Python 3.10 / 3.12 回归。便携构建工作流支持手动执行；标签发布会先校验版本及 [第三方对应源码材料](tools/release-policy.json)，当前仍处于 `pending`。验证范围与剩余发行工作见 [P3 构建说明](docs/p3-portable.zh-CN.md) 和 [第三方许可说明](THIRD_PARTY_NOTICES.md)。

| 目录 / 模块 | 职责 |
| --- | --- |
| `imadeo.py` / `app_metadata.py` | 程序入口，产品名称、版本与仓库地址 |
| `formatix.py` / `converter.py` / `compare.py` | 原图片工作区、转换与对比 |
| `video_panel.py` / `video_session.py` | 视频界面和后台事件 |
| `ffmpeg_service.py` / `video_converter.py` / `task_runner.py` | 引擎发现、媒体探测、转码与批次调度 |
| `settings_store.py` / `file_utils.py` | 配置迁移、原子写入与输出保护 |
| `scripts/` / `tests/` | 命令行、引擎安装、构建及回归测试 |
| `docs/` | 开发方案、阶段记录及使用说明 |

## 项目来源与许可证

本项目基于 **[cyber-anderson/Formatix](https://github.com/cyber-anderson/Formatix)**，原作者为 **cyber-anderson（Copyright © 2026）**。在其图片转换功能上增加视频工作区、转换核心、测试和便携构建。原 fork 名称为 ImadeoCovert，现统一更名为 **Imadeoconvert**，保留原项目历史、版权和许可声明。

应用源码按 **GPL-3.0-or-later** 分发，详见 [LICENSE](LICENSE) 和源文件声明。FFmpeg、Python、Tk 及图片编解码库使用各自许可证，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)；不能将全部捆绑组件视为仅遵循应用许可证。
