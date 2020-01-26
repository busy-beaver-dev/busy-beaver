# Wrappers

Wrappers around third-party integrations.

<!-- TOC -->

- [GitHub Integration](#github-integration)
- [Meetup Integration](#meetup-integration)
- [YouTube Adapter](#youtube-adapter)
  - [Where to get your channel id](#where-to-get-your-channel-id)
  - [How to create an api key](#how-to-create-an-api-key)
  - [Example](#example)

<!-- /TOC -->

## GitHub Integration

Create a [GitHub OAuth App](https://github.com/settings/developers). The sole function of this app is to provide a means for the Slack user to validate their GitHub account.

You will also need need to create a [Personal Access Token](https://github.com/settings/tokens) that can be used to access the GitHub API.

## Meetup Integration

Go to https://secure.meetup.com/meetup_api/key/
to get an API key

## YouTube Adapter

### Where to get your channel id

Login to youtube and go to https://www.youtube.com/account_advanced, your
channel id will be displayed.

### How to create an api key

1. Go to https://console.developers.google.com and create a project.
2. Visit https://developers.google.com/youtube/registering_an_application#Create_API_Keys
for instructions to generate the api key

### Example

```python
api_key = "..."
channel = "..."
youtube = YouTubeAdapter(api_key=api_key)
data = youtube.get_latest_videos_from_channel(channel)
```
