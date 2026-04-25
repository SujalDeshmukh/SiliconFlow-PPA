import random
from typing import Dict, List, Tuple

from ..models import Action, Observation, PlacedBlock, UnplacedBlock


class AsicFloorplannerEnv:
    """ASIC floorplanning environment following OpenEnv-style reset/step semantics."""

    DIE_WIDTH: int = 100
    DIE_HEIGHT: int = 100

    def __init__(self) -> None:
        self.occupancy_map: List[List[int]] = []
        self.unplaced_blocks: List[UnplacedBlock] = []
        self.placed_blocks: Dict[str, PlacedBlock] = {}
        self._block_specs: Dict[str, UnplacedBlock] = {}

    def reset(self) -> Tuple[Observation, float, bool, Dict[str, str]]:
        """Reset the environment and return initial observation tuple."""
        self.occupancy_map = [
            [0 for _ in range(self.DIE_WIDTH)] for _ in range(self.DIE_HEIGHT)
        ]

        block_count = random.randint(5, 8)
        self.unplaced_blocks = []
        self.placed_blocks = {}
        self._block_specs = {}

        for i in range(block_count):
            block: UnplacedBlock = {
                "id": f"blk_{i + 1}",
                "w": random.randint(5, 20),
                "h": random.randint(5, 20),
                "p": round(random.uniform(0.5, 5.0), 3),
            }
            self.unplaced_blocks.append(block)
            self._block_specs[block["id"]] = block

        observation = Observation(
            die_width=self.DIE_WIDTH,
            die_height=self.DIE_HEIGHT,
            unplaced_blocks=self.unplaced_blocks,
            placed_blocks=self.placed_blocks,
            occupancy_map=self.occupancy_map,
        )
        return observation, 0.0, False, {}

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, str]]:
        """Execute one placement action and return (observation, reward, done, info)."""
        block_id = action.block_id
        x = action.x
        y = action.y
        orientation = action.orientation

        if x < 0 or y < 0 or orientation not in (0, 90, 180, 270):
            return self._build_result(-100.0, True, {"reason": "collision"})

        block = next((b for b in self.unplaced_blocks if b["id"] == block_id), None)
        if block is None:
            return self._build_result(-100.0, True, {"reason": "collision"})

        w = block["w"]
        h = block["h"]
        if orientation in (90, 270):
            w, h = h, w

        # Anti-hacking boundary check.
        if (x + w) > self.DIE_WIDTH or (y + h) > self.DIE_HEIGHT:
            return self._build_result(-100.0, True, {"reason": "collision"})

        # Anti-hacking overlap check.
        for row in range(y, y + h):
            for col in range(x, x + w):
                if self.occupancy_map[row][col] == 1:
                    return self._build_result(-100.0, True, {"reason": "collision"})

        for row in range(y, y + h):
            for col in range(x, x + w):
                self.occupancy_map[row][col] = 1

        self.placed_blocks[block_id] = {"x": x, "y": y, "orientation": orientation}
        self.unplaced_blocks = [b for b in self.unplaced_blocks if b["id"] != block_id]

        reward = 0.0
        bounding_area = self._final_bounding_box_area()
        if bounding_area > 0:
            reward += 1000.0 / float(bounding_area)

        reward -= self._thermal_penalty_for(block_id)

        done = len(self.unplaced_blocks) == 0
        return self._build_result(reward, done, {"reason": "ok"})

    def _build_result(
        self, reward: float, done: bool, info: Dict[str, str]
    ) -> Tuple[Observation, float, bool, Dict[str, str]]:
        observation = Observation(
            die_width=self.DIE_WIDTH,
            die_height=self.DIE_HEIGHT,
            unplaced_blocks=self.unplaced_blocks,
            placed_blocks=self.placed_blocks,
            occupancy_map=self.occupancy_map,
        )
        return observation, reward, done, info

    def _placed_rect(self, block_id: str) -> Tuple[int, int, int, int]:
        block = self._block_specs[block_id]
        placement = self.placed_blocks[block_id]
        w = block["w"]
        h = block["h"]
        if placement["orientation"] in (90, 270):
            w, h = h, w
        x0 = placement["x"]
        y0 = placement["y"]
        return x0, y0, x0 + w, y0 + h

    def _final_bounding_box_area(self) -> int:
        if not self.placed_blocks:
            return 0

        min_x = self.DIE_WIDTH
        min_y = self.DIE_HEIGHT
        max_x = 0
        max_y = 0
        for block_id in self.placed_blocks:
            x0, y0, x1, y1 = self._placed_rect(block_id)
            min_x = min(min_x, x0)
            min_y = min(min_y, y0)
            max_x = max(max_x, x1)
            max_y = max(max_y, y1)
        return max(1, (max_x - min_x) * (max_y - min_y))

    def _thermal_penalty_for(self, new_block_id: str) -> float:
        new_block_spec = self._block_specs[new_block_id]
        if new_block_spec["p"] <= 3.0:
            return 0.0

        nx0, ny0, nx1, ny1 = self._placed_rect(new_block_id)
        penalty = 0.0

        for other_id in self.placed_blocks:
            if other_id == new_block_id:
                continue

            other_spec = self._block_specs[other_id]
            if other_spec["p"] <= 3.0:
                continue

            ox0, oy0, ox1, oy1 = self._placed_rect(other_id)
            horizontal_adjacent = (nx1 == ox0 or ox1 == nx0) and not (
                ny1 <= oy0 or oy1 <= ny0
            )
            vertical_adjacent = (ny1 == oy0 or oy1 == ny0) and not (
                nx1 <= ox0 or ox1 <= nx0
            )

            if horizontal_adjacent or vertical_adjacent:
                penalty += 20.0

        return penalty
