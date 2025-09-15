import os
import re


def disable_auth_in_file(filepath):
    """Disable authentication in a specific file"""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, "r") as f:
        content = f.read()

    # Comment out authentication_classes lines
    content = re.sub(
        r"^(\s*authentication_classes\s*=.*)", r"# \1", content, flags=re.MULTILINE
    )

    # Comment out permission_classes = [IsAuthenticated]
    content = re.sub(
        r"^(\s*permission_classes\s*=\s*\[IsAuthenticated\])",
        r"# \1",
        content,
        flags=re.MULTILINE,
    )

    # Comment out @permission_classes decorators
    content = re.sub(
        r"^(\s*@permission_classes\(\[IsAuthenticated\]\))",
        r"# \1",
        content,
        flags=re.MULTILINE,
    )

    content = re.sub(
        r"^(\s*@permission_classes\(\[IsAdminUser\]\))",
        r"# \1",
        content,
        flags=re.MULTILINE,
    )

    with open(filepath, "w") as f:
        f.write(content)

    print(f"✅ Updated {filepath}")


# Files to update
files_to_update = [
    "Apps/Advisory/views.py",
    "Apps/SystemStatus/views.py",
    "Apps/IrrigationAdvisor/views.py",
]

for file_path in files_to_update:
    disable_auth_in_file(file_path)

print("🎉 Authentication disabled in all view files!")
print("Restart your Django server: python manage.py runserver")
