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
                // echo 'Build - 1'
                script {
                    gv.buildApp()
                }
            }
        }
        stage('Test') {
            // when {
            //     expression {
            //         BRANCH_NAME == 'ZenNevo'
            //     }
            // }
            steps {
                // echo 'Start testing - 2'
                script {
                    gv.testApp()
                }
                // sh 'cd /home/pi/NVME_ACCELERATOR/workspace/NVME_ACCELERATOR/demo/tests && python3 -m pytest -s -v -x test_system_under_testing.py'
                sh "cd /home/pi/Projects/AutoRAID/tests && python -m pytest test_${params.MY_SUITE}.py"
            }
        }
    }
    post {
        always {
            emailext body: 'Test results are available at: $BUILD_URL', subject: 'Test Results', to: 'ctingjung@marvell.com'
        }
        success {
            echo 'todo - 1'
        }
        failure {
            echo 'todo - 2'
        }
    }
}