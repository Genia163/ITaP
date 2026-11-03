import json
import logging
import requests
import signal
import sys
import time
import tracemalloc
from google.colab import auth
from google.auth import default
from googleapiclient.discovery import build
import types 
class TimeoutException(Exception):
    pass

def _timeout_handler(signum, frame):
    raise TimeoutException("Время выполнения превысило допустимый лимит!")


func_passed = 0
def check_result(user_func, dict_all_cases, github_token: str = None, repo_owner: str = None, repo_name: str = None, lab_num: int= None, task_num: str = None):
    test_cases = dict_all_cases[task_num]['cases']
    select_count = 0
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
    return [func_passed, test_cases]

def check_time_and_memory(user_func, dict_all_cases, github_token: str = None, repo_owner: str = None, repo_name: str = None, lab_num: int= None, task_num: str = None):
    
    stress_data = dict_all_cases[task_num]['stres_data']
    MAX_TIME_FACTOR = dict_all_cases[task_num]['time']
    MAX_EXTRA_MEM_KB = dict_all_cases[task_num]['memory']

    # --- 1. Замер эталонной функции ---
    tracemalloc.start()
    t0 = time.perf_counter()
    refrensiw = dict_all_cases[task_num]['reference']
    ref_res = refrensiw(dict_all_cases[task_num]['stres_data'])
    ref_time = time.perf_counter() - t0
    _, ref_peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # --- 2. Замер студенческой функции с тайм-аутом ---
    user_time = 0.0
    user_peak_mem = 0
    timeout_occurred = False

    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(MAX_TIME_FACTOR)

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
            f"     Код выполняется дольше {MAX_TIME_FACTOR} сек (вероятно, используется неоптимальный поиск/цикл O(n²)).")
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
    else:
        func_passed+=1

    if extra_memory_kb > MAX_EXTRA_MEM_KB:
        perf_errors.append(
            f"Выделено избыточных {extra_memory_kb:.1f} KB ОЗУ (проверьте, нет ли лишних списков/копий)."
        )
    else:
        func_passed+=1

    print("-" * 65)
    if perf_errors:
        print("❌ Задание не зачтено из-за неэффективности:")
        for err in perf_errors:
            print(f"   • {err}")
    else:
        print(f"🎉 ВСЕ ТЕСТЫ И БЕНЧМАРКИ УСПЕШНО ПРОЙДЕНЫ!")

    return [func_passed, user_time, ref_time, user_peak_mem, extra_memory_kb]


# ----------------------------------------------------------------------
# Основная функция проверки
# ----------------------------------------------------------------------
def check_task(user_func, dict_all_cases, github_token: str = None, repo_owner: str = None, repo_name: str = None, lab_num: int= None, task_num: str = None):
    
    resit = check_result(user_func, dict_all_cases, github_token, repo_owner, repo_name, lab_num, task_num)  #[func_passed, test_cases]
    func_passed = resit[0]
    test_cases = resit[1]          

    memory_and_time = check_time_and_memory(user_func, dict_all_cases, github_token, repo_owner, repo_name, lab_num, task_num) #[func_passed, user_time, ref_time, user_peak_mem, extra_memory_kb]
    func_passed = memory_and_time[0]+func_passed  # т.к 2 функции
    user_time = memory_and_time[1]
    ref_time = memory_and_time[2]
    user_peak_mem = memory_and_time[3]
    extra_memory_kb = memory_and_time[4]
    
    if github_token:
        # Добавляем вызов отправки (передаем токены, если они доступны в вашей программе)
        # Допустим, github_token, repo_owner и repo_name передаются глобально или как аргументы
        metrics = {
            "total": len(test_cases)+2,
            "score": func_passed,
            "time_ms": round(user_time * 1000, 2),  # Новое значение: время работы
            "ref_time":round(ref_time * 1000,2),
            "memory_mb":round(user_peak_mem / (1024 * 1024), 2),  # Новое значение: память
            "extra_memory":round(extra_memory_kb,2)
        }
        lab_date = {
            "repo_type": "task",
            "lab_num": lab_num,      # <-- Указываем номер ЛР (создаст и откроет лист ПЗ2)
            "task_num": task_num       # <-- Указываем номер задания (запишет в Колонку 4 / Задание 1)
        }
        return (lab_date, metrics, github_token, repo_owner, repo_name)
      
    else:
      print(" ⚠️  Не указан гит токен")


if __name__ == "__main__":
  check_task()


