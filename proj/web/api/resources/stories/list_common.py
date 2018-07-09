def list_stories(resource, user_id, show_private, summary_mode):
    stories_query = resource.db.query("stories").get_all(
        user_id, index="user_id").pluck("id", "public", "sentences", "media_type").filter(
        lambda row: show_private or row["public"].eq(True)
    )

    if summary_mode:
        stories_query = stories_query.merge(summarize)

    stories = resource.db.run(stories_query.coerce_to("array"))
    if not summary_mode:
        for story in stories:
            story["media"] = "/api/story/{0}/play".format(story["id"])
            story["url"] = "/api/story/{0}".format(story["id"])
    return stories


def summarize(row):
    return {
        "sentences": row["sentences"][0].slice(0, 75)
    }
