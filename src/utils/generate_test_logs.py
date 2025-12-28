"""
Gerador de logs de teste para sistema de formulação
"""
import random
from datetime import datetime, timedelta
from pathlib import Path


# Componentes do sistema de Formulação
COMPONENTES_FORMULACAO = [
    "PC510A00", "PC510A01", "PC520A00", "PC520A01", "PC530A00"
]

OPERADORES = ["FORM", "DOSM", "MIXR", "PREP", "CTRL", "QUAL"]

# Códigos de alarmes do sistema de Formulação
ALARMES_FORMULACAO = [
    {"code": "FMDOS01", "desc": "Erro dosagem ingrediente principal"},
    {"code": "FMTMP01", "desc": "Temperatura fora de especificação"},
    {"code": "FMPRS01", "desc": "Pressão do sistema inadequada"},
    {"code": "FMMIX01", "desc": "Erro misturador batch"},
    {"code": "FMTNK01", "desc": "Nível baixo tanque ingrediente A"},
    {"code": "FMTNK02", "desc": "Nível baixo tanque ingrediente B"},
    {"code": "FMVLV01", "desc": "Erro válvula dosadora"},
    {"code": "FMBMP01", "desc": "Erro bomba de transferência"},
    {"code": "FMPH001", "desc": "pH fora de especificação"},
    {"code": "FMVSC01", "desc": "Viscosidade fora de especificação"},
    {"code": "FMAGT01", "desc": "Erro agitador principal"},
    {"code": "FMSNS01", "desc": "Falha sensor de temperatura"},
    {"code": "FMSNS02", "desc": "Falha sensor de pressão"},
    {"code": "FMPES01", "desc": "Erro pesagem ingrediente"},
    {"code": "FMTIM01", "desc": "Tempo de mistura excedido"},
    {"code": "FMHEAT1", "desc": "Erro sistema de aquecimento"},
    {"code": "FMCOOL1", "desc": "Erro sistema de resfriamento"},
    {"code": "FMCONT1", "desc": "Contaminação detectada"},
    {"code": "FMFLT01", "desc": "Erro filtro de linha"},
    {"code": "FMDOS02", "desc": "Erro bomba dosadora"},
]

# Tags do sistema de Formulação
TAGS_FORMULACAO = [
    "IX_BATCH_LOGDATA_1A.A_CV",
    "IX_BATCH_LOGDATA_1B.A_CV",
    "IX_BATCH_LOGDATA_1C.A_CV",
    "IX_BATCH_LOGDATA_1D.A_CV",
    "IX_BATCH_LOGDATA_01.F_CV",
    "IX_BATCH_LOGDATA_03.F_CV",
    "IX_BATCH_START_INIT.A_CV",
    "IX_BATCH_START_TID.A_CV",
    "IX_BATCH_STOP_TID.A_CV",
    "IX_BATCHNR.A_CV",
    "IX_VARE_NR.A_CV",
    "IX_TEMP_SETPOINT.F_CV",
    "IX_PRESS_ACTUAL.F_CV",
    "IX_DOSE_WEIGHT.F_CV",
    "IX_MIX_SPEED.F_CV",
    "IX_OPERAT1.A_DESC",
    "IX_OPERAT2.A_DESC",
    "IX_OPERNAVN1.A_DESC",
    "IX_OPERNAVN2.A_DESC",
    "IX_ANTALOPE.F_CV",
]

BATCH_PRODUTOS = [
    "Insulin Aspart FormBase 100",
    "Insulin Detemir FormMix 200",
    "Insulin Degludec FormPlus 150",
    "Biphasic Insulin FormStd 75",
    "Insulin Glargine FormAdv 125",
]


def _get_default_output_path():
    """Retorna o caminho padrão de saída (logs_formulation na raiz)"""
    script_dir = Path(__file__).parent      # src/utils/
    src_dir = script_dir.parent             # src/
    project_root = src_dir.parent           # raiz
    return project_root / "logs_formulation"


def gerar_timestamp(data_base, hora, minuto, segundo, ms):
    """Gera timestamp formatado"""
    return f"{data_base.strftime('%Y-%m-%d')} {hora:02d}:{minuto:02d}:{segundo:02d},{ms}"


def incrementar_tempo(hora, minuto, segundo, incremento_seg=None):
    """Incrementa o tempo de forma realista"""
    if incremento_seg is None:
        incremento_seg = random.randint(1, 30)

    segundo += incremento_seg
    if segundo >= 60:
        segundo -= 60
        minuto += 1
    if minuto >= 60:
        minuto = 0
        hora += 1
    if hora >= 24:
        hora = 0

    return hora, minuto, segundo


def gerar_log_batch(data_base, hora, minuto, segundo, ms, componente_pc, 
                    componente_dest, operador, tag_suffix, valor):
    """Gera uma linha de log de batch"""
    timestamp = gerar_timestamp(data_base, hora, minuto, segundo, ms)
    return f"{timestamp} [{componente_pc}] Pix32.{componente_pc}.{tag_suffix} set to {valor} by {componente_dest}::{operador}"


def gerar_sequencia_alarme(data_base, hora_inicial, minuto_inicial, segundo_inicial, 
                           alarme_info, operador, componente_pc, componente_dest):
    """
    Gera uma sequência completa de alarme: CFN → ACK → OK
    """
    sequencia = []
    hora, minuto, segundo = hora_inicial, minuto_inicial, segundo_inicial

    # 1. ALARME INICIAL (CFN ou ALARM)
    ms = random.randint(0, 9)
    tipo_inicial = random.choice(["CFN", "ALARM"])
    timestamp = gerar_timestamp(data_base, hora, minuto, segundo, ms)
    sequencia.append(
        f"{timestamp} [{componente_pc}] {alarme_info['code']:<30} "
        f"{tipo_inicial:<15} {'ALARM':<10} {alarme_info['desc']}"
    )

    # 2. MSG (opcional, 60% das vezes)
    if random.random() < 0.6:
        hora, minuto, segundo = incrementar_tempo(hora, minuto, segundo, random.randint(1, 5))
        ms = random.randint(0, 9)
        timestamp = gerar_timestamp(data_base, hora, minuto, segundo, ms)
        sequencia.append(
            f"{timestamp} [{componente_pc}] {alarme_info['code']:<30} "
            f"{'CFN':<15} {'MSG.':<10} {alarme_info['desc']}"
        )

    # 3. ACKNOWLEDGMENT (ACK)
    hora, minuto, segundo = incrementar_tempo(hora, minuto, segundo, random.randint(5, 120))
    ms = random.randint(0, 9)
    timestamp = gerar_timestamp(data_base, hora, minuto, segundo, ms)
    sequencia.append(
        f"{timestamp} [{componente_pc}] {alarme_info['code']} "
        f"ALARM is acknowledged by {componente_dest}::{operador:<30} ACK"
    )

    # 4. Logs de batch relacionados ao ACK (sequência padronizada)
    batch_logs = [
        ("IX_BATCH_LOGDATA_01.F_CV", "250"),
        ("IX_BATCH_LOGDATA_1A.A_CV", "EVENT"),
        ("IX_BATCH_LOGDATA_1B.A_CV", operador),
        ("IX_BATCH_LOGDATA_1C.A_CV", "Reconhecido alm./msg. selecionado:"),
        ("IX_BATCH_LOGDATA_1D.A_CV", ""),
        ("IX_BATCH_LOGDATA_01.F_CV", "2"),
    ]
    
    for tag_suffix, valor in batch_logs:
        hora, minuto, segundo = incrementar_tempo(hora, minuto, segundo, 1)
        ms = random.randint(0, 9)
        # Ajustar operador para 1C (apenas 3 primeiros caracteres)
        op_usado = operador[:3] if "1C" in tag_suffix else operador
        sequencia.append(gerar_log_batch(
            data_base, hora, minuto, segundo, ms, 
            componente_pc, componente_dest, op_usado, tag_suffix, valor
        ))

    # 5. RESOLUÇÃO (OK)
    hora, minuto, segundo = incrementar_tempo(hora, minuto, segundo, random.randint(30, 300))
    ms = random.randint(0, 9)
    timestamp = gerar_timestamp(data_base, hora, minuto, segundo, ms)
    sequencia.append(
        f"{timestamp} [{componente_pc}] {alarme_info['code']:<30} "
        f"{'OK':<15} {'A_OK':<10} {alarme_info['desc']}"
    )

    return sequencia, hora, minuto, segundo


def gerar_valor_tag(tag, operador, data_base, hora, minuto, segundo, ms):
    """Gera valor apropriado baseado no tipo de tag"""
    if "F_CV" in tag:
        return f"{random.uniform(0, 250):.1f}"
    elif "BATCHNR" in tag:
        return f"FORM{random.randint(1000, 9999)}BT{random.randint(10, 99)}"
    elif "VARE_NR" in tag:
        return random.choice(BATCH_PRODUTOS)
    elif "1A.A_CV" in tag:
        return random.choice(["EVENT", "COUNTERSTAT", "ANNOUNCE"])
    elif "1B.A_CV" in tag:
        return operador
    elif "1C.A_CV" in tag:
        return random.choice([a['desc'] for a in ALARMES_FORMULACAO])[:40]
    elif "1D.A_CV" in tag:
        return random.choice(["Ativo", "Inativo", ""])
    elif "TID" in tag:
        return gerar_timestamp(data_base, hora, minuto, segundo, ms)
    elif "DESC" in tag:
        return operador
    else:
        return str(random.randint(0, 2))


def gerar_linha_log_normal(data_base, hora, minuto, segundo, ms, 
                           componente, tag, operador):
    """Gera uma linha de log normal"""
    timestamp = gerar_timestamp(data_base, hora, minuto, segundo, ms)
    valor = gerar_valor_tag(tag, operador, data_base, hora, minuto, segundo, ms)
    return f"{timestamp} [{componente}] Pix32.{componente}.{tag} set to {valor} by {componente}::{operador}"


def gerar_watchdog(data_base, hora, minuto, segundo, ms, componente):
    """Gera linha de watchdog"""
    timestamp = gerar_timestamp(data_base, hora, minuto, segundo, ms)
    return f"{timestamp} [{componente}] -2147220484: FORM_Background_Schedule_WDG by {componente}"


def gerar_arquivo_log(data):
    """Gera um arquivo de log completo para uma data"""
    linhas = []
    
    # Horário inicial
    hora_atual = random.randint(6, 8)
    minuto_atual = random.randint(0, 59)
    segundo_atual = random.randint(0, 59)

    # Gerar sequências de alarmes
    num_alarmes = random.randint(15, 35)
    
    for _ in range(num_alarmes):
        # Gerar alarme
        alarme_info = random.choice(ALARMES_FORMULACAO)
        operador = random.choice(OPERADORES)
        componente_pc = random.choice(COMPONENTES_FORMULACAO)
        componente_dest = random.choice([c for c in COMPONENTES_FORMULACAO if c != componente_pc])

        sequencia_alarme, hora_atual, minuto_atual, segundo_atual = gerar_sequencia_alarme(
            data, hora_atual, minuto_atual, segundo_atual, 
            alarme_info, operador, componente_pc, componente_dest
        )
        
        linhas.extend(sequencia_alarme)

        # Adicionar logs normais entre alarmes
        num_logs_intermediarios = random.randint(5, 15)
        
        for _ in range(num_logs_intermediarios):
            hora_atual, minuto_atual, segundo_atual = incrementar_tempo(
                hora_atual, minuto_atual, segundo_atual, random.randint(15, 45)
            )
            ms = random.randint(0, 9)
            componente = random.choice(COMPONENTES_FORMULACAO)

            # 70% logs normais, 30% watchdog
            if random.random() < 0.7:
                tag = random.choice(TAGS_FORMULACAO)
                operador = random.choice(OPERADORES)
                linhas.append(gerar_linha_log_normal(
                    data, hora_atual, minuto_atual, segundo_atual, ms,
                    componente, tag, operador
                ))
            else:
                linhas.append(gerar_watchdog(
                    data, hora_atual, minuto_atual, segundo_atual, ms, componente
                ))

    return linhas


def gerar_logs_teste(num_arquivos=30, data_inicial=None, pasta_saida=None):
    """
    Gera arquivos de log de teste para o sistema de formulação
    
    Args:
        num_arquivos: Número de arquivos a gerar (default: 30)
        data_inicial: Data inicial (datetime, default: 2025-10-05)
        pasta_saida: Caminho da pasta de saída (Path ou str, default: logs_formulation/)
    """
    # Configurações padrão
    if data_inicial is None:
        data_inicial = datetime(2025, 10, 5)
    
    if pasta_saida is None:
        pasta_saida = _get_default_output_path()
    else:
        pasta_saida = Path(pasta_saida)
    
    # Criar pasta de saída
    pasta_saida.mkdir(exist_ok=True)
    
    # Header
    print("=" * 80)
    print("LOG GENERATOR - FORMULARION SYSTEM")
    print("=" * 80)
    print(f"Start Date: {data_inicial.strftime('%Y-%m-%d')}")
    print(f"Total files: {num_arquivos}")
    print(f"Output folder: {pasta_saida}")
    print("=" * 80)
    print()

    # Gerar arquivos
    for i in range(num_arquivos):
        data_arquivo = data_inicial + timedelta(days=i)
        nome_arquivo = data_arquivo.strftime("%Y-%m-%d") + "_formulation.log"
        caminho_arquivo = pasta_saida / nome_arquivo

        print(f"[{i + 1:2d}/{num_arquivos}] Generating: {nome_arquivo}")

        linhas_log = gerar_arquivo_log(data_arquivo)

        # Salvar arquivo
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write('\n'.join(linhas_log))

        print(f"         ✓ {len(linhas_log)} generated events")

    # Footer
    print()
    print("=" * 80)
    print(f"✅ Completed! {num_arquivos} files generated successfully!")
    print(f"📁 File location: {pasta_saida}")
    print("=" * 80)


if __name__ == "__main__":
    gerar_logs_teste()
