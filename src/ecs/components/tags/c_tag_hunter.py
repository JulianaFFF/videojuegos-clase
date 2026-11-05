class CTagHunter:
    def __init__(self, hunter_info:dict):
        self.velocity_chase = hunter_info["velocity_chase"]
        self.velocity_return = hunter_info["velocity_return"]
        self.distance_start_chase = hunter_info["distance_start_chase"]
        self.distance_start_return = hunter_info["distance_start_return"]
