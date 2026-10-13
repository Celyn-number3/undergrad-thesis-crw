# MH Agent Skills 解密指南

## 概述

MH Agent 的 skills 文件使用 **AES-256-GCM** 加密存储在 `.enc` 文件中。本文档记录完整的解密流程和技术细节。

## 加密架构

### 模块职责

| 模块 | 文件 | 职责 |
|------|------|------|
| `license_guard` | `services/license_guard.cp311-win_amd64.pyd` | 许可证验证、Derived Key 管理 |
| `skill_crypto` | `services/skill_crypto.cp311-win_amd64.pyd` | Skills 文件加密/解密、密钥派生 |

### 密钥层次

```
license_key (用户激活码)
     │
     ▼
master_key (硬编码在 .pyd 中)
     │
     ▼ _derive_key(master_key)
AES-256 密钥 (32 bytes)
     │
     ├── encrypt_file() / decrypt_file()  ← 文件加解密
     ├── encrypt_bytes() / decrypt_bytes() ← 内存加解密
     ├── encrypt_dk_for_transport()        ← DK 传输加密
     └── decrypt_dk_from_transport()       ← DK 传输解密
```

## 加密算法详情

### 文件加密格式

```
┌────────────┬──────────────────────────┐
│ nonce      │ ciphertext + tag         │
│ 12 bytes   │ variable length          │
└────────────┴──────────────────────────┘
```

| 参数 | 值 |
|------|-----|
| 算法 | AES-256-GCM |
| Nonce | 12 bytes（随机生成，存储在文件头） |
| Tag | 16 bytes（GCM 认证标签，附加在密文末尾） |
| Salt 前缀 | `b'mhagent-skill-enc-v2'` |
| 加密扩展名 | `.md`, `.json`, `.yaml`, `.js`, `.bib`, `.yml`, `.txt`, `.css`, `.html`, `.sh`, `.tex`, `.py` |
| 跳过目录 | `.git`, `__pycache__`, `node_modules` |

### 密钥派生

```python
# skill_crypto._derive_key 签名
_derive_key(master_key: str) -> bytes  # 返回 32 字节 AES-256 密钥
```

密钥派生使用 `_SALT_PREFIX`（`b'mhagent-skill-enc-v2'`）作为 salt，结合 `master_key` 字符串，通过 PBKDF2 或类似 KDF 派生出 32 字节 AES 密钥。

## 解密流程

### 前置条件

- Python 3.11（`.pyd` 编译目标版本）
- `cryptography` 包（项目 `requirements.txt` 已包含）
- 有效的 `license.json`（包含 `license_key`、`machine_id`、`sig`）

### 步骤

#### 1. 导入模块并验证许可证

```python
import sys
sys.path.insert(0, 'services')
sys.path.insert(0, '.')

import license_guard
import skill_crypto

# check_license_local(True) 有两个作用：
#   1. 验证本地 license.json 中的 sig 签名
#   2. 验证通过后自动调用 _apply_dk() 设置解密密钥
is_valid = license_guard.check_license_local(True)
```

密钥会缓存在 `skill_crypto._cached_decrypt_key` 中，后续解密操作自动使用。

#### 2. 解密单个文件

```python
from pathlib import Path

key = skill_crypto.get_decrypt_key()  # 获取 32 字节 AES 密钥

enc_file = Path('skills/ablation-planner/SKILL.md.enc')
decrypted = skill_crypto.decrypt_file(enc_file, key)

# decrypted 是 bytes，解码为 UTF-8（带 BOM）
text = decrypted.decode('utf-8-sig')
```

#### 3. 批量解密所有 skills

```python
skills_dir = Path('../skills')
output_dir = Path('../skills_decrypted_all')
output_dir.mkdir(exist_ok=True)

for enc_file in skills_dir.rglob('*.enc'):
    rel = enc_file.relative_to(skills_dir)
    out_file = output_dir / rel.with_suffix('')  # 去掉 .enc 后缀
    out_file.parent.mkdir(parents=True, exist_ok=True)

    decrypted = skill_crypto.decrypt_file(enc_file, key)
    out_file.write_bytes(decrypted)
```

## skill_crypto API 参考

| 函数 | 签名 | 说明 |
|------|------|------|
| `_derive_key` | `(master_key: str) -> bytes` | 从主密钥派生 AES-256 密钥 |
| `set_decrypt_key` | `(dk_hex: str) -> None` | 设置解密密钥（hex 字符串） |
| `get_decrypt_key` | `() -> Optional[bytes]` | 获取当前解密密钥 |
| `clear_decrypt_key` | `() -> None` | 清除内存中的解密密钥 |
| `encrypt_bytes` | `(plaintext: bytes, key: bytes) -> bytes` | AES-256-GCM 加密 |
| `decrypt_bytes` | `(data: bytes, key: bytes) -> bytes` | AES-256-GCM 解密 |
| `encrypt_file` | `(src: Path, key: bytes) -> bytes` | 加密文件，返回密文 |
| `decrypt_file` | `(src: Path, key: bytes) -> bytes` | 解密文件，返回明文 |
| `encrypt_dk_for_transport` | `(master_key_hex: str, license_key: str) -> str` | 加密 DK 用于传输 |
| `decrypt_dk_from_transport` | `(encrypted_dk_hex: str) -> str` | 从传输格式解密 DK |
| `encrypt_skills_dir` | `(skills_dir: Path) -> None` | 加密整个 skills 目录 |
| `decrypt_skills_to_workspace` | `(skills_dir: Path, workspace_utils: Path, sub_dir: str, license_key: str) -> bool` | 解密 skills 到工作目录 |
| `is_encrypted_skills` | `(skills_dir: Path) -> bool` | 检查 skills 是否已加密 |
| `decrypt_skill_file_to_memory` | `(enc_path: Path, license_key: str) -> Optional[bytes]` | 解密单个 skill 文件到内存 |
| `decrypt_skill_md` | `(skills_dir: Path, skill_name: str, license_key: str) -> Optional[str]` | 解密指定 skill 的 markdown |

## license_guard API 参考

| 函数 | 签名 | 说明 |
|------|------|------|
| `check_license_local` | `(is_desktop: bool) -> bool` | 离线验证许可证，通过后自动设置 DK |
| `verify_license_online` | `(license_key: str, machine_id: str, is_desktop: bool) -> Tuple[bool, str, Optional[str]]` | 在线验证激活码，返回 (valid, message, dk_encrypted) |
| `apply_dk_from_verify` | `(dk_encrypted: Optional[str], license_key: str) -> None` | 解密并应用服务器返回的 DK |
| `save_license_local` | 保存许可证到本地 `license.json` |
| `renew_license_online` | 在线续期许可证 |
| `_get_machine_fingerprint` | `() -> str` | 获取本机指纹（基于硬件信息） |
| `_compute_sig` | `(license_key: str, machine_id: str, timestamp: int) -> str` | 计算许可证签名 |

## license.json 格式

```json
{
    "license_key": "用户激活码",
    "machine_id": "MH-xxxxxxxxxxxx",
    "timestamp": 1779724930,
    "sig": "hmac 签名字符串",
    "last_online_verify": 1779724930
}
```

## 安全分析

### 保护强度

- `.pyd` 文件是 Cython 编译产物，提供**混淆级别**保护，不是真正的安全
- 熟练掌握 Ghidra/IDA 的逆向工程师可在数小时内提取密钥派生逻辑
- 验证服务器 URL 和 HMAC secret 在 `_build_endpoint` 中通过运行时拼接隐藏，但可通过动态调试提取
- API Key 在 `state_store` 中**明文存储**，这是最严重的安全问题

### 建议改进

1. API Key 应使用与 skills 相同的 AES-256-GCM 加密存储
2. 密钥派生应绑定硬件指纹，防止 `license.json` 跨机器复制
3. 考虑使用 TPM/HSM 进行密钥保护（高安全性场景）
4. 定期轮换 `master_key` 和 `_SALT_PREFIX`

## 环境要求

| 组件 | 版本 |
|------|------|
| Python | 3.11.x（与 `.pyd` 编译版本一致） |
| cryptography | >= 42.0 |
| 操作系统 | Windows x64 |

## 解密脚本示例

完整的批量解密脚本，保存为 `decrypt_all_skills.py`：

```python
"""批量解密 MH Agent 所有 skills 文件"""
import sys
from pathlib import Path

# 设置路径
BACKEND_DIR = Path(__file__).resolve().parent.parent / 'backend'
SKILLS_DIR = BACKEND_DIR.parent / 'skills'
OUTPUT_DIR = BACKEND_DIR.parent / 'skills_decrypted'

sys.path.insert(0, str(BACKEND_DIR / 'services'))
sys.path.insert(0, str(BACKEND_DIR))

import license_guard
import skill_crypto


def main():
    # 1. 验证许可证，自动加载解密密钥
    if not license_guard.check_license_local(True):
        print("ERROR: 许可证验证失败，无法解密")
        return

    key = skill_crypto.get_decrypt_key()
    print(f"DK loaded: {len(key)} bytes")

    # 2. 批量解密
    OUTPUT_DIR.mkdir(exist_ok=True)
    count = 0
    errors = []

    for enc_file in SKILLS_DIR.rglob('*.enc'):
        rel = enc_file.relative_to(SKILLS_DIR)
        out_file = OUTPUT_DIR / rel.with_suffix('')
        out_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            decrypted = skill_crypto.decrypt_file(enc_file, key)
            out_file.write_bytes(decrypted)
            count += 1
        except Exception as e:
            errors.append((str(rel), str(e)))

    print(f"Decrypted: {count} files")
    if errors:
        print(f"Errors: {len(errors)}")
        for rel, err in errors:
            print(f"  {rel}: {err}")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
```

## 执行方式

```bash
cd resources/app/backend
../runtime/python/python.exe decrypt_all_skills.py
```
