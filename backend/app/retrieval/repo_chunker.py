"""
Structure-Aware Repository Chunker for GitHub Repository Content.
Enforces type-specific chunking guidelines:
- Markdown: split by heading hierarchy (#, ##, ###), preserving parent breadcrumbs
- OpenAPI / Swagger: chunk per endpoint/path with HTTP method, parameters, and schemas
- Code (Python, Java, JS, TS): chunk by class, method, or function with docstrings
- SQL: chunk by logical statement / DDL table definition
- Configuration (YAML, JSON): preserve logical hierarchy and top-level block boundaries
"""

import re
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

MAX_CHUNK_CHARS = 1200
MIN_CHUNK_CHARS = 80


class RepoChunker:
    """Structure-aware chunker for code, OpenAPI specifications, documentation, and config."""

    @staticmethod
    def chunk_markdown(content: str, file_path: str) -> List[Dict[str, Any]]:
        """Splits markdown by headings while preserving hierarchy breadcrumbs."""
        lines = content.splitlines()
        chunks = []
        current_heading = "Overview"
        current_lines: List[str] = []
        heading_stack: List[str] = ["Document"]

        heading_regex = re.compile(r"^(#{1,6})\s+(.+)$")

        for line in lines:
            m = heading_regex.match(line)
            if m:
                level = len(m.group(1))
                title = m.group(2).strip()

                if current_lines:
                    text = "\n".join(current_lines).strip()
                    if len(text) >= MIN_CHUNK_CHARS:
                        chunks.append({
                            "section": " > ".join(heading_stack),
                            "chunk_text": f"[{' > '.join(heading_stack)}]\n{text}",
                            "file_path": file_path,
                            "chunk_type": "markdown"
                        })
                    current_lines = []

                # Update heading stack based on level
                if level <= len(heading_stack):
                    heading_stack = heading_stack[:level - 1]
                heading_stack.append(title)
                current_heading = title
                current_lines.append(line)
            else:
                current_lines.append(line)

                # Split if section becomes too large
                if len("\n".join(current_lines)) > MAX_CHUNK_CHARS:
                    text = "\n".join(current_lines).strip()
                    chunks.append({
                        "section": " > ".join(heading_stack),
                        "chunk_text": f"[{' > '.join(heading_stack)}]\n{text}",
                        "file_path": file_path,
                        "chunk_type": "markdown"
                    })
                    current_lines = []

        if current_lines:
            text = "\n".join(current_lines).strip()
            if len(text) >= MIN_CHUNK_CHARS:
                chunks.append({
                    "section": " > ".join(heading_stack),
                    "chunk_text": f"[{' > '.join(heading_stack)}]\n{text}",
                    "file_path": file_path,
                    "chunk_type": "markdown"
                })

        return chunks

    @staticmethod
    def chunk_openapi(content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parses OpenAPI / Swagger spec and generates chunks per endpoint/operation."""
        chunks = []
        spec = None
        try:
            if file_path.endswith((".yaml", ".yml")):
                spec = yaml.safe_load(content)
            elif file_path.endswith(".json"):
                spec = json.loads(content)
        except Exception:
            spec = None

        if not isinstance(spec, dict) or ("paths" not in spec and "openapi" not in spec and "swagger" not in spec):
            # Fallback to text block chunking
            return RepoChunker.chunk_generic_text(content, file_path)

        api_title = spec.get("info", {}).get("title", "SAP API")
        api_version = spec.get("info", {}).get("version", "1.0.0")
        api_desc = spec.get("info", {}).get("description", "")

        # Summary chunk for the overall API
        header_text = (
            f"API Specification: {api_title} (v{api_version})\n"
            f"File: {file_path}\n"
            f"Description: {api_desc[:400]}\n"
        )
        chunks.append({
            "section": f"{api_title} Overview",
            "chunk_text": header_text,
            "file_path": file_path,
            "chunk_type": "openapi_overview"
        })

        paths = spec.get("paths", {})
        if isinstance(paths, dict):
            for path_url, path_item in paths.items():
                if not isinstance(path_item, dict):
                    continue
                for method, op in path_item.items():
                    if method.lower() not in ("get", "post", "put", "patch", "delete", "options", "head"):
                        continue
                    if not isinstance(op, dict):
                        continue

                    summary = op.get("summary") or op.get("operationId") or f"{method.upper()} {path_url}"
                    op_desc = op.get("description", "")
                    tags = ", ".join(op.get("tags", []))
                    params = op.get("parameters", [])
                    param_names = [p.get("name") for p in params if isinstance(p, dict)]
                    responses = list(op.get("responses", {}).keys()) if isinstance(op.get("responses"), dict) else []

                    chunk_body = (
                        f"Endpoint: {method.upper()} {path_url}\n"
                        f"Summary: {summary}\n"
                        f"Tags: {tags}\n"
                        f"Description: {op_desc}\n"
                        f"Parameters: {', '.join(filter(None, param_names))}\n"
                        f"Responses: {', '.join(map(str, responses))}\n"
                    )

                    chunks.append({
                        "section": f"{method.upper()} {path_url}",
                        "chunk_text": f"[{api_title} | {method.upper()} {path_url}]\n{chunk_body.strip()}",
                        "file_path": file_path,
                        "chunk_type": "openapi_endpoint"
                    })

        return chunks if chunks else RepoChunker.chunk_generic_text(content, file_path)

    @staticmethod
    def chunk_source_code(content: str, file_path: str, lang: str) -> List[Dict[str, Any]]:
        """Chunks source code by function, method, or class boundaries."""
        lines = content.splitlines()
        chunks = []

        if lang in ("python", "py"):
            block_pattern = re.compile(r"^(class\s+[A-Za-z0-9_]+|def\s+[A-Za-z0-9_]+)")
        elif lang in ("java",):
            block_pattern = re.compile(r"^\s*(public|protected|private|static|\s)+\s+(class|interface|enum|[A-Za-z0-9_<>]+)\s+[A-Za-z0-9_]+\s*(\(|{)")
        elif lang in ("javascript", "typescript", "js", "ts"):
            block_pattern = re.compile(r"^(export\s+)?(function|class|const\s+[A-Za-z0-9_]+\s*=\s*(async\s*)?\()")
        else:
            block_pattern = re.compile(r"^[A-Za-z0-9_]")

        current_symbol = Path(file_path).name
        current_block: List[str] = []

        for line in lines:
            if block_pattern.match(line):
                if current_block:
                    text = "\n".join(current_block).strip()
                    if len(text) >= MIN_CHUNK_CHARS:
                        chunks.append({
                            "section": f"{Path(file_path).name}::{current_symbol}",
                            "chunk_text": f"File: {file_path} ({current_symbol})\n```{lang}\n{text}\n```",
                            "file_path": file_path,
                            "chunk_type": f"code_{lang}"
                        })
                    current_block = []
                current_symbol = line.strip()[:60]
            current_block.append(line)

            if len("\n".join(current_block)) > MAX_CHUNK_CHARS:
                text = "\n".join(current_block).strip()
                chunks.append({
                    "section": f"{Path(file_path).name}::{current_symbol}",
                    "chunk_text": f"File: {file_path} ({current_symbol})\n```{lang}\n{text}\n```",
                    "file_path": file_path,
                    "chunk_type": f"code_{lang}"
                })
                current_block = []

        if current_block:
            text = "\n".join(current_block).strip()
            if len(text) >= MIN_CHUNK_CHARS:
                chunks.append({
                    "section": f"{Path(file_path).name}::{current_symbol}",
                    "chunk_text": f"File: {file_path} ({current_symbol})\n```{lang}\n{text}\n```",
                    "file_path": file_path,
                    "chunk_type": f"code_{lang}"
                })

        return chunks if chunks else RepoChunker.chunk_generic_text(content, file_path)

    @staticmethod
    def chunk_sql(content: str, file_path: str) -> List[Dict[str, Any]]:
        """Chunks SQL by DDL statements (CREATE TABLE, PROCEDURE, VIEW, ALTER)."""
        statements = re.split(r";\s*\n", content)
        chunks = []
        for stmt in statements:
            s_clean = stmt.strip()
            if len(s_clean) < MIN_CHUNK_CHARS:
                continue
            first_line = s_clean.splitlines()[0][:60]
            chunks.append({
                "section": f"SQL: {first_line}",
                "chunk_text": f"File: {file_path}\n```sql\n{s_clean}\n```",
                "file_path": file_path,
                "chunk_type": "sql"
            })
        return chunks if chunks else RepoChunker.chunk_generic_text(content, file_path)

    @staticmethod
    def chunk_generic_text(content: str, file_path: str) -> List[Dict[str, Any]]:
        """Fallback chunker for plain text or unstructured configuration files."""
        paras = re.split(r"\n\s*\n", content)
        chunks = []
        curr = []
        curr_len = 0

        for p in paras:
            p_strip = p.strip()
            if not p_strip:
                continue
            if curr_len + len(p_strip) > MAX_CHUNK_CHARS and curr:
                body = "\n\n".join(curr)
                chunks.append({
                    "section": Path(file_path).name,
                    "chunk_text": f"File: {file_path}\n{body}",
                    "file_path": file_path,
                    "chunk_type": "text"
                })
                curr = []
                curr_len = 0
            curr.append(p_strip)
            curr_len += len(p_strip)

        if curr:
            body = "\n\n".join(curr)
            if len(body) >= MIN_CHUNK_CHARS:
                chunks.append({
                    "section": Path(file_path).name,
                    "chunk_text": f"File: {file_path}\n{body}",
                    "file_path": file_path,
                    "chunk_type": "text"
                })

        return chunks

    def chunk_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Routes file content to appropriate structure-aware chunker."""
        p = Path(file_path)
        ext = p.suffix.lower()

        if ext in (".md", ".markdown"):
            return self.chunk_markdown(content, file_path)
        if ext in (".yaml", ".yml", ".json") and any(k in file_path.lower() for k in ["openapi", "swagger", "api"]):
            return self.chunk_openapi(content, file_path)
        if ext in (".py",):
            return self.chunk_source_code(content, file_path, "python")
        if ext in (".java",):
            return self.chunk_source_code(content, file_path, "java")
        if ext in (".js", ".ts"):
            return self.chunk_source_code(content, file_path, "typescript")
        if ext in (".sql",):
            return self.chunk_sql(content, file_path)
        return self.chunk_generic_text(content, file_path)


repo_chunker = RepoChunker()
