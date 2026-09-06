# task1.py

def check_task1(user_func):
    """Пошаговая проверка Задания 1: filter_even_squares"""
    
    # Набор тестов: (входные данные, ожидаемый результат, описание)
    test_cases = [
        ([1, 2, 3, 4, 5, 6], [4, 16, 36], "Тест 1: Базовый список [1, 2, 3, 4, 5, 6]"),
        ([1, 3, 5], [], "Тест 2: Только нечётные числа [1, 3, 5]"),
        ([-4, -3, 0, 2], [16, 0, 4], "Тест 3: Отрицательные числа и ноль [-4, -3, 0, 2]"),
        ([], [], "Тест 4: Пустой список []"),
    ]
    
    print("🚀 Запуск автоматического тестирования...\n" + "-" * 50)
    passed_count = 0
    
    for i, (inp, expected, description) in enumerate(test_cases, 1):
        try:
            # Вызываем функцию студента
            result = user_func(inp)
            
            # Проверяем равенство с эталоном
            assert result == expected, f"Получено {result}, ожидалось {expected}"
            
            print(f"✅ {description} — PASSED")
            passed_count += 1
            
        except AssertionError as e:
            print(f"❌ {description} — FAILED: {e}")
        except Exception as e:
            print(f"⚠️ {description} — ERROR (Ошибка кода): {type(e).__name__}: {e}")
            
    print("-" * 50)
    if passed_count == len(test_cases):
        print(f"🎉 Итог: Все тесты пройдены ({passed_count}/{len(test_cases)})!")
    else:
        print(f"🧩 Итог: Пройдено {passed_count} из {len(test_cases)} тестов. Исправьте ошибки выше.")
