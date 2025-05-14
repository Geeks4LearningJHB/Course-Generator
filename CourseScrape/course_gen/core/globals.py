"""Centralized imports for the entire project with lazy loading for heavy libraries."""

# Standard Library (Direct imports - lightweight)
from __future__ import annotations
import traceback
import json
import os
import time
import re
import random
import logging
import urllib
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


# Lazy Importer for Heavy Libraries
class LazyLoader:
    """
    Lazy loader for heavy machine learning libraries.
    Caches imported modules to avoid multiple imports.
    Usage:
        from core.globals import lazy
        tokenizer = lazy.transformers.GPT2TokenizerFast.from_pretrained('gpt2')
        model = lazy.transformers.GPT2LMHeadModel.from_pretrained('gpt2')
        tensor = lazy.torch.tensor([1, 2, 3])
        with lazy.playwright() as p:
            ...
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
        elif name == 'np':
            import numpy as np
            self._cache[name] = np
        #elif name == 'async_playwright': # Call using async with lazy.playwright()() as p
            #from playwright.async_api import async_playwright
            #self._cache[name] = lambda: async_playwright()
        else:
            raise AttributeError(f"No lazy import available for {name}")

        return self._cache[name]

lazy = LazyLoader()


# Type hints for autocompletion (only active during type checking)
if TYPE_CHECKING:
    import torch
    import transformers
    import numpy as np
    #from playwright.async_api import async_playwright
else:
    # These won't be imported at runtime
    torch = None
    transformers = None
    np = None
    #async_playwright = None