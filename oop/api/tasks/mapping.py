from entities import Subtask, Task, TaskUser
from tables import subtasks, tables, task_user_rel, tasks

tables.map_imperatively(Subtask, subtasks)
tables.map_imperatively(Task, tasks)
tables.map_imperatively(TaskUser, task_user_rel)
