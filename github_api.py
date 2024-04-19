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

def put_readme_contents(owner, repo, readme_contents, commit_message, sha):
    """ Create a PR with the updated README that was based on revised content from previously merged PR."""
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    session = requests.Session()
    session.headers.update(headers)

    # Step 1: Create a new branch
    # Get the commit SHA from the previous merged PR
    default_branch_url = f'https://api.github.com/repos/{owner}/{repo}/git/ref/heads/main'
    response = session.get(default_branch_url)
    response.raise_for_status()
    latest_commit_sha = response.json()['object']['sha']

    # Create new branch
    new_branch = f'update-readme-{latest_commit_sha[:7]}'  # Create a new branch based on the commit SHA
    new_branch_url = f'https://api.github.com/repos/{owner}/{repo}/git/refs'
    new_branch_data = {
        'ref': f'refs/heads/{new_branch}',
        'sha': latest_commit_sha
    }
    response = session.post(new_branch_url, json=new_branch_data)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.reason} - {e.response.text}")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"Request exception: {e}")
        raise

    # Step 2: Update the README on the new branch
    update_url = f'https://api.github.com/repos/{owner}/{repo}/contents/README.md'
    update_date = {
        'message': commit_message,
        'content': base64.b64encode(readme_contents.encode('utf-8')).decode('utf-8'),
        'sha': sha,
        'branch': new_branch
    }
    response = session.put(update_url, json=update_date)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.reason} - {e.response.text}")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"Request exception: {e}")
        raise

    # Step 3: Create a pull request
    pr_url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
    pr_data = {
        'title': 'Update README based on PR changes',
        'head': new_branch,
        'base': 'main',
        'body': 'This PR updates the README based on the latest code changes from the previously merged PR.'
    }
    response = session.post(pr_url, json=pr_data)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.reason} - {e.response.text}")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"Request exception: {e}")
        raise

    return response.json() # Return the response JSON if the request was successful