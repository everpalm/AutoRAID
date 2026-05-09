# AutoRAID

AutoRAID is an enterprise-grade automated validation framework for RAID controllers and storage systems.

The project was designed to reduce manual validation effort for firmware regression, stress testing, and RAID configuration verification across multiple servers.

---

# Problem Statement

Storage validation in enterprise environments typically requires:

- repetitive RAID configuration testing
- long-duration stress validation
- remote machine orchestration
- firmware regression verification
- power-cycle recovery testing
- cross-platform compatibility checks

Manual execution is slow, error-prone, and difficult to scale.

AutoRAID addresses these problems by providing a scalable automation framework built around Pytest, SSH orchestration, and CI integration.

---

# Architecture

```text
Developer / QA Engineer
        ↓
     Jenkins CI
        ↓
Pytest Automation Framework
        ↓
 SSH Remote Execution Layer
        ↓
 RAID / NVMe Test Targets
        ↓
 Result Collection & Reporting
```

---

# Key Features

## RAID Validation

- RAID creation and deletion
- RAID level verification
- disk failure and rebuild testing
- consistency verification

## Automation Framework

- Pytest-based test execution
- reusable test architecture
- parameterized validation flows
- automated regression execution

## Infrastructure Integration

- Jenkins CI/CD integration
- remote execution through SSH
- multi-node validation support
- automated log collection

## Reliability Testing

- long-duration stress testing
- reboot and recovery validation
- repeated execution stability testing

---

# Design Decisions

| Design | Reason |
|---|---|
| Pytest framework | scalable and modular test structure |
| SSH orchestration | centralized remote control |
| CLI-driven validation | suitable for headless server environments |
| Jenkins integration | continuous regression execution |
| modular test layers | easier maintenance and extension |

---

# Technology Stack

- Python
- Pytest
- Jenkins
- SSH
- RAID Controller CLI
- Linux / Windows validation

---

# Installation

```bash
git clone https://github.com/everpalm/AutoRAID.git
cd AutoRAID
pip install -r requirements.txt
```

---

# Running Tests

```bash
pytest
```

---

# Future Improvements

- Kubernetes-based distributed execution
- dynamic hardware resource scheduling
- web dashboard for test visualization
- automated firmware deployment pipeline
- centralized result analytics

---

# Project Value

This project demonstrates:

- enterprise storage validation
- infrastructure automation
- CI/CD integration
- distributed test orchestration
- reliability engineering
- scalable QA architecture

---

# Contact

- GitHub: https://github.com/everpalm
- LinkedIn: https://www.linkedin.com/in/jaroncheng/
