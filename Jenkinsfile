def gv
// CODE_CHANGES = GetGitChanges()
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
        // Add parameters for any test suite
        // booleanParam(name: 'executeTest', defaultValue: true, description: '')
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
    }
    stages {
        stage ("Init") {
            steps {
                script {
                    gv = load "script.groovy"
                }
            }
        }
        stage('Build') {
            // when {
            //     expression {
            //         CODE_CHANGES == true
            //     }
            // }
            steps {
                script {
                    gv.buildApp()
                }
            }
        }
        stage('Staging') {
            when {
                expression {
                    params.MY_SUITE == 'win10_interface' || 'all'
                }
            }
            steps {
                // echo 'Start testing - 2'
                script {
                    gv.testApp()
                }
                // sh "cd /home/pi/Projects/AutoRAID/tests && pipenv run python -m pytest test_${params.MY_SUITE}.py"
            }
        }
    }
    post {
        always {
            emailext body: 'Test results are available at: $BUILD_URL', subject: 'Test Results', to: 'everpalm@ms58.url.com.tw'
        }
        success {
            echo 'todo - 1'
        }
        failure {
            echo 'todo - 2'
        }
    }
}