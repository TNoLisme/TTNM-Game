# list_structure.py
import os

# Cấu hình
paths = ["be/app", "fe/src"]
exclude_folders = ["fe/src/assets", "node_modules"]
file_extensions = [".js", ".py", ".html", ".css"]
output_file = "structure.txt"

# Chức năng kiểm tra có nằm trong folder loại trừ không
def is_excluded(path):
    for excl in exclude_folders:
        if os.path.commonpath([os.path.abspath(path), os.path.abspath(excl)]) == os.path.abspath(excl):
            return True
    return False

with open(output_file, "w", encoding="utf-8") as f:
    f.write("==== FILES ====\n")
    for root_path in paths:
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Loại bỏ folder exclude khỏi traversal
            dirnames[:] = [d for d in dirnames if not is_excluded(os.path.join(dirpath, d))]

            # Liệt kê file
            for file in filenames:
                if any(file.endswith(ext) for ext in file_extensions):
                    f.write(os.path.join(dirpath, file) + "\n")

    f.write("\n==== FOLDERS ====\n")
    for root_path in paths:
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Loại bỏ folder exclude
            dirnames[:] = [d for d in dirnames if not is_excluded(os.path.join(dirpath, d))]

            # Ghi tất cả folder (bao gồm rỗng)
            f.write(dirpath + "\n")

print("Liệt kê xong! Kết quả lưu trong structure.txt")
