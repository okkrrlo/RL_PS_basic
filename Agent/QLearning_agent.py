import numpy as np
import pandas as pd
import random

class QLearningAgent:
    def __init__(self, actions, alpha=0.3, gamma=0.9, epsilon=1, epsilon_decay=0.999, min_epsilon=0.1):
        self.actions = actions
        self.q_table = dict()
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon

    def initialize_state(self, state, initial_value=0.0):
        state = tuple(state)
        if state not in self.q_table:
            self.q_table[state] = [initial_value] * len(self.actions)

    def choose_action(self, state):
        state = tuple(state)
        self.initialize_state(state)

        if np.random.rand() < self.epsilon:
            return random.choice(self.actions)
        else:
            q_values = self.q_table[state]
            best_idx = np.argmax(q_values)
            return self.actions[best_idx]

    def update(self, state, action, reward, next_state):
        state = tuple(state)
        next_state = tuple(next_state)
        self.initialize_state(state)
        self.initialize_state(next_state)

        best_next = max(self.q_table[next_state])
        a_idx = self.actions.index(action)
        old_value = self.q_table[state][a_idx]

        self.q_table[state][a_idx] = old_value + self.alpha * (reward + self.gamma * best_next - old_value)

    def decay_epsilon(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def print_q_table(self):
        df = pd.DataFrame.from_dict(self.q_table, orient='index')
        df.index.name = 'State'
        df.columns = [str(a) for a in self.actions]
        print(df.to_string(float_format="{:.2f}".format))
