import os
import yaml
from pathlib import Path
from pydantic import BaseModel, ValidationError
from typing import Optional


class HeaderSchema(BaseModel):
    name: str
    email: str
    phone: str
    title: str


class RoleSchema(BaseModel):
    role: str
    company: str
    start: str
    end: Optional[str]
    location: str
    contract: Optional[bool] = None
    done: str
    stack: str


class ResumeSchema(BaseModel):
    header: HeaderSchema
    roles: list[RoleSchema]


def validate_data(data):
    try:
        return ResumeSchema(**data)
    except ValidationError as e:
        raise ValueError(f"Validation error: {e}")


def load_data(path=None):
    """Load and validate YAML resume data from path (defaults to repo data.yaml).

    Raises FileNotFoundError or ValueError on error.
    Returns the parsed data mapping.
    """
    ## get path of resume.yaml
    
    root = Path(__file__).parent.parent
    yaml_path = Path(root) / "data/resume.yaml"
    if not os.path.exists(yaml_path):
        raise FileNotFoundError('data.yaml was not found in the repository root.')

    with open(yaml_path, 'r', encoding='utf-8') as yf:
        data = yaml.safe_load(yf) or {}
    # Ensure data is present and is a mapping; fail fast with a clear message.
    if not isinstance(data, dict) or not data:
        raise ValueError('data.yaml is empty or malformed - expected a mapping with resume data')

    # Validate data using ResumeSchema
    return validate_data(data).dict()
