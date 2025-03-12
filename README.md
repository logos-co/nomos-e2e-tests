# nomos-e2e-tests

Nomos e2e framework used to test various implementations of the Nomos node.

## Setup and contribute

```shell
git clone git@github.com:logos-co/nomos-e2e-tests.git
cd nomos-e2e-tests
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pre-commit install
(optional) Overwrite default vars from src/env_vars.py via env vars or by adding a .env file
pytest
```
Set optional environment variable to search logs for errors after each tests:
```shell
export CHECK_LOG_ERRORS=True
```


## License

Licensed and distributed under either of

- MIT license: [LICENSE-MIT](http://opensource.org/licenses/MIT)

or

- Apache License, Version 2.0, [LICENSE-APACHE-v2](http://www.apache.org/licenses/LICENSE-2.0)

at your option. These files may not be copied, modified, or distributed except according to those terms.
