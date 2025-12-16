#!/usr/bin/env python3
"""
Convert various tabular file formats to CSV.

Supported:
- .csv, .tsv, .txt (delimited)
- .xlsx (openpyxl), .xls (xlrd)
- .parquet (pyarrow/fastparquet)
- .feather (pyarrow)
- .json (array of records or JSON Lines)
- .html (tables)
- .xml (simple row/column)
Optionally: .orc if pyarrow supports it.

Usage:
    python tabular_to_csv.py --input <path> --out <dir> [--recursive] [--pattern "*.xlsx"] [--encoding "utf-8"] [--chunksize 100000]
"""

import argparse
import csv
import json
import os
import sys
import re
from pathlib import Path
from typing import Iterable, Optional, Tuple, List
import pandas as pd

# Ensure Excel engines per environment guidance
EXCEL_XLSX_ENGINE = "openpyxl"
EXCEL_XLS_ENGINE = "xlrd"

# Try optional backends
_HAS_PYARROW = False
try:
    import pyarrow as pa  # noqa: F401
    _HAS_PYARROW = True
except Exception:
    _HAS_PYARROW = False


def safe_slug(s: str) -> str:
    """Make a safe filename component."""
    s = re.sub(r"[^\w\-]+", "_", s.strip())
    return s or "unnamed"

class Extract:
    def __init__(self, source,destination):
        self.source = source
        self.destination = destination

    def detect_delimiter(self, sample_path: Path, default=",") -> str:
        """Detect delimiter using csv.Sniffer on a small sample."""
        try:
            with open(sample_path, "r", encoding="utf-8", errors="ignore") as f:
                sample = f.read(8192)
                dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|", ":"])
            return dialect.delimiter
        except Exception:
            return default


    def write_csv(df: pd.DataFrame, out_path: Path, encoding: str = "utf-8", index: bool = False):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Use a safe CSV writer; pandas handles NA as empty by default
        df.to_csv(out_path, encoding=encoding, index=index)


    def convert_csv_tsv_txt(path: Path, out_dir: Path, encoding: str, chunksize: Optional[int]) -> List[Path]:
        delimiter = detect_delimiter(path)
        outputs = []
        out_path = out_dir / (path.stem + ".csv")
        if chunksize:
            # Chunked re-write to CSV
            first = True
            for chunk in pd.read_csv(path, sep=delimiter, encoding=encoding, chunksize=chunksize):
                write_mode = "w" if first else "a"
                header = first
                out_path.parent.mkdir(parents=True, exist_ok=True)
                chunk.to_csv(out_path, encoding=encoding, index=False, header=header, mode=write_mode)
                first = False
        else:
            df = pd.read_csv(path, sep=delimiter, encoding=encoding)
            # Ensure Excel engines per environment guidance


    def convert_excel(path: Path, out_dir: Path, encoding: str) -> List[Path]:
        """Convert each sheet in an Excel file into separate CSVs."""
        outputs = []
        # Read sheet names first
        try:
            xls = pd.ExcelFile(path, engine=EXCEL_XLSX_ENGINE if path.suffix.lower() == ".xlsx" else EXCEL_XLS_ENGINE)
        except Exception as e:
            raise RuntimeError(f"Failed to open Excel file {path}: {e}") from e

        for sheet in xls.sheet_names:
            df = xls.parse(sheet_name=sheet)
            sheet_slug = safe_slug(sheet)
            out_path = out_dir / f"{path.stem}__sheet_{sheet_slug}.csv"
            write_csv(df, out_path, encoding=encoding, index=False)
            outputs.append(out_path)
        return outputs


def convert_parquet(path: Path, out_dir: Path, encoding: str, chunksize: Optional[int]) -> List[Path]:
    """Convert Parquet to CSV."""
    if not _HAS_PYARROW:
        # pandas can still read parquet if fastparquet is installed; try anyway
        pass
    df = pd.read_parquet(path)
    out_path = out_dir / (path.stem + ".csv")
    if chunksize:
        # Manual chunk by rows if huge
        start = 0
        first = True
        while start < len(df):
            chunk = df.iloc[start:start+chunksize]
            mode = "w" if first else "a"
            header = first
            out_path.parent.mkdir(parents=True, exist_ok=True)
            chunk.to_csv(out_path, encoding=encoding, index=False, header=header, mode=mode)
            first = False
            start += chunksize
    else:
                # Ensure Excel engines per environment guidance
        EXCEL_XLSX_ENGINE = "openpyxl"
        EXCEL_XLS_ENGINE = "xlrd"

        # Try optional backends
        _HAS_PYARROW = False
        try:
            import pyarrow as pa  # noqa: F401
            _HAS_PYARROW = True
        except Exception:
            _HAS_PYARROW = False


    def convert_feather(path: Path, out_dir: Path, encoding: str) -> List[Path]:
        """Convert Feather to CSV."""
        df = pd.read_feather(path)
        out_path = out_dir / (path.stem + ".csv")
        write_csv(df, out_path, encoding=encoding, index=False)
        return [out_path]


    def _json_is_lines(path: Path, encoding: str) -> bool:
        """Heuristic: line-delimited JSON (JSONL) if each line parses to dict/list."""
        try:
            with open(path, "r", encoding=encoding) as f:
                for i, line in enumerate(f):
                    t = line.strip()
                    if not t:
                        continue
                    if t[0] in "[{":
                        # Try parse single line
                        try:
                            json.loads(t)
                            return True
                        except Exception:
                            return False
                    if i > 50:
                        break
        except Exception:
            pass
        return False


    def convert_json(path: Path, out_dir: Path, encoding: str) -> List[Path]:
        """
        Convert JSON to CSV.
        - If array of objects: map to rows.
        - If JSONL (one record per line): read lines.
        """
        outputs = []
        out_path = out_dir / (path.stem + ".csv")
        try:
            if _json_is_lines(path, encoding):
                df = pd.read_json(path, lines=True, encoding=encoding)
            else:
                df = pd.read_json(path, encoding=encoding)
                # If the JSON is a dict of columns, pandas may already shape it.
                # If nested, consider json_normalize:
                if not isinstance(df, pd.DataFrame):
                    df = pd.json_normalize(df)
        except ValueError:
            # Fallback to normalize arbitrary dict/list
            with open(path, "r", encoding=encoding) as f:
                obj = json.load(f)
            df = pd.json_normalize(obj)
        # Ensure Excel engines per environment guidance



    def convert_html(path: Path, out_dir: Path, encoding: str) -> List[Path]:
        """Convert all tables in an HTML file into separate CSVs."""
        outputs = []
        tables = pd.read_html(path, encoding=encoding)  # requires lxml
        for i, df in enumerate(tables, start=1):
            out_path = out_dir / f"{path.stem}__table_{i}.csv"
            write_csv(df, out_path, encoding=encoding, index=False)
            outputs.append(out_path)
        return outputs


    def convert_xml(path: Path, out_dir: Path, encoding: str) -> List[Path]:
        """
        Convert simple XML where rows share a tag, e.g.:

        <rows>
            <row><a>1</a><b>x</b></row>
            <row><a>2</a><b>y</b></row>
        </rows>

        Uses pandas.read_xml when available.
        """
        try:
            df = pd.read_xml(path)
        except Exception as e:
            raise RuntimeError(f"Failed to parse XML {path}: {e}") from e
        out_path = out_dir / (path.stem + ".csv")
        write_csv(df, out_path, encoding=encoding, index=False)
        return [out_path]


def convert_file(path: Path, out_dir: Path, encoding: str = "utf-8", chunksize: Optional[int] = None) -> List[Path]:
    """Dispatch conversion based on file extension."""
    ext = path.suffix.lower()

    if ext in {".csv", ".tsv", ".txt"}:
        return convert_csv_tsv_txt(path, out_dir, encoding, chunksize)
    elif ext in {".xlsx", ".xls"}:
        return convert_excel(path, out_dir, encoding)
    elif ext == ".parquet":
        return convert_parquet(path, out_dir, encoding, chunksize)
    elif ext == ".feather":
        return convert_feather(path, out_dir, encoding)
    elif ext == ".json":
        return convert_json(path, out_dir, encoding)
    elif ext in {".html", ".htm"}:
        return convert_html(path, out_dir, encoding)
    elif ext == ".xml":
        return convert_xml(path, out_dir, encoding)
    elif ext == ".orc":
        if not _HAS_PYARROW:
            raise RuntimeError("ORC requires pyarrow; install pyarrow to read ORC files.")
        # pandas doesn't have read_orc; use pyarrow to table -> pandas
        import pyarrow.orc as pa_orc
        with pa_orc.ORCFile(str(path)) as of:
            tbl = of.read()
        df = tbl.to_pandas()
        out_path = out_dir / (path.stem + ".csv")
        write_csv(df, out_path, encoding=encoding, index=False)
        return [out_path]
    else:
        raise ValueError(f"Unsupported file type: {ext}")


    def iter_paths(input_path: Path, pattern: Optional[str], recursive: bool) -> Iterable[Path]:
        if input_path.is_dir():
            if recursive:
                yield from input_path.rglob(pattern or "*")
            else:
                yield from input_path.glob(pattern or "*")
        elif input_path.is_file():
            yield input_path
        else:
            raise FileNotFoundError(f"Input path not found: {input_path}")


    def main():
        parser = argparse.ArgumentParser(description="Convert tabular files to CSV.")
        parser.add_argument("--input", "-i", required=True, help="Input file or directory.")
        parser.add_argument("--out", "-o", default="csv_out", help="Output directory.")
        parser.add_argument("--pattern", "-p", default=None, help='Glob pattern (e.g., "*.xlsx").')
        parser.add_argument("--recursive", "-r", action="store_true", help="Recursively search directories.")
        parser.add_argument("--encoding", "-e", default="utf-8", help="Output encoding (default: utf-8).")
        parser.add_argument("--chunksize", "-c", type=int, default=None, help="Row chunksize for large files.")
        args = parser.parse_args()

        in_path = Path(args.input)
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)

        converted = []
        errors: List[Tuple[Path, str]] = []

        for path in iter_paths(in_path, args.pattern, args.recursive):
            if not path.is_file():
                continue
            try:
                outs = convert_file(path, out_dir, encoding=args.encoding, chunksize=args.chunksize)
                converted.extend(outs)
                print(f"✔ Converted: {path} -> {', '.join(str(o) for o in outs)}")
            except Exception as e:
                msg = f"✖ Error converting {path}: {e}"
                print(msg, file=sys.stderr)
                errors.append((path, str(e)))


if __name__ == "__main__":
    file_path=sys.argv[1]
    dest_path=sys.argv[2]
    extractor=Extract(file_path,dest_path)
