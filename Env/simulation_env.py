class SimulationEnv:
    def __init__(self, plantsim_interface, initial_layout):

        self.sim = plantsim_interface
        self.initial_layout = list(initial_layout)
        self.layout = initial_layout.copy()
        # 위치 ID ↔ 좌표 매핑
        self.locations = {
            2: [300, 100], 3: [500, 100], 4: [700, 100],
            6: [300, 300], 7: [500, 300], 8: [700, 300],
            10: [300, 500], 11: [500, 500], 12: [700, 500],
            14: [300, 700], 15: [500, 700], 16: [700, 700],
        }
        # 설비별 유효 위치 영역 (validation zone)
        self.valid_zones = {
            0: [2, 3, 4],
            1: [6, 7, 8],
            2: [10, 11, 12],
            3: [14, 15, 16]
        }
        self.stagnant_count = 0
        self.repeat_threshold = 10

    def reset(self):
        self.layout = self.initial_layout.copy()
        self.stagnant_count = 0
        return self._layout_to_state(self.layout)

    def step(self, action):
        prev_layout = self.layout.copy()
        
        equip_idx, direction = action

        if not self._is_valid_action(equip_idx, direction):
            reward = -100
            done = False
            return self._layout_to_state(self.layout), reward, done

        self.layout = self._apply_action(equip_idx, direction, self.layout)
        layout_with_coords = self._convert_layout_with_coords(self.layout)
        self.sim.set_layout(layout_with_coords)
        self.sim.start_simulation()
        self.sim.wait_for_completion()
        reward = self.sim.get_reward()
        
        if self.layout == prev_layout:
            self.stagnant_count += 1
        else:
            self.stagnant_count = 0

        done = (self.stagnant_count >= self.repeat_threshold)

        next_state = self._layout_to_state(self.layout)
        return next_state, reward, done

    def _apply_action(self, equip_idx, direction, layout):
        layout = layout.copy()
        current_pos = layout[equip_idx]
        valid_zone = self.valid_zones[equip_idx]

        current_idx = valid_zone.index(current_pos)

        if direction == 'left' and current_idx > 0:
            new_pos = valid_zone[current_idx - 1]
        elif direction == 'right' and current_idx < len(valid_zone) - 1:
            new_pos = valid_zone[current_idx + 1]
        else:
            return layout  # 이동 불가능

        layout[equip_idx] = new_pos
        return layout

    def _layout_to_state(self, layout):
        return tuple(layout)

    def get_current_layout(self):
        return self.layout.copy()
    
    def _convert_layout_with_coords(self, layout):
        result = []
        for loc_id in layout:
            x, y = self.locations[loc_id]
            result.append((loc_id, x, y))
        return result

    def get_all_actions(self):
        actions = []
        for equip_idx in self.valid_zones.keys():
            actions.append((equip_idx, 'left'))
            actions.append((equip_idx, 'right'))
        return actions

    def _should_terminate(self, prev_layout):
        return self.layout == prev_layout
    
    def _is_valid_action(self, equip_idx, direction):
        current_pos = self.layout[equip_idx]
        valid_zone = self.valid_zones[equip_idx]
        current_idx = valid_zone.index(current_pos)

        if direction == 'left':
            return current_idx > 0
        elif direction == 'right':
            return current_idx < len(valid_zone) - 1
        return False