# Location: backend/app/utils/logger.py

import logging
from logging.handlers import RotatingFileHandler
import sys

# Create logger
logger = logging.getLogger("voice_ai_agent")
logger.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler (rotating)
file_handler = RotatingFileHandler("logs/voice_ai_agent.log", maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
