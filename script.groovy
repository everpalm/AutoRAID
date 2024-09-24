def build_app() {
    sh 'pipenv sync'
}

def test_amd_desktop() {
    echo 'test_amd_desktop'
    sh 'pipenv run pytest ${TEST_AMD_DESKTOP} --testmon --private_token=$MY_PRIVATE_TOKEN'
}

def test_unit() {
    echo 'test_unit'
    sh 'pipenv run pytest ${TEST_UNIT} --testmon --private_token=$MY_PRIVATE_TOKEN'
}

def test_raspberry() {
    echo 'test_raspberry'
    sh 'pipenv run pytest --testmon --private_token=$MY_PRIVATE_TOKEN'
}

def test_amd64_nvme() {
    sh 'pipenv run pytest ${TEST_AMD_DESKTOP}/test_amd64_nvme.py --testmon --private_token=$MY_PRIVATE_TOKEN'
}

def test_amd64_perf() {
    sh 'pipenv run pytest ${TEST_AMD_DESKTOP}/test_amd64_perf.py --testmon --private_token=$MY_PRIVATE_TOKEN'
}

def test_amd64_stress() {
    sh 'pipenv run pytest ${TEST_AMD_DESKTOP}/test_amd64_stress.py --testmon --private_token=$MY_PRIVATE_TOKEN'
}
def test_application_interface() {
    sh 'pipenv run pytest ${TEST_AMD_DESKTOP}/test_application_interface.py --testmon --private_token=$MY_PRIVATE_TOKEN'
}

def test_pep8() {
    sh 'pylint ${WORKSPACE} --exit-zero'
}
return this