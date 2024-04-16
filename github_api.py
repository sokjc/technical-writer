import requests
import os
import base64
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

def get_file_diffs_in_pull_request(owner, repo, pull_request_number):
    """ Get the diffs of files changed in a specific pull request. """
    endpoint = f'/repos/{owner}/{repo}/pulls/{pull_request_number}/files'
    files_changed = make_github_request(endpoint)

    diffs = {}
    for file in files_changed:
        if 'patch' in file:
            file_path = file['filename']
            file_diff = file['patch']
            diffs[file_path] = file_diff
        else:
            # Handle or log casses where 'patch' is not available
            print(f"No 'patch' key for file: {file['filename']}. Status: {file.get('status')}. This file may be a binary or was not modified in a way that includes a diff.")

    return  diffs 

def list_commits_on_pull_request(owner, repo, pull_request_number):
    """ List all commits on a specific pull request. """
    endpoint = f'/repos/{owner}/{repo}/pulls/{pull_request_number}/commits'
    return make_github_request(endpoint)

def get_commit_messages(owner, repo, pull_request_number):
    """Get commit messages for a specific pull request"""
    commits = list_commits_on_pull_request(owner, repo, pull_request_number)
    commit_messages = [commit['commit']['message'] for commit in commits]

    return commit_messages

def get_contents_of_file(owner, repo, path, ref=None):
    """ Get the contents of a file or directory on GitHub. """
    endpoint = f'/repos/{owner}/{repo}/contents/{path}'
    params = {'ref': ref} if ref else None
    
    # Use the 'get_contents_of_file' endpoint to get the contents of a file
    content = make_github_request(endpoint, params=params)

    # Decode the content if the request was successful
    if 'content' in content:
        decoded = base64.b64decode(content['content'])
        content['content'] = decoded.decode('utf-8')
    else:
        print(f"No 'content' key in content for file: {path}. Status: {content.get('status')}.")

    return content 