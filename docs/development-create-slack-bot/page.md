<!-- Unfortunatley markdown dosen't support CSS =( -->
<!-- <style>
note {
  background-color:grey;
  padding:8px;
}
</style> -->

# Create a Slack Bot for Development

This page contains steps for creating a **Slack App** **Bot** in a sandbox **Slack Workspace** for development.

Links:

- [Slack api - Apps](https://api.slack.com/apps)

- [ngrok get started](https://dashboard.ngrok.com/get-started)

- [Using ngrok to develop locally for Slack](https://api.slack.com/tutorials/tunneling-with-ngrok)

## Init a Slack App

1. Create a **Slack App** to contain the Dev-Bot.</br>
   <a href="images/init-slack-app-1.png">
   <img src="images/init-slack-app-1.png" width=400/>
   </a>

2. Define the **App Name** for the **Slack App** and the **Development Slack Workspace**.</br>
  <a href="images/init-slack-app-2.png">
  <img src="images/init-slack-app-2.png" width=400/>
  </a></br>
  After creating the **Slack App** will bring you to the **Basic Information** page.</br>
  <a href="images/init-slack-app-3.png">
  <img src="images/init-slack-app-3.png" width=400/>
  </a>

<div style=background-color:#262626;padding:8px;border-width:1px;border-style:solid;border-color:grey;>
<b>Note</b>

Before the **Slack App** can be installed to the **Slack Workspace** a feature or permission needs to be defined.
<a href="images/init-slack-app-4.png">
  <img src="images/init-slack-app-4.png" width=400/>
</a></div>

Follow on to setup the **Bot** for the **Slack App**.


## Add a Bot User

1. Add a **Bot User** - Features > Bot Users.</br>
  <a href="images/add-bot-user-1.png">
  <img src="images/add-bot-user-1.png" width=400>
  </a>

2. Define the **Display name** and **Default username**.</br>
  <a href="images/add-bot-user-2.png">
  <img src="images/add-bot-user-2.png" width=400/>
  </a>

## Slack App Settings

### Define App OAuth and Permissions

1. Define the **Permission Scopes** for the Dev-Bot App:

   ```python
   - channels:read
   - chat:write:bot
   - bot
   - usergroups:read
   ```

   <a href="images/setup-app permission-scopes-1.png">
   <img src="images/setup-app permission-scopes-1.png" width=400/>
   </a>

### Enable Event Subscription

Links:

- [Getting started with ngrok](https://dashboard.ngrok.com/get-started)
- [Using ngrok to develop locally for Slack](https://api.slack.com/tutorials/tunneling-with-ngrok)

1. Run `cd <directory of the Busy-Beaver git repo>`
2. Run `make up` to spin up a Busy-Beaver service locally.
3. Run `make ngrok` to open port forwarding to the internet. This will be used for the **slack-event-subscription endpoint** by the local Busy-Beaver instance.</br>
   <a href="images/event-subscriptions-1.png">
   <img src="images/event-subscriptions-1.png" width=400/>
   </a></br>
   Take note of the **forwarding address**.
4. Enable **Event Subscriptions**.</br>
   <a href="images/event-subscriptions-2.png">
   <img src="images/event-subscriptions-2.png" width=400/>
   </a>
5. Update the **Request URL** to the **slack-event-subscription endpoint** composed of the **forwarding address** defined by the **ngrok** instance i.e.

   ```http
   http://[ngrok_fowarding_address]/slack-event-subscription
   ```

   <a href="images/event-subscriptions-3.png">
   <img src="images/event-subscriptions-3.png" width=400/>
   </a>
6. Click **Change** in the **Request URL** field for the **Slack API** to verify the endpoint responds.
7. **Save Changes**.

<div style=background-color:#262626;padding:8px;border-width:1px;border-style:solid;border-color:grey;>

Update the **.env** config - `NGROK_BASE_URI` value to **Slack Event Subscription - Request URL*** as described in <a href=../../CONTRIBUTING.md#Setting-up-Development-Environment> Setting up Development Environment </a>
</div>

## Install App to Workspace

Once a feature or permission has been installed,
the **Slack App** can now be installed to the **Workspace** for development.

1. Install **Slack App** to **Slack Workspace**. </br>
   <a href="images/install-app-to-workspace-1.png">
   <img src="images/install-app-to-workspace-1.png" width=400>
   </a></br>

   Confirm the Authorization to Install the **App** to the **Workspace**. </br>
   <a href="images/install-app-to-workspace-2.png">
   <img src="images/install-app-to-workspace-2.png" width=400/>
   </a>

### OAuth Access Token

Once the Busy-Beaver **Slack App** has been installed to the development **Workspace**,
the `OAuth Access Token` should now be available.

<a href="images/oauth-tokens-1.png">
<img src="images/oauth-tokens-1.png" width=400/>
</a>

<div style=background-color:#262626;padding:8px;border-width:1px;border-style:solid;border-color:grey;>

Update the **.env** config - `SLACK_BOTUSER_OAUTH_TOKEN` value to **Bot User OAuth Access Token** as defined by [Setting up Development Environment](../../CONTRIBUTING.md#Setting-up-Development-Environment)
</div>
