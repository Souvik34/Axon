import re


def extract_github_commits(text: str) -> dict:
    """
    Extract GitHub commit URLs and SHAs from text.
    """

    if not isinstance(text, str):
        raise ValueError("Input must be a string.")

    pattern = (
        r"https?://github\.com/"
        r"([\w.-]+)/([\w.-]+)/commit/([a-fA-F0-9]{40})"
    )

    matches = re.findall(pattern, text)

    commits = [
        {
            "owner": owner,
            "repo": repo,
            "sha": sha
        }
        for owner, repo, sha in matches
    ]

    return {
        "count": len(commits),
        "commits": commits
    }