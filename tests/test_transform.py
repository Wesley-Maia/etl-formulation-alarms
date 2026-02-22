"""
Testes Unitários para o Módulo de Transformação
"""
import pytest
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transform.log_parser import LogParser


class TestLogParser:
    """Testes para a classe LogParser"""
    
    @pytest.fixture
    def parser(self):
        """Cria instância do parser"""
        return LogParser()
    
    @pytest.fixture
    def sample_lines(self):
        """Linhas de exemplo para teste"""
        return [
            "2024-01-01 10:00:00,000 [PC001] ALARM_001 CFN test message",
            "2024-01-01 10:05:00,000 [PC001] ALARM_001 ALARM is acknowledged by user",
            "2024-01-01 10:10:00,000 [PC001] ALARM_001 OK alarm cleared",
            "2024-01-01 11:00:00,000 [PC002] ALARM_002 CFN another alarm",
            "This line should not be parsed",
            "2024-01-01 12:00:00,000 [PC003] ALARM_003 N/A unknown type"
        ]
    
    def test_parser_initialization(self, parser):
        """Testa inicialização do parser"""
        assert parser is not None
        assert len(parser.filters) > 0
        assert 'CFN' in parser.filters
        assert 'OK' in parser.filters
        assert 'acknowledged' in parser.filters
    
    def test_determine_type_cfn(self, parser):
        """Testa determinação de tipo CFN"""
        line = "2024-01-01 10:00:00,000 [PC001] ALARM_001 CFN test"
        alarm_type = parser.determine_type(line)
        assert alarm_type == 'CFN'
    
    def test_determine_type_ok(self, parser):
        """Testa determinação de tipo OK"""
        line = "2024-01-01 10:00:00,000 [PC001] ALARM_001 OK test"
        alarm_type = parser.determine_type(line)
        assert alarm_type == 'OK'
    
    def test_determine_type_ack(self, parser):
        """Testa determinação de tipo ACK"""
        line = "2024-01-01 10:00:00,000 [PC001] ALARM_001 ALARM is acknowledged"
        alarm_type = parser.determine_type(line)
        assert alarm_type == 'ACK'
    
    def test_determine_type_unknown(self, parser):
        """Testa determinação de tipo desconhecido"""
        line = "2024-01-01 10:00:00,000 [PC001] ALARM_001 UNKNOWN test"
        alarm_type = parser.determine_type(line)
        assert alarm_type == 'N/A'
    
    def test_parse_line_cfn(self, parser):
        """Testa parsing de linha CFN"""
        line = "2024-01-01 10:00:00,000 [PC001] ALARM_001 CFN test"
        record = parser.parse_line(line, "test_file.txt")
        
        assert record is not None
        assert record['arquivo_origem'] == "test_file.txt"
        assert record['pc_id'] == 'PC001'
        assert record['alarm'] == 'ALARM_001'
        assert record['type'] == 'CFN'
        assert isinstance(record['datetime'], pd.Timestamp)
    
    def test_parse_line_ack(self, parser):
        """Testa parsing de linha ACK"""
        line = "2024-01-01 10:00:00,000 [PC001] ALARM_001 ALARM is acknowledged"
        record = parser.parse_line(line, "test_file.txt")
        
        assert record is not None
        assert record['type'] == 'ACK'
        assert record['pc_id'] == 'PC001'
    
    def test_parse_line_invalid(self, parser):
        """Testa parsing de linha inválida"""
        line = "This is not a valid log line"
        record = parser.parse_line(line, "test_file.txt")
        
        assert record is None
    
    def test_parse_file(self, parser, sample_lines):
        """Testa parsing de arquivo completo"""
        df = parser.parse_file(sample_lines, "test_file.txt")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'arquivo_origem' in df.columns
        assert 'pc_id' in df.columns
        assert 'alarm' in df.columns
        assert 'type' in df.columns
        
        # Verificar tipos específicos
        assert 'CFN' in df['type'].values
        assert 'OK' in df['type'].values
        assert 'ACK' in df['type'].values
    
    def test_parse_empty_file(self, parser):
        """Testa parsing de arquivo vazio"""
        df = parser.parse_file([], "empty_file.txt")
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
    
    def test_get_statistics(self, parser, sample_lines):
        """Testa geração de estatísticas"""
        df = parser.parse_file(sample_lines, "test_file.txt")
        stats = parser.get_statistics(df)
        
        assert 'total_records' in stats
        assert stats['total_records'] == len(df)
        assert 'unique_alarms' in stats
        assert 'unique_pc_ids' in stats
        assert 'records_by_type' in stats
    
    def test_get_statistics_empty(self, parser):
        """Testa estatísticas com DataFrame vazio"""
        df = pd.DataFrame()
        stats = parser.get_statistics(df)
        
        assert stats == {}
    
    def test_group_alarm_sequences(self, parser, sample_lines):
        """Testa agrupamento de sequências"""
        df = parser.parse_file(sample_lines, "test_file.txt")
        df_grouped = parser.group_alarm_sequences(df)
        
        assert isinstance(df_grouped, pd.DataFrame)
        assert len(df_grouped) == len(df)
        
        # Verificar ordenação
        if len(df_grouped) > 1:
            for i in range(len(df_grouped) - 1):
                current_pc = df_grouped.iloc[i]['pc_id']
                current_alarm = df_grouped.iloc[i]['alarm']
                next_pc = df_grouped.iloc[i + 1]['pc_id']
                next_alarm = df_grouped.iloc[i + 1]['alarm']
                
                # Deve estar ordenado por pc_id e alarm
                assert (current_pc < next_pc) or \
                       (current_pc == next_pc and current_alarm <= next_alarm)
    
    def test_parse_line_with_special_characters(self, parser):
        """Testa parsing com caracteres especiais"""
        line = "2024-01-01 10:00:00,000 [PC-001] ALARM_ÁÉÍ CFN test with special chars"
        record = parser.parse_line(line, "test_file.txt")
        
        # Pode retornar None se o padrão não suportar, mas não deve gerar exceção
        assert record is None or isinstance(record, dict)
    
    def test_timestamp_parsing(self, parser):
        """Testa parsing de diferentes formatos de timestamp"""
        valid_line = "2024-01-01 10:00:00,123 [PC001] ALARM_001 CFN test"
        record = parser.parse_line(valid_line, "test.txt")
        
        assert record is not None
        assert record['timestamp'] == "2024-01-01 10:00:00,123"
        assert isinstance(record['datetime'], pd.Timestamp)


class TestLogParserIntegration:
    """Testes de integração para LogParser"""
    
    @pytest.fixture
    def parser(self):
        return LogParser()
    
    def test_full_pipeline(self, parser):
        """Testa pipeline completo de transformação"""
        # Simular FileInfo
        from src.extract.file_reader import FileInfo
        from pathlib import Path
        
        lines = [
            "2024-01-01 10:00:00,000 [PC001] ALARM_001 CFN start\n",
            "2024-01-01 10:05:00,000 [PC001] ALARM_001 ALARM is acknowledged\n",
            "2024-01-01 10:10:00,000 [PC001] ALARM_001 OK end\n"
        ]
        
        file_info = FileInfo(
            filename="test.txt",
            filepath=Path("test.txt"),
            lines=lines,
            encoding="utf-8",
            line_count=len(lines)
        )
        
        # Processar
        df = parser.parse_multiple_files([file_info])
        
        assert len(df) == 3
        assert df['type'].tolist() == ['CFN', 'ACK', 'OK']
        assert df['pc_id'].unique()[0] == 'PC001'
        assert df['alarm'].unique()[0] == 'ALARM_001'


# Executar testes com pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
    