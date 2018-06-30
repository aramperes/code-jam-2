from proj.database.database_manager import DatabaseManager


def migrate(db: DatabaseManager, table):
    """
    Migration to set all existing story media to audio-only
    """
    all_stories_query = db.query(table)
    all_stories = db.run(all_stories_query)

    for story_doc in all_stories:
        if "media_type" not in story_doc:
            story_doc["media_type"] = "audio/mpeg"
            insert_query = db.query(table).insert(story_doc, conflict="update", durability="soft")
            db.run(insert_query)

    # Update the table
    db.run(db.query(table).sync())
