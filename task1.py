# task1.py
import time
import tracemalloc

# 1. Эталонное решение преподавателя (O(n) по времени и O(k) по памяти)
def _reference_solution(numbers: list[int]) -> list[int]:
    return [x**2 for x in numbers if x % 2 == 0]

def check_task1(user_func):
    """Строгая проверка эффективных алгоритмов"""
    
    # Задаем жесткие допустимые коэффициенты
    MAX_TIME_FACTOR = 2.5   # Функция студента не должна быть медленнее эталона более чем в 2.5 раза
    MAX_EXTRA_MEM_BYTES = 1024 * 500  # Не более 500 КБ сверх необходимого результата
    
    # Тестовый набор с достаточно большим объемом для явной разницы в сложности O(n)
    test_data = list(range(1, 500_000))
    
    print("🚀 Анализ производительности алгоритма...\n" + "-" * 65)
    
    try:
        # --- 1. Замер эталонного решения (Benchmark) ---
        tracemalloc.start()
        t0 = time.perf_counter()
        ref_res = _reference_solution(test_data)
        ref_time = time.perf_counter() - t0
        _, ref_peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # --- 2. Замер студенческого решения ---
        tracemalloc.start()
        t0 = time.perf_counter()
        user_res = user_func(test_data)
        user_time = time.perf_counter() - t0
        _, user_peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # --- 3. Валидация правильности ответа ---
        assert user_res == ref_res, "Функция вернула некорректный результат."
        
        # Вычисляем дельты
        time_ratio = user_time / ref_time if ref_time > 0 else 1.0
        extra_memory = user_peak_mem - ref_peak_mem
        
        # --- 4. Проверка критериев эффективности ---
        errors = []
        
        # Если студент сделал неоптимальный цикл/лишние проходы
        if time_ratio > MAX_TIME_FACTOR:
            errors.append(
                f"Неоптимальная сложность по времени: ваш код в {time_ratio:.1f}x "
                f"медленнее эталона (допустимо до {MAX_TIME_FACTOR}x)."
            )
            
        # Если студент создавал дубликаты массивов или промежуточные списки
        if extra_memory > MAX_EXTRA_MEM_BYTES:
            extra_kb = extra_memory / 1024
            errors.append(
                f"Избыточная память: выделено лишних {extra_kb:.1f} KB "
                f"(возможно, созданы ненужные копии списков или промежуточные структуры)."
            )
            
        # Вывод детального отчёта
        print(f"📊 Результаты профилирования:")
        print(f" ⏱ Время работы:  {user_time*1000:.2f} ms (Эталон: {ref_time*1000:.2f} ms | Соотношение: {time_ratio:.2f}x)")
        print(f" 💾 Пиковая память: {user_peak_mem / (1024*1024):.2f} MB (Избыток: {max(0, extra_memory)/1024:.1f} KB)")
        print("-" * 65)
        
        if errors:
            print("❌ Задание не зачтено из-за неэффективности:")
            for err in errors:
                print(f"   • {err}")
        else:
            print("✅ Задание успешно пройдено! Алгоритм оптимален.")

    except AssertionError as e:
        print(f"❌ Задание не пройдено (Ошибка логики): {e}")
    except Exception as e:
        print(f"⚠️ Произошла ошибка при выполнении: {type(e).__name__}: {e}")
    finally:
        if tracemalloc.is_tracing():
            tracemalloc.stop()
