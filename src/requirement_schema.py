from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator

class RequirementModel(BaseModel):
    req_id: str = Field(..., pattern=r"^SYS\.2-BMS-\d{3}$")
    title: str
    description: str
    asil: str = Field(..., pattern=r"^ASIL-[A-D]$")
    parameters: Dict[str, Any]
    scenarios: List[Dict[str, Any]]

    @field_validator("req_id")
    def validate_req_id(cls, v):
        if not v.startswith("SYS.2-BMS-"):
            raise ValueError("Requirement ID must follow format SYS.2-BMS-XXX")
        return v