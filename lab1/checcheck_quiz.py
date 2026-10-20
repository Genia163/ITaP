keys = [
     {"q1": "str", "q2": "def", "q3": "1020", "q4": "==", "q5": "4 пробела"},
     {"q1": "int", "q2": "create", "q3": "30", "q4": "is", "q5": "1 пробела"}
 ]




def check_quiz_answers(user_answers: dict, github_token: str = None, repo_owner: str = None, repo_name: str = None, task_num: int = None, lab_num: int = None):
    """Проверка ответов викторины и отправка балла"""
    keyn = keys[lab_num-1]
    score = sum(1 for q, ans in keyn.items() if user_answers.get(q) == ans)
    total = len(keyn)
    print(f"📊 Результат теста: {score}/{total} баллов.")

    if github_token:
        lab_date = {
            "repo_type": "quiz",
            "lab_num": lab_num,      # <-- Указываем номер ЛР (создаст и откроет лист ПЗ2)
            "task_num": task_num 
        }
        _send_payload_to_github(lab_date, {"score": score, "total": total}, github_token, repo_owner, repo_name)


if __name__ == "__main__":
     check_quiz_answers()
