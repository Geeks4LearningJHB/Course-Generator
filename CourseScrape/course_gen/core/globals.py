"""Centralized imports for the entire project with lazy loading for heavy libraries."""

# Standard Library (Direct imports - lightweight)
import traceback
import json
import os
import time
import re
import random
import logging
from urllib.parse import urljoin
from typing import List, Dict, Optional, Tuple, Any, Union, TYPE_CHECKING
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv

# Third-Party Libraries (Direct imports - medium weight)
import requests
from bs4 import BeautifulSoup
import markdown
import pymongo
from bson.objectid import ObjectId
from tqdm.notebook import tqdm

# MongoDB Client (Instantiated immediately)
MONGO_CLIENT = pymongo.MongoClient("mongodb://localhost:27017/") if pymongo else None

# Logger Setup (Instantiated immediately)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy Importer for Heavy Libraries
class LazyImporter:
    """
    Lazy loader for heavy machine learning libraries.
    Usage:
        from core.globals import lazy
        tokenizer = lazy.transformers.GPT2TokenizerFast.from_pretrained('gpt2')
        model = lazy.transformers.GPT2LMHeadModel.from_pretrained('gpt2')
        tensor = lazy.torch.tensor([1, 2, 3])
    """
    
    def __getattr__(self, name):
        if name == 'torch':
            import torch
            return torch
        elif name == 'transformers':
            import transformers
            return transformers
        elif name == 'np':
            import numpy as np
            return np
        raise AttributeError(f"No lazy import available for {name}")

lazy = LazyImporter()

# Type hints for autocompletion (only active during type checking)
if TYPE_CHECKING:
    import torch
    import transformers
    import numpy as np
else:
    # These won't be imported at runtime
    torch = None
    transformers = None
    np = None