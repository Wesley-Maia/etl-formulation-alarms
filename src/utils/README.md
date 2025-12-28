# 🏭 Gerador de Logs - Sistema de Formulação

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Descrição

Sistema para geração de datasets sintéticos de logs de alarmes de equipamentos de **Formulação** em ambientes farmacêuticos. O script gera dados realistas simulando sequências completas de alarmes (CFN → ACK → OK), logs de batch e eventos de watchdog, distribuídos ao longo de múltiplos dias.

## 🎯 Objetivo

Criar dados de teste para pipeline ETL de análise de alarmes industriais, permitindo:

- **Desenvolvimento e teste de pipelines ETL** (Extract, Transform, Load)
- **Análise de padrões de reconhecimento e resolução** de alarmes
- **Identificação de tendências** por turno, componente ou tipo de alarme
- **Desenvolvimento e teste de dashboards** de monitoramento
- **Validação de sistemas** de rastreamento de alarmes

## 🚀 Funcionalidades

### Geração de Logs Multi-Dias
- ✅ Suporta geração de dados para intervalos de dias personalizados (padrão: 30 dias)
- ✅ Aproximadamente 15-35 alarmes por dia
- ✅ Distribuição temporal realista ao longo das 24 horas
- ✅ Múltiplos componentes PC (5 equipamentos)

### Tipos de Registros

#### 1️⃣ Sequência Completa de Alarmes
Cada alarme segue o ciclo operacional real:

```
CFN/ALARM → MSG (opcional) → ACK → Logs Batch → OK
```

| Fase | Descrição | Tempo |
|------|-----------|-------|
| **CFN** | Confirmação do alarme | Inicial |
| **MSG** | Mensagem adicional (60% dos casos) | +1-5s |
| **ACK** | Reconhecimento pelo operador | +5-120s |
| **Batch Logs** | Registros de operação (6 logs) | +1s cada |
| **OK** | Resolução do alarme | +30-300s |

#### 2️⃣ Tipos de Alarmes (20 categorias)

| Código | Descrição | Categoria |
|--------|-----------|-----------|
| `FMDOS01` | Erro dosagem ingrediente principal | Dosagem |
| `FMTMP01` | Temperatura fora de especificação | Processo |
| `FMPRS01` | Pressão do sistema inadequada | Processo |
| `FMMIX01` | Erro misturador batch | Mecânico |
| `FMTNK01` | Nível baixo tanque ingrediente A | Tanque |
| `FMTNK02` | Nível baixo tanque ingrediente B | Tanque |
| `FMVLV01` | Erro válvula dosadora | Mecânico |
| `FMBMP01` | Erro bomba de transferência | Mecânico |
| `FMPH001` | pH fora de especificação | Qualidade |
| `FMVSC01` | Viscosidade fora de especificação | Qualidade |
| `FMAGT01` | Erro agitador principal | Mecânico |
| `FMSNS01` | Falha sensor de temperatura | Sensor |
| `FMSNS02` | Falha sensor de pressão | Sensor |
| `FMPES01` | Erro pesagem ingrediente | Dosagem |
| `FMTIM01` | Tempo de mistura excedido | Processo |
| `FMHEAT1` | Erro sistema de aquecimento | HVAC |
| `FMCOOL1` | Erro sistema de resfriamento | HVAC |
| `FMCONT1` | Contaminação detectada | Qualidade |
| `FMFLT01` | Erro filtro de linha | Mecânico |
| `FMDOS02` | Erro bomba dosadora | Dosagem |

### Componentes do Sistema

| PC ID | Descrição |
|-------|-----------|
| `PC510A00` | Controlador Formulação 1 |
| `PC510A01` | Controlador Formulação 2 |
| `PC520A00` | Controlador Dosagem 1 |
| `PC520A01` | Controlador Dosagem 2 |
| `PC530A00` | Controlador Mistura |

### Operadores

| Código | Função |
|--------|--------|
| `FORM` | Formulador |
| `DOSM` | Dosimetrista |
| `MIXR` | Operador de Mistura |
| `PREP` | Preparador |
| `CTRL` | Controlista |
| `QUAL` | Qualidade |

### Turnos de Trabalho

| Turno | Horário |
|-------|---------|
| **Manhã** | 06:00 - 14:00 |
| **Tarde** | 14:00 - 22:00 |
| **Noite** | 22:00 - 06:00 |

## 📦 Dependências

```bash
pip install pathlib
```

### Bibliotecas Utilizadas

- `pathlib`: Manipulação de caminhos de arquivos
- `datetime`: Manipulação de datas e horas
- `random`: Geração de números aleatórios
- `os` (opcional): Operações de sistema

## 💻 Como Usar

### Exemplo Básico

```python
from src.utils import gerar_logs_teste

# Gerar 30 arquivos (padrão)
gerar_logs_teste()

# Gerar 10 arquivos
gerar_logs_teste(num_arquivos=10)

# Customizar data inicial
from datetime import datetime
gerar_logs_teste(num_arquivos=15, data_inicial=datetime(2025, 11, 1))

# Customizar pasta de saída
gerar_logs_teste(pasta_saida="meus_logs")
```

### Executar via Script Wrapper

```bash
# Da raiz do projeto
python generate_logs.py
```

### Executar Diretamente

```bash
# Como módulo Python
python -m src.utils.generate_test_logs

# Ou diretamente
cd src/utils
python generate_test_logs.py
```

## 📊 Estrutura dos Dados Gerados

### Formato dos Logs

Cada linha segue o padrão:

```
YYYY-MM-DD HH:MM:SS,ms [PC_ID] ALARM_CODE STATUS MESSAGE DESCRIPTION
```

#### Exemplo de Sequência Completa:

```
2025-10-05 08:15:30,5 [PC510A00] FMDOS01                        CFN            ALARM      Erro dosagem ingrediente principal
2025-10-05 08:15:35,2 [PC510A00] FMDOS01                        CFN            MSG.       Erro dosagem ingrediente principal
2025-10-05 08:17:22,8 [PC510A00] FMDOS01 ALARM is acknowledged by PC520A00::FORM                              ACK
2025-10-05 08:17:23,3 [PC510A00] Pix32.PC510A00.IX_BATCH_LOGDATA_01.F_CV set to 250 by PC520A00::FORM
2025-10-05 08:17:24,1 [PC510A00] Pix32.PC510A00.IX_BATCH_LOGDATA_1A.A_CV set to EVENT by PC520A00::FORM
2025-10-05 08:17:25,4 [PC510A00] Pix32.PC510A00.IX_BATCH_LOGDATA_1B.A_CV set to FORM by PC520A00::FORM
2025-10-05 08:17:26,7 [PC510A00] Pix32.PC510A00.IX_BATCH_LOGDATA_1C.A_CV set to Reconhecido alm./msg. selecionado: by PC520A00::FOR
2025-10-05 08:17:27,9 [PC510A00] Pix32.PC510A00.IX_BATCH_LOGDATA_1D.A_CV set to  by PC520A00::FORM
2025-10-05 08:17:29,2 [PC510A00] Pix32.PC510A00.IX_BATCH_LOGDATA_01.F_CV set to 2 by PC520A00::FORM
2025-10-05 08:22:15,6 [PC510A00] FMDOS01                        OK             A_OK       Erro dosagem ingrediente principal
```

### Tipos de Registros

| Tipo | Formato | Frequência |
|------|---------|------------|
| **Alarme (CFN)** | `[PC] CODE CFN ALARM DESC` | 15-35/dia |
| **Reconhecimento (ACK)** | `[PC] CODE ALARM is acknowledged by PC::OP ACK` | 1 por alarme |
| **Resolução (OK)** | `[PC] CODE OK A_OK DESC` | 1 por alarme |
| **Batch Log** | `[PC] Pix32.PC.TAG set to VALUE by PC::OP` | 6 por ACK |
| **Watchdog** | `[PC] -2147220484: FORM_Background_Schedule_WDG by PC` | 30% dos intermediários |
| **Log Normal** | `[PC] Pix32.PC.TAG set to VALUE by PC::OP` | 70% dos intermediários |

### Tags de Batch Principais

| Tag | Descrição | Valores |
|-----|-----------|---------|
| `IX_BATCH_LOGDATA_01.F_CV` | Código de status | 250, 2 |
| `IX_BATCH_LOGDATA_1A.A_CV` | Tipo de evento | EVENT, COUNTERSTAT, ANNOUNCE |
| `IX_BATCH_LOGDATA_1B.A_CV` | Operador | FORM, DOSM, MIXR, etc. |
| `IX_BATCH_LOGDATA_1C.A_CV` | Descrição do reconhecimento | Texto |
| `IX_BATCH_LOGDATA_1D.A_CV` | Status adicional | Ativo, Inativo, "" |
| `IX_BATCHNR.A_CV` | Número do batch | FORM####BT## |
| `IX_VARE_NR.A_CV` | Produto | Insulin Aspart FormBase 100, etc. |

## 🔧 Características Técnicas

### Reprodutibilidade
```python
random.seed(42)  # Opcional - descomente para resultados consistentes
```

### Distribuição Temporal Realista
- Horários de início variam entre 06:00 e 08:00
- Incrementos temporais variáveis (1-30s entre eventos)
- Tempos de resposta realistas (5-120s para ACK, 30-300s para OK)

### Validação Automática
- Criação automática de diretórios de saída
- Cálculo correto de caminhos relativos
- Encoding UTF-8 para caracteres especiais

## 📈 Exemplos de Análises (Após ETL)

### Alarmes por Tipo
```python
df.groupby('alarm')['id'].count().sort_values(ascending=False).head(10)
```

### Taxa de Reconhecimento
```python
total_cfn = len(df[df['type'] == 'CFN'])
total_ack = len(df[df['type'] == 'ACK'])
taxa = (total_ack / total_cfn) * 100
```

### Alarmes por Turno
```python
df.groupby('turno')['type'].value_counts()
```

### Tempo Médio de Resolução
```python
# Requer processamento adicional para calcular delta entre CFN e OK
```

## 📁 Estrutura de Arquivos Gerados

```
logs_formulation/
├── 2025-10-05_formulacao.log
├── 2025-10-06_formulacao.log
├── 2025-10-07_formulacao.log
├── ...
└── 2025-11-03_formulacao.log
```

### Características dos Arquivos
- **Nome**: `YYYY-MM-DD_formulacao.log`
- **Encoding**: UTF-8
- **Tamanho médio**: ~50-150 KB por arquivo
- **Linhas**: ~150-400 linhas por arquivo
- **Formato**: Plain text (processável por ETL)

## ⚙️ Parâmetros Configuráveis

### Na Função `gerar_logs_teste()`

```python
gerar_logs_teste(
    num_arquivos=30,                        # Número de dias
    data_inicial=datetime(2025, 10, 5),    # Data de início
    pasta_saida=Path("logs_formulation")   # Pasta de saída
)
```

### No Código Fonte

```python
# Número de alarmes por dia
num_alarmes = random.randint(15, 35)

# Proporção watchdog vs normal
if random.random() < 0.7:  # 70% normal, 30% watchdog
```

## 🎓 Conceitos Aplicados

- ✅ **Geração de dados sintéticos**: Criação de datasets realistas para testes
- ✅ **Simulação de processos industriais**: Sequências CFN→ACK→OK
- ✅ **Manipulação de timestamps**: datetime e timedelta
- ✅ **Organização de código**: Funções modulares e reutilizáveis
- ✅ **Caminhos relativos**: Uso de pathlib para portabilidade
- ✅ **Encoding**: Suporte a caracteres especiais (UTF-8)

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'src'"
```bash
# Execute da raiz do projeto
python -m src.utils.generate_test_logs
```

### Erro: "Permission denied"
- Verifique permissões da pasta `logs_formulation/`
- Certifique-se de que nenhum arquivo está aberto

### Logs não aparecem
- Verifique se a função foi executada corretamente
- Confirme o caminho de saída com `print(PASTA_SAIDA)`

### Timestamps fora de ordem
- Os timestamps são gerados sequencialmente - não deve ocorrer
- Se ocorrer, verifique a função `incrementar_tempo()`

## 📝 Notas Importantes

⚠️ **Os dados são completamente sintéticos** e não representam alarmes reais de produção.

⚠️ **Para uso em produção**, ajuste:
- Frequência de alarmes conforme histórico real
- Tipos de alarmes específicos do seu equipamento
- Tempos de resposta baseados em SLAs reais
- Produtos e operadores reais da planta

✅ **Ideal para**:
- Desenvolvimento de pipelines ETL
- Testes de dashboards
- Treinamento de equipes
- Validação de sistemas de alarmes

## 🔄 Roadmap / Melhorias Futuras

- [ ] Adicionar sazonalidade e padrões por dia da semana
- [ ] Incluir correlação entre tipos de alarmes
- [ ] Adicionar diferentes equipamentos e linhas de produção
- [ ] Gerar também arquivos `.alm` (formato alternativo)
- [ ] Exportação para múltiplos formatos (CSV, JSON)
- [ ] Interface CLI com argumentos de linha de comando
- [ ] Configuração via arquivo YAML/JSON
- [ ] Geração de alarmes recorrentes (equipment health trends)

## 🔗 Integração com Pipeline ETL

Este gerador faz parte de um sistema ETL completo:

```
generate_test_logs.py → logs_formulation/ → ETL Pipeline → SQLite → Análises/Dashboards
```

Para processar os logs gerados:

```bash
# 1. Gerar logs
python generate_logs.py

# 2. Executar ETL
python run_etl.py

# 3. Analisar dados
jupyter notebook  # notebooks/exploratory/01_data_exploration.ipynb
```

## 👤 Autor

Desenvolvido para suporte a projetos de **Data Engineering** e **análise de dados industriais** em ambientes farmacêuticos.

## 📄 Licença

Este projeto é de código aberto para fins educacionais e de análise.

---

## 📚 Documentação Adicional

- [Tutorial Completo do Projeto ETL](../docs/ARCHITECTURE.md)
- [Schema do Banco de Dados](../docs/DATABASE_SCHEMA.md)
- [Guia de Contribuição](../CONTRIBUTING.md)

---

**🎯 Pronto para usar!** Execute `python generate_logs.py` e comece a testar seu pipeline ETL.
