# backend/ml/simulation_loop.py
from ml.rl_attacker import RLAttackerAgent, ACTIONS, N_ACTIONS
from ml.detector import score_request
from policy.smolify_client import generate_policy
import time, threading

agent = RLAttackerAgent(epsilon=0.4)

# Try loading previous Q-table — agent remembers past sessions
try:
    agent.load_qtable("backend/ml/models/rl_qtable.npy")
    print("[RL] Agent loaded — it remembers previous attacks")
except:
    print("[RL] Fresh agent — starting from scratch")

def get_defense_state() -> int:
    """
    Reads current defense posture from the system.
    Returns 0-4 based on how many policies are active.
    This is what the RL agent 'observes' about the environment.
    """
    from db.store import count_active_policies
    count = count_active_policies()
    if   count == 0: return 0  # no defense
    elif count <= 2: return 1  # light defense
    elif count <= 4: return 2  # moderate
    elif count <= 6: return 3  # strong
    else:            return 4  # lockdown

def mock_detector(attack_name: str) -> dict:
    "Asks the real ML detector what score this attack type gets"
    test_requests = {
        "jwt_forgery":       {"ip":"1.2.3.4","endpoint":"/api/admin","token":"forged.jwt.","payload_size":120,"status_code":200},
        "bola_enum":         {"ip":"1.2.3.4","endpoint":"/api/users/247","token":"valid","payload_size":0,"status_code":200},
        "mass_assignment":   {"ip":"1.2.3.4","endpoint":"/api/register","token":"","payload_size":340,"status_code":201},
        "token_refresh_abuse":{"ip":"1.2.3.4","endpoint":"/api/refresh","token":"rt_xyz","payload_size":60,"status_code":200},
        "xxe_injection":     {"ip":"1.2.3.4","endpoint":"/api/import","token":"","payload_size":890,"status_code":400},
        "rate_flood":        {"ip":"1.2.3.4","endpoint":"/login","token":"x","payload_size":80,"status_code":401},
        "slowloris":         {"ip":"1.2.3.4","endpoint":"/login","token":"","payload_size":0,"status_code":408},
    }
    req = test_requests.get(attack_name, test_requests["rate_flood"])
    return score_request(req)


def run_simulation(episodes=10, delay=3):
    """
    Main simulation loop — runs in background thread.
    Each episode: RL agent observes defense → picks attack →
    fires it → gets scored → updates strategy.
    This is the Duality AI simulation core.
    """
    print(f"\n[SIM] Starting {episodes}-episode RL simulation")
    results = []

    for ep in range(episodes):
        defense_state = get_defense_state()
        result = agent.run_episode(defense_state, mock_detector)
        results.append(result)

        # After each episode — if attack succeeded, generate counter-policy
        if result["outcome"] in ("EVADED", "PARTIAL"):
            print(f"[SIM] Agent evaded — generating new defense policy...")
            generate_policy({
                "threat_type": result["attack"],
                "risk_score":  result["risk_score"],
                "endpoint": "inferred",
                "ip":       "simulation"
            })

        time.sleep(delay)

    agent.save_qtable("backend/ml/models/rl_qtable.npy")
    print(f"\n[SIM] Simulation complete. Agent learned over {episodes} episodes.")
    best = agent.best_attack_for_state(get_defense_state())
    print(f"[SIM] Agent's current best attack: {best}")
    return results


def start_simulation_background(episodes=10):
    "Launch simulation in background — doesn't block FastAPI"
    t = threading.Thread(
        target=run_simulation, args=(episodes,), daemon=True
    )
    t.start()
    return {"status": "simulation started", "episodes": episodes}
