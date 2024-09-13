def build_app() {
    sh 'pipenv sync'
}

def test_amd_desktop() {
    echo 'test_amd_desktop'
    sh 'cd ${TEST_AMD64_DESKTOP} && pipenv run pytest --testmon --private_token=$MY_PRIVATE_TOKEN'
}

def test_unit() {
    echo 'test_unit'
    sh 'cd ${WORKSPACE_DIR}/tests/test_unit && pipenv run pytest --testmon --private_token=$MY_PRIVATE_TOKEN'
}

def test_raspberry() {
    echo 'test_raspberry'
    sh 'cd ${WORKSPACE_DIR}/tests/test_unit && pipenv run pytest --testmon --private_token=$MY_PRIVATE_TOKEN'
}

def test_amd64_nvme() {
    sh 'pipenv run pytest ${TEST_AMD64_DESKTOP}/test_amd64_nvme.py --testmon --private_token=$MY_PRIVATE_TOKEN'
}
return this