#!/usr/bin/env python3
"""
批量下载免费公版采样资源 → 本脚本所在目录
=========================================================
- CC0 / Public Domain 优先
- 自动跳过已存在文件
- 国内网络优化（gitee 镜像 + 直连 fallback）

用法:
    python download_all.py
"""

import os
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

# 2026-10-26 迁入 G:\repos\radio_special_instruments 后改为「脚本自身所在目录」，
# 不再写死旧址 G:\music\...（该目录已不存在）
ROOT = Path(__file__).resolve().parent

# ═══════════════════════════════════════════════════════════
# 资源清单: (名称, 下载方式, URL, 二级目录)
# ═══════════════════════════════════════════════════════════

RESOURCES = [
    # ── 民族打击乐（CC0）──
    {
        "name": "World Percussion (FreePats)",
        "method": "git_safe",
        "urls": [
            "https://gitee.com/mirrors/freepats-world-percussion.git",
            "https://github.com/freepats/world-percussion.git",
        ],
        "subdir": "world_percussion",
        "notes": "bongo/conga/darbuka/cajon/castanets/maracas — CC0",
    },
    # ── CC0 综合乐器库（索引+指向的子资源）──
    {
        "name": "CC0 Samples Index",
        "method": "git_safe",
        "urls": [
            "https://github.com/LoveBodhi/CC0-Samples-List.git",
        ],
        "subdir": "cc0_samples_index",
        "notes": "索引列表（指向 Salamander Piano/VCSL/VSCO-2 等 CC0 资源）",
    },
    # ── Vini CC0 合成器振荡器 ──
    {
        "name": "Vini 128 CC0 Synth Oscillators",
        "method": "download",
        "urls": [
            "https://musical-artifacts.com/artifacts/3759/download",
        ],
        "subdir": "synth_osc",
        "filename": "128_cc0_osc.sf2",
        "notes": "128 CC0 复古振荡器 SF2 格式",
    },
    {
        "name": "Vini Module'87 CC0",
        "method": "download",
        "urls": [
            "https://musical-artifacts.com/artifacts/3760/download",
        ],
        "subdir": "synth_osc",
        "filename": "module87.sf2",
        "notes": "42 复古 lo-fi 乐器采样",
    },
    # ── 电子纹理 ──
    {
        "name": "99Sounds Glitch Textures",
        "method": "download",
        "urls": [
            "https://99sounds.org/wp-content/uploads/2024/03/99Sounds-Glitch-Textures.zip",
        ],
        "subdir": "glitch_textures",
        "filename": "glitch_textures.zip",
        "notes": "25 个 24bit/192kHz WAV（电磁场/数字故障）",
    },
    # ── 环境氛围 ──
    {
        "name": "Ghosthack Free Ambient Pads",
        "method": "download",
        "urls": [
            "https://www.ghosthack.de/wp-content/uploads/freebies/chillout-ambient/Ghosthack-Free-Ambient-Pads.zip",
        ],
        "subdir": "ambient_pads",
        "filename": "ambient_pads.zip",
        "notes": "电影级铺底/氛围/纹理",
    },
]


def git_clone_safe(name, urls, target_dir):
    """尝试多个 git URL，第一个成功的为准"""
    if target_dir.exists() and list(target_dir.glob("*")):
        print(f"  ⏭️  已有内容，跳过")
        return True

    for url in urls:
        print(f"  🔄 尝试: {url}")
        result = subprocess.run(
            ["git", "clone", "--depth=1", url, str(target_dir)],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            print(f"  ✅ 成功")
            return True
        print(f"  ⚠️ 失败: {result.stderr.strip()[-60:]}")
    return False


def download_file(url, target_path):
    """下载单个文件，跳过已有"""
    if target_path.exists() and target_path.stat().st_size > 1000:
        print(f"  ⏭️  已有 {target_path.stat().st_size//1024}KB，跳过")
        return True

    try:
        print(f"  🔄 下载中...")
        urllib.request.urlretrieve(url, target_path)
        size_kb = target_path.stat().st_size // 1024
        print(f"  ✅ {size_kb}KB")
        return True
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")
        return False


def unzip_if_needed(zip_path, target_dir):
    """解压 ZIP 到目标目录"""
    if not zip_path.exists():
        return
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # 检查是否已有 wav 文件
            existing = list(target_dir.glob("*.wav"))
            if existing:
                print(f"  ⏭️  已解压 ({len(existing)} 个 wav)")
                return
            zf.extractall(target_dir)
            wavs = list(target_dir.rglob("*.wav"))
            print(f"  ✅ 解压 {len(wavs)} 个 wav")
    except zipfile.BadZipFile:
        print(f"  ⚠️ 非有效 ZIP（可能是登录页面）")
    except Exception as e:
        print(f"  ⚠️ 解压失败: {e}")


def main():
    print("=" * 60)
    print("🎵 批量下载免费公版采样资源")
    print("=" * 60)
    ROOT.mkdir(parents=True, exist_ok=True)

    ok = 0
    fail = 0

    for res in RESOURCES:
        name = res["name"]
        subdir = res["subdir"]
        target_dir = ROOT / subdir
        target_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📦 {name}")
        print(f"   📁 {target_dir}")

        success = False
        if res["method"] == "git_safe":
            success = git_clone_safe(name, res["urls"], target_dir)
        elif res["method"] == "download":
            fn = res.get("filename", f"{subdir}.zip")
            target_path = target_dir / fn
            for url in res["urls"]:
                success = download_file(url, target_path)
                if success:
                    # try unzip
                    unzip_if_needed(target_path, target_dir)
                    break

        if success:
            ok += 1
        else:
            fail += 1
            print(f"  ❌ 所有源均不可达")

    # 生成索引
    print(f"\n{'='*60}")
    print(f"✅ 完成: {ok} 成功 / {fail} 失败")
    write_index()
    print(f"{'='*60}")


def write_index():
    """生成 README + instrument pool YAML 片段"""
    lines = []
    for res in RESOURCES:
        subdir = ROOT / res["subdir"]
        status = "✅" if subdir.exists() and list(subdir.iterdir()) else "❌"
        lines.append(f"{status} **{res['name']}**")
        lines.append(f"   {res['notes']}")
        lines.append(f"   路径: `{res['subdir']}/`")
        lines.append("")

    readme = ROOT / "README.md"
    readme.write_text("\n".join([
        "# 特殊乐器采样库",
        f"自动下载时间: {__import__('datetime').datetime.now().isoformat()}",
        "",
        "## 资源状态",
        *lines,
        "## 使用方式",
        "```yaml",
        '# 在 album_maker YAML 中引用:',
        'instruments:',
        '  - name: 民族手鼓',
        '    role: drum',
        '    engine: sampler',
        '    sample_path: G:/music/radio_special_instruments/world_percussion/samples/darbuka_tak.wav',
        '    volume: 0.8',
        '```',
    ]), encoding="utf-8")


if __name__ == "__main__":
    main()
