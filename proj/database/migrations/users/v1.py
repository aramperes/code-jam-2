from proj.database.database_manager import DatabaseManager


def migrate(db: DatabaseManager, table):
    """
    Migration to add a secondary index for usernames in the users table.
    """
    index_list_query = db.query(table).index_list()
    index_list = db.run(index_list_query)
    if "username" not in index_list:
        # create secondary index
        create_index_query = db.query(table).index_create("username")
        db.run(create_index_query)
        wait_index_query = db.query(table).index_wait("username")
        db.run(wait_index_query)
