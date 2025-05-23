import os
import csv
import json
import matplotlib.pyplot as plt
from datetime import datetime

class TrainingLogger:
    def __init__(self, base_dir="Result"):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.result_dir = os.path.join(base_dir, self.timestamp)
        os.makedirs(self.result_dir, exist_ok=True)
        self.episode_rewards = []
        self.q_table_snapshots = []
        self.log_lines = []

    def log_episode(self, episode, total_reward, steps, final_state, best_action, best_q):
        line = (
            f"--- Episode {episode + 1} End ---\n"
            f"Total Reward: {total_reward:.2f}\n"
            f"Steps taken: {steps}\n"
            f"Final State: {final_state}\n"
            f"Best Action: {best_action} | Q-value: {best_q:.2f}\n"
        )
        print(line)
        self.log_lines.append(line)
        self.episode_rewards.append(total_reward)

    def save_rewards(self):
        path = os.path.join(self.result_dir, f"episode_rewards_{self.timestamp}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Episode", "TotalReward"])
            for i, r in enumerate(self.episode_rewards):
                writer.writerow([i + 1, r])

    def save_q_table(self, q_table):
        path = os.path.join(self.result_dir, f"q_table_{self.timestamp}.json")
        serializable_q_table = {str(k): v for k, v in q_table.items()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serializable_q_table, f, indent=2)

    def save_plot(self):
        path = os.path.join(self.result_dir, f"reward_plot_{self.timestamp}.png")
        plt.figure()
        plt.plot(range(1, len(self.episode_rewards) + 1), self.episode_rewards, marker="o")
        plt.title("Episode Rewards")
        plt.xlabel("Episode")
        plt.ylabel("Total Reward")
        plt.grid(True)
        plt.savefig(path)
        plt.close()

    def save_log_txt(self):
        txt_path = os.path.join(self.result_dir, f"summary_{self.timestamp}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            for line in self.log_lines:
                f.write(line + "\n")

    def save_all(self, q_table):
        self.save_rewards()
        self.save_q_table(q_table)
        self.save_plot()
        self.save_log_txt()
