# src/schema.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class DataSchema:
    target: Optional[str] = None
    numeric: List[str] = field(default_factory=list)
    categorical: List[str] = field(default_factory=list)
    datetime: List[str] = field(default_factory=list)
    text: List[str] = field(default_factory=list)
    id_like: List[str] = field(default_factory=list)  # e.g., transaction_id
    drop: List[str] = field(default_factory=list)     # columns to drop early

@dataclass
class CleaningConfig:
    # Missing values
    numeric_impute_strategy: str = "median"      # "mean" | "median" | "most_frequent" | "constant"
    categorical_impute_strategy: str = "most_frequent"
    text_impute_fill_value: str = "unknown"

    # Encoding / Scaling
    one_hot_min_frequency: float | int = 0.01    # treat infrequent cats as "other"
    scale_numeric: bool = True                   # StandardScaler on numeric

    # Outliers
    cap_outliers: bool = True
    outlier_method: str = "iqr"                  # "iqr" | "zscore"
    iqr_k: float = 1.5
    zscore_threshold: float = 4.0

    # Text cleaning
    normalize_text: bool = True
    lowercase_text: bool = True
    strip_accents: bool = True
    remove_punct: bool = True
    collapse_whitespace: bool = True

    # Datetime
    expand_datetime_parts: bool = True           # add year, month, day, dow, hour if present
    drop_original_datetime: bool = False

    # General
    drop_duplicates: bool = True
    max_missing_frac_to_drop_col: float = 0.98   # drop columns missing >98% values
    max_cardinality_for_one_hot: int = 200       # avoid exploding one-hot
