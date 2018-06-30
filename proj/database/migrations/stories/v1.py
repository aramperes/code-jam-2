from proj.database.database_manager import DatabaseManager


def migrate(db: DatabaseManager, table):
    """
    Migration to add a secondary index for user_id in stories table.
    """
    index_list_query = db.query(table).index_list()
    index_list = db.run(index_list_query)
    if "user_id" not in index_list:
        # create secondary index
        create_index_query = db.query(table).index_create("user_id")
        db.run(create_index_query)
        wait_index_query = db.query(table).index_wait("user_id")
        db.run(wait_index_query)
