import gitlab

class GitLabAPI:
    def __init__(self, private_token, project_id):
        self.gl = gitlab.Gitlab('https://gitlab.com',
                                private_token=private_token)
        self.project_id = project_id

    def fetch_test_case_content(self, test_case_id):
        project = self.gl.projects.get(self.project_id)
        test_case = project.issues.get(test_case_id)  # 假設測試項目是作為issue存在的
        return test_case.description  # 或其他需要的字段

    def push_test_result(self, test_case_id, test_result):
        project = self.gl.projects.get(self.project_id)
        test_case = project.issues.get(test_case_id)
        test_case.notes.create({'body': test_result})

    def create_issue(self, title, description):
        project = self.gl.projects.get(self.project_id)
        issue = project.issues.create({'title': title,
                                        'description': description})
        return issue

    def get_project_info(self):
        project = self.gl.projects.get(self.project_id)
        return project.attributes

    def list_issues(self):
        project = self.gl.projects.get(self.project_id)
        issues = project.issues.list(all=True)
        return issues

    def update_issue(self, issue_id, title=None, description=None):
        project = self.gl.projects.get(self.project_id)
        issue = project.issues.get(issue_id)
        if title:
            issue.title = title
        if description:
            issue.description = description
        issue.save()
        return issue

    def delete_issue(self, issue_id):
        project = self.gl.projects.get(self.project_id)
        issue = project.issues.get(issue_id)
        issue.delete()
