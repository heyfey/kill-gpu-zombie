# kill-gpu-zombie

Detect and kill zombie process that occupies Nvidia GPU.

`detect_and_kill.py` views processes that continuously consume GPU memory, but have zero GPU utilization, as "zombie process", which may be hanging or in deadlock, and kill them after a timeout period.

Please be aware that in order to kill a process, the script needs `sudo` when running directly, or needs `--privileged` and `--pid=host` when running with docker. 

## Quick Start

```
git clone https://github.com/heyfey/kill-gpu-zombie.git
cd kill-gpu-zombie
sudo python detect_and_kill.py --check-period-second 2.5 --memory-threshold-MiB 20 --kill-threshold-second 90
```
args:

`--check-period-second`: check for zombie process every # seconds

`--memory-threshold-MiB`: view GPU as occupied when memory used exceed # MiB

`--kill-threshold-second`: kill process has been a zombie for # seconds

prerequisites: `pandas`

## Run with docker

### Build Image

```
docker build .
```

### Docker Run

```
docker run -it --privileged --pid=host heyfey/kill-gpu-zombie
```

## Deploy as daemonset in kubernetes cluster

```
kubectl apply -f kill-gpu-zombie.yaml
```
