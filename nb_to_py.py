#!/usr/bin/env python3
"""
nb_to_py.py — Extract and clean code from Jupyter notebooks.

Reads all code cells from a .ipynb file, strips comments, empty lines,
and docstrings, then writes the cleaned code to a .py file.

Usage:
    python nb_to_py.py notebook.ipynb              # outputs notebook.py
    python nb_to_py.py notebook.ipynb -o output.py # custom output path
"""

import ast
import json
import re
import sys
import argparse
from pathlib import Path


# ---------------------------------------------------------------------------
# Docstring removal via AST rewriting
# ---------------------------------------------------------------------------

class DocstringRemover(ast.NodeTransformer):
    """Remove docstrings from functions, classes, and modules."""

    def _strip_docstring(self, node):
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            node.body.pop(0)
            # If the body is now empty, insert a 'pass' so the AST stays valid
            if not node.body:
                node.body.append(ast.Pass())
        return node

    def visit_Module(self, node):
        self.generic_visit(node)
        return self._strip_docstring(node)

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        return self._strip_docstring(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.generic_visit(node)
        return self._strip_docstring(node)


def remove_docstrings_via_ast(source: str) -> str:
    """
    Parse *source* as Python, strip all docstrings, and unparse back to source.
    Falls back to the original source if parsing fails (e.g. IPython magic).
    """
    try:
        tree = ast.parse(source)
        tree = DocstringRemover().visit(tree)
        ast.fix_missing_locations(tree)
        return ast.unparse(tree)
    except SyntaxError:
        return source


# ---------------------------------------------------------------------------
# Line-level cleaning (comments, blank lines, IPython magics)
# ---------------------------------------------------------------------------

# Matches a whole line that is only a comment (optional leading whitespace)
_COMMENT_RE = re.compile(r"^\s*#.*$")

# Matches IPython magic lines (%magic, %%magic, !shell)
_MAGIC_RE = re.compile(r"^\s*[%!]")


def clean_lines(source: str) -> str:
    """Remove comment-only lines, magic lines, and collapse blank lines."""
    lines = source.splitlines()
    cleaned = []
    for line in lines:
        if _COMMENT_RE.match(line):
            continue
        if _MAGIC_RE.match(line):
            continue
        cleaned.append(line)

    # Collapse runs of blank lines to a single blank line
    result = []
    prev_blank = False
    for line in cleaned:
        is_blank = line.strip() == ""
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank

    return "\n".join(result)


# ---------------------------------------------------------------------------
# Inline comment stripping
# ---------------------------------------------------------------------------

def strip_inline_comments(source: str) -> str:
    """
    Remove inline comments (the  # … part at the end of code lines).
    Uses tokenize so it correctly ignores # inside strings.
    """
    import io
    import tokenize

    result_lines = source.splitlines(keepends=True)
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except tokenize.TokenError:
        return source  # bail on incomplete/magic-heavy cells

    # Collect comment token positions
    comment_ranges = []
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            srow, scol = tok.start  # 1-based row, 0-based col
            comment_ranges.append((srow - 1, scol))  # convert to 0-based row

    if not comment_ranges:
        return source

    for row_idx, col in comment_ranges:
        if row_idx < len(result_lines):
            line = result_lines[row_idx]
            # Trim everything from the comment start, then rstrip trailing space
            trimmed = line[:col].rstrip()
            # Preserve the newline if the original had one
            nl = "\n" if line.endswith("\n") else ""
            result_lines[row_idx] = trimmed + nl if trimmed else nl

    return "".join(result_lines)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def extract_code_cells(notebook_path: Path) -> list[str]:
    """Return raw source strings for every code cell in the notebook."""
    with notebook_path.open(encoding="utf-8") as f:
        nb = json.load(f)

    cells = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source", "")
        # source can be a list of lines or a single string
        if isinstance(source, list):
            source = "".join(source)
        if source.strip():
            cells.append(source)
    return cells


def clean_cell(source: str) -> str:
    """Full cleaning pipeline for a single code cell."""
    # 1. Strip inline comments (before AST so line numbers stay intact)
    source = strip_inline_comments(source)
    # 2. Remove docstrings via AST (also normalises indentation via ast.unparse)
    source = remove_docstrings_via_ast(source)
    # 3. Remove comment-only lines, magic lines, collapse blank lines
    source = clean_lines(source)
    return source.strip()


def process_notebook(notebook_path: Path, output_path: Path) -> None:
    raw_cells = extract_code_cells(notebook_path)
    if not raw_cells:
        print(f"No code cells found in {notebook_path}")
        sys.exit(0)

    cleaned_blocks = []
    for i, cell_source in enumerate(raw_cells, start=1):
        cleaned = clean_cell(cell_source)
        if cleaned:
            cleaned_blocks.append(cleaned)
        else:
            print(f"  Cell {i}: empty after cleaning — skipped")

    output_source = "\n\n".join(cleaned_blocks) + "\n"

    output_path.write_text(output_source, encoding="utf-8")
    print(
        f"Done. {len(raw_cells)} code cell(s) → {len(cleaned_blocks)} non-empty "
        f"block(s) written to {output_path}"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Extract and clean code from a Jupyter notebook."
    )
    parser.add_argument("notebook", help="Path to the .ipynb file")
    parser.add_argument(
        "-o", "--output",
        help="Output .py file path (default: same name as notebook with .py extension)",
    )
    args = parser.parse_args()

    notebook_path = Path(args.notebook)
    if not notebook_path.exists():
        print(f"Error: file not found: {notebook_path}", file=sys.stderr)
        sys.exit(1)
    if notebook_path.suffix.lower() != ".ipynb":
        print(f"Warning: expected a .ipynb file, got {notebook_path.suffix!r}")

    output_path = Path(args.output) if args.output else notebook_path.with_suffix(".py")

    print(f"Reading:  {notebook_path}")
    print(f"Writing:  {output_path}")
    process_notebook(notebook_path, output_path)


if __name__ == "__main__":
    main()
