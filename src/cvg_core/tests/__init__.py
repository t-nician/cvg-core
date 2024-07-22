from time import sleep

from cvg_core.tests import tool

from cvg_core.tests import test_send, test_receive, test_send_and_receive, test_stream, test_login, test_establish
from cvg_core.tests import test_crypto_send, test_crypto_receive, test_crypto_send_and_receive, test_crypto_stream, test_crypto_login, test_crypto_establish


NON_CRYPTO_TESTS = [
    test_send, test_receive, test_stream, test_send_and_receive, test_login, 
    test_establish
]

CRYPTO_TESTS = [
    test_crypto_send, test_crypto_receive, test_crypto_send_and_receive, 
    test_crypto_stream, test_crypto_login, test_crypto_establish
]


def __generic_start(
    module, 
    skip_modules_missing_start_tests: bool | None = False
):
    if not skip_modules_missing_start_tests:
        assert hasattr(module, "start_tests"), f"target {module} does not have 'start_tests' function."
    elif not hasattr(module, "start_tests"):
        print(module, "does not have 'start_tests' function! skipping is enabled, fix this later!")
    else:
        module.start_tests()


def start_non_crypto_tests(
    skip_modules_missing_start_tests: bool | None = False
):
    print("starting non crypto tests...")
    
    sleep(1)
    
    for test_module in NON_CRYPTO_TESTS:
        __generic_start(test_module, skip_modules_missing_start_tests)


def start_crypto_tests(skip_modules_missing_start_tests: bool | None = False):
    print("starting crypto tests...")
    
    sleep(1)
    
    for test_module in CRYPTO_TESTS:
        __generic_start(test_module, skip_modules_missing_start_tests)


def start_tests(skip_modules_missing_start_tests: bool | None = False):
    print("starting tests...")
    
    start_non_crypto_tests(skip_modules_missing_start_tests)
    start_crypto_tests(skip_modules_missing_start_tests)
    
    