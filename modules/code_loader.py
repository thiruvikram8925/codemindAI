
from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".py", ".java", ".js", ".jsx",
    ".ts", ".tsx", ".html", ".css",
    ".cpp", ".c", ".h", ".cs",
    ".php", ".go", ".rs", ".sql",
    ".json", ".yaml", ".yml",
    ".md", ".txt", ".xml", ".sh"
}

IGNORED_DIRECTORIES = {
    ".git", "venv", ".venv",
    "node_modules", "__pycache__",
    "dist", "build"
}


def load_code_files(folder):

    documents = []

    for path in Path(folder).rglob("*"):

        if not path.is_file():
            continue

        if any(
            part in IGNORED_DIRECTORIES
            for part in path.parts
        ):
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            content = path.read_text(
                encoding="utf-8"
            )

            if content.strip():

                documents.append({
                    "file": str(path),
                    "content": content
                })

        except (UnicodeDecodeError, OSError):
            continue

    return documents
