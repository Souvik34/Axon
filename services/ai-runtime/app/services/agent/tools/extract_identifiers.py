
import re


GITHUB_COMMIT_PATTERN = re.compile(
    r"https?://(?:www\.)?github\.com/"
    r"(?P<owner>[\w.-]+)/"
    r"(?P<repo>[\w.-]+)/"
    r"commit/"
    r"(?P<sha>[a-fA-F0-9]{7,40})"
    r"(?=$|[\s?#/)\]}>.,;:!])",
    re.IGNORECASE,
)


def extract_github_commits(text: str) -> dict:
    """
    Extract GitHub commit references from arbitrary text.

    Supports:
    - Full GitHub commit URLs.
    - www.github.com URLs.
    - Full 40-character and abbreviated commit SHAs.
    - Multiple commits in the same text.
    - Duplicate removal.

    Repository names are preserved exactly as found in the URL.
    """

    if not isinstance(text, str):
        raise ValueError("Input must be a string.")

    if not text.strip():
        return {
            "count": 0,
            "commits": [],
        }

    commits = []
    seen = set()

    for match in GITHUB_COMMIT_PATTERN.finditer(text):
        owner = match.group("owner")
        repo = match.group("repo")
        sha = match.group("sha")

        # Remove a possible .git suffix.
        if repo.lower().endswith(".git"):
            repo = repo[:-4]

        # Avoid duplicate commit references.
        identity = (
            owner.lower(),
            repo.lower(),
            sha.lower(),
        )

        if identity in seen:
            continue

        seen.add(identity)

        commits.append({
            "owner": owner,
            "repo": repo,
            "sha": sha,
        })

    return {
        "count": len(commits),
        "commits": commits,
    }
