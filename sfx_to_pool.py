#!/usr/bin/env python3
"""sfx下载器产出的音频 → 追加到 special_instruments 采样池"""
from pathlib import Path
import os
import shutil
import sys

ROOT = Path(__file__).resolve().parent
# 外部输入目录（sfx 下载器的产出）。本机该路径当前不存在，可用环境变量 SFX_OUTPUT 覆盖。
SFX_OUTPUT = Path(os.environ.get("SFX_OUTPUT", r"G:/tools/sfx/sounds/output"))
# 2026-10-26 迁入 G:\repos\radio_special_instruments 后改为脚本相对路径（旧址 G:\music\... 已不存在）
POOL_DIR = ROOT / "sfx_downloads"
POOL_YAML = ROOT / "instrument_pool.yaml"

CATEGORY_ROLE = {
    "sfx": "fx",
    "music": "melody",
    "audiobook": "pad",
    "field": "pad",
}

def main():
    if not SFX_OUTPUT.exists():
        print(f"❌ sfx 输出目录不存在: {SFX_OUTPUT}")
        print(f"   请先运行 sfx 下载工具，或用环境变量 SFX_OUTPUT 指定其产出目录")
        return

    POOL_DIR.mkdir(parents=True, exist_ok=True)
    new_count = 0

    for audio_file in SFX_OUTPUT.rglob("*"):
        if not audio_file.is_file():
            continue
        suffix = audio_file.suffix.lower()
        if suffix not in (".wav", ".mp3", ".ogg", ".flac"):
            continue

        # 按分类组织
        rel = audio_file.relative_to(SFX_OUTPUT)
        category = rel.parts[0] if len(rel.parts) > 0 else "sfx"
        dst_dir = POOL_DIR / category
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / audio_file.name

        if not dst.exists():
            shutil.copy2(audio_file, dst)
            new_count += 1

    print(f"✅ 已同步 {new_count} 个新文件到 {POOL_DIR}/")

    # 更新 YAML（追加新乐器）
    if new_count > 0:
        import subprocess
        subprocess.run([
            sys.executable,
            str(ROOT / "generate_pool_yaml.py"),
        ])
        print(f"📋 instrument_pool.yaml 已更新")

if __name__ == "__main__":
    main()
