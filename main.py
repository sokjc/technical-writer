import os
import base64
from openai import OpenAI
from github import Github

def format_data_for_openai(diffs, readme_content, commit_messages):
    # Combine the changes into a string with clear delineation.
    changes = '\n'.join([
        f'File: {file["filename"]}\nDiff: \n{file["patch"]}\n'
        for file in diffs
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
        f"{readme_content}\n"
        "Consider the code changes and commit messages, determine if the README needs to be updated. If so, edit the README, ensuring to maintain its existing style and clarity.\n"
        "Updated README:\n"
    )

    return prompt

def call_openai(prompt):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    try:
        # Construct the chat messages for the conversation
        messages = [
            {"role": "system", "content": "You are an AI trained to help with updating README files based on code changes."},
            {"role": "user", "content": prompt},
        ]

        # Make the API call to OpenAI chat interface
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )

        return response.choices[0].message.content 
    except Exception as e:
        print(f"Error making OpenAI API call: {e}")

def update_readme_and_create_pr(repo, updated_readme, readme_content):
    """Submit Updated README content as a PR in new branch."""
    commit_message = "Proposed README update based on recent code changes."

    # Create a new branch
    commit_sha = os.getenv('COMMIT_SHA')
    main_branch = repo.get_branch("main")
    new_branch_name = f"update-readme-{commit_sha[:7]}"
    new_branch = repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=main_branch.commit.sha)

    # Encode README
    updated_readme = base64.b64encode(updated_readme.encode('utf-8')).decode('utf-8')

    # Update the README on the new branch
    repo.update_file("README.md", commit_message, updated_readme, readme_content.sha, branch=new_branch_name)

    # Create a pull request    
    pr_title = "Update README based on recent changes"
    pr_body = "This PR proposes an update to the README based on recent code changes from the previous pull request."
    pull_request = repo.create_pull(title=pr_title, body=pr_body, head=new_branch_name, base="main")
    
    return pull_request # Return the pull request object if needed

def main():
    # Initialize GitHub API with token
    g = Github(os.getenv('GITHUB_TOKEN'))

    # Get the owner, repo name, and PR number from the environment variables
    owner = os.getenv('OWNER')
    repo_name = os.getenv('REPO')
    pull_request_number = int(os.getenv('PR_NUMBER'))
    
    # Get the repo object
    repo = g.get_repo(f"{owner}/{repo_name}")

    # Fetch README content (assuming README.md)
    readme_content = repo.get_contents("README.md").decoded_content.decode('utf-8')
    
    # print(readme_content)
    # Fetch pull request by number
    pull_request = repo.get_pull(pull_request_number)

    # Get the diffs of the pull request
    pull_request_diffs = [
        {
            "filename": file.filename,
            "patch": file.patch 
        } 
        for file in pull_request.get_files()
    ]
    
    # Get the commit messages associated with the pull request
    commit_messages = [commit.commit.message for commit in pull_request.get_commits()]

    # Format data for OpenAI prompt
    # prompt = format_data_for_openai(pull_request_diffs, readme_content, commit_messages)

    # Call OpenAI to generate the updated README content
    # updated_readme = call_openai(prompt)

    # Create PR for Updated PR
    # update_readme_and_create_pr(repo, updated_readme, readme_content)

if __name__ == '__main__':
    main()
