from flask import url_for


def list_stories(resource, user_id, show_private, summary_mode):
    stories_query = resource.db.query("stories").get_all(
        user_id, index="user_id").pluck("id", "public", "user_id", "sentences", "media_type").filter(
        lambda row: show_private or row["public"].eq(True)
    )

    if summary_mode:
        stories_query = stories_query.merge(summarize)

    stories = resource.db.run(stories_query.coerce_to("array"))
    if not summary_mode:
        stories = _post_process_list(resource, stories)
    return stories


def sample_stories(resource, sample_size, summary_mode):
    stories_query = resource.db.query("stories").filter({"public": True}).sample(sample_size).pluck(
        "id", "public", "sentences", "user_id", "media_type")
    if summary_mode:
        stories_query = stories_query.merge(summarize)

    stories = resource.db.run(stories_query.coerce_to("array"))
    if not summary_mode:
        stories = _post_process_list(resource, stories)
    return stories


def _post_process_list(resource, stories):
    for story in stories:
        story["url"] = url_for("api.stories.story", story_id=story["id"])
        story["media"] = url_for("api.stories.play", story_id=story["id"])
        author = resource.db.get_doc("users", story["user_id"])["username"]
        story["author"] = author
    return stories


def summarize(row):
    return {
        "sentences": row["sentences"][0].slice(0, 75)
    }
