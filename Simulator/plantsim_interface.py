from .plantsim.plantsim import Plantsim

class PlantSimInterface:
    def __init__(self, version='24.4', visible=True, license_type='Educational'):

        self.plantsim = Plantsim(version=version, visible=visible, license_type=license_type)
        self.layout_table_path = "EQPInfo"
        self.result_table_path = "result_table"

    def start_simulation(self):
        self.plantsim.reset_simulation()
        self.plantsim.start_simulation()

    def initialize_simulation(self, path):
        self.plantsim.load_model(path)
        self.plantsim.set_path_context(".Models.Model")
        self.plantsim.set_event_controller()
        self.plantsim.set_value("Eventcontroller.RealtimeScale", 10000)
        self.plantsim.reset_simulation()

    def quit(self):
        self.plantsim.quit()

    def set_layout(self, layout_with_coords):
        for i, (loc_id, x, y) in enumerate(layout_with_coords):
            eqp_id = "B0"+str(i+1)
            self.plantsim.set_value(f'{self.layout_table_path}["x location", "{eqp_id}"]', x)
            self.plantsim.set_value(f'{self.layout_table_path}["y location", "{eqp_id}"]', y)
            self.plantsim.set_value(f'{self.layout_table_path}["location num", "{eqp_id}"]', loc_id)

    def wait_for_completion(self):
        import time
        while True:
            is_running = self.plantsim.get_value("EventController.isRunning")
            if not is_running:
                break
            time.sleep(0.1)
        time.sleep(0.1)

    def get_reward(self):
        """시뮬레이션 결과 보상 반환"""
        return - self.plantsim.get_value(f'{self.result_table_path}["Total time", 1]') + 500