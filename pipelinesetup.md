### Setup a new workflow .yml file in your repository to run the pipeline for mutation testing for new commits

<!-- add the below script as a .yml file-->

    ```yml
    name: Python Mutation Testing Pipeline

    on:
        push:
            # This will trigger the workflow for push events to any branch

        pull_request:
            types:
                - opened
                - synchronize

    jobs:
        test:
            runs-on: ubuntu-latest
            
            steps:
            - uses: actions/checkout@v2
                with:
                    fetch-depth: 0 # Fetch all history for all tags and branches

            - name: Set up Python >= 3.8
            uses: actions/setup-python@v2
            with:
                python-version: '3.9' # Use the version of Python required by the project

            - name: Install dependencies
            run: |
                python -m pip install --upgrade pip
                pip install pytest pytest-cov

            - name: Clone Mutatest repository
            run: |
                git clone https://github.com/meghansh36/mutatest

            - name: Run Mutatest with pytest
            run: |
                cd ./mutatest/mutatest
                python3 cli.py -s ../../fastapi/ -t "pytest --cov=../../fastapi/ --cov-report=term --cov-report=html ../../tests --ignore=../../tests/test_tutorial"
