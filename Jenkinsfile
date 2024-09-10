pipeline {
    triggers {
        // Trigger build every 5 minutes
        pollSCM('H/5 * * * *')
        // Weekly cleanup trigger (e.g., every Monday at midnight)
        cron('H 0 * * 1')
    }
    agent {
        // Run tests on the nodes with the specified label
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
                'application_interface',
                'device_under_testing'
            ],
            description: 'My Test Suite',
            name: 'MY_SUITE'
        )
        choice(
            choices: [
                'all',
                'system_under_testing',
                'application_interface',
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
                    // Unstash the .testmondata file from the previous build, if exists
                    catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                        unstash name: 'testmondata'
                    }
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
                        sh 'cd /home/pi/Projects/AutoRAID/tests/test_unit && pipenv run pytest --testmon --private_token=$MY_PRIVATE_TOKEN'
                    } else if (params.TEST_ENVIRONMENT == 'test_amd_desktop') {
                        sh 'cd /home/pi/Projects/AutoRAID/tests/test_amd_desktop && pipenv run pytest --testmon --private_token=$MY_PRIVATE_TOKEN'
                    }
                }
            }
        }
        stage('Staging') {
            when {
                expression {
                    params.MY_SUITE == 'application_interface' || params.MY_SUITE == 'all'
                }
            }
            steps {
                script {
                    gv.testApp()
                }
            }
        }
        stage('Weekly Cleanup') {
            when {
                triggeredBy 'TimerTrigger'
            }
            steps {
                script {
                    echo "Weekly cleanup: Removing .testmondata file"
                    sh 'rm -f .testmondata'
                }
            }
        }
    }
    post {
        always {
            // Send email notification
            emailext body: 'Test results are available at: $BUILD_URL', subject: 'Test Results', to: 'everpalm@yahoo.com.tw'
            // Stash the .testmondata file for the next build
            stash includes: '.testmondata', name: 'testmondata'
        }
        success {
            echo 'Build succeeded.'
        }
        failure {
            echo 'Build failed.'
        }
    }
}
