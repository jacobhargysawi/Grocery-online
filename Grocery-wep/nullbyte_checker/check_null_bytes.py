import os

def scan_null_bytes(base_dir):
    print("\n🔍 Scanning for null bytes in .py files...\n")
    found = False

    for folder, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(folder, file)
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                        if b'\x00' in content:
                            print(f"🚨 Null bytes found in: {file_path}")
                            found = True
                except Exception as e:
                    print(f"⚠️  Could not read {file_path}: {e}")

    if not found:
        print("✅ All Python files are clean. No null bytes found.\n")

# Scan one level up (your main project)
scan_null_bytes("..")