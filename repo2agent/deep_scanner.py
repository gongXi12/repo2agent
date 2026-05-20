"""AST-based deep scanning using tree-sitter."""
from __future__ import annotations

import logging
from pathlib import Path

from repo2agent.models import Interface

logger = logging.getLogger(__name__)

LANG_EXTENSIONS: dict[str, list[str]] = {
    "Python": [".py"],
    "JavaScript": [".js", ".jsx"],
    "TypeScript": [".ts", ".tsx"],
    "Go": [".go"],
    "Rust": [".rs"],
}


def deep_scan(project_path: Path, languages: list[str]) -> list[Interface]:
    """Scan source files with tree-sitter and extract interfaces."""
    project_path = project_path.resolve()
    all_interfaces: list[Interface] = []

    for lang in languages:
        extensions = LANG_EXTENSIONS.get(lang)
        if not extensions:
            continue

        parser = _get_parser(lang)
        if parser is None:
            logger.warning("tree-sitter parser not available for %s, skipping", lang)
            continue

        for ext in extensions:
            for source_file in project_path.rglob(f"*{ext}"):
                parts = source_file.relative_to(project_path).parts
                if any(p in (".git", "node_modules", "__pycache__", "venv", ".venv", "vendor", "target", "dist", "build") for p in parts):
                    continue
                try:
                    source = source_file.read_bytes()
                    tree = parser.parse(source)
                    file_path = str(source_file.relative_to(project_path))
                    interfaces = _extract_interfaces(tree.root_node, lang, file_path)
                    all_interfaces.extend(interfaces)
                except (OSError, Exception) as e:
                    logger.debug("Failed to parse %s: %s", source_file, e)

    return all_interfaces


def _get_parser(lang: str):
    """Get a tree-sitter parser for the given language, or None if unavailable."""
    try:
        from tree_sitter import Language, Parser
        if lang == "Python":
            import tree_sitter_python as tslang
        elif lang in ("JavaScript", "TypeScript"):
            if lang == "JavaScript":
                import tree_sitter_javascript as tslang
            else:
                import tree_sitter_typescript as tslang
        elif lang == "Go":
            import tree_sitter_go as tslang
        elif lang == "Rust":
            import tree_sitter_rust as tslang
        else:
            return None
        return Parser(Language(tslang.language()))
    except ImportError:
        return None


def _extract_interfaces(root_node, lang: str, file_path: str) -> list[Interface]:
    """Extract Interface objects from an AST root node."""
    if lang in ("Python",):
        return _extract_python(root_node, file_path)
    elif lang in ("JavaScript", "TypeScript"):
        return _extract_js_ts(root_node, file_path)
    elif lang == "Go":
        return _extract_go(root_node, file_path)
    elif lang == "Rust":
        return _extract_rust(root_node, file_path)
    return []


def _extract_python(root_node, file_path: str) -> list[Interface]:
    interfaces = []
    for node in root_node.children:
        if node.type == "function_definition":
            iface = _python_func(node, file_path)
            if iface:
                interfaces.append(iface)
        elif node.type == "class_definition":
            iface = _python_class(node, file_path)
            if iface:
                interfaces.append(iface)
        elif node.type == "decorated_definition":
            iface = _python_decorated(node, file_path)
            if iface:
                interfaces.append(iface)
    return interfaces


def _python_func(node, file_path: str) -> Interface | None:
    name_node = node.child_by_field_name("name")
    if not name_node:
        return None
    name = name_node.text.decode("utf-8", errors="replace")
    params_node = node.child_by_field_name("parameters")
    params = params_node.text.decode("utf-8", errors="replace") if params_node else "()"
    return_node = node.child_by_field_name("return_type")
    ret = ""
    if return_node:
        ret = " -> " + return_node.text.decode("utf-8", errors="replace")
    signature = f"def {name}{params}{ret}"
    docstring = _extract_python_docstring(node)
    return Interface(name=name, kind="function", file_path=file_path, signature=signature, docstring=docstring)


def _python_class(node, file_path: str) -> Interface | None:
    name_node = node.child_by_field_name("name")
    if not name_node:
        return None
    name = name_node.text.decode("utf-8", errors="replace")
    docstring = _extract_python_docstring(node)
    return Interface(name=name, kind="class", file_path=file_path, signature=f"class {name}", docstring=docstring)


def _python_decorated(node, file_path: str) -> Interface | None:
    func_node = None
    decorator_text = ""
    for child in node.children:
        if child.type == "decorator":
            decorator_text = child.text.decode("utf-8", errors="replace")
        elif child.type == "function_definition":
            func_node = child
        elif child.type == "class_definition":
            func_node = child

    if func_node is None:
        return None

    # Check for route decorators
    if any(kw in decorator_text for kw in (".route(", ".get(", ".post(", ".put(", ".delete(", ".patch(")):
        route = decorator_text
        name_node = func_node.child_by_field_name("name")
        name = name_node.text.decode("utf-8", errors="replace") if name_node else "unknown"
        docstring = _extract_python_docstring(func_node)
        return Interface(name=name, kind="route", file_path=file_path, signature=f"{decorator_text} -> {name}", docstring=docstring)

    # Regular decorated function/class
    if func_node.type == "function_definition":
        iface = _python_func(func_node, file_path)
        if iface:
            iface.signature = f"{decorator_text}\n{iface.signature}"
        return iface
    elif func_node.type == "class_definition":
        iface = _python_class(func_node, file_path)
        if iface:
            iface.signature = f"{decorator_text}\n{iface.signature}"
        return iface

    return None


def _extract_python_docstring(node) -> str | None:
    """Extract docstring from a Python function/class body."""
    body = node.child_by_field_name("body")
    if not body:
        return None
    for child in body.children:
        if child.type == "expression_statement":
            expr = child.children[0] if child.children else None
            if expr and expr.type == "string":
                text = expr.text.decode("utf-8", errors="replace")
                for q in ('"""', "'''", '"', "'"):
                    if text.startswith(q) and text.endswith(q):
                        text = text[len(q):-len(q)]
                        break
                return text.strip()
        if child.type not in ("expression_statement", "decorated_definition"):
            break
    return None


def _extract_js_ts(root_node, file_path: str) -> list[Interface]:
    interfaces = []
    for node in root_node.children:
        if node.type == "function_declaration":
            iface = _js_function(node, file_path)
            if iface:
                interfaces.append(iface)
        elif node.type == "class_declaration":
            iface = _js_class(node, file_path)
            if iface:
                interfaces.append(iface)
        elif node.type == "export_statement":
            for child in node.children:
                if child.type == "function_declaration":
                    iface = _js_function(child, file_path)
                    if iface:
                        interfaces.append(iface)
                elif child.type == "class_declaration":
                    iface = _js_class(child, file_path)
                    if iface:
                        interfaces.append(iface)
    return interfaces


def _js_function(node, file_path: str) -> Interface | None:
    name_node = node.child_by_field_name("name")
    if not name_node:
        return None
    name = name_node.text.decode("utf-8", errors="replace")
    params_node = node.child_by_field_name("parameters")
    params = params_node.text.decode("utf-8", errors="replace") if params_node else "()"
    signature = f"function {name}{params}"
    return Interface(name=name, kind="function", file_path=file_path, signature=signature)


def _js_class(node, file_path: str) -> Interface | None:
    name_node = node.child_by_field_name("name")
    if not name_node:
        return None
    name = name_node.text.decode("utf-8", errors="replace")
    return Interface(name=name, kind="class", file_path=file_path, signature=f"class {name}")


def _extract_go(root_node, file_path: str) -> list[Interface]:
    interfaces = []
    for node in root_node.children:
        if node.type == "function_declaration":
            iface = _go_func(node, file_path)
            if iface:
                interfaces.append(iface)
        elif node.type == "type_declaration":
            for child in node.children:
                if child.type == "type_spec":
                    name_node = child.child_by_field_name("name")
                    type_node = child.child_by_field_name("type")
                    if name_node:
                        name = name_node.text.decode("utf-8", errors="replace")
                        type_text = type_node.text.decode("utf-8", errors="replace") if type_node else ""
                        if "struct" in type_text or "interface" in type_text:
                            interfaces.append(Interface(
                                name=name, kind="class", file_path=file_path,
                                signature=f"type {name} {type_text[:40]}"
                            ))
    return interfaces


def _go_func(node, file_path: str) -> Interface | None:
    name_node = node.child_by_field_name("name")
    if not name_node:
        return None
    name = name_node.text.decode("utf-8", errors="replace")
    params_node = node.child_by_field_name("parameters")
    params = params_node.text.decode("utf-8", errors="replace") if params_node else "()"
    result_node = node.child_by_field_name("result")
    result = " " + result_node.text.decode("utf-8", errors="replace") if result_node else ""
    signature = f"func {name}{params}{result}"
    return Interface(name=name, kind="function", file_path=file_path, signature=signature)


def _extract_rust(root_node, file_path: str) -> list[Interface]:
    interfaces = []
    for node in root_node.children:
        if node.type == "function_item":
            iface = _rust_func(node, file_path)
            if iface:
                interfaces.append(iface)
        elif node.type in ("struct_item", "enum_item"):
            name_node = node.child_by_field_name("name")
            if name_node:
                name = name_node.text.decode("utf-8", errors="replace")
                kind_text = "struct" if node.type == "struct_item" else "enum"
                interfaces.append(Interface(
                    name=name, kind="class", file_path=file_path,
                    signature=f"{kind_text} {name}"
                ))
        elif node.type == "impl_item":
            type_node = node.child_by_field_name("type")
            if type_node:
                name = type_node.text.decode("utf-8", errors="replace")
                interfaces.append(Interface(
                    name=name, kind="class", file_path=file_path,
                    signature=f"impl {name}"
                ))
    return interfaces


def _rust_func(node, file_path: str) -> Interface | None:
    name_node = node.child_by_field_name("name")
    if not name_node:
        return None
    name = name_node.text.decode("utf-8", errors="replace")
    params_node = node.child_by_field_name("parameters")
    params = params_node.text.decode("utf-8", errors="replace") if params_node else "()"
    return_type = ""
    for child in node.children:
        if child.type == "->":
            idx = list(node.children).index(child)
            if idx + 1 < len(node.children):
                return_type = " -> " + node.children[idx + 1].text.decode("utf-8", errors="replace")
    signature = f"fn {name}{params}{return_type}"
    return Interface(name=name, kind="function", file_path=file_path, signature=signature)
