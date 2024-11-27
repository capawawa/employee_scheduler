import logging
from pathlib import Path

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "scheduler.log"),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)
logger.info("Starting scheduler application with %d workers", 1) 