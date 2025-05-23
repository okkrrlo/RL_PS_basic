import os
from Simulator.plantsim_interface import PlantSimInterface
from Env.simulation_env import SimulationEnv
from Agent.QLearning_agent import QLearningAgent
from utils.training_logger import TrainingLogger
import numpy as np

def main():
    # 1. 플심 모델 경로 설정 (main.py와 동일경로라 가정)
    model_file = "250512_marker_F.spp"
    model_path = os.path.abspath(model_file)

    # 2. Plant Simulation 연결 및 초기화
    sim = PlantSimInterface()
    sim.initialize_simulation(model_path)
    logger = TrainingLogger()

    # 3. 환경 및 에이전트 초기화
    initial_layout = [4, 8, 12, 16]
    env = SimulationEnv(plantsim_interface=sim, initial_layout=initial_layout)
    actions = env.get_all_actions()
    agent = QLearningAgent(actions)

    # 4. 학습 루프
    num_episodes = 50
    max_steps_per_episode = 50
    all_rewards = []

    for episode in range(num_episodes):
        print(f"--- Episode {episode + 1} ---")

        state = env.reset()
        agent.initialize_state(state)
        total_reward = 0
        steps = 0

        for step in range(max_steps_per_episode):
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)
            
            agent.initialize_state(next_state)
            agent.update(state, action, reward, next_state)
            agent.decay_epsilon()
            
            state = next_state
            total_reward += reward
            steps += 1

            if step % 10 == 0:
                print(f"State: {state} | Action: {action} | Reward: {reward:.2f} | ε: {agent.epsilon:.3f}")

            if done:
                break
            
        all_rewards.append(total_reward)

        q_values = agent.q_table[state]
        best_action_idx = max(enumerate(q_values), key=lambda x: x[1])[0]
        best_q = q_values[best_action_idx]
        best_action = agent.actions[best_action_idx]
        logger.log_episode(episode, total_reward, steps, state, best_action, best_q)

    logger.save_all(agent.q_table)

    # 5. 시뮬레이터 종료
    sim.quit()

if __name__ == "__main__":

    main()