"""Purify dict"""


def purify_dict(dictionarie: dict):
    """Función para obtener un dictionario sin los valores vacíos"""
    return {k: v for k, v in dictionarie.items() if v is not None}
