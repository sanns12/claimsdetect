"""
Model Loader - XGBoost model training, loading, saving
Includes SMOTE for balancing and evaluation metrics
"""

import xgboost as xgb
import joblib
import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, recall_score, precision_score, f1_score

def train_model(X_train, y_train, X_test, y_test, target_ratio=0.4, random_state=42):
    """
    Train XGBoost model with SMOTE balancing
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        target_ratio: Target fraud ratio after SMOTE (default 0.4 = 40%)
        random_state: Random seed for reproducibility
        
    Returns:
        trained model, metrics dictionary
    """
    print("Applying SMOTE to balance training data...")
    
    # Apply SMOTE
    smote = SMOTE(random_state=random_state, sampling_strategy=target_ratio)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    
    print(f"  Before SMOTE - Non-fraud: {(y_train == 0).sum()}, Fraud: {(y_train == 1).sum()}")
    print(f"  After SMOTE  - Non-fraud: {(y_train_resampled == 0).sum()}, Fraud: {(y_train_resampled == 1).sum()}")
    
    # Calculate scale_pos_weight for XGBoost
    non_fraud = (y_train_resampled == 0).sum()
    fraud = (y_train_resampled == 1).sum()
    scale_pos_weight = non_fraud / fraud
    print(f"  scale_pos_weight: {scale_pos_weight:.2f}")
    
    # Train model
    print("Training XGBoost model...")
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        random_state=random_state,
        eval_metric='logloss',
        use_label_encoder=False
    )
    
    model.fit(X_train_resampled, y_train_resampled)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    cm = confusion_matrix(y_test, y_pred)
    
    # Handle case where test set might have only one class
    if len(np.unique(y_test)) > 1:
        recall = recall_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
    else:
        # Only one class in test set
        if (y_test == 1).sum() > 0:  # Only fraud
            recall = (y_pred == 1).sum() / len(y_test) if len(y_test) > 0 else 0
            precision = recall if (y_pred == 1).sum() > 0 else 0
        else:  # Only legit
            recall = 0
            precision = 0
        f1 = 0
    
    metrics = {
        'recall': recall,
        'precision': precision,
        'f1_score': f1,
        'confusion_matrix': cm.tolist(),
        'feature_importance': dict(zip(X_train.columns if hasattr(X_train, 'columns') else range(X_train.shape[1]), 
                                       model.feature_importances_))
    }
    
    print(f"  Recall: {recall:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  F1 Score: {f1:.4f}")
    
    return model, metrics

def save_model(model, path):
    """
    Save trained model to disk
    
    Args:
        model: Trained XGBoost model
        path: File path to save to
    """
    joblib.dump(model, path)
    print(f"✅ Model saved to {path}")

def load_model(path):
    """
    Load trained model from disk
    
    Args:
        path: File path to load from
        
    Returns:
        Loaded XGBoost model
    """
    try:
        model = joblib.load(path)
        print(f"✅ Model loaded from {path}")
        return model
    except Exception as e:
        print(f"❌ Error loading model from {path}: {e}")
        return None

def train_test_split_stratified(X, y, test_size=0.2, random_state=42):
    """
    Perform stratified train-test split to maintain class distribution
    
    Args:
        X: Features
        y: Labels
        test_size: Proportion for test set
        random_state: Random seed
        
    Returns:
        X_train, X_test, y_train, y_test
    """
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
