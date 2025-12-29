"""
Configurações do Projeto ETL - Alarmes de Formulação
"""
import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
LOGS_DIR = BASE_DIR / "logs"
DATABASE_DIR = BASE_DIR / "database"
DATA_DIR = BASE_DIR / "logs_formulation"

# Configurações de Database
DATABASE_CONFIG = {
    'database_name': 'alarmes_formulacao.db',
    'database_path': DATABASE_DIR / 'alarmes_formulacao.db',
    'echo': False  # SQLAlchemy echo (verbose)
}

# Configurações de Extração
EXTRACT_CONFIG = {
    'source_directory': DATA_DIR,
    'file_extension': '.log',
    'encodings_to_try': ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252', 'cp850'],
    'recursive_search': False
}

# Configurações de Transformação
TRANSFORM_CONFIG = {
    'filters': ['CFN', 'OK', 'acknowledged'],
    'timestamp_format': '%Y-%m-%d %H:%M:%S,%f',
    'alarm_types': {
        'ACK': 'acknowledged',
        'CFN': 'CFN',
        'OK': 'OK'
    }
}

# Configurações de Log
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': LOGS_DIR / 'etl_pipeline.log',
            'mode': 'a',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'etl_pipeline': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}

# Configurações de Performance
PERFORMANCE_CONFIG = {
    'batch_size': 1000,
    'max_workers': 4,
    'chunk_size': 10000
}

# Criar diretórios se não existirem
for directory in [LOGS_DIR, DATABASE_DIR, DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
