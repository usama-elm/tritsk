from entities import Project, ProjectUser
from tables import project_user_rel, projects, tables

tables.map_imperatively(
    Project,
    projects,
)
tables.map_imperatively(ProjectUser, project_user_rel)
