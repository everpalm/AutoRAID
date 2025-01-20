'''Copyright (c) 2025 Jaron Cheng'''
import pytest
from storage.stress import WindowsStress


class MockPlatform:
    """Mock implementation of a platform object for WindowsStress."""
    def __init__(self):
        self.disk_info = [('C', 1024), ('D', 2048)]
        self.memory_size = 16  # GB
        self.api = MockAPI()


class MockAPI:
    """Mock implementation of an API for executing commands."""
    def io_command(self, command):
        return r"""
        Command Line: diskspd -c12 -t1 -o7 -b4k -r4k -Sh -D -L -w0 -d30 -c1G M:\IO.dat

        Input parameters:
                duration: 30s

        Results for timespan 1:
        *******************************************************************************
        actual test time:       30.02s
        thread count:           1

        Read IO
        ------------------------------------------------------------------------------------------------------------------
            total:        8963465216 |      2188346 |     284.80 |   72908.34 |    0.094 |   35727.09 |     0.311

        Write IO
        ------------------------------------------------------------------------------------------------------------------
            total:                 0 |            0 |       0.00 |       0.00 |    0.000 |       0.00 |       N/A

        Core | CPU |  Usage |  User  | Kernel |  Idle
        -----------------------------------------------
            0|    0|  15.04%|   1.35%|  13.69%|  84.96%
            1|    1|   2.65%|   0.00%|   2.65%|  97.35%
        """


@pytest.fixture
def platform():
    """Fixture to create a mock platform for testing."""
    return MockPlatform()


@pytest.fixture
def windows_stress(platform):
    """Fixture to create a WindowsStress object."""
    return WindowsStress(platform, platform)


def test_run_io_operation(windows_stress):
    """Test the run_io_operation method of WindowsStress."""
    read_bw, read_iops, write_bw, write_iops, cpu_usage = \
        windows_stress.run_io_operation(
            thread=1,
            iodepth=7,
            block_size="4k",
            random_size="4k",
            write_pattern="0",
            duration=30
        )

    # Assert read/write metrics
    assert read_bw == pytest.approx(284.80)
    assert read_iops == pytest.approx(72908.34)
    assert write_bw == pytest.approx(0.0)
    assert write_iops == pytest.approx(0.0)

    # Assert CPU usage metrics
    assert 0 in cpu_usage
    assert cpu_usage[0]["Total"] == pytest.approx(15.04)
    assert cpu_usage[0]["User"] == pytest.approx(1.35)
    assert cpu_usage[0]["Kernel"] == pytest.approx(13.69)
    assert cpu_usage[0]["Idle"] == pytest.approx(84.96)

    assert 1 in cpu_usage
    assert cpu_usage[1]["Total"] == pytest.approx(2.65)
    assert cpu_usage[1]["User"] == pytest.approx(0.0)
    assert cpu_usage[1]["Kernel"] == pytest.approx(2.65)
    assert cpu_usage[1]["Idle"] == pytest.approx(97.35)
