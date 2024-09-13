def build_app() {
    echo 'Build - 1'
}

def test_amd_desktop() {
    echo 'test_amd_desktop'
    sh 'cd /home/pi/Projects/AutoRAID/tests/test_amd_desktop && pipenv run python -m pytest --testmon --private_token=$MY_PRIVATE_TOKEN'
}

def test_unit() {
    echo 'test_unit'
    sh 'cd /home/pi/Projects/AutoRAID/tests/test_unit && pipenv run python -m pytest --testmon --private_token=$MY_PRIVATE_TOKEN'
}

return this