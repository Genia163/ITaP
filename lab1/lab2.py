# test.py
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
def _load_remote_(name, url):
    code=requests.get(f"{url}?v={int(time.time())}", timeout=10).text
    mod=types.ModuleType(name)
    exec(code,mod.__dict__)
    return mod
checcheck_quiz=_load_remote_(
    "checcheck_quiz", "https://raw.githubusercontent.com/Genia163/ITaP/refs/heads/main/checcheck_quiz.py"
)
checker_task = _load_remote_(
    "check_task.py", "https://raw.githubusercontent.com/Genia163/ITaP/refs/heads/main/check_task.py"
)

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


def _send_payload_to_github(lab_date: dict, data: dict, github_token: str, repo_owner: str, repo_name: str):
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
            "type": lab_date, 
            **data
        }
    }
    res = requests.post(url, headers=headers, data=json.dumps(payload))
    if res.status_code == 204:
        print("📡 Результат успешно отправлен в ведомость!")
    else:
        print(f"⚠️ Ошибка отправки на GitHub: {res.status_code}")

def check_task_all(user_func, github_token: str = None, repo_owner: str = None, repo_name: str = None, lab_num: int= None, task_num: int = None):
    result = check_task.checker_task(user_func, github_token, repo_owner, repo_name, lab_num, task_num)
    if result:
        _send_payload_to_github(*result)
        
def check_quiz(user_answers: dict, github_token: str = None, repo_owner: str = None, repo_name: str = None, task_num: int = None, lab_num: int = None):
    result = checcheck_quiz.check_quiz_answers(user_answers, github_token, repo_owner, repo_name, task_num, lab_num)
    if result:
        _send_payload_to_github(*result)
    
