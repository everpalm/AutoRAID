def build_app() {
    sh 'pipenv sync'
}

def test_amd_desktop() {
    echo 'test_amd_desktop'
    sh 'pipenv run pytest ${TEST_AMD_DESKTOP} --testmon --private_token=$MY_PRIVATE_TOKEN --cov-report=html'
}

def test_raspberry() {
    echo 'test_raspberry'
    sh 'pipenv run pytest --private_token=$MY_PRIVATE_TOKEN --cov-report=html'
}

def test_amd64_nvme() {
    sh 'pipenv run pytest ${TEST_AMD_DESKTOP}/test_amd64_nvme.py --private_token=$MY_PRIVATE_TOKEN --cov-report=html'
}

def test_amd64_perf() {
    sh 'pipenv run pytest ${TEST_AMD_DESKTOP}/test_amd64_perf.py --private_token=$MY_PRIVATE_TOKEN --cov-report=html'
}

def test_amd64_stress() {
    sh 'pipenv run pytest ${TEST_AMD_DESKTOP}/test_amd64_stress.py --private_token=$MY_PRIVATE_TOKEN --cov-report=html'
}
def test_application_interface() {
    sh 'pipenv run pytest ${TEST_AMD_DESKTOP}/test_application_interface.py --private_token=$MY_PRIVATE_TOKEN'
}

def test_pep8() {
    // sh 'pipenv run pylint ${TEST_UNIT} --exit-zero' //Forcibly pass
    sh 'pipenv run pylint ${TEST_UNIT} --fail-under=7.0'
}

def test_smoke() {
    sh 'pipenv run pytest ${TEST_AMD_DESKTOP}/test_amd64_warmboot.py --testmon --private_token=$MY_PRIVATE_TOKEN --cov-report=html --count=3 --repeat-scope=module'    
}

def test_sanity() {
    sh 'pipenv run pytest ${TEST_AMD_DESKTOP} --testmon --cov-report=html'    
}

def test_regression() {
    sh 'pipenv run pytest ${TEST_AMD_DESKTOP} --cov-report=html'    
}

def test_unit() {
    echo 'test_unit'
    sh 'pipenv run pytest ${TEST_UNIT} --private_token=$MY_PRIVATE_TOKEN --cov-report=html'
}
return this