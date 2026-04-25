
from typing import List, Dict, Literal, Optional  # Added Literal here
from typing_extensions import TypedDict

from pydantic import BaseModel, Field


class UnplacedBlock(TypedDict):
    id: str
    w: int
    h: int
    p: float


class PlacedBlock(TypedDict):
    x: int
    y: int
    orientation: Literal[0, 90, 180, 270]


class Action(BaseModel):
    block_id: str = Field(
        ...,
        description="The unique identifier of the block being placed.",
    )
    x: int = Field(
        ...,
        description="The X-coordinate for the bottom-left corner.",
    )
    y: int = Field(
        ...,
        description="The Y-coordinate for the bottom-left corner.",
    )
    orientation: Literal[0, 90, 180, 270] = Field(
        ...,
        description="Strictly limited block rotation (degrees).",
    )


class Observation(BaseModel):
    die_width: int
    die_height: int
    unplaced_blocks: List[UnplacedBlock]
    placed_blocks: Dict[str, PlacedBlock]
    occupancy_map: List[List[int]]
