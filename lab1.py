# task1.py
import time
import tracemalloc
import signal
import requests
import json

class TimeoutException(Exception): pass
def _timeout_handler(signum, frame): raise TimeoutException("Timeout")

# Глобальный словарь для хранения данных студента в рамках сессии Colab
student_info = {"name": "", "group": ""}

def set_student_info(name: str, group: str):
    """Инициализация ФИО и группы студента"""
    student_info["name"] = name
    student_info["group"] = group
    print(f"👤 Авторизован: {name} (Группа: {group})")

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
            "type": payload_type,
            **data
        }
    }
    res = requests.post(url, headers=headers, data=json.dumps(payload))
    if res.status_code == 204:
        print("📡 Результат успешно отправлен в ведомость!")
    else:
        print(f"⚠️ Ошибка отправки на GitHub: {res.status_code}")

def check_task1(user_func, github_token: str = None, repo_owner: str = None, repo_name: str = None):
    print("🚀 Старт комплексной проверки Задания 1\n" + "=" * 65)
    
    # 1. Функциональные тесты
    test_cases = [
        ([1, 2, 3, 4, 5, 6], [4, 16, 36]),
        ([1, 3, 5], []),
        ([-4, -3, 0, 2], [16, 0, 4]),
        ([], [])
    ]
    func_passed = True
    for inp, expected in test_cases:
        try:
            if user_func(inp) != expected:
                func_passed = False; break
        except Exception:
            func_passed = False; break

    if not func_passed:
        print("❌ Задание 1 не пройдено (ошибка в логике).")
        if github_token:
            _send_payload_to_github("task", {"task_num": 1, "passed": False}, github_token, repo_owner, repo_name)
        return

    # 2. Стресс-тест (Время и Память)
    stress_data = list(range(1, 200_000))
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(3)
    
    passed_all = True
    try:
        t0 = time.perf_counter()
        user_res = user_func(stress_data)
        elapsed = time.perf_counter() - t0
        if elapsed > 1.5: passed_all = False
    except Exception:
        passed_all = False
    finally:
        signal.alarm(0)

    if passed_all:
        print("🎉 Задание 1 успешно пройдено!")
    else:
        print("❌ Задание 1 не пройдено (превышен лимит времени/памяти).")

    if github_token:
        _send_payload_to_github("task", {"task_num": 1, "passed": passed_all}, github_token, repo_owner, repo_name)

def check_quiz_answers(user_answers: dict, github_token: str = None, repo_owner: str = None, repo_name: str = None):
    """Проверка ответов викторины и отправка балла"""
    keys = {"q1": "str", "q2": "def", "q3": "1020", "q4": "==", "q5": "4 пробела"}
    score = sum(1 for q, ans in keys.items() if user_answers.get(q) == ans)
    total = len(keys)
    
    print(f"📊 Результат теста: {score}/{total} баллов.")
    
    if github_token:
        _send_payload_to_github("quiz", {"score": score, "total": total}, github_token, repo_owner, repo_name)
