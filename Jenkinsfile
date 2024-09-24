pipeline {
    triggers {
        // Poll SCM every 5 minutes for new commits on development branch
        pollSCM('H/5 * * * *')
    }
    agent {
        label 'test_my_node'
    }
    environment {
        MY_PRIVATE_TOKEN = credentials('gitlab-private-token')
        VERSION_FILE = "${WORKSPACE}/version.txt"
        GIT_TOKEN = credentials('github-token')
        TEST_UNIT = "${WORKSPACE}/tests/test_unit"
        TEST_AMD_DESKTOP = "${WORKSPACE}/test_amd_desktop"
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
                    gv.test_unit()
                }
            }
        }
    }
    post {
        success {
            script {
                def versionContent = readFile(file: VERSION_FILE).trim()
                def (mainVersion, subVersion, buildVersion) = versionContent.tokenize('.')
                buildVersion = buildVersion.toInteger() + 1
                def newVersion = "${mainVersion}.${subVersion}.${buildVersion}"
                writeFile(file: VERSION_FILE, text: newVersion)

                sh """
                git config user.name "everpalm"
                git config user.email "everpalm@yahoo.com.tw"
                git add version.txt
                git commit -m "Bumped build version to ${newVersion} after successful development"
                git tag -a "v${newVersion}" -m "Tagging version v${newVersion} after Development stage"
                git push https://everpalm:${GIT_TOKEN}@github.com/everpalm/AutoRAID.git --tags
                """
                echo "Build version updated and tagged to v${newVersion}"

                // Merge development to staging
                sh """
                git checkout staging
                git merge development
                git push https://everpalm:${GIT_TOKEN}@github.com/everpalm/AutoRAID.git staging
                """
            }
        }
    }
}
