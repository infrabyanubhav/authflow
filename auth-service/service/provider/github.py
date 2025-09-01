import httpx


async def get_github_token(code: str):
    github_token_url = "https://github.com/login/oauth/access_token"
    response = httpx.post(github_token_url, json={"code": code})
    return response.json()
