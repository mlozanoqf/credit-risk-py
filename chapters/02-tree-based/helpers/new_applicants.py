"""Apply a fixed training encoding to incoming credit applications."""
import numpy as np
import pandas as pd
from shared.scoring import design


def make_xgb_encoder(training, reference_columns):
    categories = {name: training[name].cat.categories.copy()
                  for name in ('grade', 'home', 'sex', 'region')}
    required = ['age', 'int', 'grade', 'l_amnt', 'income',
                'emp_len', 'home', 'sex', 'region']
    reference_columns = list(reference_columns)
    if list(design(training, intercept=False).columns) != reference_columns:
        raise ValueError('Training schema differs from fitted model columns.')

    def encode(applicants):
        if applicants.empty or not set(required).issubset(applicants.columns):
            raise ValueError('Supply at least one applicant and every predictor.')
        frame = applicants[required].copy()
        for name, levels in categories.items():
            if frame[name].isna().any() or not frame[name].isin(levels).all():
                raise ValueError(f'Missing or unseen category in {name}; review before scoring.')
            frame[name] = pd.Categorical(frame[name], categories=levels)
        numeric = [name for name in required if name not in categories]
        if not all(pd.api.types.is_numeric_dtype(frame[name]) for name in numeric):
            raise ValueError('Numeric predictors must be numbers.')
        if not np.isfinite(frame[numeric].to_numpy(float)).all():
            raise ValueError('Numeric predictors must be finite.')
        if (frame[['l_amnt', 'income']] <= 0).any().any():
            raise ValueError('Loan amount and income must be positive before taking logs.')
        encoded = design(frame, intercept=False)
        if list(encoded.columns) != reference_columns or not np.isfinite(encoded).all().all():
            raise ValueError('New applicants do not match the fitted model schema.')
        return encoded

    return encode
