def buildApp() {
    echo 'Build - 1'
}

def testApp() {
    echo 'Start testing - 2'
    sh "cd /home/pi/Projects/AutoRAID/worksapce/AutoRAID && pipenv run python -m pytest --testmon"
}

return this