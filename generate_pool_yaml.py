#!/usr/bin/env python3
"""扫描特殊乐器采样 → 生成 album_maker instrument_pool YAML"""
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent

# 乐器名→角色映射（支持子串匹配）
ROLE_MAP = [
    (["violin", "viola", "cello", "contrabass", "harp", "flute", "clarinet", "oboe", "bassoon",
      "trumpet", "f horn", "french horn", "sax", "piccolo", "solo"], "melody"),
    (["cello section", "viola section", "violin section", "trombone", "tuba",
      "contrabass section", "bass section", "string"], "bass"),
    (["piano", "organ", "upright", "celesta", "glock", "marimba", "xylo", "vibra", "bell", "gong"], "chord"),
    (["timpani", "snare", "bass drum", "cymb", "triangle", "tambourine", "perc",
      "bongo", "conga", "cajon", "darbuka", "maraca", "castanet", "shaker", "clap", "clave",
      "old snare"], "drum"),
    (["choir", "chorus", "voice", "vocal", "pad", "atmos", "texture", "drone"], "pad"),
    (["fx", "effect", "glitch", "noise", "misc", "sound effect"], "fx"),
    # Brass: melody or bass depending on range
    (["horn", "brass"], "melody"),
]

def assign_role(name_lower: str) -> str:
    for patterns, role in ROLE_MAP:
        for pat in patterns:
            if pat in name_lower:
                return role
    return "chord"

def collect_wavs(root: Path):
    """收集所有 WAV 并按乐器归类"""
    instruments = {}
    for wav in sorted(root.rglob("*.wav")):
        rel = wav.relative_to(root)
        parts = rel.parts

        # VSCO-2: .../InstrumentFamily/InstrumentName/Articulation/wav.wav
        # 取倒数第3个（乐器名），跳过纯数字和技法名
        if len(parts) >= 2:
            inst_name = parts[-2]  # 先取上一级
            # 如果上一级像技法名（短小），再往上一级
            if len(inst_name) <= 6 or inst_name[0].isdigit():
                if len(parts) >= 3:
                    inst_name = parts[-3]
        elif len(parts) >= 1:
            inst_name = parts[-1]
        else:
            inst_name = "unknown"

        inst_name = inst_name.replace("_", " ").strip()
        if inst_name not in instruments:
            instruments[inst_name] = []
        instruments[inst_name].append(wav)

    return instruments

def generate_yaml(instruments: dict, pool_name: str) -> str:
    lines = [
        f"# 自动生成: {datetime.now().isoformat()}",
        f"# 来源: G:\music\radio_special_instruments",
        f"name: {pool_name}",
        f"bpm: 120",
        f"key: C",
        f"scale: major",
        f"global_volume: 0.85",
        f"generation:",
        f"  diversity: 0.5",
        f"  humanize: true",
        f"  seed: 42",
        f"  chord_progression: dreamy",
        f"instruments:",
    ]

    for inst_name, wavs in sorted(instruments.items()):
        if not wavs:
            continue
        # 取第一个 WAV 作为代表
        wav = wavs[0]
        name_lower = inst_name.lower()
        role = assign_role(name_lower)

        lines.append(f"  - name: {inst_name}")
        lines.append(f"    role: {role}")
        lines.append(f"    engine: sampler")
        lines.append(f"    sample_path: {wav.as_posix()}")
        lines.append(f"    volume: 0.75")
        lines.append(f"    pan: 0.0")
        lines.append(f"    # {len(wavs)} samples in '{inst_name}'")

    return "\n".join(lines)

def main():
    # 扫描两个目录
    all_instruments = {}

    for src_dir in ["world_percussion", "VSCO-2-CE-master"]:
        src = ROOT / src_dir
        if src.exists():
            insts = collect_wavs(src)
            all_instruments.update(insts)

    if not all_instruments:
        print("❌ 未找到 WAV 文件")
        return

    # 生成
    yaml = generate_yaml(all_instruments, "Special Instruments Pool")
    out = ROOT / "instrument_pool.yaml"
    out.write_text(yaml, encoding="utf-8")
    print(f"✅ {out}  — {len(all_instruments)} 乐器, {sum(len(v) for v in all_instruments.values())} 采样")

    # 统计
    for role in ["melody", "chord", "bass", "drum", "pad", "fx"]:
        count = sum(1 for n in all_instruments if assign_role(n.lower()) == role)
        print(f"   {role}: {count} 乐器")

    print(f"\n📋 使用方式：")
    print(f"   复制 instrument_pool 段到你的 album YAML 中")

if __name__ == "__main__":
    main()
