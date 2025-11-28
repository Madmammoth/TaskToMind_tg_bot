from app.database.models import LevelEnum, TaskStatusEnum, AccessRoleEnum

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
TASK_STATUS_LABELS = {
    TaskStatusEnum.NEW: "Новая",
    TaskStatusEnum.IN_PROGRESS: "В работе",
    TaskStatusEnum.DONE: "Выполнена",
    TaskStatusEnum.CANCELED: "Отменена",
}
ACCESS_LABELS = {
    AccessRoleEnum.OWNER: "Владелец",
    AccessRoleEnum.EDITOR: "Редактор",
    AccessRoleEnum.VIEWER: "Наблюдатель",
}
