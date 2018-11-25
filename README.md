# Busy Beaver

Project to aggregate ChiPy members GitHub activity to post on Slack.

## Usage

```console
export GITHUB_OAUTH_TOKEN="[token-here]"
pip install -r requirements.txt
```

```python
from adapters.github import GitHubAdapter

client = GithubAdapter(oauth_token="[insert_token_here]")
```

### Development Environment

```console
pip install -r requirements_dev.txt
```

### Stack

- [requests](https://github.com/requests/requests)

#### Tests

- [pytest](https://github.com/pytest-dev/pytest)
- [vcr.py](https://github.com/kevin1024/vcrpy)
- [pytest-vcr](https://github.com/ktosiek/pytest-vcr)

`vcr.py` records cassettes of requests and responses for new tests, and replays them for previously written tests. Make sure to [filter credentials](https://vcrpy.readthedocs.io/en/latest/advanced.html#filter-information-from-http-headers).

---

## Todo

- [x] Builds on Travis
  - [ ] Get codecov working
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
