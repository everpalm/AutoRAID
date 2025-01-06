pipeline {
    agent {
        label 'test_my_node'
    }
    // triggers {
    //     pollSCM('H/5 * * * *')
    // }
    environment {
        MY_PRIVATE_TOKEN = credentials('gitlab-private-token')
        VERSION_FILE = "${WORKSPACE}/version.txt"
        GIT_TOKEN = credentials('github-token')
        TEST_UNIT = "${WORKSPACE}/tests/test_unit"
        TEST_AMD_DESKTOP = "${WORKSPACE}/tests/test_amd_desktop"
        TEST_STORAGE = "${WORKSPACE}/tests/test_storage"
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
        stage('Unit Testing') {
            steps {
                script {
                    gv.test_pep8(env.TEST_AMD_DESKTOP)
                    gv.test_pep8(env.TEST_STORAGE)
                    gv.test_unit(env.TEST_UNIT, env.MY_PRIVATE_TOKEN)
                }
            }
        }
        stage('Sanity Testing') {
            steps {
                script {
                    gv.test_sanity(env.TEST_AMD_DESKTOP)
                    gv.test_regression(env.TEST_STORAGE)
                }
            }
        }
    }
    post {
        always {
            script {
                archiveArtifacts artifacts: 'htmlcov/**', allowEmptyArchive: true
            }
        }
        success {
            emailext(
                to: 'everpalm@yahoo.com.tw',
                subject: "Build Success: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """<p>All tests passed successfully!</p>
                         <p>Please check the attached test coverage report.</p>""",
                mimeType: 'text/html',
                attachmentsPattern: 'htmlcov/index.html'
            )
            script {
                try {
                    sh """
                    git fetch origin
                    git checkout staging
                    git merge origin/staging
                    git merge origin/development
                    git push https://everpalm:$GIT_TOKEN@github.com/everpalm/AutoRAID.git staging
                    """
                    build job: 'AutoRAID_Staging', wait: false
                } catch (e) {
                    echo "An error occurred: ${e.getMessage()}"
                    currentBuild.result = 'FAILURE'
                }
            }
        }
        failure {
            emailext(
                to: 'everpalm@yahoo.com.tw',
                subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: 'The build has failed. Please check the Jenkins console output for details.',
                mimeType: 'text/html',
                attachmentsPattern: 'htmlcov/index.html'
            )
        }
    }
}
