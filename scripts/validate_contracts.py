"""Validate BrainOn OpenAPI syntax, references, and Django public URL coverage."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import yaml
from openapi_spec_validator import validate_spec


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
PUBLIC_SPEC = ROOT / "contracts" / "openapi" / "public-api.yaml"
INFERENCE_SPEC = ROOT / "contracts" / "openapi" / "inference-api.yaml"
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def load_spec(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        spec = yaml.safe_load(stream)
    validate_spec(spec)
    return spec


def resolve_internal_refs(spec: dict) -> None:
    def resolve(ref: str):
        if not ref.startswith("#/"):
            return
        node = spec
        for part in ref[2:].split("/"):
            node = node[part.replace("~1", "/").replace("~0", "~")]

    def walk(node):
        if isinstance(node, dict):
            if "$ref" in node:
                resolve(node["$ref"])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(spec)


def normalize_openapi(path: str) -> str:
    return re.sub(r"\{([^}]+)\}", r"{\1}", path.rstrip("/"))


def normalize_django(route: str) -> str:
    route = "/" + route.rstrip("/")
    return re.sub(r"<[^:>]+:([^>]+)>", r"{\1}", route)


def django_operations() -> set[tuple[str, str]]:
    sys.path.insert(0, str(BACKEND))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.test_settings")
    import django
    django.setup()
    from django.urls import URLPattern, URLResolver, get_resolver

    operations = set()

    def visit(patterns, prefix=""):
        for entry in patterns:
            route = prefix + str(entry.pattern)
            if isinstance(entry, URLResolver):
                visit(entry.url_patterns, route)
                continue
            if not isinstance(entry, URLPattern):
                continue
            path = normalize_django(route)
            if not path.startswith("/api/v1/") and path != "/api/v1/health":
                continue
            callback = entry.callback
            actions = getattr(callback, "actions", None)
            if actions:
                methods = actions.keys()
            else:
                view_class = getattr(callback, "view_class", None) or getattr(callback, "cls", None)
                methods = [method for method in HTTP_METHODS if view_class and hasattr(view_class, method)]
            operations.update((path, method.lower()) for method in methods)

    visit(get_resolver().url_patterns)
    return operations


def openapi_operations(spec: dict) -> set[tuple[str, str]]:
    return {
        (normalize_openapi(path), method.lower())
        for path, item in spec["paths"].items()
        if path.startswith("/api/v1/")
        for method in item
        if method.lower() in HTTP_METHODS
    }


def main() -> int:
    public = load_spec(PUBLIC_SPEC)
    inference = load_spec(INFERENCE_SPEC)
    resolve_internal_refs(public)
    resolve_internal_refs(inference)
    expected = openapi_operations(public)
    actual = django_operations()
    missing = sorted(expected - actual)
    if missing:
        for path, method in missing:
            print(f"MISSING {method.upper()} {path}")
        return 1
    print(f"Validated two OpenAPI documents and {len(expected)} public operations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
