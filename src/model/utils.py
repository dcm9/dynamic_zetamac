import numpy as np
import pandas as pd
import os

def parse_historical_data(data_dir):
    all_data = []

    for file_name in os.listdir(data_dir):
        if file_name.endswith('.csv'):
            file_path = os.path.join(data_dir, file_name)
            data = pd.read_csv(file_path)

            if len(data) == 0:
                os.remove(file_path)
                continue

            all_data.append(data)
    combined_data = pd.concat(all_data, ignore_index=True)

    return combined_data

def model(data):
    ema_prob = {}

    for problem in data['problem'].unique():
        problem_data = data[data['problem'] == problem]

        ema_prob[problem] = (problem_data['duration_seconds'] * problem_data['attempts']).ewm(span=10, adjust=False).mean().iloc[-1]

    problem_weights = {problem: ema / sum(ema_prob.values()) for problem, ema in ema_prob.items()}

    return problem_weights

def sample_problems(data_dir, sample_size):
    data = parse_historical_data(data_dir)
    problem_weights = model(data)
    problems = list(problem_weights.keys())
    probabilities = list(problem_weights.values())

    sampled_problems = np.random.choice(problems, size=sample_size, p=probabilities)
    return sampled_problems