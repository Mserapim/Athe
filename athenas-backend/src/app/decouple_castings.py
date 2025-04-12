def dj_mongo_url(uri):

    if uri.startswith("mongodb://"):
        uri = uri.strip("mongodb://")

    db_dict = {
        "USER": "",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "27017",
        "AUTH_DATABASE": "auth",
    }

    if "/" in uri:
        uri, auth_db = uri.split("/")
        db_dict["AUTH_DATABASE"] = auth_db

    if "@" in uri:
        auth, resource = uri.split("@")
        auth = auth.split(":")
        resource = resource.split(":")

        db_dict["USER"] = auth[0]
        if len(auth) > 1:
            db_dict["PASSWORD"] = auth[1]

        db_dict["HOST"] = resource[0]
        if len(resource) > 1:
            db_dict["PORT"] = resource[1]

    return db_dict
