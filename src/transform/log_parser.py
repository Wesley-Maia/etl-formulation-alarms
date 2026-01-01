"""
Módulo de Transformação - Log Parser
Responsável por parsear e transformar logs em estruturas de dados
"""
import re
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

from config.config import TRANSFORM_CONFIG
from src.utils.logger import get_logger


class LogParser:
    """Classe para parsing e transformação de logs"""
    
    # Padrões regex para diferentes formatos de log
    PATTERN_FULL = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+\[([^\]]+)\]\s+(\S+)\s+.*'
    PATTERN_ACK = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+)\s+\[([^\]]+)\]\s+(\S+)\s+ALARM\s+is\s+acknowledged.*'
    
    def __init__(self):
        """Inicializa o LogParser"""
        self.filters = TRANSFORM_CONFIG['filters']
        self.timestamp_format = TRANSFORM_CONFIG['timestamp_format']
        self.alarm_types = TRANSFORM_CONFIG['alarm_types']
        self.logger = get_logger('etl_pipeline.transform')
        
    def determine_type(self, line: str) -> str:
        """
        Determina o tipo de alarme baseado no conteúdo
        
        Args:
            line: Linha do log
            
        Returns:
            Tipo do alarme (ACK, CFN, OK, N/A)
        """
        if 'ALARM is acknowledged' in line:
            return 'ACK'
        elif 'CFN' in line:
            return 'CFN'
        elif 'OK' in line:
            return 'OK'
        else:
            return 'N/A'
    
    def parse_line(self, line: str, source_file: str) -> Optional[Dict]:
        """
        Parseia uma linha do log
        
        Args:
            line: Linha a ser parseada
            source_file: Nome do arquivo de origem
            
        Returns:
            Dicionário com dados parseados ou None
        """
        # Verificar se a linha contém algum filtro
        if not any(filter_term in line for filter_term in self.filters):
            return None
        
        line_stripped = line.strip()
        alarm_type = self.determine_type(line_stripped)
        
        # Tentar padrão ACK primeiro
        match = re.match(self.PATTERN_ACK, line_stripped)
        if match:
            timestamp, pc_id, alarm = match.groups()
            return self._create_record(
                source_file, timestamp, pc_id, alarm, 'ACK', line_stripped
            )
        
        # Tentar padrão completo (CFN/OK)
        match = re.match(self.PATTERN_FULL, line_stripped)
        if match:
            timestamp, pc_id, alarm = match.groups()
            return self._create_record(
                source_file, timestamp, pc_id, alarm, alarm_type, line_stripped
            )
        
        return None
    
    def _create_record(self, source_file: str, timestamp: str, 
                       pc_id: str, alarm: str, alarm_type: str, 
                       original_line: str) -> Dict:
        """
        Cria um registro estruturado
        
        Args:
            source_file: Arquivo de origem
            timestamp: Timestamp da linha
            pc_id: ID do PC
            alarm: Código do alarme
            alarm_type: Tipo do alarme
            original_line: Linha original
            
        Returns:
            Dicionário com dados estruturados
        """
        try:
            dt = pd.to_datetime(timestamp, format=self.timestamp_format)
        except:
            dt = None
            self.logger.warning(f"Não foi possível parsear timestamp: {timestamp}")
        
        return {
            'arquivo_origem': source_file,
            'timestamp': timestamp,
            'datetime': dt,
            'pc_id': pc_id,
            'alarm': alarm.strip(),
            'type': alarm_type,
            'linha_original': original_line
        }
    
    def parse_file(self, lines: List[str], source_file: str) -> pd.DataFrame:
        """
        Parseia todas as linhas de um arquivo
        
        Args:
            lines: Lista de linhas do arquivo
            source_file: Nome do arquivo de origem
            
        Returns:
            DataFrame com dados parseados
        """
        records = []
        
        for line in lines:
            record = self.parse_line(line, source_file)
            if record:
                records.append(record)
        
        df = pd.DataFrame(records)
        
        self.logger.info(
            f"Arquivo {source_file}: {len(records)} registros parseados "
            f"de {len(lines)} linhas"
        )
        
        return df
    
    def parse_multiple_files(self, file_infos: List) -> pd.DataFrame:
        """
        Parseia múltiplos arquivos e consolida em um DataFrame
        
        Args:
            file_infos: Lista de FileInfo objects
            
        Returns:
            DataFrame consolidado
        """
        dataframes = []
        
        for file_info in file_infos:
            df = self.parse_file(file_info.lines, file_info.filename)
            if not df.empty:
                dataframes.append(df)
        
        if not dataframes:
            self.logger.warning("Nenhum dado foi parseado")
            return pd.DataFrame()
        
        # Consolidar todos os DataFrames
        df_consolidated = pd.concat(dataframes, ignore_index=True)
        
        # Ordenar por datetime
        if 'datetime' in df_consolidated.columns:
            df_consolidated = df_consolidated.sort_values('datetime').reset_index(drop=True)
        
        self.logger.info(
            f"Total consolidado: {len(df_consolidated)} registros de "
            f"{len(dataframes)} arquivo(s)"
        )
        
        return df_consolidated
    
    def get_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Gera estatísticas sobre os dados transformados
        
        Args:
            df: DataFrame com dados
            
        Returns:
            Dicionário com estatísticas
        """
        if df.empty:
            return {}
        
        stats = {
            'total_records': len(df),
            'unique_alarms': df['alarm'].nunique() if 'alarm' in df.columns else 0,
            'unique_pc_ids': df['pc_id'].nunique() if 'pc_id' in df.columns else 0,
            'records_by_type': df['type'].value_counts().to_dict() if 'type' in df.columns else {},
            'records_by_file': df['arquivo_origem'].value_counts().to_dict() if 'arquivo_origem' in df.columns else {},
        }
        
        if 'datetime' in df.columns and df['datetime'].notna().any():
            stats['period_start'] = df['datetime'].min()
            stats['period_end'] = df['datetime'].max()
            stats['period_days'] = (stats['period_end'] - stats['period_start']).days
        
        return stats
    
    def group_alarm_sequences(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Agrupa alarmes em sequências CFN -> ACK -> OK
        
        Args:
            df: DataFrame com dados
            
        Returns:
            DataFrame agrupado
        """
        if df.empty:
            return df
        
        # Ordenar por pc_id, alarm e datetime
        df_sorted = df.sort_values(
            ['pc_id', 'alarm', 'datetime']
        ).reset_index(drop=True)
        
        self.logger.info(f"Alarmes agrupados por sequência")
        
        return df_sorted


# Exemplo de uso e testes
if __name__ == "__main__":
    from src.extract.file_reader import FileReader
    
    print("\n" + "="*80)
    print("TESTE DO LOG PARSER")
    print("="*80)
    
    # Ler arquivos
    reader = FileReader()
    file_infos = reader.read_all_files()
    
    if file_infos:
        # Parsear arquivos
        parser = LogParser()
        df = parser.parse_multiple_files(file_infos)
        
        print(f"\nDataFrame criado: {len(df)} registros")
        print("\nPrimeiras linhas:")
        print(df.head())
        
        # Estatísticas
        stats = parser.get_statistics(df)
        print("\n" + "-"*80)
        print("ESTATÍSTICAS")
        print("-"*80)
        for key, value in stats.items():
            if key != 'records_by_file':
                print(f"{key}: {value}")
