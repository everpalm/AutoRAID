def gv
pipeline {
    triggers {
        // Trigger hook every 5 minutes
        pollSCM('H/5 * * * *')
    }
    agent {
        // Run test on the nodes with the same label
        label 'test_my_node'
    }
    parameters {
        // Add parameters for test suite selection
        choice(
            choices: [
                'test_amd_desktop',
                'test_unit'
            ],
            description: 'Select the test environment',
            name: 'TEST_ENVIRONMENT'
        )
        choice(
            choices: [
                'all',
                'system_under_testing',
                'win10_interface',
                'device_under_testing'
            ],
            description: 'My Test Suite',
            name: 'MY_SUITE'
        )
        choice(
            choices: [
                'all',
                'system_under_testing',
                'win10_interface',
                'device_under_testing'
            ],
            description: 'Functional Test',
            name: 'FUNCTIONAL'
        )
    }
    environment {
        MY_PRIVATE_TOKEN = credentials('gitlab-private-token')
    }
    stages {
        stage("Init") {
            steps {
                script {
                    gv = load "script.groovy"
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    gv.buildApp()
                }
            }
        }
        stage('Testing') {
            steps {
                script {
                    if (params.TEST_ENVIRONMENT == 'test_unit') {
                        // sh "cd /home/pi/Projects/AutoRAID/tests/test_unit && pipenv run python -m pytest --testmon --private_token=${MY_PRIVATE_TOKEN}"
                        sh 'cd /home/pi/Projects/AutoRAID/tests/test_unit && pipenv run python -m pytest --testmon --private_token=$MY_PRIVATE_TOKEN'
                    } else if (params.TEST_ENVIRONMENT == 'test_amd_desktop') {
                        // sh "cd /home/pi/Projects/AutoRAID/tests/test_amd_desktop && pipenv run python -m pytest --testmon --private_token=${MY_PRIVATE_TOKEN}"
                        sh 'cd /home/pi/Projects/AutoRAID/tests/test_amd_desktop && pipenv run python -m pytest --testmon --private_token=$MY_PRIVATE_TOKEN'
                    }
                }
            }
        }
        stage('Staging') {
            when {
                expression {
                    params.MY_SUITE == 'win10_interface' || params.MY_SUITE == 'all'
                }
            }
            steps {
                script {
                    gv.testApp()
                }
            }
        }
    }
    post {
        always {
            emailext body: 'Test results are available at: $BUILD_URL', subject: 'Test Results', to: 'everpalm@yahoo.com.tw'
            // sh "pipenv run python -m pytest --cache-clear"
        }
        success {
            echo 'todo - 1'
        }
        failure {
            echo 'todo - 2'
        }
    }
}
