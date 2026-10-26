class AnimationData:

    def __init__(self, name: str, start: int, end: int, framerate: float) -> None:
        if end < start:
            raise ValueError(f"Animation '{name}': end frame must be >= start frame")
        if framerate <= 0:
            raise ValueError(f"Animation '{name}': framerate must be greater than zero")
        self.name = name
        self.start = start
        self.end = end
        self.framerate = 1.0 / framerate  # Seconds per frame


class CAnimation:

    def __init__(self, animations: dict) -> None:
        self.number_frames = animations["number_frames"]
        self.animations_list: list[AnimationData] = [
            AnimationData(anim["name"], anim["start"], anim["end"], anim["framerate"])
            for anim in animations["list"]
        ]
        self.curr_anim = 0
        self.curr_anim_time = self.animations_list[self.curr_anim].framerate
        self.curr_frame = self.animations_list[self.curr_anim].start
        # True once the current animation has played all its frames at least once
        self.finished = False

    def set_animation(self, name: str) -> None:
        for index, anim in enumerate(self.animations_list):
            if anim.name == name:
                if index != self.curr_anim:
                    self.curr_anim = index
                    self.curr_anim_time = anim.framerate
                    self.curr_frame = anim.start
                    self.finished = False
                return
