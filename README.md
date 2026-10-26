# radio_special_instruments

特殊乐器采样包库（CC0 等），含下载与乐器池生成脚本。

## 类型
数据目录（采样包库，含脚本）

## 目录要点
- CC0-Samples-List-master / SalamanderGrandPiano-master / VSCO-2-CE-master / world_percussion/：
  已解压的采样包 —— **本地保留，不入库**（3264 wav + 836 flac + 6 mp3）
- 同名 .zip：采样包压缩包 —— 不入库
- download_all.py：批量下载采样包
- generate_pool_yaml.py：扫描采样生成 instrument_pool.yaml（按乐器角色映射）
- sfx_to_pool.py：音效转乐器池
- instrument_pool.yaml / demo_special_album.yaml：乐器池配置与示例
- DOWNLOAD_GUIDE.html：下载说明
- demo_output/：示例输出（由工具生成，不入库）

## 用途
为专辑生成器/混音管线提供特殊乐器（钢琴、管弦、世界打击乐等）采样池。

## 仓库说明
- 本仓只入库**脚本 + 乐器池清单 + 说明**；采样包与音频（6.8 GB）属资源池，由 `.gitignore` 排除。
- 2026-10-26 由 `G:\assets\radio_special_instruments` 迁入 `G:\repos\radio_special_instruments`
  （合并同类项：G:\assets 整体是资源池，其中带脚本的项按 fonts / csmusic 的路子建仓归位）。
  同期修掉脚本里写死的旧址：
  - `download_all.py` 的 `ROOT`：`G:\music\radio_special_instruments` → **脚本自身所在目录**
  - `sfx_to_pool.py` 的 `POOL_DIR` / `POOL_YAML`：同上；`F:/Python314` 解释器路径 → `sys.executable`
  - `sfx_to_pool.py` 的外部输入 `SFX_OUTPUT`（原 `G:/tools/sfx/sounds/output`，该路径本机已不存在）
    → 改为**可用环境变量 `SFX_OUTPUT` 覆盖**

## 测试状态
3 个脚本通过 py_compile 语法检查（syntax_ok，含转义序列 SyntaxWarning，不影响运行）。
