from api.tables import tables_metadata, tasks
from api.tasks.entities import Tasks

tables_metadata.map_imperatively(Tasks, tasks)
