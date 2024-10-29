# Contents of test_gitlab.py
'''Unit tests for the GitLab API integration. This module includes tests
   for fetching, creating, updating, and deleting issues, as well as 
   interacting with project information within a simulated GitLab environment.
   Copyright (c) 2024 Jaron Cheng
'''
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture(scope="session")
def gitlab_api(request):
    """Fixture to provide a GitLab API client instance for testing.

    Args:
        request (FixtureRequest): Access to the requesting test context.

    Returns:
        Mocked GitLab API instance from the test configuration store.
    """
    return request.config._store.get('gitlab_api', None)


class TestGitLabAPI:
    """Test suite for GitLab API interactions, including issue management 
    and project details.
    """
    def test_fetch_test_case_content(self, gitlab_api):
        """Tests `fetch_test_case_content` by simulating fetching a specific 
        test case description for a given issue ID.

        Args:
            gitlab_api (MagicMock): Mocked GitLab API instance.

        Verifies:
            - Correct test case description is returned.
            - Project and issue retrieval calls occur with expected parameters.
        """
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
        """Tests `push_test_result` by simulating adding a test result 
        note and label to a specified issue in GitLab.

        Args:
            gitlab_api (MagicMock): Mocked GitLab API instance.

        Verifies:
            - Note is added to the correct issue.
            - Project and issue retrieval calls are performed as expected.
        """
        with patch.object(gitlab_api.gl.projects, 'get') as mock_get:
            mock_project = MagicMock()
            mock_issue = MagicMock()
            mock_project.issues.get.return_value = mock_issue
            mock_get.return_value = mock_project

            gitlab_api.push_test_result(test_case_id=1,
                                        test_result="All pass",
                                        label='Test Status::Passed',
                                        color='#00FF00')
            mock_get.assert_called_once_with('storage7301426/AutoRAID')
            mock_project.issues.get.assert_called_once_with(1)
            mock_issue.notes.create.assert_called_once_with({'body': "All pass"})

    def test_create_issue(self, gitlab_api):
        """Tests `create_issue` by simulating the creation of a new issue 
        in a GitLab project.

        Args:
            gitlab_api (MagicMock): Mocked GitLab API instance.

        Verifies:
            - A new issue is created with specified title and description.
            - Correct project retrieval and issue creation calls occur.
        """
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
        """Tests `get_project_info` by simulating retrieval of project 
        details such as name and ID.

        Args:
            gitlab_api (MagicMock): Mocked GitLab API instance.

        Verifies:
            - Project details are accurately retrieved.
            - Correct project retrieval call is made.
        """
        with patch.object(gitlab_api.gl.projects, 'get') as mock_get:
            mock_project = MagicMock()
            mock_project.attributes = {"name": "AutoRAID", "id": 12345}
            mock_get.return_value = mock_project

            project_info = gitlab_api.get_project_info()
            assert project_info == {"name": "AutoRAID", "id": 12345}
            mock_get.assert_called_once_with('storage7301426/AutoRAID')

    def test_list_issues(self, gitlab_api):
        """Tests `list_issues` by simulating retrieval of all issues in 
        a GitLab project.

        Args:
            gitlab_api (MagicMock): Mocked GitLab API instance.

        Verifies:
            - Issues are correctly listed from the project.
            - Project and issues listing calls occur as expected.
        """
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
        """Tests `update_issue` by simulating the update of an issue's title 
        and description in a GitLab project.

        Args:
            gitlab_api (MagicMock): Mocked GitLab API instance.

        Verifies:
            - Issue is updated with new title and description.
            - Project, issue retrieval, and update calls are correctly executed.
        """
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
        """Tests `delete_issue` by simulating the deletion of a specific 
        issue from a GitLab project.

        Args:
            gitlab_api (MagicMock): Mocked GitLab API instance.

        Verifies:
            - Issue is deleted as expected.
            - Project and issue retrieval, as well as delete calls, occur.
        """
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
        """Tests `get_test_case_id` by simulating retrieval of a specific 
        test case ID based on the title of a GitLab issue.

        Args:
            gitlab_api (MagicMock): Mocked GitLab API instance.

        Verifies:
            - Correct test case ID is retrieved for the given issue title.
            - Project and issue listing calls are executed as expected.
        """
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

