## Youtube Adapter

### Where to get your channel id?

Login to youtube and go to https://www.youtube.com/account_advanced, your
channel id will be displayed.

### How to create an api key?

Go to https://console.developers.google.com and create a project. After you can
visit https://developers.google.com/youtube/registering_an_application#Create_API_Keys
for instructions to generate the api key. After you have both, you can move to
the examples.

### Example

```
api_key = "..."
channel_id = "..."
youtube = YoutubeAdapter(api_key=api_key)
data = youtube.get_latest_videos_from_channel(channel_id)
videos = data["items"]
```
