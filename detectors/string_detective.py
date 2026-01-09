import pandas as pd
from typing import Dict, Any, List, Tuple
from core.base import BaseDetector

class StringDetective(BaseDetector):
    @property
    def name(self) -> str:
        return "String Detective"

    @property
    def description(self) -> str:
        return "Detects near-duplicate entity names (Ghost Vendors) using Levenshtein distance."

    def run(self, df: pd.DataFrame, name_col: str = 'vendor_name') -> Dict[str, Any]:
        """
        Identifies similar names that might be the same entity with slight variations.
        """
        unique_names = df[name_col].unique().tolist()
        potential_duplicates = []
        
        # O(N^2) - suitable for small to medium lists, or could be optimized with blocking
        for i in range(len(unique_names)):
            for j in range(i + 1, len(unique_names)):
                name1 = str(unique_names[i])
                name2 = str(unique_names[j])
                
                score = self.levenshtein_ratio(name1.lower(), name2.lower())
                
                if 0.85 <= score < 1.0: # High similarity but not identical
                    potential_duplicates.append((name1, name2, float(score)))

        return {
            "detector": self.name,
            "potential_ghost_vendors": sorted(potential_duplicates, key=lambda x: x[2], reverse=True)[:20],
            "explanation": "Finds names with high Levenshtein similarity. This often reveals 'Ghost Vendors' or split identities."
        }

    def levenshtein_ratio(self, s1: str, s2: str) -> float:
        """
        Hand-rolled Levenshtein distance ratio to keep Zero AI / Zero dependency.
        """
        rows = len(s1) + 1
        cols = len(s2) + 1
        distance = [[0 for _ in range(cols)] for _ in range(rows)]

        for i in range(1, rows):
            distance[i][0] = i
        for i in range(1, cols):
            distance[0][i] = i

        for col in range(1, cols):
            for row in range(1, rows):
                if s1[row-1] == s2[col-1]:
                    cost = 0
                else:
                    cost = 1
                distance[row][col] = min(distance[row-1][col] + 1,      # Deletion
                                     distance[row][col-1] + 1,          # Insertion
                                     distance[row-1][col-1] + cost)     # Substitution

        ratio = ((len(s1) + len(s2)) - distance[row][col]) / (len(s1) + len(s2))
        return ratio
