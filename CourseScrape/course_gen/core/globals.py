"""Centralized imports for the entire project with lazy loading for heavy libraries."""

# Standard Library (Direct imports - lightweight)
from __future__ import annotations
import traceback
import json
import os
import time
import unicodedata
import re
import random
import logging
import urllib
import hashlib
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Tuple, Any, Union, Set, TYPE_CHECKING
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import asyncio
import nest_asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from copy import copy
import sys
from rest_framework import serializers
from threading import Lock
import uuid
from datetime import datetime
# APIs
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from trafilatura import extract

# Third-Party Libraries (Direct imports - medium weight)
import requests
from bs4 import BeautifulSoup
import markdown
import pymongo
from bson.objectid import ObjectId
from tqdm.notebook import tqdm
import aiohttp


# MongoDB Client (Instantiated immediately)
MONGO_CLIENT = pymongo.MongoClient("mongodb://localhost:27017/") if pymongo else None

# Logger Setup (Instantiated immediately)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


from typing import TYPE_CHECKING

class LazyLoader:
    """
    Lazy loader for heavy ML libraries, including transformers and accelerate.
    Caches imports to avoid repeated imports.
    """

    _cache = {}

    def __getattr__(self, name):
        if name in self._cache:
            return self._cache[name]

        if name == 'torch':
            import torch
            self._cache[name] = torch
        elif name == 'transformers':
            import transformers
            self._cache[name] = transformers
        elif name == 'accelerate':
            try:
                import accelerate
                self._cache[name] = accelerate
            except ImportError:
                # Optional: Warn user about missing accelerate if used
                raise ImportError(
                    "The 'accelerate' package is required for device_map or tp_plan. "
                    "Install with: pip install accelerate"
                )
        elif name == 'np':
            import numpy as np
            self._cache[name] = np
        elif name == 'AutoTokenizer':
            from transformers import AutoTokenizer
            self._cache[name] = AutoTokenizer
        elif name == 'AutoModelForCausalLM':
            from transformers import AutoModelForCausalLM
            self._cache[name] = AutoModelForCausalLM
        else:
            raise AttributeError(f"No lazy import available for {name}")

        return self._cache[name]


lazy = LazyLoader()

if TYPE_CHECKING:
    import torch
    import transformers
    import accelerate
    import numpy as np
else:
    torch = None
    transformers = None
    accelerate = None
    np = None