import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Decorator to add multithreading
def multithreaded(max_workers=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_args = {executor.submit(func, arg): arg for arg in args[0]}
                results = []
                for future in as_completed(future_to_args):
                    arg = future_to_args[future]
                    try:
                        result = future.result()
                    except Exception as exc:
                        print(f'{arg} generated an exception: {exc}')
                    else:
                        results.append(result)
                return results
        return wrapper
    return decorator

if __name__ == '__main__':
    # Function to square a number
    @multithreaded(max_workers=5)
    def square_number(number):
        time.sleep(1)  # Simulate a time-consuming task
        return number * number


    # List of numbers to process
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Using the decorated function
    start_time = time.time()
    squared_numbers = square_number(numbers)
    end_time = time.time()

    print("Squared numbers:", squared_numbers)
    print("Time taken:", end_time - start_time, "seconds")