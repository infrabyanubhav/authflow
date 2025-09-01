import dotenv


def setup_environment(env: str):
    if env == "development":
        print("Loading development env ")
        return dotenv.load_dotenv("env/development.env")
    elif env == "production":
        print("Loading production env ")
        return dotenv.load_dotenv()
    else:
        print("Loading ", env, " environment")
        return dotenv.load_dotenv("env/" + env)
