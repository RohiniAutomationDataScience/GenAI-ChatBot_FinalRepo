# ============================================================================= 
# © 2025 [SapkalRohini77@gmail.com]. All rights reserved. 
# This code is shared for evaluation purposes only with [NorthBay] 
# Unauthorized use, copying, or redistribution is prohibited.
# =============================================================================    

from sentence_transformers import SentenceTransformer, util
from functools import lru_cache
@lru_cache(maxsize=2)
def _model(name:str):
    return SentenceTransformer(name)
def sim_en(a:str,b:str)->float:
    m=_model("all-MiniLM-L6-v2")
    return float(util.cos_sim(m.encode(a), m.encode(b)))
def sim_xl(a:str,b:str)->float:
    m=_model("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    return float(util.cos_sim(m.encode(a), m.encode(b)))
