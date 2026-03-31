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

        # ✅ AFTER patients created
        self.total_critical = sum(p["critical"] for p in self.patients)
        self.critical_treated = 0

        return HospitalObservation(
            waiting_patients=[p["id"] for p in self.patients],
            free_doctors=list(range(self.num_doctors)),
            critical_patients=[p["id"] for p in self.patients if p["critical"]],
            reward=0.0,
            done=False
        )

    def get_score(self):
        treated = sum(p["treated"] for p in self.patients)
        total = len(self.patients)

        efficiency = treated / self.step_count if self.step_count > 0 else 0
        critical_ratio = (
            self.critical_treated / self.total_critical
            if self.total_critical > 0 else 1
        )

        score = (
            0.4 * (treated / total) +
            0.4 * critical_ratio +
            0.2 * efficiency
        )

        return {
            "score": round(score, 3),
            "treated": treated,
            "total": total,
            "critical_treated": self.critical_treated,
            "critical_total": self.total_critical,
            "steps": self.step_count,
            "efficiency": round(efficiency, 3)
        }

    def step(self, action: HospitalAction):
        self.step_count += 1
        reward = 0

        valid_assignment = False

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
                    valid_assignment = True
                    doctor["busy"] = True
                    patient["treated"] = True

                    # ✅ track critical treated
                    if patient["critical"]:
                        self.critical_treated += 1

                    doctor["busy"] = False

        # 🔥 REWARD SYSTEM (UPGRADED)
        if valid_assignment:
            if patient["critical"]:
                reward += 5
            else:
                reward += 1
            reward += 0.5
        else:
            reward -= 1

        # 🔥 waiting penalty
        for p in self.patients:
            if not p["treated"]:
                if p["critical"]:
                    reward -= 0.5
                else:
                    reward -= 0.1

        reward -= 0.05  # step penalty

        done = all(p["treated"] for p in self.patients)
        done = done or self.step_count >= self.max_steps

        obs = HospitalObservation(
            waiting_patients=[p["id"] for p in self.patients if not p["treated"]],
            free_doctors=[i for i, d in enumerate(self.doctors) if not d["busy"]],
            critical_patients=[p["id"] for p in self.patients if p["critical"] and not p["treated"]],
            reward=reward,
            done=done
        )

        # ✅ print final score when done
        if done:
            print("FINAL SCORE:", self.get_score())

        return obs

    def state(self):
        return HospitalState(
            step_count=self.step_count,
            total_patients=len(self.patients),
            treated_patients=sum(p["treated"] for p in self.patients),
            critical_treated=self.critical_treated
        )

    def close(self):
        pass

    async def reset_async(self):
        return self.reset()

    async def step_async(self, action):
        return self.step(action)