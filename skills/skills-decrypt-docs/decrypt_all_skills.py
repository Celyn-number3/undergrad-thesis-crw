"""批量解密 MH Agent 所有 skills 文件
使用方法:
    cd resources/app/backend
    ../runtime/python/python.exe ../skills-decrypt-docs/decrypt_all_skills.py

或者指定 Python 3.11:
    /path/to/python3.11 decrypt_all_skills.py --backend-dir ../backend
"""
import sys
from pathlib import Path


def main():
    # 路径配置
    script_dir = Path(__file__).resolve().parent
    backend_dir = script_dir.parent / 'backend'
    skills_dir = backend_dir.parent / 'skills'
    output_dir = backend_dir.parent / 'skills_decrypted'

    # 允许命令行覆盖
    args = sys.argv[1:]
    if '--backend-dir' in args:
        idx = args.index('--backend-dir')
        backend_dir = Path(args[idx + 1]).resolve()
    if '--skills-dir' in args:
        idx = args.index('--skills-dir')
        skills_dir = Path(args[idx + 1]).resolve()
    if '--output-dir' in args:
        idx = args.index('--output-dir')
        output_dir = Path(args[idx + 1]).resolve()

    sys.path.insert(0, str(backend_dir / 'services'))
    sys.path.insert(0, str(backend_dir))

    import license_guard
    import skill_crypto

    # 1. 验证许可证，自动加载解密密钥
    if not license_guard.check_license_local(True):
        print("ERROR: License verification failed")
        return 1

    key = skill_crypto.get_decrypt_key()
    print(f"DK loaded: {len(key)} bytes (AES-256)")

    # 2. 检查 skills 目录
    if not skills_dir.exists():
        print(f"ERROR: Skills directory not found: {skills_dir}")
        return 1

    if not skill_crypto.is_encrypted_skills(skills_dir):
        print("Skills not encrypted, copying directly...")

    # 3. 批量解密
    output_dir.mkdir(parents=True, exist_ok=True)
    enc_files = list(skills_dir.rglob('*.enc'))

    if not enc_files:
        print("No .enc files found")
        return 0

    print(f"Found {len(enc_files)} encrypted files, decrypting...")

    count = 0
    errors = []

    for enc_file in enc_files:
        rel = enc_file.relative_to(skills_dir)
        out_file = output_dir / rel.with_suffix('')
        out_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            decrypted = skill_crypto.decrypt_file(enc_file, key)
            out_file.write_bytes(decrypted)
            count += 1
            if count % 50 == 0:
                print(f"  {count}/{len(enc_files)} ...")
        except Exception as e:
            errors.append((str(rel), str(e)))

    print(f"\nDone: {count}/{len(enc_files)} decrypted")
    if errors:
        print(f"Errors: {len(errors)}")
        for rel, err in errors:
            print(f"  {rel}: {err}")
    print(f"Output: {output_dir}")
    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
