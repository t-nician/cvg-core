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

def start_non_crypto_tests():
    print("starting non crypto tests...")
    
    sleep(1)


def start_crypto_tests():
    print("starting crypto tests...")
    
    sleep(1)


def start_tests():
    print("starting tests...")
    
    
    start_non_crypto_tests()
    start_crypto_tests()
    
    