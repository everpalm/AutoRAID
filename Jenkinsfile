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
                'all',
                'amd_desktop',
                'raspberry',
                'unit'
            ],
            description: 'Test Suite',
            name: 'TEST_SUITE'
        )
        choice(
            choices: [
                'amd64_nvme',
                'amd64_perf',
                'amd64_ping',
                'amd64_stress',
                'application_interface',
                'test_pi3_gpio',
            ],
            description: 'Test case',
            name: 'TEST_CASE'
        )
        choice(
            choices: [
                'TestRandomReadWrite',
                'TestSequentialReadWrite',
                'TestRampTimeReadWrite',
                'TestAMD64MultiPathStress',
                'TestAMD64Ping',
                'TestApplicationInterface'
            ],
            description: 'Test step',
            name: 'TEST_STEP'
        )
    }
    environment {
        MY_PRIVATE_TOKEN = credentials('gitlab-private-token')
        WORKSPACE_DIR = '/home/pi/Projects/AutoRAID/workspace/AutoRAID'
        TEST_AMD64_DESKTOP = '${WORKSAPCE_DIR}/tests/test_amd64_desktop'
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
                    gv.build_app()
                }
            }
        }
        stage('Testing') {
            steps {
                script {
                    if (params.TEST_SUIT == 'unit' || params.TEST_SUIT == 'all') {
                        gv.test_unit()
                    } else if (params.TEST_SUIT == 'amd_desktop' || params.TEST_SUITE == 'all') {
                        gv.test_amd_desktop()
                    } else if (params.TEST_SUIT == 'rasperberry' || params.TEST_SUIT == 'all') {
                        gv.test_raspberry()
                    } else if (params.TEST_CASE == 'amd64_nvme') {
                        gv.test_amd64_nvme()
                    } else if (params.TEST_CASE == 'amd64_perf') {
                        gv.test_amd64_perf()
                    } else if (params.TEST_CASE == 'amd64_stress') {
                        gv.test_amd64_stress()
                    } else if (params.TEST_CASE == 'application_interface') {
                        gv.test_application_interface()
                    }
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
            stash includes: '.testmondata', name: 'testmondata', allowEmpty: true
        }
        success {
            echo 'Build succeeded.'
        }
        failure {
            echo 'Build failed.'
        }
    }
}
