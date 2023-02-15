async def store_tags(sender, tags, target):
    query = {"name": str(sender)}
    db_entry = target.find_one(query)
    if db_entry is None:
        target.insert_one({"name": str(sender), "tags": tags})
    else:
        target.update_one(query, {"$set": {"tags": tags}})


async def get_tags(sender, target):
    query = {"name": str(sender)}
    db_entry = target.find_one(query)
    if db_entry is None:
        return "-"
    else:
        return db_entry.get('tags')


async def change_tags_listing(sender, target):
    query = {"name": str(sender)}
    db_entry = target.find_one(query)
    if db_entry is None:
        target.insert_one({"name": str(sender), "tags_listing": "enabled"})
    else:
        if db_entry.get('tags_listing') == "enabled":
            target.update_one(query, {"$set": {"tags_listing": "disabled"}})
        else:
            target.update_one(query, {"$set": {"tags_listing": "enabled"}})


async def get_tags_listing(sender, target):
    query = {"name": str(sender)}
    db_entry = target.find_one(query)
    if db_entry is None:
        return "disabled"
    else:
        return db_entry.get('tags_listing')
