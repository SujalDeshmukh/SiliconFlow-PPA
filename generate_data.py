import json
import random
import os

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

def generate_chip_tasks(count=100):
    tasks = []
    for i in range(count):
        # Determine difficulty
        if i < 30:
            diff, num_macros, die_size = "easy", random.randint(3, 5), (500, 500)
        elif i < 70:
            diff, num_macros, die_size = "medium", random.randint(8, 12), (800, 800)
        else:
            diff, num_macros, die_size = "hard", random.randint(15, 25), (1000, 1000)

        # 1. Generate Macros
        macros = []
        for j in range(num_macros):
            macros.append({
                "id": f"M{j}",
                "width": random.randint(40, 120),
                "height": random.randint(40, 120),
                "power": random.uniform(0.5, 2.0) # High power = heat risk!
            })

        # 2. Generate Netlist (Connections)
        netlist = []
        # Connect each macro to at least one other to ensure no "islands"
        for j in range(num_macros - 1):
            netlist.append({
                "source": f"M{j}",
                "target": f"M{j+1}",
                "weight": random.randint(1, 5)
            })

        tasks.append({
            "task_id": f"CHIP_{i:03d}",
            "die_size": die_size,
            "macros": macros,
            "netlist": netlist,
            "difficulty": diff
        })
    return tasks

# Execute and Save
chip_library = generate_chip_tasks()
with open("data/tasks.json", "w") as f:
    json.dump(chip_library, f, indent=4)

print(f"✅ Successfully generated {len(chip_library)} tasks in data/tasks.json")