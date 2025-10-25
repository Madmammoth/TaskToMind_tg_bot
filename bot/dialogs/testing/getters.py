async def actions(**kwargs):
    products = [
        {"id": 1, "name": "Ferrari", "category": "car",
         "url": "https://www.ferrari.com/"},
        {"id": 2, "name": "Detroit", "category": "game",
         "url": "https://wikipedia.org/wiki/Detroit:_Become_Human"},
    ]
    return {
        "products": products,
    }