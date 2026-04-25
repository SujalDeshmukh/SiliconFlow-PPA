from pydantic import BaseModel
from typing import List, Tuple

class Macro(BaseModel):
    id: str
    width: int
    height: int
    power: float  # Helps calculate thermal hotspots

class Connection(BaseModel):
    source: str
    target: str
    weight: int  # Number of wires (higher = must be closer)

class ChipTask(BaseModel):
    task_id: str
    die_size: Tuple[int, int]  # [Width, Height]
    macros: List[Macro]
    netlist: List[Connection]
    difficulty: str  # easy, medium, hard