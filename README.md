# pydra

While playing around with thc-hydra I found out it does not work on website that use CSRF tokens or any other modern protection.

This tool does the same thing user/password brute-force but using the browser thanks to `playwright` library.

## installation

```
python3 venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

## usage

```
python3 pydra.py --login-form-url http://10.129.136.248:8080/login --user-list /usr/share/workdlists/top-usernames-shortlist.txt --passwd-list /usr/share/workdlists/default-passwords.txt --user-selector "#j_username" --passwd-selector "div.formRow:nth-child(2) > input:nth-child(1)" --button-selector ".submit-button" --incorrect-selector ".alert" 
```