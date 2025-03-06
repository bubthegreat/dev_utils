import logging
import os
import git
from git import RemoteProgress
import datetime

from typing import List, Dict

LOGGER = logging.getLogger(__name__)


class Progress(RemoteProgress):
    """Download progress class for git cloning operations."""

    def __init__(self, *args, **kwargs):
        """Track the progress of a git clone operation."""
        super(Progress, self).__init__(*args, **kwargs)
        self.start_time = datetime.datetime.now()
        self.end_time = None

    def update(self, op_code, cur_count, max_count=None, message=''):
        """Print the update if one exists."""
        if message:
            LOGGER.debug(f'Downloading: (Elapsed time: {self.elapsed_time}) {message}\r')

    @property
    def elapsed_time(self):
        """Return a string of the elapsed time for the progress instantiation."""
        now = datetime.datetime.now()
        elapsed_time = now - self.start_time
        return str(elapsed_time)


def get_repo(repo_name, repo_config, branch=None):
    """Get a repository item or download it."""
    repo_path = os.path.join(repo_config['repo_base_path'], repo_name)
    if os.path.exists(repo_path):
        repo = git.Repo(repo_path)
        repo.git.pull(tags=True)
    else:
        repo = _download_repo(repo_name, branch=branch)
    return repo


def get_repos(repo_names: List[str], updated=True):
    repos: Dict[str, git.Repo] = {}
    for repo_name in repo_names:
        repo = get_repo(repo_name)
        default_branch = repo.git.symbolic_ref('HEAD')
        default_branch_name = default_branch.split('/')[-1]
        repos[repo_name] = repo
        if updated:
            repo.git.checkout(default_branch_name)
            repo.remotes.origin.fetch()
            repo.git.reset('--hard', f'origin/{default_branch_name}')
    return repos


def _download_repo(repo_name, repo_config, branch=None, ):
    """Download a respository."""
    repo_url = f"{repo_config['git_base_url']}{repo_name}.git"
    repo_path = os.path.join(repo_config['repo_base_path'], repo_name)
    repo = git.Repo.clone_from(repo_url, repo_path, progress=Progress())

    # Ensure we have dev and master locally.
    if branch is None:
        default_branch = repo.git.symbolic_ref('HEAD')
        default_branch_name = default_branch.split('/')[-1]
        branch = default_branch_name
    repo.git.checkout(branch)
    repo.git.pull()
    return repo