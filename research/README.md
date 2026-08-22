# CFHM Preserved Research

This directory contains the actual historical CFHM execution and its preserved outputs. The reusable package model remains at [`../src/cfhm/model.py`](../src/cfhm/model.py).

| Actual item | Location |
|---|---|
| F1-v2 experiment runner | [`source/run_experiment.py`](source/run_experiment.py) |
| F1-v2 metric runner | [`source/score_metrics.py`](source/score_metrics.py) |
| F1-v2 evidence tree | [`f1_v2/`](f1_v2/) |
| SPEC-002 autopsy runner | [`f1_v2_autopsy/run_autopsy.py`](f1_v2_autopsy/run_autopsy.py) |
| SPEC-002 autopsy evidence | [`f1_v2_autopsy/`](f1_v2_autopsy/) |
| Authored specification chain | [`spec/`](spec/) |

The historical trees are immutable evidence. Any new experiment must use a new output root and a new binding specification. The summaries and manifests do not replace the actual source, data, configurations, logs, and result files in these directories.
