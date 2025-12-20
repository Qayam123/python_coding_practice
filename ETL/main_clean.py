# main_clean.py
import pandas as pd
from pathlib import Path
from src.schema import DataSchema, CleaningConfig
from src.cleaning import clean_raw
from src.pipeline import build_preprocess_pipeline

def main(
    input_csv: str = "data/raw.csv",
    output_csv: str = "data/cleaned.csv",
):
    # 1) Define schema for your dataset
    schema = DataSchema(
        target="is_fraud",                     # or None if not supervised
        numeric=["amount", "hour", "account_age_days", "tx_count_24h", "merchant_risk_score"],
        categorical=["country", "device_type", "channel"],
        datetime=["event_time"],               # example
        text=["user_notes"],                   # example
        id_like=["transaction_id"],            # example
        drop=["redundant_col"],                # example
    )

    # 2) Configure cleaning
    cfg = CleaningConfig(
        numeric_impute_strategy="median",
        categorical_impute_strategy="most_frequent",
        one_hot_min_frequency=0.01,
        cap_outliers=True,
        outlier_method="iqr",
        iqr_k=1.5,
        normalize_text=True,
        expand_datetime_parts=True,
        drop_original_datetime=False,
        drop_duplicates=True,
        max_missing_frac_to_drop_col=0.98,
        max_cardinality_for_one_hot=200,
        scale_numeric=True,
    )

    # 3) Load
    df = pd.read_csv(input_csv)

    # 4) Split out target (if present)
    y = None
    if schema.target and schema.target in df.columns:
        y = df[schema.target]
        X = df.drop(columns=[schema.target])
    else:
        X = df

    # 5) Clean raw
    X_clean = clean_raw(X, schema, cfg)

    # 6) Persist cleaned data (optional)
    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    X_out = X_clean.copy()
    if y is not None:
        X_out[schema.target] = y.values
    X_out.to_csv(output_csv, index=False)

    # 7) Build preprocessing pipeline (fit on cleaned training sample)
    pre_pipe, feature_names = build_preprocess_pipeline(schema, cfg, df_fit_sample=X_clean)
    # You can now integrate `pre_pipe` with a model: Pipeline([("pre", pre_pipe), ("clf", ...)])

    print(f"Cleaned rows: {len(X_clean):,}")
    print(f"Output saved to: {output_csv}")
    if feature_names:
        print(f"Transformed features: {len(feature_names)}")

if __name__ == "__main__":
    main()
