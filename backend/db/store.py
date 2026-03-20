_active_policies = []

def add_policy(policy: dict):
    _active_policies.append(policy)

def count_active_policies() -> int:
    return len(_active_policies)

def clear_policies():
    _active_policies.clear()
