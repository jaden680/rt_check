from collections import namedtuple
import subprocess
import re
import logging

CommitInfo = namedtuple('CommitInfo', 'commit_hash message branch_name jira_issue pull_request, parent_issue')

class GitCommitTracker:
    def __init__(self, repo_path='.'):
        self.repo_path = repo_path

    def update_branch(self, branch_name):
        try:
            subprocess.run(["git", "-C", self.repo_path, "checkout", branch_name], check=True)
            subprocess.run(["git", "-C", self.repo_path, "fetch", "origin"], check=True)
            subprocess.run(["git", "-C", self.repo_path, "reset", "--hard", f"origin/{branch_name}"], check=True)

        except subprocess.CalledProcessError as e:
            logging.error(f"Error: {e}")
        
    def get_merge_pull_request_commits(self, from_branch='main', to_branch='develop'):
        self.update_branch(from_branch)
        self.update_branch(to_branch)

        parsed_data = []

        command = ['git', 'log', f'{from_branch}..{to_branch}', '--oneline', '--grep=Merge pull request']
        # command = ['git', 'log', f'v7.80.0..v7.81.0', '--oneline', '--grep=Merge pull request']
        result = subprocess.run(command, cwd=self.repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        lines = result.stdout.strip().split('\n')
        
        for line in lines:
            # 빈 줄이 아닌 경우에만 처리
            if line.strip():
                # 공백을 기준으로 분리하여 커밋 해시와 메시지를 추출
                commit_hash, message = line.split(' ', 1)
                branch_name = message.split('from ')[-1] if 'from ' in message else None

                # 브랜치 이름에서 특정 패턴 (예: APP-xxxx) 찾기
                pattern = r'\b[A-Za-z]+-[A-Za-z0-9]+\b'
                issue_match = re.search(pattern, branch_name)
                jira_issue = issue_match.group() if issue_match else None

                # PR 번호 찾기
                pr_match = re.search(r'#\d+', message)
                pull_request = pr_match.group() if pr_match else None

                commit_info = CommitInfo(commit_hash, message, branch_name, jira_issue, pull_request, "-")
                parsed_data.append(commit_info)

        return parsed_data