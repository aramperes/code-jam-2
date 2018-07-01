from proj.database.database_manager import DatabaseManager


def migrate(db: DatabaseManager, table):
    """
    Migration to add a secondary index for name in characters table.
    """
    index_list_query = db.query(table).index_list()
    index_list = db.run(index_list_query)
    if "name" not in index_list:
        # create secondary index
        create_index_query = db.query(table).index_create("name")
        db.run(create_index_query)
        wait_index_query = db.query(table).index_wait("name")
        db.run(wait_index_query)
