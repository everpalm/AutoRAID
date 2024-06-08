def buildApp() {
    echo 'Build - 1'
}

def testApp() {
    echo 'Start testing - 2'
    sh "cd /home/pi/Projects/AutoRAID/tests && pipenv run python -m pytest test_w10_interface.py --testmon"
}

return this