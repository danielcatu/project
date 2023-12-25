import requests
import random
import time
import threading
from datetime import datetime
import re
import request_prometheus as req


def make_invocation(url, minute_duration, num_invocation, total_num_invocation,current_minute, data_list, data_lock):
    wait_time = random.uniform(0, minute_duration)
    time.sleep(wait_time)
    headers = {"Content-Type": "application/json"}

    start_time = time.time()
    avg_cpu_usage = []
    timestamp = []
    stop_event = threading.Event()
    avg_cpu_thread = threading.Thread(
        target=get_cpu_usage, args=(avg_cpu_usage, timestamp, stop_event))
    avg_cpu_thread.start()

    memory_usage = []
    memory_thread = threading.Thread(
        target=get_memory_usage, args=(memory_usage, stop_event))
    memory_thread.start()

    response = requests.get(url, headers=headers, timeout=60*30)

    end_time = time.time()

    stop_event.set()

    elapsed_time = end_time - start_time

    print(f"Delay: {str(elapsed_time)}, Current invocation {num_invocation+1}/{total_num_invocation}, Current Minute: {current_minute} \n ResponseBase: {str(response)}")
    print(f"Delay: {str(elapsed_time)}, Current invocation {num_invocation+1}/{total_num_invocation}, Current Minute: {current_minute} \n Response: {str(response.text)}")

    tiempo_real_segundos, tiempo_user_segundos = get_data_from_result(
        response.text)

    with data_lock:
        avg_cpu_usage = [float(cpu) for cpu in avg_cpu_usage]
        memory_usage = [float(me) for me in memory_usage]
        for i in range(min(len(memory_usage), len(avg_cpu_usage))):
            data_list.append([
                num_invocation + 1,
                total_num_invocation,
                wait_time,
                elapsed_time,
                tiempo_real_segundos,
                tiempo_user_segundos,
                avg_cpu_usage[i],
                memory_usage[i],
                timestamp[i]
            ])


def make_random_invocations(url, num_invocations, minute_duration, current_minute):
    threads = []
    data = []
    data_lock = threading.Lock()

    for i in range(num_invocations):
        thread = threading.Thread(
            target=make_invocation,
            args=(url, minute_duration, i, num_invocations,current_minute, data, data_lock)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    return data


def get_cpu_usage(avg_cpu_usage, timestamp, stop_event):
    while not stop_event.is_set():
        try:
            query = 'sum(node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate{cluster="", namespace="blackscholes"})'
            result = req.execute_query(query)

            if result and len(result) > 0:
                dateTime = datetime.fromtimestamp(result[0]['value'][0])
                timestamp.append(dateTime.hour * 60 + dateTime.minute)
                avg_cpu_usage.append(float(result[0]['value'][1]))

            time.sleep(5)
        except Exception as e:
            print(f"Error getting CPU usage: {str(e)}")
            break


def get_memory_usage(memory_usage, stop_event):
    while not stop_event.is_set():
        try:
            query = 'sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", namespace="blackscholes"})'
            result = req.execute_query(query)

            if result and len(result) > 0:
                memory_usage.append(float(result[0]['value'][1]))

            time.sleep(5)
        except Exception as e:
            print(f"Error getting memory usage: {str(e)}")
            break


def get_data_from_result(result):
    patron_real = re.compile(r'real\s+(\d+m[\d.]+s)')
    patron_user = re.compile(r'user\s+(\d+m[\d.]+s)')

    coincidencia_real = patron_real.search(result)
    coincidencia_user = patron_user.search(result)

    if coincidencia_real and coincidencia_user:
        tiempo_real = coincidencia_real.group(1)
        tiempo_user = coincidencia_user.group(1)

        tiempo_real_segundos = sum(
            float(x) * 60 ** i for i, x in enumerate(reversed(tiempo_real[:-1].split('m'))))
        tiempo_user_segundos = sum(
            float(x) * 60 ** i for i, x in enumerate(reversed(tiempo_user[:-1].split('m'))))

        print(f'Tiempo real: {tiempo_real_segundos} segundos')
        print(f'Tiempo user: {tiempo_user_segundos} segundos')
        return tiempo_real_segundos, tiempo_user_segundos
    else:
        print('No se encontraron coincidencias.')