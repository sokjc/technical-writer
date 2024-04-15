import os
from dotenv import load_dotenv
from github_api import *

# Load environment variables
load_dotenv()

# Informal testing of api functions
def test_list_pull_requests(owner, repo):
    print("Testing: List Pull Requests")
    response = list_pull_requests(owner, repo)
    print(response)

def test_get_specific_pull_request(owner, repo, pull_request_number):
    print("Testing: Get Specific Pull Request")
    response = get_specific_pull_request(owner, repo, pull_request_number)
    print(response)

def test_list_commits_on_pull_request(owner, repo, pull_request_number):
    print("Testing: List Commits on Pull Request")
    response = list_commits_on_pull_request(owner, repo, pull_request_number)
    print(response)

def test_get_contents_of_file(owner, repo, path):
    print("Testing: Get Contents of File")
    response = get_contents_of_file(owner, repo, path)
    print(response)

if __name__ == '__main__':
    owner = os.getenv('GITHUB_OWNER')
    repo = os.getenv('GITHUB_REPO')
    pull_request_number = '1'
    path = 'README.md'

    test_list_pull_requests(owner, repo)
    test_get_specific_pull_request(owner, repo, pull_request_number)
    test_list_commits_on_pull_request(owner, repo, pull_request_number)
    test_get_contents_of_file(owner, repo, path)