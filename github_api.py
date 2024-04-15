import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variables to store GitHub token
GITHUB_TOKEN = os.getenv('GITHUB_PAT')

def make_github_request(endpoint, params=None):
    """ Make a GET request to the specified GitHub API endpoint. """
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
    }
    base_url = 'https://api.github.com'
    response = requests.get(f'{base_url}{endpoint}', headers=headers, params=params)

    if response.ok:
        return response.json() # Return the response as JSON if the request was successful
    else:
        # Handle errors
        response.raise_for_status()

def list_pull_requests(owner, repo):
    """ List all pull requests for the specified repository. """
    endpoint = f'/repos/{owner}/{repo}/pulls'
    return make_github_request(endpoint)

def get_specific_pull_request(owner, repo, pull_request_number):
    """ Get a specific pull request."""
    endpoint = f'/repos/{owner}/{repo}/pulls/{pull_request_number}'
    return make_github_request(endpoint)

def list_commits_on_pull_request(owner, repo, pull_request_number):
    """ List all commits on a specific pull request. """
    endpoint = f'/repos/{owner}/{repo}/pulls/{pull_request_number}/commits'
    return make_github_request(endpoint)

def get_contents_of_file(owner, repo, path, ref=None):
    """ Get the contents of a file or directory on GitHub. """
    endpoint = f'/repos/{owner}/{repo}/contents/{path}'
    params = {'ref': ref} if ref else None
    return make_github_request(endpoint, params=params)