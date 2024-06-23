def buildApp() {
    echo 'Build - 1'
}

def testApp() {
    echo 'Start testing - 2'
    sh "cd /home/pi/Projects/AutoRAID/tests/test_amd_desktop && pipenv run python -m pytest tests/--testmon"
}

return this