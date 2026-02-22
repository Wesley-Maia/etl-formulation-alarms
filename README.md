# ETL - Alarmes de Formulação 🚀

Pipeline ETL profissional para análise e processamento de logs de alarmes de sistemas de formulação industrial.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Testes](#testes)
- [Análise Exploratória](#análise-exploratória)
- [Contribuindo](#contribuindo)

## 🎯 Sobre o Projeto

Este projeto implementa um pipeline ETL (Extract, Transform, Load) completo para processar logs de alarmes de sistemas industriais. O sistema é capaz de:

- ✅ Ler arquivos de log em múltiplos encodings
- ✅ Parsear e transformar dados não estruturados
- ✅ Carregar dados em banco SQLite com schema otimizado
- ✅ Gerar análises e visualizações interativas
- ✅ Rastrear histórico de execuções
- ✅ Identificar sequências de alarmes (CFN → ACK → OK)

### Tecnologias Utilizadas

- **Python 3.9+**: Linguagem principal
- **Pandas**: Manipulação de dados
- **SQLAlchemy**: ORM e gerenciamento de banco
- **SQLite**: Banco de dados relacional
- **Jupyter**: Análise exploratória
- **Matplotlib/Seaborn**: Visualizações
- **Pytest**: Testes unitários

## 🏗️ Arquitetura

O projeto segue a arquitetura clássica de ETL com separação clara de responsabilidades:

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   EXTRACT   │      │  TRANSFORM  │      │    LOAD     │
│             │─────▶│             │─────▶│             │
│ File Reader │      │ Log Parser  │      │  Database   │
└─────────────┘      └─────────────┘      └─────────────┘
```

### Fluxo de Dados

1. **Extract**: Lê arquivos .txt do diretório `logs_formulacao/`
2. **Transform**: Parseia logs e aplica regras de negócio
3. **Load**: Persiste dados no SQLite com índices otimizados

## 📦 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

## 🚀 Instalação

### 1. Clonar o Repositório

```bash
git clone git@github.com:Wesley-Maia/etl-formulation-alarms.git
cd etl-alarmes-formulacao
```

### 2. Criar Ambiente Virtual

```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verificar Instalação

```bash
python -c "import pandas; import sqlalchemy; print('✓ Instalação OK')"
```

## 💻 Uso

### Execução Básica

```bash
# Executar pipeline completo
python run_etl.py

# Limpar banco antes de carregar
python run_etl.py --clear

# Especificar diretório fonte
python run_etl.py --source /caminho/para/logs
```

### Consultas ao Banco

```bash
# Consultar alarmes tipo CFN
python run_etl.py --query --type CFN --limit 20

# Consultar por PC específico
python run_etl.py --query --pc-id PC001

# Ver histórico de execuções
python run_etl.py --history
```

### Uso Programático

```python
from src.etl_pipeline import ETLPipeline

# Criar instância do pipeline
pipeline = ETLPipeline()

# Executar ETL
success, stats = pipeline.run(clear_database=False)

# Consultar dados
df = pipeline.query_database(alarm_type='CFN', limit=100)
print(df)
```

## 📂 Estrutura do Projeto

```
etl-alarmes-formulacao/
├── src/
│   ├── extract/
│   │   ├── __init__.py
│   │   └── file_reader.py          # Leitura de arquivos
│   ├── transform/
│   │   ├── __init__.py
│   │   └── log_parser.py           # Parsing e transformação
│   ├── load/
│   │   ├── __init__.py
│   │   └── database.py             # Carga no banco
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py               # Sistema de logging
│   └── etl_pipeline.py             # Orquestrador principal
├── tests/
│   ├── test_extract.py             # Testes de extração
│   └── test_transform.py           # Testes de transformação
├── config/
│   └── config.py                   # Configurações centralizadas
├── database/
│   └── alarmes_formulacao.db       # Banco SQLite
├── logs/
│   └── etl_pipeline.log            # Logs de execução
├── logs_formulacao/                # Arquivos fonte (TXT)
├── notebooks/
│   └── 01_exploratory_analysis.ipynb
├── run_etl.py                      # Script principal
├── requirements.txt                # Dependências
└── README.md                       # Este arquivo
```

## 🧪 Testes

### Executar Todos os Testes

```bash
pytest tests/ -v
```

### Executar com Cobertura

```bash
pytest tests/ --cov=src --cov-report=html
```

### Testes Individuais

```bash
# Testar apenas extração
pytest tests/test_extract.py -v

# Testar apenas transformação
pytest tests/test_transform.py -v
```

## 📊 Análise Exploratória

### Jupyter Notebook

```bash
# Iniciar Jupyter
jupyter notebook

# Abrir notebook
# notebooks/01_exploratory_analysis.ipynb
```

O notebook inclui:
- 📈 Estatísticas descritivas
- 📊 Visualizações de distribuições
- ⏰ Análise temporal (diária, horária, semanal)
- 🔄 Identificação de sequências de alarmes
- 📁 Exportação para Excel

### Análises Disponíveis

1. **Distribuição de Alarmes**: Por tipo, PC, arquivo
2. **Padrões Temporais**: Hora do dia, dia da semana, tendências
3. **Sequências**: CFN → ACK → OK com tempos de resolução
4. **Top Alarmes**: Mais frequentes, maior tempo de resolução

## 🗄️ Banco de Dados

### Schema

**Tabela: alarm_logs**
```sql
- id (INTEGER, PK, AUTO_INCREMENT)
- arquivo_origem (STRING)
- timestamp (STRING)
- datetime (DATETIME, INDEXED)
- pc_id (STRING, INDEXED)
- alarm (STRING, INDEXED)
- type (STRING, INDEXED)
- linha_original (TEXT)
- created_at (DATETIME)
```

**Tabela: etl_statistics**
```sql
- id (INTEGER, PK)
- execution_date (DATETIME)
- total_files (INTEGER)
- total_records (INTEGER)
- cfn_count, ok_count, ack_count (INTEGER)
- period_start, period_end (DATETIME)
- execution_time_seconds (INTEGER)
- status (STRING)
```

### Índices Otimizados

- `idx_pc_alarm`: (pc_id, alarm)
- `idx_type_datetime`: (type, datetime)
- `idx_arquivo_datetime`: (arquivo_origem, datetime)

## 🔄 Workflow Git

### Branches

- `main`: Produção (estável)
- `develop`: Desenvolvimento
- `feature/*`: Novas funcionalidades
- `bugfix/*`: Correções de bugs
- `hotfix/*`: Correções urgentes

### 📝 Histórico de Commits

```bash
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Alterações em documentação
- `style:` - Formatação, ponto e vírgula faltando, etc
- `refactor:` - Refatoração de código
- `chore:` - Atualização de tarefas, configurações, etc
```

## 📝 Logs

Logs são salvos em `logs/etl_pipeline.log` com níveis:
- **DEBUG**: Detalhes de operações
- **INFO**: Progresso do pipeline
- **WARNING**: Avisos
- **ERROR**: Erros

## 🎯 Roadmap

- [x] Pipeline ETL básico
- [x] Testes unitários
- [x] Análise exploratória
- [ ] Dashboard interativo com Streamlit
- [ ] Alertas automáticos
- [ ] API REST
- [ ] Dockerização
- [ ] CI/CD com GitHub Actions

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Autores

- Wesley Oliveira Maia - Desenvolvedor Principal

## 📞 Contato

- Email: maia.weol@gmail.com
- LinkedIn: [seu-perfil](https://www.linkedin.com/in/wesley-om/)

---

⭐ Se este projeto foi útil, considere dar uma estrela!