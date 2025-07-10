import sys
import timeit
from functools import lru_cache
import matplotlib.pyplot as plt

# Збільшимо ліміт рекурсії для обчислення великих чисел Фібоначчі
sys.setrecursionlimit(2000)


# --- 1. Реалізація Splay Tree ---

class Node:
    """
    Клас, що представляє вузол у Splay Tree.
    Кожен вузол зберігає ключ (номер числа Фібоначчі n),
    значення (саме число Фібоначчі) та вказівники на батьківський
    і дочірні вузли.
    """

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.parent = None
        self.left = None
        self.right = None


class SplayTree:
    """
    Реалізація структури даних Splay Tree.
    Ключова особливість - операція 'splay', яка переміщує
    вузол, до якого відбувся доступ, у корінь дерева.
    Це забезпечує швидкий доступ до нещодавно використаних елементів.
    """

    def __init__(self):
        self.root = None

    def _left_rotate(self, x):
        """Виконує лівий поворот навколо вузла x."""
        y = x.right
        x.right = y.left
        if y.left:
            y.left.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _right_rotate(self, x):
        """Виконує правий поворот навколо вузла x."""
        y = x.left
        x.left = y.right
        if y.right:
            y.right.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def _splay(self, node):
        """
        Переміщує вузол 'node' у корінь дерева за допомогою
        послідовності поворотів (zig, zig-zig, zig-zag).
        """
        while node.parent:
            if not node.parent.parent:
                # Zig
                if node == node.parent.left:
                    self._right_rotate(node.parent)
                else:
                    self._left_rotate(node.parent)
            elif node == node.parent.left and node.parent == node.parent.parent.left:
                # Zig-Zig
                self._right_rotate(node.parent.parent)
                self._right_rotate(node.parent)
            elif node == node.parent.right and node.parent == node.parent.parent.right:
                # Zig-Zig
                self._left_rotate(node.parent.parent)
                self._left_rotate(node.parent)
            elif node == node.parent.right and node.parent == node.parent.parent.left:
                # Zig-Zag
                self._left_rotate(node.parent)
                self._right_rotate(node.parent)
            else:
                # Zig-Zag
                self._right_rotate(node.parent)
                self._left_rotate(node.parent)

    def insert(self, key, value):
        """Вставляє новий вузол і виконує splay для нього."""
        new_node = Node(key, value)
        if not self.root:
            self.root = new_node
            return

        current = self.root
        parent = None
        while current:
            parent = current
            if key < current.key:
                current = current.left
            elif key > current.key:
                current = current.right
            else:
                # Якщо ключ вже існує, оновлюємо значення і робимо splay
                current.value = value
                self._splay(current)
                return

        new_node.parent = parent
        if key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        self._splay(new_node)

    def find(self, key):
        """Шукає вузол за ключем і виконує splay."""
        current = self.root
        while current:
            if key == current.key:
                self._splay(current)
                return current.value
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return None


# --- 2. Функції для обчислення чисел Фібоначчі ---

@lru_cache(maxsize=None)
def fibonacci_lru(n: int) -> int:
    """
    Обчислює число Фібоначчі з використанням декоратора @lru_cache.
    Кеш зберігає результати попередніх викликів.
    """
    if n < 2:
        return n
    return fibonacci_lru(n - 1) + fibonacci_lru(n - 2)


def fibonacci_splay(n: int, tree: SplayTree) -> int:
    """
    Обчислює число Фібоначчі з використанням Splay Tree для кешування.
    """
    if n < 2:
        return n

    # Шукаємо значення в дереві
    found_value = tree.find(n)
    if found_value is not None:
        return found_value

    # Якщо не знайдено, обчислюємо та зберігаємо в дереві
    result = fibonacci_splay(n - 1, tree) + fibonacci_splay(n - 2, tree)
    tree.insert(n, result)
    return result


# --- 3. Основний блок для вимірювання та візуалізації ---

if __name__ == "__main__":
    n_values = list(range(0, 1000, 50))
    lru_times = []
    splay_times = []

    # Кількість повторів для timeit для отримання середнього часу
    num_repeats = 1000

    print("Порівняння продуктивності LRU Cache та Splay Tree (вимірювання доступу)\n")

    # --- Вимірювання для LRU Cache ---
    for n in n_values:
        fibonacci_lru.cache_clear()
        for i in range(n + 1):
            fibonacci_lru(i)
        t = timeit.timeit(lambda: fibonacci_lru(n), number=num_repeats)
        lru_times.append(t / num_repeats)

    # --- Вимірювання для Splay Tree ---
    for n in n_values:
        splay_tree = SplayTree()
        for i in range(n + 1):
            fibonacci_splay(i, splay_tree)
        t = timeit.timeit(lambda: fibonacci_splay(n, splay_tree), number=num_repeats)
        splay_times.append(t / num_repeats)

    # --- 4. Виведення таблиці результатів ---
    print(f"{'n':<10}| {'LRU Cache Time (s)':<20}| {'Splay Tree Time (s)':<20}")
    print("-" * 54)
    for i, n in enumerate(n_values):
        print(f"{n:<10}| {lru_times[i]:<20.8f}| {splay_times[i]:<20.8f}")

    # --- 5. Побудова графіка ---
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 7))

    plt.plot(n_values, lru_times, marker='o', linestyle='-', label='LRU Cache (Lookup)')
    plt.plot(n_values, splay_times, marker='x', linestyle='--', label='Splay Tree (Lookup)')

    plt.title('Порівняння часу доступу: LRU Cache vs Splay Tree', fontsize=16)
    plt.xlabel('n (номер числа Фібоначчі)', fontsize=12)
    plt.ylabel('Середній час доступу (с)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    plt.tight_layout()
    plt.show()

