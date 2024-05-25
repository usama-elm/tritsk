from litestar.contrib.htmx.response import HTMXTemplate
from litestar.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from toolz import curry


@curry
def check_user_id(user_id):
    return user_id if user_id else None


@curry
def create_values_map(title, rank, description=None):
    values = {"title": title, "rank": rank}
    if description:
        values["description"] = description
    return values


@curry
def execute_statement(session, stmt):
    task = session.execute(stmt)
    session.commit()
    return task


@curry
def execute_template(template_name, context):
    return HTMXTemplate(template_name=template_name, context=context)


@curry
def handle_exceptions(session, func, *args):
    try:
        return func(*args)
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(
            detail=f"Failed to execute database operation: {e}", status_code=400
        )
    except Exception as ex:
        raise HTTPException(detail=f"Invalid information: {ex}", status_code=400)
