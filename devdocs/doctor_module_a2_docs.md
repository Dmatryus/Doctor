# Module A.2: Data Models - Documentation

## Overview
Модуль A.2 определяет все модели данных для системы Doctor, включая Pydantic модели, перечисления (Enums) и валидаторы. Это основа для типизации данных и валидации во всей системе.

## Component Architecture

```mermaid
graph TB
    subgraph "Module A.2 - Data Models"
        style "Module A.2 - Data Models" fill:#e1f5fe,stroke:#01579b,stroke-width:3px
        
        subgraph "Enums & Constants"
            DF[DocumentFormat]
            TS[TaskStatus]
            CT[ConversionTheme]
            CS[CodeStyle]
            EC[ErrorCode]
            CONST[Constants]
        end
        
        subgraph "Core Models"
            FI[FileInfo]
            TASK[Task]
            CO[ConversionOptions]
            STATS[TaskStats]
        end
        
        subgraph "API Models"
            CR[ConversionRequest]
            CRESP[ConversionResponse]
            ER[ErrorResponse]
        end
        
        subgraph "Validators"
            FV[FileValidator]
            UV[URLValidator]
            TV[TextValidator]
            CV[ConversionValidator]
        end
    end
    
    DF --> FI
    DF --> TASK
    TS --> TASK
    CT --> CO
    CS --> CO
    CO --> TASK
    EC --> ER
    
    FV --> FI
    CV --> CR
    
    style DF fill:#ffeb3b,stroke:#f57c00
    style TASK fill:#4caf50,stroke:#1b5e20
    style FV fill:#ff9800,stroke:#e65100
```

## Module Integration

```mermaid
graph LR
    subgraph "Previous"
        A1[A.1 Project Setup<br/>✅ COMPLETED]
    end
    
    subgraph "Current Module"
        style "Current Module" fill:#fff3e0,stroke:#e65100,stroke-width:3px
        A2[A.2 Data Models<br/>✅ CURRENT]
    end
    
    subgraph "Next Modules"
        A3[A.3 Storage]
        B1[B.1 Upload API]
        C1[C.1 Converters]
    end
    
    subgraph "Dependencies"
        PYD[Pydantic]
        MAG[python-magic]
    end
    
    A1 --> A2
    PYD --> A2
    MAG --> A2
    
    A2 --> A3
    A2 --> B1
    A2 --> C1
    
    style A2 fill:#4caf50,stroke:#1b5e20,stroke-width:3px
    style A3 fill:#e0e0e0
    style B1 fill:#e0e0e0
```

## Data Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Validator
    participant Model
    participant Storage
    
    Client->>API: Upload file (raw data)
    API->>Validator: Validate file
    Validator-->>API: Validation result
    
    alt Valid file
        API->>Model: Create FileInfo
        Model->>Model: Generate UUID
        Model->>Model: Set timestamps
        Model-->>API: FileInfo instance
        
        API->>Model: Create Task
        Model->>Model: Validate conversion
        Model-->>API: Task instance
        
        API->>Storage: Save models
        Storage-->>API: Saved
        
        API-->>Client: ConversionResponse
    else Invalid file
        API->>Model: Create ErrorResponse
        Model-->>API: ErrorResponse
        API-->>Client: Error (400/413/etc)
    end
```

## Enum System

```mermaid
graph TD
    subgraph "Document Format Handling"
        INPUT[User Input<br/>'md', 'markdown', '.md']
        NORM[normalize<br/>Method]
        ENUM[DocumentFormat.MARKDOWN]
        
        INPUT --> NORM
        NORM --> ENUM
        
        ENUM --> MIME[to_mime_type<br/>'text/markdown']
        ENUM --> EXT[get_extensions<br/>'.md', '.markdown']
    end
    
    subgraph "Task Status Flow"
        CREATED[CREATED]
        QUEUED[QUEUED]
        WAITING[WAITING]
        PROCESSING[PROCESSING]
        SUCCESS[SUCCESS]
        FAILED[FAILED]
        
        CREATED --> QUEUED
        QUEUED --> WAITING
        QUEUED --> PROCESSING
        WAITING --> PROCESSING
        PROCESSING --> SUCCESS
        PROCESSING --> FAILED
        
        style SUCCESS fill:#4caf50
        style FAILED fill:#f44336
        style PROCESSING fill:#2196f3
    end
```

## Model Relationships

```mermaid
classDiagram
    class Task {
        +UUID id
        +TaskStatus status
        +Priority priority
        +UUID input_file_id
        +UUID output_file_id
        +DocumentFormat source_format
        +DocumentFormat target_format
        +ConversionOptions options
        +int progress
        +set_processing()
        +set_completed()
        +set_failed()
    }
    
    class FileInfo {
        +UUID id
        +str filename
        +DocumentFormat format
        +int size
        +str path
        +str content_hash
        +datetime created_at
    }
    
    class ConversionOptions {
        +ConversionTheme theme
        +CodeStyle code_style
        +str page_size
        +bool include_toc
        +bool embed_images
    }
    
    class ConversionRequest {
        +UUID file_id
        +DocumentFormat source_format
        +DocumentFormat target_format
        +ConversionOptions options
        +Priority priority
    }
    
    class ConversionResponse {
        +UUID task_id
        +TaskStatus status
        +str message
        +str websocket_url
    }
    
    Task "1" --> "1" FileInfo : input_file
    Task "1" --> "0..1" FileInfo : output_file
    Task "1" --> "1" ConversionOptions : options
    ConversionRequest "1" --> "1" ConversionOptions : options
    ConversionRequest --> Task : creates
    Task --> ConversionResponse : generates
```

## Validation Pipeline

```mermaid
graph TB
    subgraph "File Upload Validation"
        FILE[File Upload]
        
        FILE --> V1{Filename<br/>Valid?}
        V1 -->|No| ERR1[Error: Invalid filename]
        V1 -->|Yes| V2{Size<br/>Valid?}
        
        V2 -->|No| ERR2[Error: File too large]
        V2 -->|Yes| V3{Format<br/>Detected?}
        
        V3 -->|No| ERR3[Error: Unknown format]
        V3 -->|Yes| V4{Content<br/>Valid?}
        
        V4 -->|No| ERR4[Error: Corrupted file]
        V4 -->|Yes| V5{Conversion<br/>Supported?}
        
        V5 -->|No| ERR5[Error: Unsupported conversion]
        V5 -->|Yes| SUCCESS[Create FileInfo & Task]
        
        style ERR1 fill:#ffebee,stroke:#c62828
        style ERR2 fill:#ffebee,stroke:#c62828
        style ERR3 fill:#ffebee,stroke:#c62828
        style ERR4 fill:#ffebee,stroke:#c62828
        style ERR5 fill:#ffebee,stroke:#c62828
        style SUCCESS fill:#e8f5e9,stroke:#2e7d32
    end
```

## Key Components

### 1. Enumerations (enums.py)

**DocumentFormat**
- Поддерживаемые форматы: MARKDOWN, PDF, HTML
- Методы нормализации для гибкого ввода
- Маппинг расширений и MIME типов

**TaskStatus**
- Жизненный цикл задачи: CREATED → QUEUED → PROCESSING → SUCCESS/FAILED
- Свойства для проверки состояния (is_final, is_active, can_cancel)

**Constants**
- Системные лимиты (MAX_FILE_SIZE: 500MB)
- Матрица конвертации
- Пути к директориям

### 2. Core Models (models.py)

**FileInfo**
- Полная информация о файле
- UUID идентификатор
- Хеш содержимого для кеширования
- Timestamps для отслеживания

**Task**
- Центральная модель для операций конвертации
- Отслеживание прогресса (0-100%)
- Связь с входным и выходным файлами
- Методы жизненного цикла

**ConversionOptions**
- Настройки конвертации
- Темы оформления
- Стили подсветки кода
- Параметры PDF

### 3. Validators (validators.py)

**FileValidator**
- Проверка размера файла (с учетом источника)
- Валидация имени файла (безопасность)
- Определение формата через magic bytes
- Проверка содержимого

**URLValidator**
- Проверка схемы (http/https)
- Блокировка локальных адресов
- Проверка приватных IP

**TextValidator**
- Валидация текстового ввода
- Проверка синтаксиса HTML/Markdown
- Защита от XSS

**ConversionValidator**
- Проверка поддержки конвертации
- Валидация опций конвертации

## Usage Examples

### Creating a Task

```python
from app.models import Task, FileInfo, ConversionOptions
from app.models.enums import DocumentFormat, ConversionTheme

# Create file info
file = FileInfo(
    filename="report.md",
    format=DocumentFormat.MARKDOWN,
    size=1024000,
    path="uploads/2024/report.md",
    content_hash="sha256:abc123",
    mime_type="text/markdown"
)

# Create task with options
task = Task(
    input_file_id=file.id,
    source_format=DocumentFormat.MARKDOWN,
    target_format=DocumentFormat.PDF,
    options=ConversionOptions(
        theme=ConversionTheme.GITHUB,
        include_toc=True
    )
)

# Process task
task.set_processing()
# ... conversion logic ...
task.set_completed(output_file_id)
```

### Validation Flow

```python
from app.models.validators import FileValidator, ConversionValidator

# Validate file
is_valid, error = FileValidator.validate_filename("document.md")
if not is_valid:
    raise ValueError(error)

# Validate conversion
is_valid, error = ConversionValidator.validate_conversion(
    DocumentFormat.MARKDOWN,
    DocumentFormat.PDF
)
if not is_valid:
    raise ValueError(error)
```

## Error Handling

```mermaid
graph TD
    subgraph "Error Code System"
        ERROR[ErrorCode Enum]
        
        ERROR --> FILE_ERR[File Errors]
        ERROR --> TASK_ERR[Task Errors]
        ERROR --> CONV_ERR[Conversion Errors]
        ERROR --> SYS_ERR[System Errors]
        
        FILE_ERR --> FTL[FILE_TOO_LARGE<br/>413]
        FILE_ERR --> FNF[FILE_NOT_FOUND<br/>404]
        
        TASK_ERR --> TNF[TASK_NOT_FOUND<br/>404]
        TASK_ERR --> TLE[TASK_LIMIT_EXCEEDED<br/>429]
        
        CONV_ERR --> CF[CONVERSION_FAILED<br/>500]
        CONV_ERR --> UC[UNSUPPORTED_CONVERSION<br/>400]
        
        SYS_ERR --> SE[STORAGE_ERROR<br/>507]
        SYS_ERR --> IE[INTERNAL_ERROR<br/>500]
    end
```

## Pydantic Features Used

### Validation
- **Field validators** - для кастомной валидации
- **AfterValidator** - для пост-обработки
- **ConfigDict** - для конфигурации моделей

### Serialization
- **model_dump()** - в словарь Python
- **model_dump_json()** - в JSON строку
- **model_validate()** - из словаря
- **model_validate_json()** - из JSON

### Schema
- **JSON Schema** - автоматическая генерация
- **Field descriptions** - документация полей
- **Examples** - примеры в схеме

## Demo Script Features

`demo_models.py` демонстрирует:

1. **Enum функциональность**
   - Нормализация форматов
   - Маппинг расширений
   - Проверка конвертации

2. **Создание моделей**
   - FileInfo с валидацией
   - Task с жизненным циклом
   - ConversionOptions

3. **Валидация**
   - Проверка имен файлов
   - Валидация размеров
   - URL проверки

4. **Сериализация**
   - В JSON и обратно
   - Генерация схемы

5. **Real-world сценарий**
   - Полный процесс конвертации
   - От загрузки до результата

## Files Created/Modified

### Created Files:
- `/backend/app/models/enums.py` - перечисления и константы
- `/backend/app/models/models.py` - основные модели данных
- `/backend/app/models/validators.py` - валидаторы
- `/demo_models.py` - демонстрационный скрипт
- `/Module_A2_Models_Documentation.md` - эта документация

### Structure:
```
backend/app/models/
├── __init__.py
├── enums.py        # 250+ lines
├── models.py       # 400+ lines
└── validators.py   # 350+ lines
```

## Integration Points

### With Module A.3 (Storage)
- Модели готовы для сохранения в хранилища
- UUID идентификаторы для связей
- Timestamps для отслеживания

### With Module B.1 (Upload API)
- Request/Response модели для endpoints
- Валидаторы для проверки входных данных
- ErrorResponse для обработки ошибок

### With Module C (Converters)
- DocumentFormat для определения конвертеров
- ConversionOptions для настроек
- Task для отслеживания процесса

## Success Metrics

✅ **Выполнено**:
- Полная система Enum с 7+ перечислениями
- 10+ Pydantic моделей с валидацией
- 4 класса валидаторов с 15+ методами
- Поддержка всех форматов (MD, PDF, HTML)
- Полная типизация с type hints
- JSON сериализация/десериализация
- Автоматическая генерация схем
- Обработка ошибок с HTTP кодами

## Next Steps

После завершения Module A.2:

1. **Module A.3**: Реализация хранилищ с использованием моделей
2. **Module B.1**: Создание API endpoints с моделями запросов/ответов
3. **Module C.1**: Использование моделей в конвертерах

## Summary

Module A.2 успешно создает полную систему моделей данных:
- ✅ Типизированные модели с Pydantic
- ✅ Валидация на всех уровнях
- ✅ Гибкая система Enum
- ✅ Поддержка сериализации
- ✅ Готовность к интеграции с API и хранилищами

Система моделей готова к использованию в следующих модулях проекта Doctor.