
# src/pipeline.py
from __future__ import annotations
import pandas as pd
from typing import Tuple, Optional
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .schema import DataSchema, CleaningConfig

def build_preprocess_pipeline(
    schema: DataSchema,
    cfg: CleaningConfig,
    df_fit_sample: Optional[pd.DataFrame] = None,
) -> Tuple[Pipeline, list[str]]:
    """
    Returns:
      - sklearn Pipeline that transforms features into model-ready numpy array
      - list of feature names after transformation (best effort for OHE)
    """
    num_cols = [c for c in schema.numeric if c in (df_fit_sample.columns if df_fit_sample is not None else schema.numeric)]
    cat_cols = [c for c in schema.categorical if c in (df_fit_sample.columns if df_fit_sample is not None else schema.categorical)]
    text_cols = [c for c in schema.text if c in (df_fit_sample.columns if df_fit_sample is not None else schema.text)]
    # For a light template, treat text as categorical after normalization; in real projects use vectorizers.
    cat_cols += text_cols

    numeric_steps = []
    numeric_steps.append(("impute", SimpleImputer(strategy=cfg.numeric_impute_strategy)))
    if cfg.scale_numeric:
        numeric_steps.append(("scale", StandardScaler()))
    numeric_pipe = Pipeline(steps=numeric_steps)

    # OneHot with min_frequency to bucket rare categories (sklearn>=1.1)
    ohe = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=False,
        min_frequency=cfg.one_hot_min_frequency if isinstance(cfg.one_hot_min_frequency, (float, int)) else None,
    )
    categorical_pipe = Pipeline(steps=[
        ("impute", SimpleImputer(strategy=cfg.categorical_impute_strategy, fill_value="unknown")),
        ("ohe", ohe),
    ])

    pre = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, num_cols),
            ("cat", categorical_pipe, cat_cols),
        ],
        remainder="drop",
        sparse_threshold=0.0,
        n_jobs=None,
        verbose_feature_names_out=True,
    )

    pipe = Pipeline(steps=[("pre", pre)])

    # Fit once to extract feature names (optional)
    feature_names = []
    if df_fit_sample is not None:
        pipe.fit(df_fit_sample)
        # Extract names best-effort (sklearn>=1.0)
        try:
            feature_names = pipe.get_feature_names_out().tolist()
        except Exception:
            feature_names = []

    return pipe, feature_names
