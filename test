import time
import tracemalloc
import signal
import json
import base64
import urllib.request
import urllib.error
import ipywidgets as widgets
from IPython.display import display, clear_output

# ==========================================
# 1. КОНФИГУРАЦИЯ И СТРУКТУРА ТЕСТОВ (Из Варианта 1)
# ==========================================

# Базовые функциональные тесты (Этап 1)
FUNC_TESTS = [
    {"input": [1, 2, 3, 4, 5], "expected": [2, 4]},
    {"input": [10, 15, 20, 25], "expected": [10, 20]},
    {"input": [1, 3, 5], "expected": []},
    {"input": [], "expected": []}
]

# Параметры бенчмаркинга производительности (Этап 2)
LARGE_N = 100000          # Размер массива для стресс-теста
MAX_TIME_FACTOR = 3.0     # Коэффициент замедления относительно эталона
MAX_EXTRA_MEM_KB = 1024   # Допустимый перерасход памяти (1 МБ)
TIMEOUT_SECONDS = 3       # Лимит времени на исполнение кода (сек)

# Эталонное решение для объективного сравнения производительности
def reference_solution(data):
    return [x for x in data if x % 2 == 0]

# Исключение для обработки таймаута
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("TIME LIMIT EXCEEDED! Код выполняется слишком долго (вероятно, $O(n^2)$).")

# ==========================================
# 2. ПОЛНЫЙ МОДУЛЬ ТЕСТИРОВАНИЯ (Вариант 1)
# ==========================================

def run_comprehensive_tests(user_func):
    """
    Проводит комплексную проверку студенческой функции:
    1. Функциональные тесты с детальным отчетом.
    2. Бенчмарк производительности (время и память) в сравнении с эталоном.
    """
    print("=" * 60)
    print("📋 ЭТАП 1: Функциональное тестирование")
    print("=" * 60)
    
    passed_func_tests = 0
    total_func_tests = len(FUNC_TESTS)

    for i, test in enumerate(FUNC_TESTS, 1):
        try:
            result = user_func(test["input"].copy())
            if result == test["expected"]:
                print(f"  [✓] Тест {i}: PASSED (Вход: {test['input']} -> Выход: {result})")
                passed_func_tests += 1
            else:
                print(f"  [✗] Тест {i}: FAILED!")
                print(f"      Ожидалось: {test['expected']}")
                print(f"      Получено:  {result}")
        except Exception as e:
            print(f"  [💥] Тест {i}: ERROR! Вызвано исключение: {e}")

    print(f"\nРезультат этапа 1: {passed_func_tests}/{total_func_tests} тестов пройдено.")
    
    if passed_func_tests < total_func_tests:
        print("\n❌ Корректность работы не подтверждена. Стресс-тест отменен.")
        return False, "Не пройдены функциональные тесты"

    print("\n" + "=" * 60)
    print("⚡ ЭТАП 2: Бенчмарк производительности и памяти")
    print("=" * 60)

    # Подготовка больших тестовых данных
    large_input = list(range(LARGE_N))

    # --- 1. Замер эталонного решения ---
    tracemalloc.start()
    t0 = time.perf_counter()
    _ = reference_solution(large_input)
    t1 = time.perf_counter()
    _, ref_mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    ref_time = t1 - t0
    ref_mem_kb = ref_mem_peak / 1024

    # --- 2. Замер студенческого решения с таймером безопасности ---
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(TIMEOUT_SECONDS)

    user_time = 0
    user_mem_kb = 0
    is_performance_ok = False
    details = ""

    try:
        tracemalloc.start()
        t0 = time.perf_counter()
        
        _ = user_func(large_input.copy())
        
        t1 = time.perf_counter()
        _, user_mem_peak = tracemalloc.get_traced_memory()
        
        user_time = t1 - t0
        user_mem_kb = user_mem_peak / 1024

        # Вычисление метрик производительности
        time_factor = user_time / ref_time if ref_time > 0 else 1.0
        extra_mem_kb = user_mem_kb - ref_mem_kb

        print(f"⏱ Время работы: {user_time*1000:.2f} ms (Эталон: {ref_time*1000:.2f} ms | Соотношение: {time_factor:.2f}x)")
        print(f"💾 Пиковая память: {user_mem_kb:.2f} KB (Эталон: {ref_mem_kb:.2f} KB | Прирост: {extra_mem_kb:.2f} KB)")

        # Оценка соблюдения ограничений
        time_ok = time_factor <= MAX_TIME_FACTOR
        mem_ok = extra_mem_kb <= MAX_EXTRA_MEM_KB

        if time_ok and mem_ok:
            print("\n✅ ВСЕ ТЕСТЫ И БЕНЧМАРКИ УСПЕШНО ПРОЙДЕНЫ!")
            is_performance_ok = True
            details = f"OK (Time: {user_time*1000:.1f}ms, Mem: {user_mem_kb:.1f}KB)"
        else:
            print("\n⚠️ ВНИМАНИЕ: Решение работает корректно, но неоптимально!")
            if not time_ok:
                print(f"  - Превышение по времени: код медленнее эталона в {time_factor:.2f} раз (лимит: {MAX_TIME_FACTOR}x)")
            if not mem_ok:
                print(f"  - Перерасход памяти: избыточно {extra_mem_kb:.2f} KB (лимит: {MAX_EXTRA_MEM_KB} KB)")
            details = f"Performance issue (Factor: {time_factor:.2f}x, Mem: {user_mem_kb:.1f}KB)"

    except TimeoutException as e:
        print(f"\n❌ {e}")
        details = "Timeout Limit Exceeded"
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении на больших данных: {e}")
        details = f"Runtime Error: {e}"
    finally:
        signal.alarm(0)  # Сброс таймера
        tracemalloc.stop()

    return is_performance_ok, details

# ==========================================
# 3. ОТПРАВКА РЕЗУЛЬТАТОВ НА GITHUB API
# ==========================================

def send_payload_to_github(token, repo, path, data_dict):
    """Отправляет или обновляет JSON-файл с результатами в репозитории GitHub."""
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Проверяем, существует ли уже файл (чтобы получить sha для обновления)
    sha = None
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 200:
                res_data = json.loads(resp.read().decode("utf-8"))
                sha = res_data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"⚠️ Ошибка при запросе структуры GitHub: {e}")

    # Формируем тело запроса
    json_str = json.dumps(data_dict, ensure_ascii=False, indent=2)
    b64_content = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

    payload = {
        "message": f"Submission from {data_dict.get('student_name', 'Student')}",
        "content": b64_content
    }
    if sha:
        payload["sha"] = sha

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers=headers, method="PUT")

    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status in (200, 201):
                print("🚀 Результаты успешно сохранены в репозитории GitHub!")
            else:
                print(f"⚠️ Ответ сервера GitHub: STATUS {resp.status}")
    except Exception as e:
        print(f"❌ Не удалось отправить данные на GitHub: {e}")

# ==========================================
# 4. ИНТЕРФЕЙС colab (Widgets + Авторизация)
# ==========================================

# Поля ввода для авторизации студента
student_name_input = widgets.Text(description="ФИО:", placeholder="Иванов Иван")
student_group_input = widgets.Text(description="Группа:", placeholder="4201-090301D")
github_token_input = widgets.Password(description="GH Token:", placeholder="ghp_xxxxxxxxxxxx")
github_repo_input = widgets.Text(description="Репозиторий:", placeholder="owner/repo_name")

submit_btn = widgets.Button(
    description="Запустить проверку",
    button_style="primary",
    icon="check"
)

output_area = widgets.Output()

def on_submit_click(b):
    with output_area:
        clear_output()
        
        # 1. Валидация полей авторизации
        name = student_name_input.value.strip()
        group = student_group_input.value.strip()
        token = github_token_input.value.strip()
        repo = github_repo_input.value.strip()

        if not name or not group:
            print("❌ Ошибка: Введите ФИО и Номер группы перед запуском.")
            return

        # 2. Поиск студенческой функции в глобальной области
        if "get_even_numbers" not in globals():
            print("❌ Ошибка: Функция 'get_even_numbers' не найдена.")
            print("   Убедитесь, что вы запустили ячейку с вашим решением!")
            return

        user_func = globals()["get_even_numbers"]

        # 3. Запуск комплексной проверки (Вариант 1)
        is_passed, details = run_comprehensive_tests(user_func)

        # 4. Отправка результатов (если указаны данные GitHub)
        if token and repo:
            print("\n" + "=" * 60)
            print("📤 Отправка результатов преподавателю...")
            print("=" * 60)
            
            filepath = f"submissions/{group}/{name.replace(' ', '_')}_task1.json"
            payload = {
                "student_name": name,
                "student_group": group,
                "task": "Task 1 - Filter Even Numbers",
                "passed": is_passed,
                "details": details,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            send_payload_to_github(token, repo, filepath, payload)
        else:
            print("\nℹ️ Поля GH Token/Репозиторий не заполнены. Отправка результатов пропущена.")

submit_btn.on_click(on_submit_click)

# Отрисовка интерфейса
print("=== АВТОРИЗАЦИЯ И СДАЧА ЛАБОРАТОРНОЙ РАБОТЫ ===")
display(student_name_input, student_group_input, github_token_input, github_repo_input, submit_btn, output_area)
