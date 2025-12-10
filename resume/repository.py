import os
import yaml
from pathlib import Path
from pydantic import BaseModel, ValidationError, Field
from typing import Optional
from enum import Enum


class HeaderSchema(BaseModel):
    name: str
    email: str
    phone: str
    title: str
    contact: Optional[str] = ''


class EmploymentType(Enum):
    PERMANENT = "permanent"
    CONTRACT = "contract"


class RoleSchema(BaseModel):
    role: str
    company: str
    # start and end must be in YYYY-MM format (e.g., 2025-01)
    start: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    end: Optional[str] = Field(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    location: str
    employment: EmploymentType 
    done: str
    stack: str
    # Optional flags and computed fields used by PDF renderer
    is_hybrid: Optional[bool] = False
    dates: Optional[str] = ''


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

    # Validate data using ResumeSchema and return the DTO instance
    return validate_data(data)
