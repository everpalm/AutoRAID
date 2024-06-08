def buildApp() {
    echo 'Build - 1'
    sh "pipenv shell"
}

def testApp() {
    echo 'Start testing - 2'
}

return this