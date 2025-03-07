import random
import time

import pytest

from src.libs.common import to_app_id, to_index, delay
from src.steps.da import StepsDataAvailability, logger
from src.test_data import DATA_TO_DISPERSE


class TestHighLoadDos(StepsDataAvailability):
    main_nodes = []
    client_nodes = []

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_sustained_high_rate_upload(self):
        timeout = 60
        start_time = time.time()
        successful_dispersals = 0
        unsuccessful_dispersals = 0

        while True:
            if time.time() - start_time > timeout:
                break

            delay(0.01)
            try:
                response = self.disperse_data(DATA_TO_DISPERSE[7], to_app_id(1), to_index(0), timeout_duration=0)
                if response.status_code == 200:
                    successful_dispersals += 1
                else:
                    unsuccessful_dispersals += 1
            except Exception:
                unsuccessful_dispersals += 1

        assert successful_dispersals > 0, "No successful dispersals"

        failure_ratio = unsuccessful_dispersals / successful_dispersals
        logger.info(f"Unsuccessful dispersals ratio: {failure_ratio}")

        assert failure_ratio < 0.20, f"Dispersal failure ratio {failure_ratio} too high"

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_sustained_high_rate_download(self):
        timeout = 60
        successful_downloads = 0
        unsuccessful_downloads = 0

        try:
            self.disperse_data(DATA_TO_DISPERSE[7], to_app_id(1), to_index(0))
        except Exception as ex:
            raise Exception(f"Initial dispersal was not successful with error {ex}")

        delay(5)
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                break

            delay(0.01)
            try:
                self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5), timeout_duration=0)
                successful_downloads += 1
            except Exception:
                unsuccessful_downloads += 1

        assert successful_downloads > 0, "No successful data downloads"

        failure_ratio = unsuccessful_downloads / successful_downloads
        logger.info(f"Unsuccessful download ratio: {failure_ratio}")

        assert failure_ratio < 0.20, f"Data download failure ratio {failure_ratio} too high"

    @pytest.mark.usefixtures("setup_2_node_cluster")
    def test_sustained_high_rate_mixed(self):
        timeout = 60
        start_time = time.time()
        successful_dispersals = 0
        unsuccessful_dispersals = 0
        successful_downloads = 0
        unsuccessful_downloads = 0

        while True:
            if time.time() - start_time > timeout:
                break

            delay(0.01)
            try:
                response = self.disperse_data(DATA_TO_DISPERSE[6], to_app_id(1), to_index(0), timeout_duration=0)
                if response.status_code == 200:
                    successful_dispersals += 1
                else:
                    unsuccessful_dispersals += 1
            except Exception:
                unsuccessful_dispersals += 1

            try:
                self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5), timeout_duration=0)
                successful_downloads += 1
            except Exception:
                unsuccessful_downloads += 1

        assert successful_dispersals > 0, "No successful dispersals"
        assert successful_downloads > 0, "No successful downloads"

        failure_ratio_w = unsuccessful_dispersals / successful_dispersals
        failure_ratio_r = unsuccessful_downloads / successful_downloads

        logger.info(f"Unsuccessful dispersals ratio: {failure_ratio_w}")
        logger.info(f"Unsuccessful download ratio: {failure_ratio_r}")

        assert failure_ratio_w < 0.20, f"Dispersal failure ratio {failure_ratio_w} too high"
        assert failure_ratio_r < 0.20, f"Data download failure ratio {failure_ratio_r} too high"

    @pytest.mark.usefixtures("setup_2_node_cluster", "setup_client_nodes")
    def test_sustained_high_rate_multiple_clients(self):
        timeout = 10
        start_time = time.time()
        successful_dispersals = 0
        unsuccessful_dispersals = 0
        successful_downloads = 0
        unsuccessful_downloads = 0

        while True:
            if time.time() - start_time > timeout:
                break

            dispersal_cl, download_cl = random.choice(self.client_nodes), random.choice(self.client_nodes)

            delay(0.01)
            try:
                response = self.disperse_data(DATA_TO_DISPERSE[6], to_app_id(1), to_index(0), client_node=dispersal_cl, timeout_duration=0)
                if response.status_code == 200:
                    successful_dispersals += 1
                else:
                    unsuccessful_dispersals += 1
            except Exception:
                unsuccessful_dispersals += 1

            try:
                self.get_data_range(self.node2, to_app_id(1), to_index(0), to_index(5), client_node=download_cl, timeout_duration=0)
                successful_downloads += 1
            except Exception:
                unsuccessful_downloads += 1

        assert successful_dispersals > 0, "No successful dispersals"
        assert successful_downloads > 0, "No successful downloads"

        failure_ratio_w = unsuccessful_dispersals / successful_dispersals
        failure_ratio_r = unsuccessful_downloads / successful_downloads

        logger.info(f"Unsuccessful dispersals ratio: {failure_ratio_w}")
        logger.info(f"Unsuccessful download ratio: {failure_ratio_r}")

        assert failure_ratio_w < 0.20, f"Dispersal failure ratio {failure_ratio_w} too high"
        assert failure_ratio_r < 0.20, f"Data download failure ratio {failure_ratio_r} too high"

    @pytest.mark.usefixtures("setup_2_node_cluster", "setup_client_nodes")
    def test_sustained_high_rate_with_invalid_requests(self):
        timeout = 10
        start_time = time.time()
        successful_dispersals = 0
        unsuccessful_dispersals = 0
        successful_downloads = 0
        unsuccessful_downloads = 0

        while True:
            if time.time() - start_time > timeout:
                break

            dispersal_cl, download_cl = random.choice(self.client_nodes), random.choice(self.client_nodes)

            delay(0.01)
            invalid = random.choice([True, False])

            try:
                response = self.disperse_data(
                    DATA_TO_DISPERSE[6], to_app_id(1), to_index(0), client_node=dispersal_cl, timeout_duration=0, send_invalid=invalid
                )
                if response.status_code == 200:
                    successful_dispersals += 1
                elif not invalid:
                    unsuccessful_dispersals += 1
            except Exception:
                if not invalid:
                    unsuccessful_dispersals += 1

            try:
                invalid = random.choice([True, False])
                self.get_data_range(
                    self.node2, to_app_id(1), to_index(0), to_index(5), client_node=download_cl, timeout_duration=0, send_invalid=invalid
                )
                successful_downloads += 1
            except Exception:
                if not invalid:
                    unsuccessful_downloads += 1

        assert successful_dispersals > 0, "No successful dispersals"
        assert successful_downloads > 0, "No successful downloads"

        failure_ratio_w = unsuccessful_dispersals / successful_dispersals
        failure_ratio_r = unsuccessful_downloads / successful_downloads

        logger.info(f"Unsuccessful dispersals ratio: {failure_ratio_w}")
        logger.info(f"Unsuccessful download ratio: {failure_ratio_r}")

        assert failure_ratio_w < 0.20, f"Dispersal failure ratio {failure_ratio_w} too high"
        assert failure_ratio_r < 0.20, f"Data download failure ratio {failure_ratio_r} too high"
