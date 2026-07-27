def calc_heat_loss(U_W_m2K: float, area_m2: float, dT_K: float) -> float:
    """Calculate heat loss in Watts.

    Args:
        U_W_m2K: Overall heat transfer coefficient (W/m²K)
        area_m2: Surface area (m²)
        dT_K: Temperature difference (K)

    Returns:
        Heat loss in Watts.
    """
    return U_W_m2K * area_m2 * dT_K
