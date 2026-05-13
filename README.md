graph TD
    A([Начало: process_block tokens, indent]) --> B{Перебор токенов t}
    B --> C{t == 'УПЛ'?}
    C -- Да --> D[Поп: label, cond]
    D --> E{Поиск label: в tokens}
    E --> F{Есть ли 'БП' до label?}
    F -- Нет --> G[IF: if cond { body }]
    F -- Да --> H{label начинается с 'P'?}
    H -- Нет --> I[IF-ELSE: if cond { then } else { else }]
    H -- Да --> J[WHILE: while cond { body }]
    G --> K[Рекурсия _process_block для body]
    I --> L[Рекурсия _process_block для then/else]
    J --> M[Рекурсия _process_block для body]
    K --> B
    L --> B
    M --> B
    
    C -- Нет --> N{t == ':='?}
    N -- Да --> O[Поп: right, left. Генерация: var left = right;]
    O --> B
    
    N -- Нет --> P{t Оператор (+, -, ==...)?}
    P -- Да --> Q[Поп: right, left. Пуш: (left t right)]
    Q --> B
    
    P -- Нет --> R{t Операнд/Идентификатор?}
    R -- Да --> S[Пуш t в стек]
    S --> B
    
    R -- Нет --> T{t Функция 'Ф' / Массив 'АЭС'?}
    T -- Да --> U[Поп аргументы/индексы. Пуш: call/index]
    U --> B
    
    T -- Нет --> V{t Метка 'label:' или 'БП'?}
    V -- Да --> W[Пропуск/Обработка]
    W --> B
    
    B -- Конец токенов --> X[Остаток стека -> expr;]
    X --> Y([Конец блока])

    subgraph Функции (в методе generate)
    Z[Поиск 'НП' в RPN] --> Z1[Извлечение имени функции]
    Z1 --> Z2[Поиск парного 'КП']
    Z2 --> Z3[Генерация метода public static void func()]
    end
