from proj.database.database_manager import DatabaseManager


def migrate(db: DatabaseManager, table):
    """
    Migration to add secondary indices for challenger_username and defender_username in games table.
    """
    index_list_query = db.query(table).index_list()
    index_list = db.run(index_list_query)
    if "challenger_username" not in index_list:
        # create secondary index
        create_index_query = db.query(table).index_create("challenger_username")
        db.run(create_index_query)
        wait_index_query = db.query(table).index_wait("challenger_username")
        db.run(wait_index_query)

    if "defender_username" not in index_list:
        # create secondary index
        create_index_query = db.query(table).index_create("defender_username")
        db.run(create_index_query)
        wait_index_query = db.query(table).index_wait("defender_username")
        db.run(wait_index_query)
