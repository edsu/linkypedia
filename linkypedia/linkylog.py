"""
Common logging for linkypedia.log
"""

import logging

logging.basicConfig(
        filename="linkypedia.log", 
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s")

log = logging.getLogger()
