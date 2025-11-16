import logging

logger = logging.getLogger(__name__)


def filter_kwargs(model, kwargs: dict) -> dict:
    """
    Фильтрация по доступности ключей в таблице
    :param model: модель таблицы
    :param kwargs: ключи-значения для фильтрации
    :return: словарь с ключами-значениями, подходящими для таблицы
    """
    logger.debug("Фильтрация полученных ключ-значений: %s", kwargs)
    columns = {c.name for c in model.__table__.columns}
    filtered_dict = {k: v for k, v in kwargs.items() if k in columns}
    logger.debug("Отфильтрованный словарь: %s", filtered_dict)
    return filtered_dict
