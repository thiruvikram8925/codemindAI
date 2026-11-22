
import ast
from pathlib import Path


def analyze_project(documents):

    file_details = []
    dependencies = []

    # Build a map of Python module names to file paths
    module_map = {}

    for document in documents:

        path = Path(document["file"])

        if path.suffix.lower() == ".py":

            module_name = ".".join(path.with_suffix("").parts)

            module_map[module_name] = str(path)

            module_map[path.stem] = str(path)

    # Analyze each Python file
    for document in documents:

        filename = document["file"]
        content = document["content"]

        functions = []
        classes = []
        imports = []

        if not filename.lower().endswith(".py"):
            file_details.append({
                "file": filename,
                "functions": [],
                "classes": [],
                "imports": []
            })
            continue

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):

                if isinstance(
                    node,
                    (ast.FunctionDef, ast.AsyncFunctionDef)
                ):
                    functions.append(node.name)

                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)

                elif isinstance(node, ast.Import):

                    for alias in node.names:
                        imports.append(alias.name)

                elif isinstance(node, ast.ImportFrom):

                    if node.module:
                        imports.append(node.module)

            # Identify local project dependencies
            for imported in imports:

                if imported in module_map:

                    dependencies.append({
                        "source": filename,
                        "imports": module_map[imported]
                    })

                else:

                    # Check whether a dotted import matches
                    # a known local module.
                    for module_name, module_path in module_map.items():

                        if imported.startswith(module_name + "."):

                            dependencies.append({
                                "source": filename,
                                "imports": module_path
                            })
                            break

        except SyntaxError:
            pass

        file_details.append({
            "file": filename,
            "functions": sorted(set(functions)),
            "classes": sorted(set(classes)),
            "imports": sorted(set(imports))
        })

    return {
        "files": file_details,
        "dependencies": dependencies,
        "total_files": len(documents),
        "python_files": sum(
            1 for doc in documents
            if doc["file"].lower().endswith(".py")
        ),
        "total_functions": sum(
            len(item["functions"]) for item in file_details
        ),
        "total_classes": sum(
            len(item["classes"]) for item in file_details
        )
    }
