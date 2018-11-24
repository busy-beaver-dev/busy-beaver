# Github Adapter

Creating synchronous and asynchronous adapters to practice my programming skills.

## Usage

```console
export GITHUB_OAUTH_TOKEN="[token-here]"
pip install -r requirements.txt
```

```python
from adapters.github import GitHubAdapter

client = GithubAdapter(oauth_token="[insert_token_here]")
```

## Todo

- [ ] tests
  - [ ] [vcr.py](https://github.com/kevin1024/vcrpy)
- [ ] ETag, need to set up DB for this
  - [ ] mark events that are new
- [ ] [rate limiting](https://developer.github.com/v3/#rate-limiting)
- [ ] [GraphQL](https://developer.github.com/v4/)

## Scratchpad

```python
import aiohttp
import asyncio


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def main():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, "http://python.org")
        print(html)


asyncio.run(main())
```
