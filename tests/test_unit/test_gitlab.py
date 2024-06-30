# import pytest
from unittest.mock import MagicMock, patch


class TestGitLabAPI:
    def test_fetch_test_case_content(self, gitlab_api):
        with patch.object(gitlab_api.gl.projects, 'get') as mock_get:
            mock_project = MagicMock()
            mock_issue = MagicMock()
            mock_issue.description = "This is a mock"
            mock_project.issues.get.return_value = mock_issue
            mock_get.return_value = mock_project

            content = gitlab_api.fetch_test_case_content(test_case_id=1)
            assert content == "This is a mock"
            mock_get.assert_called_once_with('storage7301426/AutoRAID')
            mock_project.issues.get.assert_called_once_with(1)

    def test_push_test_result(self, gitlab_api):
        with patch.object(gitlab_api.gl.projects, 'get') as mock_get:
            mock_project = MagicMock()
            mock_issue = MagicMock()
            mock_project.issues.get.return_value = mock_issue
            mock_get.return_value = mock_project

            gitlab_api.push_test_result(test_case_id=1, test_result="All pass")
            mock_get.assert_called_once_with('storage7301426/AutoRAID')
            mock_project.issues.get.assert_called_once_with(1)
            mock_issue.notes.create.assert_called_once_with({'body': "All pass"})

    def test_create_issue(self, gitlab_api):
        with patch.object(gitlab_api.gl.projects, 'get') as mock_get:
            mock_project = MagicMock()
            mock_issue = MagicMock()
            mock_project.issues.create.return_value = mock_issue
            mock_get.return_value = mock_project

            issue = gitlab_api.create_issue(title="New issue",
                                            description="A new issue")
            assert issue == mock_issue
            mock_get.assert_called_once_with('storage7301426/AutoRAID')
            mock_project.issues.create.assert_called_once_with(
                {'title': "New issue", 
                'description': "A new issue"})

    def test_get_project_info(self, gitlab_api):
        with patch.object(gitlab_api.gl.projects, 'get') as mock_get:
            mock_project = MagicMock()
            mock_project.attributes = {"name": "AutoRAID", "id": 12345}
            mock_get.return_value = mock_project

            project_info = gitlab_api.get_project_info()
            assert project_info == {"name": "AutoRAID", "id": 12345}
            mock_get.assert_called_once_with('storage7301426/AutoRAID')

    def test_list_issues(self, gitlab_api):
        with patch.object(gitlab_api.gl.projects, 'get') as mock_get:
            mock_project = MagicMock()
            mock_issue = MagicMock()
            mock_project.issues.list.return_value = [mock_issue]
            mock_get.return_value = mock_project

            issues = gitlab_api.list_issues()
            assert issues == [mock_issue]
            mock_get.assert_called_once_with('storage7301426/AutoRAID')
            mock_project.issues.list.assert_called_once_with(all=True)

    def test_update_issue(self, gitlab_api):
        with patch.object(gitlab_api.gl.projects, 'get') as mock_get:
            mock_project = MagicMock()
            mock_issue = MagicMock()
            mock_get.return_value = mock_project
            mock_project.issues.get.return_value = mock_issue

            updated_issue = gitlab_api.update_issue(issue_id=1,
                    title="Updated title",
                    description="Updated description")
            assert updated_issue == mock_issue
            mock_get.assert_called_once_with('storage7301426/AutoRAID')
            mock_project.issues.get.assert_called_once_with(1)
            mock_issue.save.assert_called_once()
            assert mock_issue.title == "Updated title"
            assert mock_issue.description == "Updated description"

    def test_delete_issue(self, gitlab_api):
        with patch.object(gitlab_api.gl.projects, 'get') as mock_get:
            mock_project = MagicMock()
            mock_issue = MagicMock()
            mock_get.return_value = mock_project
            mock_project.issues.get.return_value = mock_issue

            gitlab_api.delete_issue(issue_id=1)
            mock_get.assert_called_once_with('storage7301426/AutoRAID')
            mock_project.issues.get.assert_called_once_with(1)
            mock_issue.delete.assert_called_once()

    def test_get_test_case_id(self, gitlab_api):
        with patch.object(gitlab_api.gl.projects, 'get') as mock_get:
            mock_project = MagicMock()
            mock_issue_1 = MagicMock()
            mock_issue_2 = MagicMock()
            mock_issue_1.title = "test_case_1"
            mock_issue_1.iid = 1
            mock_issue_2.title = "test_case_2"
            mock_issue_2.iid = 2
            mock_project.issues.list.return_value = [mock_issue_1, mock_issue_2]
            mock_get.return_value = mock_project

            test_case_id = gitlab_api.get_test_case_id("test_case_2")
            assert test_case_id == 2
            mock_get.assert_called_once_with('storage7301426/AutoRAID')
            mock_project.issues.list.assert_called_once_with(all=True)
    
    def test_get_case1(self):
        assert 1 == 1

    def test_get_case2(self):
        assert 1 == 2
