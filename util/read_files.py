
def read_files(file_path):
    with open("public/layout/layout.html", "rb") as f:
        layout_content = f.read()
    with open(file_path, "rb") as f:
        content = f.read()

    final_content = layout_content.replace(b"{{content}}", content)
    return final_content