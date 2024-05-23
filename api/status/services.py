from toolz import curry


@curry
def execute_query(session, stmt):
    return list(map(dict, session.execute(stmt).mappings()))


@curry
def row_to_dict(row, columns):
    return dict(map(lambda col: (col, row[col]), columns))


@curry
def handle_results(results, columns):
    match results:
        case []:
            return {}
        case [row, *_]:
            return row_to_dict(row, columns)
