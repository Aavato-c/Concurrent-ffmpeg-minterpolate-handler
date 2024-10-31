import multiprocessing

available_processors = multiprocessing.cpu_count()
print(f"Available processors: {available_processors}")