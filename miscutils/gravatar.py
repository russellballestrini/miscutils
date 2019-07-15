from hashlib import md5

def gravatar_client(email, size=48, rating="g", default="retro", force_default=False):
    """Return a gravatar API URI."""
    query_params = ["s={}".format(size), "r={}".format(rating), "d={}".format(default)]
    if force_default:
        query_params.append("f=y")
    uri = "https://secure.gravatar.com/avatar/{0}?{1}"
    return uri.format(md5(email).hexdigest(), "&".join(query_params))
