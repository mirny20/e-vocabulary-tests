# E-Vocabulary UI Tests

This project contains automated UI tests for the [E-Vocabulary](https://e-vocabulary.vercel.app) web application.
The tests are written in Python using the Playwright framework and are run with Pytest.

## 1. Prerequisites

Before you begin, ensure you have Python 3.11+ installed.

You also need an active account in the E-Vocabulary application.
*   You can register a new account here: [https://e-vocabulary.vercel.app/](https://e-vocabulary.vercel.app/)
⚠️ After registering your account, you must update the "My known language:" setting to "ua", because the test project is configured to work with the "ua-en" language pair.

You can change this setting on the "My account" page: https://e-vocabulary.vercel.app/#/user

To open this page, either:

* navigate directly using the link above, or

* click on your profile photo to open the user menu and select "My account".

## 2. Setup and Configuration

1.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Install Playwright browsers:**
    This command will download the necessary browser binaries for Playwright.
    ```bash
    playwright install --with-deps
    ```

3.  **Create an environment file:**
    Create a file named `.env` in the root (`e-vocabulary-tests`) directory. This file will store your credentials for running tests locally.

    Populate the `.env` file with the following content, replacing the placeholder values with your actual account details:
    ```.env
    USERNAME_MAIN_USER="your-username"
    PASSWORD_MAIN_USER="your-password"
    EMAIL_MAIN_USER="your-email@example.com"
    ```

## 3. Running Tests

*   **Run all tests:**
    ```bash
    pytest
    ```

*   **Run a specific suite (using markers):**
    You can run tests marked as `smoke` or `regression`.
    ```bash
    pytest -m smoke
    pytest -m regression
    ```

*   **Run tests in parallel:**
    To speed up execution, you can run tests in parallel. The `-n` flag specifies the number of workers (or `auto` for automatic detection).
    ```bash
    pytest -n auto
    ```

## 4. Test Reports

This project uses [Allure](https://allurereport.org/) for test reporting. Test runs automatically generate data in the `allure-results` directory.

1.  **Generate the report:**
    After the tests have finished, you can generate and review report with the following command:
    ```bash
    allure serve allure-results
    ```


