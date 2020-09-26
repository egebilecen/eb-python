class Compass:
    # Convert atan2 degree that is mapped between 0, 360 to compass bearing degree
    @staticmethod
    def atan2_mapped_deg_to_compass_deg(deg: int) -> int:
        return (deg + 270) % 360

    @staticmethod
    def add_to_heading(heading: int, deg: int) -> int:
        return (heading + deg) % 360

    @staticmethod
    def substract_from_heading(heading: int, deg: int) -> int:
        return ((heading - deg) + 360) % 360

    @staticmethod
    def get_counter_heading(heading: int) -> int:
        return Compass.add_to_heading(heading, 180)
