import os
from github_api import *
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def format_data_for_openai(diffs, file_content, commit_messages):
    # Combine the changes into a string with clear delineation.
    changes = '\n'.join([
        f'File: {file_path}\nDiff: \n{diff}\n' 
        for file_path, diff in diffs.items()
    ])

    # Combine all commit messages
    commit_messages = '\n'.join(commit_messages) + '\n\n'

    # Construct the prompt with clear instructions for the LLM.
    prompt = (
        "Please review the following code changes and commit messages from a GitHub pull request:\n"
        "Code changes from Pull Request:\n"
        f"{changes}\n"
        "Commit messages:\n"
        f"{commit_messages}"
        "Here is the current README file content:\n"
        f"{file_content}\n"
        "Consider the code changes and commit messages, determine if the README needs to be updated. If so, edit the README, ensuring to maintain its existing style and clarity.\n"
        "Updated README:\n"
    )

    return prompt

def main():
    # Example owner, repo, and PR number - replace with dynamic values as necessary
    owner = os.getenv('OWNER')
    repo = os.getenv('REPO')
    pull_request_number = 3

    # Fetch README content, PR diffs, and commit messages
    readme_content = get_contents_of_file(owner, repo, 'README.md')
    pull_request_diffs = get_file_diffs_in_pull_request(owner, repo, pull_request_number)
    commit_messages = get_commit_messages(owner, repo, pull_request_number)

    # Format data for OpenAI prompt
    prompt = format_data_for_openai(pull_request_diffs, readme_content['content'], commit_messages)

    # For testing purposes
    print(prompt)

if __name__ == '__main__':
    main()