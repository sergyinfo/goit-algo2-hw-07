import random
import time
from collections import OrderedDict

# --- Реалізація LRU-кешу ---
# Використаємо OrderedDict, оскільки він запам'ятовує порядок вставки
# і дозволяє легко переміщати елементи в кінець та видаляти з початку.

class LRUCache:
    """
    Проста реалізація LRU-кешу на базі OrderedDict.
    """
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: tuple) -> int:
        """
        Отримує значення за ключем. Якщо ключ існує,
        переміщує його в кінець як "найновіший" і повертає значення.
        Інакше повертає -1.
        """
        if key not in self.cache:
            return -1
        else:
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: tuple, value: int) -> None:
        """
        Додає або оновлює пару ключ-значення.
        Якщо кеш переповнений, видаляє найстаріший елемент.
        """
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


# --- Функції без кешування ---

def range_sum_no_cache(array: list, left: int, right: int) -> int:
    """Обчислює суму елементів у діапазоні без використання кешу."""
    return sum(array[left: right + 1])


def update_no_cache(array: list, index: int, value: int) -> None:
    """Оновлює елемент у масиві без кешування."""
    array[index] = value


# --- Функції з кешуванням ---

def range_sum_with_cache(array: list, left: int, right: int, cache: LRUCache) -> int:
    """
    Обчислює суму елементів, використовуючи LRU-кеш.
    Якщо значення немає в кеші, обчислює його, додає в кеш і повертає.
    """
    key = (left, right)
    result = cache.get(key)
    if result == -1:  # Cache-miss
        result = sum(array[left: right + 1])
        cache.put(key, result)
    return result


def update_with_cache(array: list, index: int, value: int, cache: LRUCache) -> None:
    """
    Оновлює елемент у масиві та інвалідує всі записи в кеші, що містять цей індекс.
    """
    array[index] = value
    keys_to_invalidate = []
    for l, r in cache.cache.keys():
        if l <= index <= r:
            keys_to_invalidate.append((l, r))

    for key in keys_to_invalidate:
        if key in cache.cache:
            del cache.cache[key]


# --- Функція для генерації запитів ---

def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03) -> list:
    """Генерує список запитів для тестування."""
    hot = [(random.randint(0, n // 2), random.randint(n // 2, n - 1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


# --- Головний блок для тестування ---

if __name__ == "__main__":
    # Параметри симуляції
    N = 100_000
    Q = 50_000
    K_CAPACITY = 1000

    # 1. Генерація початкових даних
    initial_array = [random.randint(1, 100) for _ in range(N)]
    queries = make_queries(N, Q)

    # 2. Тестування без кешу
    print("Тестування без використання кешу...")
    array_no_cache = initial_array.copy()
    start_time_no_cache = time.time()

    for query in queries:
        q_type = query[0]
        if q_type == "Range":
            _, left, right = query
            range_sum_no_cache(array_no_cache, left, right)
        elif q_type == "Update":
            _, index, value = query
            update_no_cache(array_no_cache, index, value)

    end_time_no_cache = time.time()
    duration_no_cache = end_time_no_cache - start_time_no_cache
    print(f"Час виконання без кешу: {duration_no_cache:.2f} секунд\n")

    # 3. Тестування з LRU-кешем
    print("Тестування з використанням LRU-кешу...")
    array_with_cache = initial_array.copy()
    lru_cache = LRUCache(K_CAPACITY)
    start_time_with_cache = time.time()

    for query in queries:
        q_type = query[0]
        if q_type == "Range":
            _, left, right = query
            range_sum_with_cache(array_with_cache, left, right, lru_cache)
        elif q_type == "Update":
            _, index, value = query
            update_with_cache(array_with_cache, index, value, lru_cache)

    end_time_with_cache = time.time()
    duration_with_cache = end_time_with_cache - start_time_with_cache
    print(f"Час виконання з LRU-кешем: {duration_with_cache:.2f} секунд\n")

    # 4. Виведення результатів порівняння
    print("Ефективність LRU-кешу:")
    if duration_with_cache > 0:
        speedup = duration_no_cache / duration_with_cache
        print(f"- Версія з кешем швидша у {speedup:.1f} разів.")
    else:
        print("- Неможливо розрахувати прискорення (час виконання з кешем дуже малий).")