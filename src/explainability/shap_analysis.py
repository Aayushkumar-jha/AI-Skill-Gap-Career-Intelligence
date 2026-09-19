import numpy as np
import pandas as pd
from typing import Dict, List, Any

class ExplainabilityEngine:
    def __init__(self, classifier, feature_names: List[str]):
        self.classifier = classifier
        self.feature_names = feature_names

    def explain_candidate_prediction(self, feature_vector: np.ndarray, target_role: str) -> Dict[str, Any]:
        feat_scaled = self.classifier.scaler.transform(feature_vector.reshape(1, -1))[0]
        
        # Determine base weights from model tree importances or linear coefficients
        if hasattr(self.classifier.model, 'feature_importances_'):
            importances = self.classifier.model.feature_importances_
        else:
            importances = np.ones(len(self.feature_names)) / len(self.feature_names)
            
        contributions = feat_scaled * importances
        
        factors = []
        for name, val, cont in zip(self.feature_names, feature_vector, contributions):
            # Clean human readable name
            clean_name = name.replace('RoleFit_', 'Role Fit: ').replace('Cat_', 'Domain: ').replace('_', ' ')
            is_pos = cont >= 0
            factors.append({
                'feature': clean_name,
                'raw_value': round(float(val), 2),
                'contribution': round(float(cont), 3),
                'direction': 'Positive Driver' if is_pos else 'Missing Gap Penalty'
            })
            
        df_factors = pd.DataFrame(factors)
        pos_drivers = df_factors[df_factors['contribution'] > 0].sort_values(by='contribution', ascending=False).head(6).to_dict(orient='records')
        neg_drivers = df_factors[df_factors['contribution'] <= 0].sort_values(by='contribution').head(6).to_dict(orient='records')
        
        return {
            'target_role': target_role,
            'positive_drivers': pos_drivers,
            'negative_penalties': neg_drivers,
            'all_factors': factors
        }
