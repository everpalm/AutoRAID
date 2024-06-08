def buildApp() {
    echo 'Build - 1'
}

def testApp() {
    echo 'Start testing - 2'
    sh "cd /home/pi/Projects/AutoRAID/tests && pipenv run python -m pytest test_${params.MY_SUITE}.py --testmon"
}

return this