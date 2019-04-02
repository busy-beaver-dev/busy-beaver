<!-- Unfortunatley markdown dosen't support CSS =( -->
<!-- <style>
note {
  background-color:grey;
  padding:8px;
}
</style> -->

# Create a Slack Bot for Development

This page contains steps for creating a **Slack App** **Bot** in a sandbox **Slack Workspace** for development.

<table><tr><td>
<strong>:link: Links:</strong></br>
- <a href=https://api.slack.com/apps>Slack api - Apps</a></br>
- <a href=https://dashboard.ngrok.com/get-started>Ngrok get started</a></br>
- <a href=https://api.slack.com/tutorials/tunneling-with-ngrok>Using ngrok to develop locally for Slack</a>
</tr></td></table>

## Init a Slack App

1. Create a **Slack App** to contain the Dev-Bot.</br>
   <a href="images/init-slack-app-1.png">
   <img src="images/init-slack-app-1.png" width=400/>
   </a>

2. Define the **App Name** for the **Slack App** and the **Development Slack Workspace**.
   <a href="images/init-slack-app-2.png">
   <img src="images/init-slack-app-2.png" width=400/>
   </a></br>
   After creating the **Slack App** will bring you to the **Basic Information** page.</br>
   <a href="images/init-slack-app-3.png">
   <img src="images/init-slack-app-3.png" width=400/>
   </a>

<table><tr><td>
<strong>📝 Note</strong>

Before the **Slack App** can be installed to the **Slack Workspace** a feature or permission needs to be defined.</br>
<a href="images/init-slack-app-4.png">
  <img src="images/init-slack-app-4.png" width=400/>
</a>
</tr></td></table>

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

<table><tr><td>
<strong>:link: Links:</strong></br>
- <a href=https://dashboard.ngrok.com/get-started>Getting started with ngrok</a></br>
- <a href=https://api.slack.com/tutorials/tunneling-with-ngrok>Using ngrok to develop locally for Slack</a></br>
</td></tr></table></br>

1. Run `cd <directory of the Busy-Beaver git repo>`.
2. Run `make up` to spin up a Busy-Beaver service locally.
3. Run `make ngrok` to open port forwarding to the internet.
This will be used for the **slack-event-subscription endpoint** by the local Busy-Beaver instance.</br>
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

<table><tr><td>
:link: Update the <strong>.env</strong> config - <strong>NGROK_BASE_URI</strong> value to <strong>Slack Event Subscription - Request URL</strong> as defined in  <a href=../../CONTRIBUTING.md#Setting-up-Development-Environment>Setting up Development Environment</a>.
</td></tr></table>

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

<table><tr><td>
:link: Update the <strong>.env</strong> config - <strong>SLACK_BOTUSER_OAUTH_TOKEN</strong> value to <strong>Bot User OAuth Access Token</strong> as defined in <a href=../../CONTRIBUTING.md#Setting-up-Development-Environment>Setting up Development Environment</a>.
</td></tr></table>

### Signing Secret

In order to [verify requests are sent from Slack](https://api.slack.com/docs/verifying-requests-from-slack), find the `Signing Secret` and add it to your `.env` file.

<a href="images/signing-secret-1.png">
<img src="images/signing-secret-1.png" width=300/>
</a>
