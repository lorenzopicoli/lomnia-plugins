from typing import Optional

from pydantic import BaseModel, ConfigDict


class MyEntity(BaseModel):
    model_config = ConfigDict(
        extra="ignore",  # ignore unexpected fields
        validate_assignment=True,  # re-validate on mutation if you ever change fields
    )

    id: Optional[int]

    # ...
