from jira import JIRA
from datetime import datetime
import pytz
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

class JiraReleaseIssueTracker:
    def __init__(self, jira_url, username, api_token, project_key, filter):
        options = {
            'server': jira_url,
            'verify': False
        }
        self.jira = JIRA(options=options, basic_auth=(username, api_token))
        self.project_key = project_key
        self.filter = filter

    def get_filtered_issues_by_version_and_filter(self, fix_version, filter):
        jql = f'project = "{self.project_key}" AND fixVersion = "{fix_version}" order by created DESC'
        issues = self.jira.search_issues(jql, maxResults=1000)

        filter_lower = filter.lower()
        filtered_issues = [issue for issue in issues if filter_lower in issue.fields.summary.lower()]
        return filtered_issues

    def get_release_version(self, project_key):
        project = self.jira.project(project_key)
        versions = self.jira.project_versions(project)
        current_date = datetime.now(pytz.utc).date()

        unreleased_versions = []
        for version in versions:
            try:
                if not version.released:
                    release_date = datetime.strptime(version.releaseDate, '%Y-%m-%d').date()
                    if release_date >= current_date:
                        unreleased_versions.append(version)
                else:
                    pass
            except:  # releaseDate is None
                pass

        unreleased_versions.sort(key=lambda x: x.releaseDate, reverse=False)
        return unreleased_versions[0] if unreleased_versions else None

    def get_issue_in_upcoming_release(self, issue_key):
        matched_issue = next((issue for issue in self.issues if issue.key == issue_key), None)
        if matched_issue is not None:
            return {"issue": matched_issue, "is_sub_issue": False}
        
        try:
            issue = self.jira.issue(issue_key)
        except:
            return None
    

        issue = self.jira.issue(issue_key)

        if issue is None:
            return None
        
        parent_issues = getattr(issue.fields, 'parent', None)

        if parent_issues is None:
            return None
        else:
            if parent_issues in self.issues:
                return {"issue": parent_issues, "is_sub_issue": True}
            else:
                return None

    def load_issues_for_upcoming_release(self):
        self.version = self.get_release_version(self.project_key)
        if self.version is None:
            logging.error("미 배포 버전이 없습니다.")
            return
        
        # self.issues = self.get_filtered_issues_by_version_and_filter("23' 12월 2주차(12/11)", self.filter)
        self.issues = self.get_filtered_issues_by_version_and_filter(self.version.name, self.filter)
        if not self.issues:
            logging.error(f"{self.version.name} - 등록된 이슈가 없습니다.")
            return