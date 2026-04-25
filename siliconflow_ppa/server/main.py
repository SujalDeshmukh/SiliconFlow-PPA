from fastapi import FastAPI
from env import AsicFloorplannerEnv
from models import Action, Observation

app = FastAPI(title="SiliconFlow-PPA Environment")
# Initialize your physics engine
environment = AsicFloorplannerEnv()

@app.post("/reset")
def reset():
    # Returns (observation, reward, done, info)
    obs, reward, done, info = environment.reset()
    return {"observation": obs, "reward": reward, "done": done, "info": info}

@app.post("/step")
def step(action: Action):
    # Returns (observation, reward, done, info)
    obs, reward, done, info = environment.step(action)
    return {"observation": obs, "reward": reward, "done": done, "info": info}

@app.get("/state")
def get_state():
    # Useful for Member 2 to check the current board
    return environment._build_result(0, False, {"status": "monitoring"})[0]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)