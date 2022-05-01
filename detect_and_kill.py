import logging as log
from argparse import ArgumentParser
import subprocess
import pandas as pd
from io import StringIO
from typing import List
import time

log.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                level=log.INFO,
                datefmt='%Y-%m-%d %H:%M:%S')

parser = ArgumentParser()
parser.add_argument("--check-period-second",
                    dest="check_period_second",
                    type=float,
                    default=2.5,
                    help="check for zombie process every # seconds")
parser.add_argument("--memory-threshold-MiB",
                    dest="memory_threshold_MiB",
                    type=int,
                    default=20.0,
                    help="view GPU as occupied when memory used exceed # MiB")
parser.add_argument("--kill-threshold-second",
                    dest="kill_threshold_second",
                    type=float,
                    default=90.0,
                    help="kill process has been a zombie for # seconds")
args = parser.parse_args()

log.info('[param] check_period_second : {:f}'.format(args.check_period_second))
log.info('[param] memory_threshold_MiB : {:f}'.format(
    args.memory_threshold_MiB))
log.info('[param] kill_threshold_second : {:f}'.format(
    args.kill_threshold_second))

# dict{ gpu_id: dict{pid: timestamp} }
gpu_process_map = {}


def to_df(gpu_status: bytes) -> pd.core.frame.DataFrame:
    gpu_status = StringIO(gpu_status.decode())
    df = pd.read_csv(gpu_status,
                     sep=',',
                     lineterminator='\n',
                     skipinitialspace=True)
    return df


def gpus_has_zombie_process() -> List[int]:
    try:
        gpu_status = subprocess.check_output([
            'nvidia-smi', '--query-gpu=index,utilization.gpu,memory.used',
            '--format=csv,nounits'
        ])
    except:
        log.info("nvidia-smi failed, no GPU card detected")
        return []

    df = to_df(gpu_status)
    df = df.loc[(df['utilization.gpu [%]'] == 0)
                & (df['memory.used [MiB]'] > args.memory_threshold_MiB)]
    return list(df['index'])


def kill_process(pid: int):
    try:
        subprocess.check_output(['kill', '-9', '{:d}'.format(pid)])
        log.info("Killed process: {:d}".format(pid))
    except:
        log.info("Failed to kill process: {:d}".format(pid))


def check_gpu_process(gpu_id: int, kill_threshold_second: float):
    if gpu_id not in gpu_process_map:
        gpu_process_map[gpu_id] = {}

    try:
        gpu_status = subprocess.check_output([
            'nvidia-smi', '--query-compute-apps=pid,used_memory',
            '--format=csv,nounits', '--id={:d}'.format(gpu_id)
        ])
    except:
        return

    df = to_df(gpu_status)
    for pid in df['pid']:
        now = time.time()
        if pid in gpu_process_map[gpu_id]:
            # kill process that had been zombie for more than kill_threshold_second seconds
            if now - gpu_process_map[gpu_id][pid] > kill_threshold_second:
                kill_process(pid)
        else:
            gpu_process_map[gpu_id][pid] = now


while True:
    gpus_has_zombie_process_list = gpus_has_zombie_process()
    log.info("GPUs might have zombie process: " +
             str(gpus_has_zombie_process_list))

    for gpu_id in gpu_process_map:
        if gpu_id not in gpus_has_zombie_process_list:  # doesn't has zombie process on this GPU
            gpu_process_map[gpu_id] = {}  # clear dict

    for gpu_id in gpus_has_zombie_process_list:
        check_gpu_process(gpu_id, args.kill_threshold_second)

    log.info("[GPUs: Process]: " + str(gpu_process_map))

    time.sleep(args.check_period_second)
