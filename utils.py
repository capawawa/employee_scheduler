from pathlib import Path
from typing import List
import pandas as pd

def validate_csv_file(file_path: str, required_columns: List[str]) -> bool:
    """
    Validates CSV file format and content.
    
    Args:
        file_path: Path to the CSV file
        required_columns: List of required column names
    
    Raises:
        ValueError: If file is invalid
    """
    path = Path(file_path)
    if not path.exists():
        raise ValueError(f"File not found: {file_path}")
    
    if path.suffix.lower() != '.csv':
        raise ValueError("File must be a CSV")
        
    if path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
        raise ValueError("File too large")
        
    df = pd.read_csv(file_path)
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    return True 