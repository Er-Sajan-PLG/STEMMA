"""Regression guard for the L371 bug class.

A function-local ``import json`` (or sys, yaml, ...) makes that name local for
the WHOLE function, so every other branch that uses the module-level name
raises UnboundLocalError. webapp/server.py's request dispatchers hit this twice
(semantic endpoints; /api/export). Forbid local re-imports of names that are
already imported at module level in the long-running servers.
"""
from __future__ import annotations

import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "webapp" / "server.py",
    ROOT / "webapp" / "core.py",
    ROOT / "adapters" / "python" / "stemma_adapter" / "server.py",
]


def _bound_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    if isinstance(node, ast.Import):
        for a in node.names:
            names.add(a.asname or a.name.split(".")[0])
    elif isinstance(node, ast.ImportFrom):
        for a in node.names:
            names.add(a.asname or a.name)
    return names


def test_no_function_reimports_a_module_level_name() -> None:
    problems = []
    for path in FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        module_names: set[str] = set()
        for node in tree.body:
            module_names |= _bound_names(node)
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(fn):
                clash = _bound_names(node) & module_names
                if clash:
                    problems.append(f"{path.relative_to(ROOT)}:{node.lineno} in {fn.name}(): re-imports {sorted(clash)}")
    assert not problems, "local imports shadow module-level names (UnboundLocalError risk):\n" + "\n".join(problems)
