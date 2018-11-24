# Github Adapter

Creating synchronous and asynchronous adapters to practice my programming skills.

## Setup

`export GITHUB_OAUTH_TOKEN="[token-here]"`

## Todo

- [ ] tests
  - [ ] [vcr.py](https://github.com/kevin1024/vcrpy)
- [ ] ETag, need to set up DB for this
  - [ ] mark events that are new
- [ ] [rate limiting](https://developer.github.com/v3/#rate-limiting)

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
