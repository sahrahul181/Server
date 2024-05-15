def calculate_kc(growing_season_length: int, stages: list[int], kc: list[float]):
    # Initialize Kc values array for the entire growing season
    KC = []
    stage = ""

    for i in range(1, growing_season_length + 1):
        if i < stages[0]:
            stage = "ini"
            KC.append(kc[0])
        elif i < stages[0] + stages[1]:
            stage = "dev"
            kci = kc[0] + (i - stages[0]) * (kc[1] - kc[0]) / (stages[1])
            kci = float(format(kci, ".3f"))
            KC.append(kci)
        elif i < stages[0] + stages[1] + stages[2]:
            stage = "mid"
            KC.append(kc[1])
        else:
            stage = "end"
            kci = kc[1] + (i - stages[0] - stages[1] - stages[2]) * (kc[2] - kc[1]) / (
                stages[3]
            )
            kci = float(format(kci, ".3f"))
            KC.append(kci)
    return KC


def get_KC(crop: str = "rice"):
    KCi = [0.15, 1.19, 0.35]
    stages = [25, 30, 35, 20, 110]
    KC = calculate_kc(100, stages, KCi)
    return KC


# Example usage:
KCi = [0.15, 1.19, 0.35]
stages = [25, 25, 30, 20, 100]

# KC = calculate_kc(100, stages, KCi)
# print(KC)
