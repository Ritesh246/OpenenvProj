import requests

BASE_URL = "http://localhost:8000"
EPISODE_ID = "agent-run"   # ✅ FIX


def reset_env():
    response = requests.post(f"{BASE_URL}/reset", json={
        "episode_id": EPISODE_ID,
        "seed": 42
    })
    return response.json()


def step_env(action):
    response = requests.post(f"{BASE_URL}/step", json={
        "episode_id": EPISODE_ID,   # ✅ VERY IMPORTANT FIX
        "action": action
    })
    return response.json()


def choose_action(obs):
    observation = obs["observation"]

    critical = observation["critical_patients"]
    waiting = observation["waiting_patients"]
    doctors = observation["free_doctors"]

    if not doctors:
        return {"action_type": "wait"}

    if critical:
        return {
            "action_type": "assign_doctor",
            "patient_id": critical[0],
            "doctor_id": doctors[0]
        }

    if waiting:
        return {
            "action_type": "assign_doctor",
            "patient_id": waiting[0],
            "doctor_id": doctors[0]
        }

    return {"action_type": "wait"}

def run_agent():
    obs = reset_env()
    step = 0
    MAX_STEPS = 20   # ✅ same as backend

    print("\n🚀 Starting Agent...\n")

    while step < MAX_STEPS:   # ✅ FIXED LOOP
        action = choose_action(obs)
        obs = step_env(action)

        print(f"Step {step}")
        print("Action:", action)
        print("Reward:", obs.get("reward"))
        print("Remaining:", obs["observation"]["waiting_patients"])
        print("-" * 40)

        # ✅ optional early stop if no patients left
        if len(obs["observation"]["waiting_patients"]) == 0:
            print("\n✅ ALL PATIENTS TREATED")
            break

        step += 1

    print("\n✅ EPISODE FINISHED")

if __name__ == "__main__":
    run_agent()