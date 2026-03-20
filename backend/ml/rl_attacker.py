# backend/ml/rl_attacker.py
import numpy as np
import random, json
from attack.real_attacks import (
    jwt_alg_none_attack, bola_attack,
    mass_assignment_attack, token_refresh_abuse,
    xxe_injection_attack
)

# ── State space ───────────────────────────────────────────────
# State = what the defense is currently doing
# 0 = no defense active
# 1 = rate limiting active
# 2 = token validation tightened
# 3 = IP blocking active
# 4 = full lockdown
N_STATES  = 5

# ── Action space ─────────────────────────────────────────────
# Each action is an attack type the agent can choose
ACTIONS = {
    0: ("rate_flood",         lambda: __import__('attack.real_attacks', fromlist=['rate_flood_attack']).rate_flood_attack()),
    1: ("jwt_forgery",        jwt_alg_none_attack),
    2: ("bola_enum",          lambda: bola_attack(1, 100)),
    3: ("mass_assignment",    mass_assignment_attack),
    4: ("token_refresh_abuse",token_refresh_abuse),
    5: ("xxe_injection",      xxe_injection_attack),
    6: ("slowloris",          lambda: __import__('attack.real_attacks', fromlist=['slowloris_attack']).slowloris_attack(20)),
}
N_ACTIONS = len(ACTIONS)

class RLAttackerAgent:
    """
    Q-learning agent that plays the role of the attacker.
    Learns which attack type is most effective against
    the current defense state.

    Reward signal:
      +1.0  if attack evades detection (risk_score < 0.5)
      -1.0  if attack is detected and blocked (risk_score > 0.8)
      +0.5  if attack partially evades (0.5 <= score <= 0.8)
    """
    def __init__(self, lr=0.1, gamma=0.9, epsilon=0.3):
        self.lr      = lr       # learning rate
        self.gamma   = gamma    # discount factor
        self.epsilon = epsilon  # exploration rate
        # Q-table: rows = states, cols = actions
        self.q_table = np.zeros((N_STATES, N_ACTIONS))
        self.history = []       # (state, action, reward, next_state)
        self.episode = 0

    def choose_action(self, state: int) -> int:
        # Epsilon-greedy: explore randomly or exploit best known action
        if random.random() < self.epsilon:
            return random.randint(0, N_ACTIONS - 1)  # explore
        return int(np.argmax(self.q_table[state]))      # exploit

    def observe_reward(self, state: int, action: int,
                        reward: float, next_state: int):
        # Q-learning update rule
        old_q  = self.q_table[state, action]
        best_next = np.max(self.q_table[next_state])
        new_q  = old_q + self.lr * (reward + self.gamma * best_next - old_q)
        self.q_table[state, action] = new_q
        self.history.append({
            "episode":    self.episode,
            "state":      state,
            "action":     ACTIONS[action][0],
            "reward":     reward,
            "next_state": next_state,
            "q_values":   self.q_table[state].tolist()
        })

    def run_episode(self, defense_state: int, detector_fn) -> dict:
        """
        One full attack episode:
        1. Agent picks an attack based on current defense state
        2. Attack fires
        3. Detector scores it
        4. Agent gets reward based on whether it evaded detection
        5. Q-table updates — agent learns
        """
        self.episode += 1
        action_idx  = self.choose_action(defense_state)
        attack_name, attack_fn = ACTIONS[action_idx]

        print(f"\n[RL] Episode {self.episode} — Agent chose: {attack_name}")
        print(f"[RL] Defense state: {defense_state} — Q-values: {self.q_table[defense_state].round(2)}")

        # Fire the attack
        attack_fn()

        # Ask detector what score the attack got
        detection_result = detector_fn(attack_name)
        risk_score = detection_result.get("risk_score", 0.5)

        # Reward: evade = +1, partial = +0.5, caught = -1
        if risk_score < 0.5:
            reward     = 1.0
            next_state = max(0, defense_state - 1)  # defense relaxes
            outcome    = "EVADED"
        elif risk_score > 0.8:
            reward     = -1.0
            next_state = min(N_STATES-1, defense_state + 1)  # defense tightens
            outcome    = "BLOCKED"
        else:
            reward     = 0.5
            next_state = defense_state
            outcome    = "PARTIAL"

        self.observe_reward(defense_state, action_idx, reward, next_state)

        print(f"[RL] Risk score: {risk_score:.2f} → Outcome: {outcome} → Reward: {reward}")
        print(f"[RL] Updated Q-table for state {defense_state}:")
        for i, (name, _) in ACTIONS.items():
            print(f"     {name:25s}: {self.q_table[defense_state,i]:+.3f}")

        # Decay exploration — agent gets smarter over time
        self.epsilon = max(0.05, self.epsilon * 0.95)

        return {
            "episode":     self.episode,
            "attack":      attack_name,
            "risk_score":  risk_score,
            "outcome":     outcome,
            "reward":      reward,
            "next_state":  next_state,
            "q_table":     self.q_table.tolist()
        }

    def best_attack_for_state(self, state: int) -> str:
        "Returns the attack the agent currently thinks is best"
        best = int(np.argmax(self.q_table[state]))
        return ACTIONS[best][0]

    def save_qtable(self, path="models/rl_qtable.npy"):
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        np.save(path, self.q_table)
        print(f"[RL] Q-table saved → {path}")

    def load_qtable(self, path="models/rl_qtable.npy"):
        self.q_table = np.load(path)
        print(f"[RL] Q-table loaded — agent has memory")
