from time import sleep

from cvg_core.tests import test_send, test_receive, test_send_and_receive, test_stream, test_login, test_establish
from cvg_core.tests import test_crypto_send, test_crypto_receive, test_crypto_send_and_receive, test_crypto_stream, test_crypto_login, test_crypto_establish

from cvg_core.tests.shortcut import print_and_save

print = print_and_save

NON_CRYPTO_TESTS = [
    test_send, test_receive, test_stream, test_send_and_receive, test_login, 
    test_establish
]

CRYPTO_TESTS = [
    test_crypto_send, test_crypto_receive, test_crypto_send_and_receive, 
    test_crypto_stream, test_crypto_login, test_crypto_establish
]

SPLIT_LINE = "-" * 60
SHORT_LINE = "-" * 30

def __generic_start(
    module, 
    skip_modules_missing_start_tests: bool | None = False
):
    module_str = str(module).removeprefix("<module '").split("'").pop(0).removesuffix("'")
    
    if not skip_modules_missing_start_tests:
        assert hasattr(module, "start_tests"), f"target {module_str} does not have 'start_tests' function."
    elif not hasattr(module, "start_tests"):
        print(f"[???????] {module_str} missing 'start_tests' skipping... fix this later!")
    else:
        print(
            f"{SPLIT_LINE}\n[TESTING] {module_str}\n{SHORT_LINE}"
        )
        
        result = module.start_tests()
        
        print(
            f"{SHORT_LINE}\n[FINISHED] {module_str}\n[RESULT] {result}\n{SPLIT_LINE}"
        )


def start_non_crypto_tests(
    skip_modules_missing_start_tests: bool | None = False
):
    print("[RUNNING NON-CRYPTO TESTS]")
    
    sleep(1)
    
    for test_module in NON_CRYPTO_TESTS:
        __generic_start(test_module, skip_modules_missing_start_tests)


def start_crypto_tests(skip_modules_missing_start_tests: bool | None = False):
    print("[RUNNING CRYPTO TESTS]")
    
    sleep(1)
    
    for test_module in CRYPTO_TESTS:
        __generic_start(test_module, skip_modules_missing_start_tests)


def start_tests(skip_modules_missing_start_tests: bool | None = False):
    print("[INITIALIZING TESTS]")
    
    start_non_crypto_tests(skip_modules_missing_start_tests)
    
    print(SPLIT_LINE)
    
    start_crypto_tests(skip_modules_missing_start_tests)
    
    print(SPLIT_LINE)
    
    