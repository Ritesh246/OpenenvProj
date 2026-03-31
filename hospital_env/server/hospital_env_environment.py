import random
from ..models import HospitalAction, HospitalObservation, HospitalState

class HospitalEnvironment:

    def __init__(self):
        self.reset()

    def reset(self):
        self.step_count = 0
        self.max_steps = 20

        self.num_doctors = random.randint(2, 5)
        self.num_patients = random.randint(5, 10)

        self.doctors = [{"busy": False} for _ in range(self.num_doctors)]

        self.patients = [
            {"id": i, "critical": random.choice([True, False]), "treated": False}
            for i in range(self.num_patients)
        ]

        return HospitalObservation(
            waiting_patients=[p["id"] for p in self.patients],
            free_doctors=list(range(self.num_doctors)),
            critical_patients=[p["id"] for p in self.patients if p["critical"]],
            reward=0.0,
            done=False
        )

    # ✅ STEP FUNCTION (MISSING BEFORE)
    def step(self, action: HospitalAction):
        self.step_count += 1
        reward = 0

        if action.action_type == "assign_doctor":
            if (
                action.patient_id is not None and
                action.doctor_id is not None and
                0 <= action.patient_id < len(self.patients) and
                0 <= action.doctor_id < len(self.doctors)
            ):
                patient = self.patients[action.patient_id]
                doctor = self.doctors[action.doctor_id]

                if not doctor["busy"] and not patient["treated"]:
                    doctor["busy"] = True
                    patient["treated"] = True

                    reward += 1
                    if patient["critical"]:
                        reward += 2

                    doctor["busy"] = False
                else:
                    reward -= 0.5
            else:
                reward -= 0.5

        reward -= 0.1

        done = all(p["treated"] for p in self.patients)
        done = done or self.step_count >= self.max_steps

        return HospitalObservation(
            waiting_patients=[p["id"] for p in self.patients if not p["treated"]],
            free_doctors=[i for i, d in enumerate(self.doctors) if not d["busy"]],
            critical_patients=[p["id"] for p in self.patients if p["critical"] and not p["treated"]],
            reward=reward,
            done=done
        )

    def state(self):
        return HospitalState(
            step_count=self.step_count,
            total_patients=len(self.patients),
            treated_patients=sum(p["treated"] for p in self.patients)
        )

    def close(self):
        pass

    async def reset_async(self):
        return self.reset()

    async def step_async(self, action):
        return self.step(action)