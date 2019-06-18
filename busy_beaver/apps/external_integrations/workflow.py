from busy_beaver import slack_oauth


def slack_generate_and_save_auth_tuple():
    auth = slack_oauth.generate_authentication_tuple()
    # TODO save auth.state somewhere
    return auth
    # jsonify({"url": auth.url, "state": auth.state})


def slack_verify_callback_and_save_access_tokens_in_database(callback_url, state):
    state  # pull user from this
    oauth_details = slack_oauth.process_callback(callback_url, state)

    # TODO pull user from state
    # patch user with oauth_detail
    print(oauth_details)
