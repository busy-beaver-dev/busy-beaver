# Github Adapter

Creating synchronous and asynchronous adapters to practice my programming skills.

## Setup

`export GITHUB_OAUTH_TOKEN="[token-here]"`

## Todo

- [ ] pagination
  - [x] fetch all events in last 24 hours
    - [ ] refactor and add tests
  - [ ] fetch all repos
  - [ ] fetch all stars
- [ ] ETag, need to set up DB for this
  - [ ] mark events that are new
- [ ] add test with vcr.py

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
