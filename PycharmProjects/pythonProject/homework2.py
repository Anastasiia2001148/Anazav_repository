import time
from multiprocessing import cpu_count,Pool

def one_number(number):
    list_num = []
    for i in range(1,int(number**0.5)+1):
        if number % i == 0:
            list_num.append(i)
            if number !=number//i:
                list_num.append(number//i)
    return sorted(list_num)
def factorize(*numbers):
    return [one_number(number) for number in numbers]

def parallel(*numbers):
    with Pool (cpu_count()) as pool:
        result = pool.map(one_number,numbers)
    return result


if __name__ == "__main__":
    start_s = time.time()
    a, b, c, d = factorize(128, 255, 99999, 10651060)
    end = time.time()
    print(f'Sinhron version: {end-start_s} sec')
    print(a)
    print(b)
    print(c)
    print(d)
    start_p = time.time()
    a, b, c, d = parallel(128, 255, 99999, 10651060)
    end_p = time.time()
    print(f'Parallel version: {end_p-start_p} sec')
    print(a)
    print(b)
    print(c)
    print(d)

