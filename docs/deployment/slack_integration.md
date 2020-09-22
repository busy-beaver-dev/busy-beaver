# Slack Integration

Details related to Busy Beaver's Slack integration.

## Integration Checklist

For both staging and production apps

- [ ] Update URL in App Home Screen
- [ ] Name Bot: `Busy Beaver` with the username `@busybeaver`
- [ ] Slash Command: Enable `/busybeaver` and set up URL
- [ ] Update app permission
  - [ ] NEED TO DOCUMENT ALL OF THIS SOMEWHERE
- [ ] Update Auth Callback URL for installation
- [ ] Set up event subscriptions and put them to the URL
  - [ ] WHAT EVENT SUBSCRIPTIONS DO WE NEED TO ENABLE

### App Details

|Environment|Name|Workspace|workspace_id
|---|---|---|---|
|Production|Busy Beaver|[BusyBeaverDev](https://busybeaverdev.slack.com/)|`TPDB2AV4K`
|Staging|Busy Beaver Staging|[Busy Beaver Staging](https://busybeaverbot.slack.com/)|`TKT910ZU0`
|Development|Busy Beaver Development|[SivBots](https://sivbots.slack.com/)|`T5G0FCMNW`
