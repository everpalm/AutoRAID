pipeline {
    agent {
        label 'test_my_node'
    }
    triggers {
        // Poll SCM every 5 minutes for new commits on development branch
        pollSCM('H/5 * * * *')
    }
    environment {
        MY_PRIVATE_TOKEN = credentials('gitlab-private-token')
        VERSION_FILE = "${WORKSPACE}/version.txt"
        GIT_TOKEN = credentials('github-token')
        TEST_UNIT = "${WORKSPACE}/tests/test_unit"
        TEST_AMD_DESKTOP = "${WORKSPACE}/tests/test_amd_desktop"
        PATH = "/home/pi/.pyenv/shims:/home/pi/.pyenv/bin:${env.PATH}"
    }
    stages {
        stage('Init') {
            steps {
                script {
                    echo 'Initializing development pipeline...'
                    gv = load "${WORKSPACE}/script.groovy"
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    gv.build_app()
                }
            }
        }
        stage('Testing') {
            steps {
                script {
                    gv.test_pep8()
                    gv.test_unit()
                    gv.test_amd64_nvme()
                }
            }
        }
    }
    post {
        always {
            script {
                // 總是將測試報告存檔
                archiveArtifacts artifacts: '**/htmlcov/**', allowEmptyArchive: true
            }
        }
        success {
            emailext(
                to: 'everpalm@yahoo.com.tw',
                subject: "Build Success: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """<p>All tests passed successfully!</p>
                         <p>Please check the attached test coverage report.</p>""",
                mimeType: 'text/html',
                attachmentsPattern: '**/htmlcov/index.html'
            )
            script {
                try {
                    // 合併 development 到 staging
                    sh """
                    git fetch origin
                    git checkout staging
                    git merge origin/staging
                    git merge origin/development
                    """
                    sh('git push https://everpalm:$GIT_TOKEN@github.com/everpalm/AutoRAID.git staging')
                } catch (e) {
                    echo "An error occurred during the post-build process: ${e.getMessage()}"
                    currentBuild.result = 'FAILURE'
                }
            }
        }
        failure {
            emailext(
                to: 'everpalm@yahoo.com.tw',
                subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: 'The build has failed. Please check the Jenkins console output for details.',
                mimeType: 'text/html'
            )
        }
    }
}
