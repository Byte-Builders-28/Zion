# backend/routes/rl_routes.py
from fastapi import APIRouter
from ml.simulation_loop import agent, start_simulation_background, ACTIONS, N_ACTIONS

router = APIRouter()

@router.post("/api/rl/start")
def start_rl(episodes: int = 10):
    return start_simulation_background(episodes)

@router.get("/api/rl/status")
def rl_status():
    "Returns Q-table + history for the frontend RL visualisation"
    attack_names = [ACTIONS[i][0] for i in range(N_ACTIONS)]
    return {
        "episode":      agent.episode,
        "epsilon":      round(agent.epsilon, 3),
        "q_table":      agent.q_table.tolist(),
        "attack_names": attack_names,
        "history":      agent.history[-20:],
        "best_attack":  agent.best_attack_for_state(0)
    }
