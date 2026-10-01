# test.py
import json
import logging
import requests
import signal
import sys
import time
import tracemalloc
from google.colab import auth, output
from google.auth import default
from googleapiclient.discovery import build

logging.getLogger('google_auth_httplib2').setLevel(logging.ERROR)
student_info = {"name": "", "group": "", "mail": ""}

def set_student_info(name: str, group: str):
    """Автоматическая инициализация ФИО, группы и РЕАЛЬНОЙ почты студента"""
    try:
        # Запрашиваем авторизацию у Google в Colab
        auth.authenticate_user()
        creds, _ = default()
        
        # Получаем реальную почту из профиля Google
        oauth2_service = build('oauth2', 'v2', credentials=creds)
        user_info = oauth2_service.userinfo().get().execute()
        real_mail = user_info.get('email')
        
        if not real_mail:
            raise Exception("Не удалось прочитать email из профиля")
            
        student_info["name"] = name
        student_info["group"] = group
        student_info["mail"] = real_mail  # Записываем скрыто от студента
        
        print(f"👤 Авторизован: {name} (Группа: {group})")
        
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")


def _send_payload_to_github(payload_type: str, data: dict, github_token: str, repo_owner: str, repo_name: str):
    """Отправка метрик в GitHub Actions via repository_dispatch"""
    if not student_info["name"]:
        print("⚠️ Ошибка: Сначала укажите ФИО и группу через set_student_info()!")
        return

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dispatches"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "event_type": "update_sheet",
        "client_payload": {
            "student": student_info["name"],
            "group": student_info["group"],
            "mail": student_info["mail"],
            "type": payload_type,
            **data
        }
    }
    res = requests.post(url, headers=headers, data=json.dumps(payload))
    if res.status_code == 204:
        print("📡 Результат успешно отправлен в ведомость!")
    else:
        print(f"⚠️ Ошибка отправки на GitHub: {res.status_code}")

def get_current_notebook_name() -> str:
    """Внутренний системный поиск имени блокнота в памяти ядра Colab"""
    try:
        # Способ 1: Извлекаем метаданные сессии через встроенные переменные
        import sys
        if 'google.colab' in sys.modules:
            # Colab регистрирует сессию в пространстве имен
            for name, val in globals().items():
                if name == '__session__' and hasattr(val, 'get'):
                    return val.get('name', 'unknown.ipynb')
            
            # Способ 2: Прямое чтение переменной окружения Jupyter сессии
            import os
            # В современных версиях Colab имя передается в метаданные ядра
            if '__vsc_notebook__' in globals():
                return globals()['__vsc_notebook__']
                
            # Способ 3: Поиск через инспекцию стека вызовов (где запущен .ipynb)
            import __main__
            if hasattr(__main__, '__file__'):
                return os.path.basename(__main__.__file__)
    except Exception:
        pass
        
    return "unknown.ipynb"

# --- Пример использования для защиты ---
def verify_notebook():
    filename = get_current_notebook_name()
    # Переводим в нижний регистр, чтобы поймать и "Копия", и "копия", и "copy"
    filename_lower = filename.lower()
    ru_copies = filename_lower.count("копия")
    en_copies = filename_lower.count("copy")
    total_copies = ru_copies + en_copies
    
    if total_copies > 1:
        return False
    
    return True
# ----------------------------------------------------------------------
# 1. Эталонное решение преподавателя для сравнения производительности
# ----------------------------------------------------------------------
def _reference_solution(numbers: list[int]) -> list[int]:
    return [x ** 2 for x in numbers if x % 2 == 0]


# Исключение для перехвата зависших функций по тайм-ауту
class TimeoutException(Exception):
    pass


def _timeout_handler(signum, frame):
    raise TimeoutException("Время выполнения превысило допустимый лимит!")


# ----------------------------------------------------------------------
# Основная функция проверки
# ----------------------------------------------------------------------
def check_task1(user_func, github_token: str = None, repo_owner: str = None, repo_name: str = None):
    """
    Комплексная проверка Задания 1:
    - Функциональные тесты на корректность вычислений
    - Замер времени работы (Benchmark)
    - Замер расхода памяти (Memory Profiling)
    """
    if verify_notebook() is False:
        print("Ой кажется ты жульничаешь")
        return
    else:
        print("???????????????????????????????????")
    
    print("🚀 Старт комплексной проверки Задания 1\n" + "=" * 65)
    select_count = 0
    # ------------------------------------------------------------------
    # ЭТАП 1: Функциональное тестирование
    # ------------------------------------------------------------------
    print("📋 ЭТАП 1: Проверка корректности работы (Функциональные тесты)")
    print("-" * 65)

    test_cases = [
        ([1, 2, 3, 4, 5, 6], [4, 16, 36], "Тест 1.1: Базовый список [1, 2, 3, 4, 5, 6]"),
        ([1, 3, 5], [], "Тест 1.2: Список без чётных чисел [1, 3, 5]"),
        ([-4, -3, 0, 2], [16, 0, 4], "Тест 1.3: Отрицательные числа и ноль [-4, -3, 0, 2]"),
        ([], [], "Тест 1.4: Пустой список []"),
    ]

    
    func_passed = 0
    for inp, expected, description in test_cases:
        try:
            res = user_func(inp)
            assert res == expected, f"Получено {res}, ожидалось {expected}"
            print(f"  ✅ {description} — PASSED")
            func_passed += 1
        except AssertionError as e:
            print(f"  ❌ {description} — FAILED: {e}")
        except Exception as e:
            print(f"  ⚠️ {description} — ERROR ({type(e).__name__}): {e}")

    print(f"\n📊 Результат Этапа 1: {func_passed}/{len(test_cases)} тестов пройдено.")

    if func_passed < len(test_cases):
        print("\n❌ Проверка остановлена: исправьте логические ошибки в коде.")
        return

    # ------------------------------------------------------------------
    # ЭТАП 2 и 3: Стресс-тестирование (Время и Память)
    # ------------------------------------------------------------------
    print("\n⚡ ЭТАП 2 и 3: Анализ производительности (Время и Память)")
    print("-" * 65)

    stress_data = list(range(1, 200_000))

    TIMEOUT_SECONDS = 3
    MAX_TIME_FACTOR = 3.0
    MAX_EXTRA_MEM_KB = 1024

    # --- 1. Замер эталонной функции ---
    tracemalloc.start()
    t0 = time.perf_counter()
    ref_res = _reference_solution(stress_data)
    ref_time = time.perf_counter() - t0
    _, ref_peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # --- 2. Замер студенческой функции с тайм-аутом ---
    user_time = 0.0
    user_peak_mem = 0
    timeout_occurred = False

    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(TIMEOUT_SECONDS)

    try:
        tracemalloc.start()
        t0 = time.perf_counter()

        user_res = user_func(stress_data)

        user_time = time.perf_counter() - t0
        _, user_peak_mem = tracemalloc.get_traced_memory()

    except TimeoutException:
        timeout_occurred = True
    except Exception as e:
        print(f"  ⚠️ Ошибка при выполнении стресс-теста: {type(e).__name__}: {e}")
        return
    finally:
        signal.alarm(0)
        if tracemalloc.is_tracing():
            tracemalloc.stop()

    # --- 3. Вывод результатов стресс-теста ---
    if timeout_occurred:
        print(f"  ⏳ [ВРЕМЯ] TIME LIMIT EXCEEDED!")
        print(
            f"     Код выполняется дольше {TIMEOUT_SECONDS} сек (вероятно, используется неоптимальный поиск/цикл O(n²)).")
        print("\n❌ Задание не зачтено из-за зависания алгоритма.")
        return


    if user_res != ref_res:
        print("  ❌ [ОШИБКА] Код вернул некорректный результат на большом массиве.")
        return


    time_ratio = user_time / ref_time if ref_time > 0 else 1.0
    extra_memory_kb = (user_peak_mem - ref_peak_mem) / 1024

    print(
        f"  ⏱ Время работы:  {user_time * 1000:.2f} ms (Эталон: {ref_time * 1000:.2f} ms | Соотношение: {time_ratio:.2f}x)")
    print(f"  💾 Пиковая память: {user_peak_mem / (1024 * 1024):.2f} MB (Избыток: {max(0, extra_memory_kb):.1f} KB)")

    # --- 4. Проверка критериев эффективности ---
    perf_errors = []

    if time_ratio > MAX_TIME_FACTOR:
        perf_errors.append(
            f"Код работает слишком медленно ({time_ratio:.1f}x от эталона, порог {MAX_TIME_FACTOR}x)."
        )

    if extra_memory_kb > MAX_EXTRA_MEM_KB:
        perf_errors.append(
            f"Выделено избыточных {extra_memory_kb:.1f} KB ОЗУ (проверьте, нет ли лишних списков/копий)."
        )

    print("-" * 65)
    if perf_errors:
        print("❌ Задание не зачтено из-за неэффективности:")
        for err in perf_errors:
            print(f"   • {err}")
    else:
        print(f"🎉 ВСЕ ТЕСТЫ И БЕНЧМАРКИ УСПЕШНО ПРОЙДЕНЫ! {select_count}")
    
    if github_token:
        # Добавляем вызов отправки (передаем токены, если они доступны в вашей программе)
        # Допустим, github_token, repo_owner и repo_name передаются глобально или как аргументы
        metrics = {
            "total": len(test_cases),
            "score": func_passed,
            "time_ms": round(user_time * 1000, 2),  # Новое значение: время работы
            "ref_time":round(ref_time * 1000,2),
            "memory_mb":round(user_peak_mem / (1024 * 1024), 2),  # Новое значение: память
            "extra_memory":round(extra_memory_kb,2)
        }
        _send_payload_to_github("task1", metrics, github_token, repo_owner, repo_name)

def check_quiz_answers(user_answers: dict, github_token: str = None, repo_owner: str = None, repo_name: str = None):
    """Проверка ответов викторины и отправка балла"""
    keys = {"q1": "str", "q2": "def", "q3": "1020", "q4": "==", "q5": "4 пробела"}
    score = sum(1 for q, ans in keys.items() if user_answers.get(q) == ans)
    total = len(keys)

    print(f"📊 Результат теста: {score}/{total} баллов.")

    if github_token:
        _send_payload_to_github("quiz", {"score": score, "total": total}, github_token, repo_owner, repo_name)
    
