import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
import config

class RoleClassifier:
    def __init__(self):
        self.model_path = config.MODELS_DIR / 'role_model.pkl'
        self.scaler_path = config.MODELS_DIR / 'scaler.pkl'
        self.metadata_path = config.MODELS_DIR / 'model_metadata.json'
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.load_or_initialize()

    def load_or_initialize(self):
        if self.model_path.exists() and self.scaler_path.exists():
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            if self.metadata_path.exists():
                import json
                with open(self.metadata_path, 'r') as f:
                    meta = json.load(f)
                    self.feature_names = meta.get('feature_names', [])
        else:
            self.model = RandomForestClassifier(n_estimators=120, max_depth=14, random_state=config.RANDOM_STATE)
            self.scaler = StandardScaler()

    def train(self, X: np.ndarray, y: List[str], feature_names: List[str] = None):
        self.feature_names = feature_names or []
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=config.RANDOM_STATE, stratify=y)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model.fit(X_train_scaled, y_train)
        train_acc = self.model.score(X_train_scaled, y_train)
        test_acc = self.model.score(X_test_scaled, y_test)
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
            
        import json
        with open(self.metadata_path, 'w') as f:
            json.dump({
                'feature_names': self.feature_names,
                'train_accuracy': round(float(train_acc), 4),
                'test_accuracy': round(float(test_acc), 4),
                'classes': list(self.model.classes_)
            }, f, indent=2)
            
        return {'train_acc': train_acc, 'test_acc': test_acc}

    def predict_roles(self, feature_vector: np.ndarray) -> pd.DataFrame:
        if self.model is None or self.scaler is None:
            self.load_or_initialize()
            
        feat_2d = feature_vector.reshape(1, -1)
        feat_scaled = self.scaler.transform(feat_2d)
        
        probabilities = self.model.predict_proba(feat_scaled)[0]
        classes = self.model.classes_
        
        results = []
        for role, prob in zip(classes, probabilities):
            suitability = round(float(prob) * 100, 1)
            results.append({
                'role': role,
                'suitability_score': suitability,
                'raw_prob': round(float(prob), 4)
            })
            
        df = pd.DataFrame(results).sort_values(by='suitability_score', ascending=False).reset_index(drop=True)
        df['rank'] = df.index + 1
        return df
