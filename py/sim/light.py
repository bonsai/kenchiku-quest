def calc_illuminance(window_area_m2: float, room_area_m2: float, sky_lux: float) -> float:
    """Rough daylight illuminance estimation.

    Args:
        window_area_m2: Total window area (m²)
        room_area_m2: Room floor area (m²)
        sky_lux: Outdoor illuminance (lux)

    Returns:
        Estimated average indoor illuminance (lux).
    """
    if room_area_m2 <= 0:
        return 0.0
    ratio = window_area_m2 / room_area_m2
    return sky_lux * ratio * 0.6
