def safe_sh(String command) {
    try {
        sh command
    } catch (Exception e) {
        echo "Command failed: ${command}"
        error "Stopping pipeline due to failure."
    }
}

def build_app() {
    safe_sh 'pipenv sync'
}

def run_test(String path, String key = '', String additional_args = '') {
    safe_sh "pipenv run pytest '${path}' --private_token='${key}' ${additional_args}"
}

def test_amd_desktop(String path) {
    run_test(path, '', '--testmon --cov-report=html')
}

def test_raspberry(String path) {
    run_test(path, '', '--cov-report=html')
}

def test_amd64_nvme(String path) {
    run_test(path + '/test_amd64_nvme.py', '', '--cov-report=html')
}

def test_amd64_perf(String path) {
    run_test(path + '/test_amd64_perf.py', '', '--cov-report=html')
}

def test_amd64_stress(String path) {
    run_test(path + '/test_amd64_stress.py', '', '--cov-report=html')
}

def test_application_interface(String path) {
    run_test(path + '/test_application_interface.py', '')
}

def test_pep8(String path) {
    safe_sh "pipenv run pylint '${path}' --fail-under=7.0"
}

def test_smoke(String path, int rep_number, String key, String scope) {
    run_test(path + '/test_amd64_warmboot.py', key, "--count=${rep_number} --repeat-scope=${scope} --cov=${path} --json-report")
}

def test_sanity(String path) {
    run_test(path, '', "-m 'not PERFORMANCE and not STRESS' --testmon --cov=${path} --json-report")
}

def test_regression(String path) {
    run_test(path, '', "-m 'not STRESS and not TRAINING' --cov=${path} --json-report")
}

def test_unit(String path, String key) {
    run_test(path, key, "--cov=${path} --json-report")
}

def test_training(String path) {
    run_test(path, '', "-m 'TRAINING' --cov=${path} --json-report")
}
return this
