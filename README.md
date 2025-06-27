# nomos-e2e-tests

Nomos E2E framework used to test various implementations of the Nomos node.

## Setup and contribute

```shell
git clone git@github.com:logos-co/nomos-e2e-tests.git
cd nomos-e2e-tests
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p kzgrs
wget https://raw.githubusercontent.com/logos-co/nomos-node/master/tests/kzgrs/kzgrs_test_params -O kzgrs/kzgrs_test_params
pre-commit install
(optional) Overwrite default vars from src/env_vars.py via env vars or by adding a .env file
(optional) python download_nltk_resources.py # Used when CHECK_LOG_ERRORS=True
pytest
```

### Additional instructions for dispersal resilience tests  

1. Build prerequisites
```sh
git clone https://github.com/logos-co/nomos-security-tests.git
cd nomos-security-tests
git fetch; git switch test-dispersal-resilience

git checkout d8bbc464420ef86337df963c64ac2f7c3fd97008
docker build --no-cache -f testnet/Dockerfile.debug -t nomos-mod-da-d8bbc46:testnet .
# (x86_64) docker build --no-cache -f testnet/Dockerfile -t nomos-mod-da-d8bbc46:testnet .

git checkout d19a1f3d8c80f654e6cf6139641519f16fe670ec
docker build --no-cache -f testnet/Dockerfile.debug -t nomos-executor-mod-da-d19a1f3:testnet . 

git checkout 7f54114b6c320dc32577b0e8bb85c2d543b4bd56
docker build --no-cache -f testnet/Dockerfile.debug -t nomos-executor-mod-da-7f54114:testnet . 

git checkout 4a58376ac4956d87502b9fd72b64a756396f2a8d
docker build --no-cache -f testnet/Dockerfile.debug -t nomos-executor-mod-da-4a58376:testnet . 
```

2. Run tests with `pytest --run-with-mod-da-node tests/dispersal_resilience/test_dispersal_resilience.py`

### Enable node log search with environment variable:
```shell
export CHECK_LOG_ERRORS=True
```

## License

Licensed and distributed under either of

- MIT license: [LICENSE-MIT](http://opensource.org/licenses/MIT)

or

- Apache License, Version 2.0, [LICENSE-APACHE-v2](http://www.apache.org/licenses/LICENSE-2.0)

at your option. These files may not be copied, modified, or distributed except according to those terms.
