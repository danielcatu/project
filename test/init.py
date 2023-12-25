import pandas as pd
import prometheus as ptheus
import resource_manage as resource_manage
import bayes_op as bayes_op
import threading
import time

# Blackscholes
# Canneal
# Ferret
# Fluidanimate
# Freqmine
# Swaptions
# Streamcluster

# Base config
benchmark = "blackscholes"
base_url = "http://blackscholes.blackscholes.127.0.0.1.sslip.io"
url = f'{base_url}/?command=./run%20-k%20-a%20run%20-p%20parsec.{benchmark}%20-i%20native'
start_time = 0
end_time = 24 * 60 + 25
filename = './dataset/dataset.csv'
target_day = 1
minute_duration = 60
generation = 1
time_into_future_prediction = 10
percentage_error=1.2
# Test Config
# start_time = 20
# generation = 1
# end_time = 70


def save_data_and_optimize(results_df, gen):
    file_name = f'{benchmark}_{target_day}_{gen}'
    file_path = f'./result/{file_name}.csv'

    results_df.to_csv(file_path, index=False)

    next_cpu_usage, next_memory_usage = bayes_op.optimize(
        file_name, time_into_future_prediction)

    limit_cpu = str(next_cpu_usage.max()*percentage_error * 1000) + 'm'
    limit_memory = str(next_memory_usage.max()*percentage_error / (1024 * 1024)) + 'Mi'
    request_cpu = str(next_cpu_usage.mean()*percentage_error * 1000) + 'm'
    request_memory = str(next_memory_usage.mean()*percentage_error / (1024 * 1024)) + 'Mi'

    print(f'limit_cpu: {limit_cpu}, limit_memory: {limit_memory}')
    print(f'request_cpu: {request_cpu}, request_memory: {request_memory}')

    resource_manage.load_and_save_yaml(
        "function",
        limit_cpu,
        limit_memory,
        request_cpu,
        request_memory,
    )
    resource_manage.apply_yaml("function")


def process_minute_data(data, current_minute, result_array, data_lock):
    num_invocations = data["NumInvocations"].item()
    print(f'Current Minute: {current_minute}, NumInvocations: {num_invocations}')
    results = ptheus.make_random_invocations(
        url,
        num_invocations,
        minute_duration,
        current_minute
    )
    print('\n')
    with data_lock:
        if len(results) > 0:
            new_df = pd.DataFrame(results,
                                  columns=[
                                      "num_invocation",
                                      "current_num_invocation",
                                      "wait_time",
                                      "elapsed_time",
                                      "real_time",
                                      "user_time",
                                      "cpu_usage",
                                      "memory_usage",
                                      "timestamp"
                                  ])
            new_df['current_minute'] = int(current_minute)
            if len(result_array) == 1:
                result_array.append(new_df)
            else:
                result_array[1] = pd.concat(
                    [result_array[1], new_df], ignore_index=True)


if __name__ == "__main__":
    dataset = pd.read_csv(filename)
    data_lock = threading.Lock()
    threads = []
    results_df = pd.DataFrame([], columns=[
                              "current_minute",
                              "num_invocation",
                              "current_num_invocation",
                              "wait_time",
                              "elapsed_time",
                              "response",
                              "real_time",
                              "user_time",
                              "cpu_usage",
                              "memory_usage"
                              ])
    result_array = [generation]

    filtered_data = dataset[dataset["Day"] == target_day]

    if filtered_data.empty:
        print("No se encontraron datos para la función y día especificados.")
    else:
        for current_minute in range(start_time, end_time):
            print('----------------------------------')
            print('----------------------------------')
            print(f'Current Minute: {current_minute}')
            data = filtered_data[filtered_data["Minute"] == current_minute]

            if data.empty != True:
                thread = threading.Thread(
                    target=process_minute_data,
                    args=(data, current_minute, result_array, data_lock)
                )

                threads.append(thread)
                thread.start()

            if current_minute >= time_into_future_prediction * result_array[0]:
                print('----------------------------------')
                print('----------------------------------')
                print(f'Change generation time: {current_minute}')
                for thread in threads:
                    thread.join()
                
                save_data_and_optimize(
                    result_array[1], result_array[0])
                # result_array[1] = results_df
                result_array[0] += 1
                time.sleep(60*3)
                print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                print(f'Start New generation')
                threads = []
            if end_time-start_time > 1:
                time.sleep(minute_duration)
