import pytest

from src.steps.da import StepsDataAvailability
from src.test_data import DATA_TO_DISPERSE


@pytest.mark.usefixtures("setup_main_nodes")
class TestDataIntegrity(StepsDataAvailability):
    main_nodes = []

    def test_da_identify_retrieve_missing_columns(self):
        for node in self.main_nodes:
            print(node)

    def test_da_sampling_determines_data_presence(self):
        self.disperse_data(DATA_TO_DISPERSE[0])

        # Get data from range
        # Compare
