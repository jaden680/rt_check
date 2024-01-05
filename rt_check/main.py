from jira_issue_tracker import JiraReleaseIssueTracker
from git_commit_tracker import GitCommitTracker
from rich.console import Console
from rich.table import Table
import argparse

import constants

console = Console()

def get_commit_and_issue_data(commits, filter):
    jira_tracker = JiraReleaseIssueTracker(constants.JIRA_URL, constants.USER_NAME, constants.API_TOKEN, constants.PROJECT_KEY, filter)
    jira_tracker.load_issues_for_upcoming_release()
    
    unchecked_commits = []
    checked_commits = []
    checked_issues = []
    
    for commit in commits:
        issue_key = commit.jira_issue
        issue = jira_tracker.get_issue_in_upcoming_release(issue_key)

        commit_info = commit
        
        if issue is None:
            unchecked_commits.append(commit_info)
        else:
            if issue.get("is_sub_issue"):
                commit_info = commit._replace(parent_issue=issue.get("issue").key)
            checked_commits.append(commit_info)
            checked_issues.append(issue.get("issue"))

    
    # jira_tracker.issues에서 checked_issue에 없는 이슈만 필터링
    checked_issue_keys = {issue.key for issue in checked_issues}
    unchecked_issues = [issue for issue in jira_tracker.issues if issue.key not in checked_issue_keys]

    return checked_commits, unchecked_commits, unchecked_issues, jira_tracker


# 각각의 커밋과 이슈를 출력
def print_result(checked_commits, unchecked_commits, unchecked_issues, jira_tracker):
    console.print()
    console.print()

    # Table title
    title_all_issues = f"[bold white]All Issues ({len(jira_tracker.issues)})[/bold white]"
    title_checked_commits = f"[bold white]Checked Commits ({len(checked_commits)})[/bold white]"
    title_unchecked_commits = f"[bold white]Unchecked Commits ({len(unchecked_commits)})[/bold white]"
    title_unchecked_issues = f"[bold white]Unchecked Issues ([bold red]{len(unchecked_issues)}[/bold red])[/bold white]"

    #  Total Issues
    table = Table(title=title_all_issues, title_justify="left")
    table.add_column("Issue Key", style="white")
    table.add_column("Summary", style="white")

    for issue in jira_tracker.issues:
        table.add_row(issue.key, f"{issue.fields.summary}")

    console.print(table)
    console.print()

    # Checked Commits 표 생성
    table = Table(title=title_checked_commits, title_justify="left")
    table.add_column("Issue Key", style="white")
    table.add_column("Message", style="white")
    table.add_column("Commit Hash", style="white")
    table.add_column("Parent Issue Key", style="white")

    for commit in checked_commits:
        table.add_row(commit.jira_issue, commit.message, commit.commit_hash, commit.parent_issue)

    console.print(table)
    console.print()

    # Unchecked Commits 표 생성
    table = Table(title=title_unchecked_commits, title_justify="left")
    table.add_column("Issue Key", style="white")
    table.add_column("Message", style="white")
    table.add_column("Commit Hash", style="white")

    for commit in unchecked_commits:
        table.add_row(commit.jira_issue, commit.message, commit.commit_hash)

    console.print(table)
    console.print()

    # Unchecked Issues 표 생성
    table = Table(title=title_unchecked_issues, title_justify="left")
    table.add_column("Issue Key", style="white")
    table.add_column("Summary", style="white")

    for issue in unchecked_issues:
        table.add_row(issue.key, issue.fields.summary)

    console.print(table)
    console.print()

    # summary 출력
    table = Table(title=f"Summary [{jira_tracker.version.name} - {jira_tracker.filter}]", title_style="bold white", title_justify="left")
    table.add_column("Content", style="white")
    table.add_column("Count", style="white")
    
    table.add_row("Total_Issues              ", f"{len(jira_tracker.issues)}")
    table.add_row("Checked_commits           ", f"{len(checked_commits)}")
    table.add_row("Unchecked_commits         ", f"{len(unchecked_commits)}")
    table.add_row("Unchecked_issues          ", f"[bold red]{len(unchecked_issues)}[/bold red]")

    console.print(table)
    console.print()

    # 결과 출력
    if unchecked_issues:
        console.print(f"[bold red] {len(unchecked_issues)}[/bold red] 개의 이슈가 남아있습니다.")
    else:
        console.print("🎉🎉[bold green]Complete🎉🎉[/bold green]")
        if unchecked_commits:
            console.print("[티켓에 연결되지 않은 커밋이 있습니다. 확인해주세요 :)]")
            

def main(repo_path, ticket_filter):
    print(f"repo_path: {repo_path}, filter: {ticket_filter}")
    git_tracker = GitCommitTracker(repo_path)
    commits = git_tracker.get_merge_pull_request_commits()
    
    if not commits:
        print("Merge된 커밋이 없습니다.")
        return
    
    for commit in commits:
        console.print(f"[[bold green]{commit.jira_issue}[/bold green]] : [white]{commit.message}[/white]")

    checked_commits, unchecked_commits, unchecked_issues, jira_tracker = get_commit_and_issue_data(commits, ticket_filter)
    print_result(checked_commits, unchecked_commits, unchecked_issues, jira_tracker)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jira Issue Checker for Git")
    parser.add_argument('--path', type=str, default='.', help='Path to the Git directory')
    parser.add_argument('--filter', type=str, default=f'{constants.TICKET_FILTER}', help='Ticket filter')
    args = parser.parse_args()
    main(args.path, args.filter)
