# src/cleaning.py
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Tuple
from .schema import DataSchema, CleaningConfig
from .utils_text import basic_text_normalize

def _coerce_types(df: pd.DataFrame, schema: DataSchema) -> pd.DataFrame:
    df = df.copy()
    for col in schema.numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in schema.categorical:
        if col in df.columns:
            df[col] = df[col].astype("string")
    for col in schema.datetime:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=False, infer_datetime_format=True)
    for col in schema.text:
        if col in df.columns:
            df[col] = df[col].astype("string")
    return df

def _drop_high_missing(df: pd.DataFrame, cfg: CleaningConfig) -> pd.DataFrame:
    frac_missing = df.isna().mean()
    to_drop = frac_missing[frac_missing > cfg.max_missing_frac_to_drop_col].index.tolist()
    return df.drop(columns=to_drop, errors="ignore")

def _handle_duplicates(df: pd.DataFrame, schema: DataSchema, cfg: CleaningConfig) -> pd.DataFrame:
    if not cfg.drop_duplicates:
        return df
    if schema.id_like:
        # prefer dropping duplicate IDs only
        dup_mask = df.duplicated(subset=schema.id_like, keep="first")
        return df.loc[~dup_mask].copy()
    # fallback: full row duplicates
    return df.drop_duplicates().copy()

def _cap_outliers_numeric(df: pd.DataFrame, schema: DataSchema, cfg: CleaningConfig) -> pd.DataFrame:
    if not cfg.cap_outliers:
        return df
    df = df.copy()
    for col in schema.numeric:
        if col not in df.columns:
            continue
        s = df[col]
        if s.dtype.kind not in "fi":
            continue
        if cfg.outlier_method == "iqr":
            q1, q3 = s.quantile([0.25, 0.75])
            iqr = q3 - q1
            lo = q1 - cfg.iqr_k * iqr
            hi = q3 + cfg.iqr_k * iqr
            df[col] = s.clip(lower=lo, upper=hi)
        elif cfg.outlier_method == "zscore":
            mu, sigma = s.mean(), s.std(ddof=0)
            if sigma > 0:
                z = (s - mu) / sigma
                df[col] = s.where(z.abs() <= cfg.zscore_threshold, np.sign(z) * cfg.zscore_threshold * sigma + mu)
    return df

def _normalize_text_columns(df: pd.DataFrame, schema: DataSchema, cfg: CleaningConfig) -> pd.DataFrame:
    if not cfg.normalize_text:
        return df
    df = df.copy()
    for col in schema.text:
        if col in df.columns:
            df[col] = df[col].map(lambda x: basic_text_normalize(
                x,
                lowercase=cfg.lowercase_text,
                strip_accents=cfg.strip_accents,
                remove_punct=cfg.remove_punct,
                collapse_whitespace=cfg.collapse_whitespace,
            ))
    return df

def _expand_datetime(df: pd.DataFrame, schema: DataSchema, cfg: CleaningConfig) -> pd.DataFrame:
    if not cfg.expand_datetime_parts or not schema.datetime:
        return df
    df = df.copy()
    for col in schema.datetime:
        if col not in df.columns:
            continue
        dt = pd.to_datetime(df[col], errors="coerce")
        if "year" not in df.columns:
            df[f"{col}__year"] = dt.dt.year
        df[f"{col}__month"] = dt.dt.month
        df[f"{col}__day"] = dt.dt.day
        df[f"{col}__dayofweek"] = dt.dt.dayofweek
        df[f"{col}__hour"] = dt.dt.hour
        if cfg.drop_original_datetime:
            df.drop(columns=[col], inplace=True)
    return df

def clean_raw(
    df: pd.DataFrame,
    schema: DataSchema,
    cfg: CleaningConfig,
) -> pd.DataFrame:
    """
    Pure data cleaning (no leakage-prone imputing/encoding).
    - drop declared columns
    - coerce types
    - drop duplicates
    - drop high-missing columns
    - outlier capping
    - text normalize
    - datetime expansion
    """
    df = df.copy()
    df = df.drop(columns=[c for c in schema.drop if c in df.columns], errors="ignore")
    df = _coerce_types(df, schema)
    df = _handle_duplicates(df, schema, cfg)
    df = _drop_high_missing(df, cfg)
    df = _cap_outliers_numeric(df, schema, cfg)
    df = _normalize_text_columns(df, schema, cfg)
    df = _expand_datetime(df, schema, cfg)
    return df