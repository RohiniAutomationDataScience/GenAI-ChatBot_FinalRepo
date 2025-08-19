# ============================================================================= 
# © 2025 [SapkalRohini77@gmail.com]. All rights reserved. 
# This code is shared for evaluation purposes only with [NorthBay] 
# Unauthorized use, copying, or redistribution is prohibited.
# =============================================================================    

# lib/utils/common.py

import re

def normalize(text: str) -> str:
    """
    Normalize text by converting to lowercase and removing punctuation.
    Useful for semantic/fact matching.
    """
    return re.sub(r"[^\w\s]", "", text.lower())
    
def _norm(t:str)->str:
    t = re.sub(r"[•\-–·]\s*", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip().lower()