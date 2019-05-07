from busy_beaver.extensions import rq


@rq.job
def dispatch_slash_command(command_text: str) -> None:
    """Dispatch and take action to slash command (e.g., /bb next) from Slack."""
    # TODO: do something with the command.
