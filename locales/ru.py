from database.models import LevelEnum

PRIORITY_LABELS = {
    LevelEnum.HIGH: "Высокий",
    LevelEnum.MEDIUM: "Средний",
    LevelEnum.LOW: "Низкий",
}
URGENCY_LABELS = {
    LevelEnum.HIGH: "Высокая",
    LevelEnum.MEDIUM: "Средняя",
    LevelEnum.LOW: "Низкая",
}
