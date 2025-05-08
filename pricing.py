# pricing.py

def compute_price(qty, slabs, box_qty):
    """
    Compute (unit_price, total_price) based on:
    - 20/100/1box/4box slab logic
    - fallback to earlier slabs
    - if box_qty is None, assume >100 and disable box pricing
    """
    # fallback logic
    if slabs["100pc"] is None:
        slabs["100pc"] = slabs["20pcs"]
    if slabs["1box"] is None:
        slabs["1box"] = slabs["100pc"]
    if slabs["4box"] is None:
        slabs["4box"] = slabs["1box"]

    if qty is None or qty < 20:
        return None, None

    if box_qty is None:
        if qty < 100:
            p1, p2 = slabs["20pcs"], slabs["100pc"]
            unit_price = p1 + (p2 - p1) * ((qty - 20) / 80)
        else:
            unit_price = slabs["100pc"]
        return unit_price, round(unit_price * qty, 2)

    if qty < 100:
        p1, p2 = slabs["20pcs"], slabs["100pc"]
        unit_price = p1 + (p2 - p1) * ((qty - 20) / 80)
    elif qty == box_qty:
        unit_price = slabs["1box"]
    elif qty < box_qty:
        p1, p2 = slabs["100pc"], slabs["1box"]
        unit_price = p1 + (p2 - p1) * ((qty - 100) / (box_qty - 100))
    elif qty >= 4 * box_qty:
        unit_price = slabs["4box"]
    else:
        unit_price = slabs["1box"]

    return unit_price, round(unit_price * qty, 2)
