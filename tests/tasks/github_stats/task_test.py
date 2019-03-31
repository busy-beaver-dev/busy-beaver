# from busy_beaver.tasks.github_stats.task import start_post_github_summary_task


def test_start_post_github_summary_task(create_api_user):
    user = create_api_user("admin")
    assert user
