pipeline {
    agent {
        label 'test_my_node'
    }
    environment {
        MY_PRIVATE_TOKEN = credentials('gitlab-private-token')
        VERSION_FILE = "${WORKSPACE}/version.txt"
        GIT_TOKEN = credentials('github-token')
        TEST_UNIT = "${WORKSPACE}/tests/test_unit"
        TEST_AMD_DESKTOP = "${WORKSPACE}/tests/test_amd_desktop"
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
                }
            }
        }
    }
    post {
        success {
            script {
                try {
                    // 合併 development 到 staging
                    sh """
                    git fetch origin
                    git checkout staging
                    git merge origin/staging
                    git merge origin/development
                    git push https://everpalm:${env.GIT_TOKEN}@github.com/everpalm/AutoRAID.git staging
                    """
                } catch (e) {
                    echo "An error occurred during the post-build process: ${e.getMessage()}"
                    currentBuild.result = 'FAILURE'
                }
            }
        }
    }
}
