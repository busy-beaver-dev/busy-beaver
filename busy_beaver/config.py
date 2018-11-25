import os

IN_PRODUCTION = os.getenv("ENV_NAME", False)

# infrastructure
local_db = "sqlite:///busy_beaver.db"
DATABASE_URI = os.getenv("DATABASE_URI", local_db)

# credentials
oauth_token = os.getenv("GITHUB_OAUTH_TOKEN")
