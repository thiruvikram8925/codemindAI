
import ast


def create_chunks(documents, chunk_size=1000, overlap=150):

    chunks = []

    for document in documents:

        filename = document["file"]
        content = document["content"]
        lines = content.splitlines()

        # Python AST-based chunking
        if filename.lower().endswith(".py"):

            try:
                tree = ast.parse(content)

                definitions = [
                    node for node in ast.walk(tree)
                    if isinstance(
                        node,
                        (
                            ast.FunctionDef,
                            ast.AsyncFunctionDef,
                            ast.ClassDef
                        )
                    )
                ]

                for node in definitions:

                    start = node.lineno
                    end = node.end_lineno

                    code = "\n".join(
                        lines[start - 1:end]
                    )

                    chunks.append({

                        "text": code,
                        "file": filename,
                        "start_line": start,
                        "end_line": end,
                        "type": type(node).__name__,
                        "name": node.name

                    })

                # Also retain top-level code not covered
                # by a function or class.
                covered = set()

                for node in definitions:
                    covered.update(
                        range(node.lineno, node.end_lineno + 1)
                    )

                remaining = [
                    line for number, line in enumerate(
                        lines, start=1
                    )
                    if number not in covered
                ]

                if remaining and not definitions:

                    chunks.append({
                        "text": "\n".join(remaining),
                        "file": filename,
                        "start_line": 1,
                        "end_line": len(lines),
                        "type": "Module",
                        "name": filename
                    })

            except SyntaxError:

                # Fallback for invalid Python syntax
                chunks.extend(
                    split_text(
                        content,
                        filename,
                        chunk_size,
                        overlap
                    )
                )

        else:

            # Chunking for Java, JS, HTML and other files
            chunks.extend(
                split_text(
                    content,
                    filename,
                    chunk_size,
                    overlap
                )
            )

    return chunks


def split_text(content, filename, chunk_size, overlap):

    chunks = []
    lines = content.splitlines()

    start = 0

    while start < len(lines):

        end = min(
            start + chunk_size // 50,
            len(lines)
        )

        code = "\n".join(lines[start:end])

        if code.strip():

            chunks.append({
                "text": code,
                "file": filename,
                "start_line": start + 1,
                "end_line": end,
                "type": "Code",
                "name": filename
            })

        if end == len(lines):
            break

        step = max(1, chunk_size // 50 - overlap // 50)
        start += step

    return chunks
