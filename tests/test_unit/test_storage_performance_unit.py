# Content of tests/test_unit/test_storage_performance_unit.py
'''Copyright (c) 2025 Jaron Cheng'''
import pytest
from storage.performance import WindowsPerf


class MockPlatform:
    """Mock implementation of a platform object.

    Attributes:
        cpu_num (int): Number of CPUs in the platform.
        memory_size (int): Size of the memory in GB.
        api (MockAPI): Mock API object for simulating command execution.
    """
    def __init__(self, cpu_num=24, memory_size=16):
        self.cpu = MockAPI()
        self.cpu_num = cpu_num
        self._logic_processors = cpu_num
        self.cpu.cores = cpu_num
        self.memory_size = memory_size
        self.api = MockAPI()


class MockAPI:
    """Mock implementation of an API for executing commands."""
    def io_command(self, command):
        return r"""
        WARNING: Error adjusting token privileges for SeManageVolumePrivilege
        (error code: 1300)
        WARNING: Could not set privileges for setting valid file size; will
        use a slower method of preparing the file

        Command Line:diskspd -c12 -t1 -o7 -b4k -r4k -Sh -D -L -w0 -d30 -c1G M:\IO.dat

        Input parameters:

                timespan:   1
                -------------
                duration: 30s
                warm up time: 5s
                cool down time: 0s
                measuring latency
                gathering IOPS at intervals of 1000ms
                random seed: 0
                path: 'M:\IO.dat'
                        think time: 0ms
                        burst size: 0
                        software cache disabled
                        hardware write cache disabled, writethrough on
                        performing read test
                        block size: 4KiB
                        using random I/O (alignment: 4KiB)
                        number of outstanding I/O operations per thread: 7
                        threads per file: 1
                        using I/O Completion Ports
                        IO priority: normal

        System information:

                computer name: MY-TESTBED-01
                start time: 2024/12/20 03:37:25 UTC

                cpu count:              24
                core count:             12
                group count:            1
                node count:             1
                socket count:           1
                heterogeneous cores:    n

                active power scheme:    High performance (8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c)

        Results for timespan 1:
        *******************************************************************************

        actual test time:       30.02s
        thread count:           1

        Core | CPU |  Usage |  User  | Kernel |  Idle
        -----------------------------------------------
            0|    0|  15.04%|   1.35%|  13.69%|  84.96%
            0|    1|   2.65%|   0.00%|   2.65%|  97.35%
            1|    2|   0.05%|   0.05%|   0.00%|  99.95%
            1|    3|   0.10%|   0.05%|   0.05%|  99.90%
            2|    4|   0.05%|   0.00%|   0.05%|  99.95%
            2|    5|   0.16%|   0.00%|   0.16%|  99.84%
            3|    6|   0.00%|   0.00%|   0.00%| 100.00%
            3|    7|   0.00%|   0.00%|   0.00%| 100.00%
            4|    8|   0.10%|   0.00%|   0.10%|  99.90%
            4|    9|   0.00%|   0.00%|   0.00%| 100.00%
            5|   10|   0.00%|   0.00%|   0.00%| 100.00%
            5|   11|   0.00%|   0.00%|   0.00%| 100.00%
            6|   12|   0.05%|   0.00%|   0.05%|  99.95%
            6|   13|   0.05%|   0.00%|   0.05%|  99.95%
            7|   14|   0.10%|   0.05%|   0.05%|  99.90%
            7|   15|   0.00%|   0.00%|   0.00%| 100.00%
            8|   16|   0.42%|   0.00%|   0.42%|  99.58%
            8|   17|   0.47%|   0.05%|   0.42%|  99.53%
            9|   18|   0.05%|   0.00%|   0.05%|  99.95%
            9|   19|   0.00%|   0.00%|   0.00%| 100.00%
           10|   20|   0.10%|   0.00%|   0.10%|  99.90%
           10|   21|   0.16%|   0.00%|   0.16%|  99.84%
           11|   22|   0.00%|   0.00%|   0.00%| 100.00%
           11|   23|   0.10%|   0.00%|   0.10%|  99.90%
        -----------------------------------------------
               avg.|   0.82%|   0.07%|   0.75%|  99.18%

Total IO
thread |       bytes     |     I/Os     |    MiB/s   |  I/O per s |  AvgLat  | IopsStdDev | LatStdDev |  file
------------------------------------------------------------------------------------------------------------------
     0 |      8963465216 |      2188346 |     284.80 |   72908.34 |    0.094 |   35727.09 |     0.311 | M:\IO.dat (1GiB)
------------------------------------------------------------------------------------------------------------------
total:        8963465216 |      2188346 |     284.80 |   72908.34 |    0.094 |   35727.09 |     0.311

Read IO
thread |       bytes     |     I/Os     |    MiB/s   |  I/O per s |  AvgLat  | IopsStdDev | LatStdDev |  file
------------------------------------------------------------------------------------------------------------------
     0 |      8963465216 |      2188346 |     284.80 |   72908.34 |    0.094 |   35727.09 |     0.311 | M:\IO.dat (1GiB)
------------------------------------------------------------------------------------------------------------------
total:        8963465216 |      2188346 |     284.80 |   72908.34 |    0.094 |   35727.09 |     0.311

Write IO
thread |       bytes     |     I/Os     |    MiB/s   |  I/O per s |  AvgLat  | IopsStdDev | LatStdDev |  file
------------------------------------------------------------------------------------------------------------------
     0 |               0 |            0 |       0.00 |       0.00 |    0.000 |       0.00 |       N/A | M:\IO.dat (1GiB)
------------------------------------------------------------------------------------------------------------------
total:                 0 |            0 |       0.00 |       0.00 |    0.000 |       0.00 |       N/A

Total latency distribution:
  %-ile |  Read (ms) | Write (ms) | Total (ms)
----------------------------------------------
    min |      0.053 |        N/A |      0.053
   25th |      0.058 |        N/A |      0.058
   50th |      0.067 |        N/A |      0.067
   75th |      0.079 |        N/A |      0.079
   90th |      0.115 |        N/A |      0.115
   95th |      0.481 |        N/A |      0.481
   99th |      0.502 |        N/A |      0.502
3-nines |      0.512 |        N/A |      0.512
4-nines |      0.556 |        N/A |      0.556
5-nines |     12.622 |        N/A |     12.622
6-nines |    161.167 |        N/A |    161.167
7-nines |    161.193 |        N/A |    161.193
8-nines |    161.193 |        N/A |    161.193
9-nines |    161.193 |        N/A |    161.193
    max |    161.193 |        N/A |    161.193
        """


@pytest.fixture
def platform():
    """Fixture for creating a mock platform object."""
    return MockPlatform()


@pytest.fixture
def amd64_perf(platform):
    """Fixture for creating an AMD64Perf object with the mock platform."""
    return WindowsPerf(platform, "/mock/path/to/io.dat")


def test_run_io_operation(amd64_perf):
    """Test the run_io_operation method of the AMD64Perf class.

    This test validates the extracted read/write metrics and CPU usage from
    the simulated DiskSpd output.

    Args:
        amd64_perf (AMD64Perf): AMD64Perf object initialized with mock data.

    Assertions:
        - Validates that the read/write bandwidth and IOPS are correctly
        parsed.
        - Validates that the CPU usage dictionary contains accurate data.
    """
    read_bw, read_iops, write_bw, write_iops, _ = amd64_perf.run_io_operation(
        iodepth=8,
        block_size="4k",
        random_size=None,
        write_pattern="50",
        duration=30
    )

    # Check the extracted read/write metrics
    assert read_bw == 284.80
    assert read_iops == 72908.34
    assert write_bw == 0.0
    assert write_iops == 0.0
