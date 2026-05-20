from __future__ import annotations

import json
import tomllib
from pathlib import Path


def parse_configs(project_path: Path) -> dict:
    result = {
        "name": None,
        "description": None,
        "scripts": {},
        "dependencies": {"prod": [], "dev": []},
        "languages": [],
        "frameworks": [],
        "has_tests": False,
        "has_docs": False,
        "has_ci": False,
    }

    package_json = project_path / "package.json"
    if package_json.exists():
        _parse_package_json(package_json, result)

    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        _parse_pyproject_toml(pyproject, result)

    cargo = project_path / "Cargo.toml"
    if cargo.exists():
        _parse_cargo_toml(cargo, result)

    go_mod = project_path / "go.mod"
    if go_mod.exists():
        _parse_go_mod(go_mod, result)

    _detect_features(project_path, result)

    return result


def _parse_package_json(path: Path, result: dict) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return

    result["name"] = data.get("name") or result["name"]
    result["description"] = data.get("description") or result["description"]
    result["scripts"].update(data.get("scripts", {}))

    for dep in data.get("dependencies", {}):
        result["dependencies"]["prod"].append(dep)
    for dep in data.get("devDependencies", {}):
        result["dependencies"]["dev"].append(dep)

    if "JavaScript" not in result["languages"]:
        result["languages"].append("JavaScript")

    _detect_js_frameworks(data, result)


def _parse_pyproject_toml(path: Path, result: dict) -> None:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return

    project = data.get("project", {})
    result["name"] = project.get("name") or result["name"]
    result["description"] = project.get("description") or result["description"]

    for dep in project.get("dependencies", []):
        name = dep.split(">=")[0].split("==")[0].split("<")[0].split("[")[0].strip()
        result["dependencies"]["prod"].append(name)

    result["scripts"].update(project.get("scripts", {}))

    if "Python" not in result["languages"]:
        result["languages"].append("Python")

    _detect_python_frameworks(project, result)


def _parse_cargo_toml(path: Path, result: dict) -> None:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return

    pkg = data.get("package", {})
    result["name"] = pkg.get("name") or result["name"]
    result["description"] = pkg.get("description") or result["description"]

    for dep in data.get("dependencies", {}):
        result["dependencies"]["prod"].append(dep)

    if "Rust" not in result["languages"]:
        result["languages"].append("Rust")


def _parse_go_mod(path: Path, result: dict) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return

    for line in content.splitlines():
        line = line.strip()
        if line.startswith("module "):
            result["name"] = line.split(" ", 1)[1].strip()

    if "Go" not in result["languages"]:
        result["languages"].append("Go")


def _detect_js_frameworks(data: dict, result: dict) -> None:
    all_deps = set(data.get("dependencies", {})) | set(data.get("devDependencies", {}))
    framework_map = {
        "react": "React",
        "next": "Next.js",
        "vue": "Vue.js",
        "nuxt": "Nuxt.js",
        "angular": "Angular",
        "svelte": "Svelte",
        "express": "Express",
        "fastify": "Fastify",
        "koa": "Koa",
        "nestjs": "NestJS",
    }
    for dep, framework in framework_map.items():
        if dep in all_deps and framework not in result["frameworks"]:
            result["frameworks"].append(framework)


def _detect_python_frameworks(project: dict, result: dict) -> None:
    all_deps = [d.split(">=")[0].split("==")[0].split("<")[0].split("[")[0].strip().lower() for d in project.get("dependencies", [])]
    framework_map = {
        "django": "Django",
        "flask": "Flask",
        "fastapi": "FastAPI",
        "starlette": "Starlette",
        "tornado": "Tornado",
        "click": "Click CLI",
        "typer": "Typer CLI",
    }
    for dep, framework in framework_map.items():
        if dep in all_deps and framework not in result["frameworks"]:
            result["frameworks"].append(framework)


def _detect_features(project_path: Path, result: dict) -> None:
    test_indicators = ["tests", "test", "spec", "__tests__"]
    for indicator in test_indicators:
        if (project_path / indicator).is_dir():
            result["has_tests"] = True
            break

    if (project_path / "docs").is_dir():
        result["has_docs"] = True

    ci_path = project_path / ".github" / "workflows"
    if ci_path.is_dir() and any(ci_path.glob("*.yml")):
        result["has_ci"] = True
