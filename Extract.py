#!/usr/bin/env python3
"""Convert various tabular file formats to CSV."""
#!/usr/bin/env python3
import argparse
import csv
import json
import sys
import re
from pathlib import Path
from typing import Iterable, Optional, Tuple, List

import pandas as pd

# Excel engines
EXCEL_XLSX_ENGINE = "openpyxl"
EXCEL_XLS_ENGINE = "xlrd"

# Optional backends
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
    """Convert a single input file (self.source) to CSV(s) under self.destination."""

    def __init__(self, source: Path, destination: Path):
        self.source = Path(source)
        self.destination = Path(destination)

    # ---------- helpers ----------

    def detect_delimiter(self, sample_path: Path, default: str = ",") -> str:
        """Detect delimiter using csv.Sniffer on a small sample."""
        try:
            with open(sample_path, "r", encoding="utf-8", errors="ignore") as f:
                sample = f.read(8192)
            dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|", ":"])
            return dialect.delimiter
        except Exception:
            return default

    def write_csv(self, df: pd.DataFrame, out_path: Path, encoding: str = "utf-8", index: bool = False) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, encoding=encoding, index=index)

    # ---------- converters (return list of CSV paths) ----------

    def convert_csv_tsv_txt(self, encoding: str, chunksize: Optional[int]) -> List[Path]:
        """Normalize any delimited file into standard CSV."""
        path = self.source
        out_dir = self.destination

        delimiter = self.detect_delimiter(path)
        outputs: List[Path] = []
        out_path = out_dir / (path.stem + ".csv")

        if chunksize:
            first = True
            for chunk in pd.read_csv(path, sep=delimiter, encoding=encoding, chunksize=chunksize):
                mode = "w" if first else "a"
                header = first
                out_path.parent.mkdir(parents=True, exist_ok=True)
                chunk.to_csv(out_path, encoding=encoding, index=False, header=header, mode=mode)
                first = False
        else:
            df = pd.read_csv(path, sep=delimiter, encoding=encoding)
            self.write_csv(df, out_path, encoding=encoding, index=False)

        outputs.append(out_path)
        return outputs

    def convert_excel(self, encoding: str) -> List[Path]:
        """Convert each sheet in an Excel file into separate CSVs."""
        path = self.source
        out_dir = self.destination
        outputs: List[Path] = []

        try:
            xls = pd.ExcelFile(path, engine=EXCEL_XLSX_ENGINE if path.suffix.lower() == ".xlsx" else EXCEL_XLS_ENGINE)
        except Exception as e:
            raise RuntimeError(f"Failed to open Excel file {path}: {e}") from e

        for sheet in xls.sheet_names:
            df = xls.parse(sheet_name=sheet)
            sheet_slug = safe_slug(sheet)
            out_path = out_dir / f"{path.stem}__sheet_{sheet_slug}.csv"
            self.write_csv(df, out_path, encoding=encoding, index=False)
            outputs.append(out_path)

        return outputs

    def convert_parquet(self, encoding: str, chunksize: Optional[int]) -> List[Path]:
        """Convert Parquet to CSV."""
        path = self.source
        out_dir = self.destination

        df = pd.read_parquet(path)
        out_path = out_dir / (path.stem + ".csv")
        outputs: List[Path] = []

        if chunksize:
            start = 0
            first = True
            while start < len(df):
                chunk = df.iloc[start:start + chunksize]
                mode = "w" if first else "a"
                header = first
                out_path.parent.mkdir(parents=True, exist_ok=True)
                chunk.to_csv(out_path, encoding=encoding, index=False, header=header, mode=mode)
                first = False
                start += chunksize
        else:
            self.write_csv(df, out_path, encoding=encoding, index=False)

        outputs.append(out_path)
        return outputs

    def convert_feather(self, encoding: str) -> List[Path]:
        """Convert Feather to CSV."""
        path = self.source
        out_dir = self.destination
        df = pd.read_feather(path)
        out_path = out_dir / (path.stem + ".csv")
        self.write_csv(df, out_path, encoding=encoding, index=False)
        return [out_path]

    def _json_is_lines(self, path: Path, encoding: str) -> bool:
        """Heuristic: line-delimited JSON (JSONL) if each line is a JSON object/array."""
        try:
            with open(path, "r", encoding=encoding) as f:
                for i, line in enumerate(f):
                    t = line.strip()
                    if not t:
                        continue
                    if t[0] in "[{":
                        try:
                            json.loads(t)
                            return True
                        except Exception:
                            return False
                    if i > 50:  # don't read huge files just for detection
                        break
        except Exception:
            pass
        return False

    def convert_json(self, encoding: str) -> List[Path]:
        """Convert JSON or JSONL to CSV."""
        path = self.source
        out_dir = self.destination
        outputs: List[Path] = []
        out_path = out_dir / (path.stem + ".csv")

        try:
            if self._json_is_lines(path, encoding):
                df = pd.read_json(path, lines=True, encoding=encoding)
            else:
                df = pd.read_json(path, encoding=encoding)
                # If nested structures, normalize
                if not isinstance(df, pd.DataFrame):
                    df = pd.json_normalize(df)
        except ValueError:
            with open(path, "r", encoding=encoding) as f:
                obj = json.load(f)
            df = pd.json_normalize(obj)

        self.write_csv(df, out_path, encoding=encoding, index=False)
        outputs.append(out_path)
        return outputs

    def convert_html(self, encoding: str) -> List[Path]:
        """Convert all tables in an HTML file into separate CSVs."""
        path = self.source
        out_dir = self.destination
        outputs: List[Path] = []
        tables = pd.read_html(path, encoding=encoding)  # requires lxml
        for i, df in enumerate(tables, start=1):
            out_path = out_dir / f"{path.stem}__table_{i}.csv"
            self.write_csv(df, out_path, encoding=encoding, index=False)
            outputs.append(out_path)
        return outputs

    def convert_xml(self, encoding: str) -> List[Path]:
        """Convert simple XML table structures to CSV."""
        path = self.source
        out_dir = self.destination
        try:
            df = pd.read_xml(path)
        except Exception as e:
            raise RuntimeError(f"Failed to parse XML {path}: {e}") from e
        out_path = out_dir / (path.stem + ".csv")
        self.write_csv(df, out_path, encoding=encoding, index=False)
        return [out_path]

    def convert(self, encoding: str = "utf-8", chunksize: Optional[int] = None) -> List[Path]:
        """Dispatch based on extension."""
        ext = self.source.suffix.lower()
        if ext in {".csv", ".tsv", ".txt"}:
            return self.convert_csv_tsv_txt(encoding, chunksize)
        elif ext in {".xlsx", ".xls"}:
            return self.convert_excel(encoding)
        elif ext == ".parquet":
            return self.convert_parquet(encoding, chunksize)
        elif ext == ".feather":
            return self.convert_feather(encoding)
        elif ext == ".json":
            return self.convert_json(encoding)
        elif ext in {".html", ".htm"}:
            return self.convert_html(encoding)
        elif ext == ".xml":
            return self.convert_xml(encoding)
        elif ext == ".orc":
            if not _HAS_PYARROW:
                raise RuntimeError("ORC requires pyarrow; install pyarrow to read ORC files.")
            import pyarrow.orc as pa_orc
            with pa_orc.ORCFile(str(self.source)) as of:
                tbl = of.read()
            df = tbl.to_pandas()
            out_path = self.destination / (self.source.stem + ".csv")
            self.write_csv(df, out_path, encoding=encoding, index=False)
            return [out_path]
        else:
            raise ValueError(f"Unsupported file type: {ext}")


# ---------- CLI utilities ----------

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

    converted: List[Path] = []
    errors: List[Tuple[Path, str]] = []

    for path in iter_paths(in_path, args.pattern, args.recursive):
        if not path.is_file():
            continue
        try:
            extractor = Extract(source=path, destination=out_dir)
            outs = extractor.convert(encoding=args.encoding, chunksize=args.chunksize)
            converted.extend(outs)
            print(f"✔ Converted: {path} -> {', '.join(str(o) for o in outs)}")
        except Exception as e:
            msg = f"✖ Error converting {path}: {e}"
            print(msg, file=sys.stderr)
            errors.append((path, str(e)))

    print("\nSummary:")
    print(f"  Converted files: {len(converted)}")
    print(f"  Errors: {len(errors)}")
    if errors:
        for p, m in errors:
                       print(f"    - {p}: {m}")


if __name__ == "__main__":
    main()
