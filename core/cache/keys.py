def product_list_key(page: int, query: str):
    return f"product:list:{page}:{query}"


def product_detail_key(product_id: str):
    return f"product:detail:{product_id}"


def market_list_key(page: int):
    return f"market:list:{page}"


def market_detail_key(market_id: str):
    return f"market:detail:{market_id}"
