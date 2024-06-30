import gitlab
import logging

logger = logging.getLogger(__name__)

class GitLabAPI:
    def __init__(self, private_token, project_id):
        self.gl = gitlab.Gitlab('https://gitlab.com',
                                private_token=private_token)
        self.project_id = project_id

    def fetch_test_case_content(self, test_case_id):
        project = self.gl.projects.get(self.project_id)
        test_case = project.issues.get(test_case_id)  # 假設測試項目是作為issue存在的
        return test_case.description  # 或其他需要的字段

    def push_test_result(self, test_case_id, test_result, label, color):
        # project = self.gl.projects.get(self.project_id)
        # # logger.debug(f'project = f{project}')
        # test_case = project.issues.get(test_case_id)
        # test_case.notes.create({'body': test_result})
        project = self.gl.projects.get(self.project_id)
        test_case = project.issues.get(test_case_id)
        
        # 創建測試結果筆記
        note = test_case.notes.create({'body': test_result})
        logger.debug(f'Pushed test result: {note.body}')
        
        # 添加標籤
        labels = test_case.labels
        if label not in labels:
            labels.append(label)
        # test_case.labels = labels
        # test_case.save()
        
        # logger.debug(f'Updated labels for test case: {test_case.labels}')
        # return note
        # 創建或更新標籤
        try:
            project.labels.create({'name': label, 'color': color})
        except gitlab.exceptions.GitlabCreateError:
            # 標籤已存在，更新其顏色
            existing_label = project.labels.get(label)
            existing_label.color = color
            existing_label.save()
        
        test_case.labels = labels
        test_case.save()
        
        logger.debug(f'Updated labels for test case: {test_case.labels}')
        return note

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
    
    def get_test_case_id(self, test_case_name):
        project = self.gl.projects.get(self.project_id)
        issues = project.issues.list(all=True)
        for issue in issues:
            if issue.title == test_case_name:
                return issue.iid
        return None
    
    def get_test_case_notes(self, test_case_id):
        project = self.gl.projects.get(self.project_id)
        test_case = project.issues.get(test_case_id)
        notes = test_case.notes.list()
        return notes
