"""
Pipeline ETL Principal
Orquestra as etapas de Extract, Transform e Load
"""
import time
from datetime import datetime
from typing import Optional, Tuple
import pandas as pd

from src.extract.file_reader import FileReader
from src.transform.log_parser import LogParser
from src.load.database import DatabaseLoader
from src.utils.logger import ETLLogger


class ETLPipeline:
    """Classe principal do pipeline ETL"""
    
    def __init__(self, source_directory: Optional[str] = None):
        """
        Inicializa o pipeline ETL
        
        Args:
            source_directory: Diretório fonte (opcional)
        """
        self.source_directory = source_directory
        self.logger_manager = ETLLogger('etl_pipeline')
        self.logger = self.logger_manager.get_logger()
        
        # Inicializar componentes
        self.file_reader = FileReader(source_directory)
        self.log_parser = LogParser()
        self.db_loader = DatabaseLoader()
        
        self.execution_stats = {}
        self.start_time = None
        self.end_time = None
    
    def run(self, clear_database: bool = False) -> Tuple[bool, dict]:
        """
        Executa o pipeline ETL completo
        
        Args:
            clear_database: Se True, limpa dados antigos antes de carregar
            
        Returns:
            Tuple (success, statistics)
        """
        self.start_time = time.time()
        self.logger_manager.log_etl_start("Alarmes de Formulação")
        
        try:
            # ============================================================
            # FASE 1: EXTRACT
            # ============================================================
            self.logger_manager.log_phase_start("EXTRACT - Leitura de Arquivos")
            
            file_infos = self.file_reader.read_all_files()
            
            if not file_infos:
                self.logger.error("Nenhum arquivo encontrado para processar")
                return False, {}
            
            extract_stats = self.file_reader.get_statistics(file_infos)
            self.logger_manager.log_phase_end("EXTRACT", extract_stats['total_lines'])
            self.logger_manager.log_stats(extract_stats)
            
            # ============================================================
            # FASE 2: TRANSFORM
            # ============================================================
            self.logger_manager.log_phase_start("TRANSFORM - Parsing e Transformação")
            
            df_transformed = self.log_parser.parse_multiple_files(file_infos)
            
            if df_transformed.empty:
                self.logger.error("Nenhum dado foi transformado")
                return False, {}
            
            transform_stats = self.log_parser.get_statistics(df_transformed)
            self.logger_manager.log_phase_end("TRANSFORM", transform_stats['total_records'])
            self.logger_manager.log_stats(transform_stats)
            
            # Agrupar sequências
            df_grouped = self.log_parser.group_alarm_sequences(df_transformed)
            
            # ============================================================
            # FASE 3: LOAD
            # ============================================================
            self.logger_manager.log_phase_start("LOAD - Carga no Banco de Dados")
            
            # Limpar banco se solicitado
            if clear_database:
                self.logger.info("Limpando dados antigos do banco...")
                self.db_loader.clear_table('alarm_logs')
            
            # Carregar dados
            load_mode = 'replace' if clear_database else 'append'
            success = self.db_loader.load_dataframe(
                df_grouped, 
                table_name='alarm_logs',
                if_exists=load_mode
            )
            
            if not success:
                self.logger.error("Falha ao carregar dados no banco")
                return False, {}
            
            self.logger_manager.log_phase_end("LOAD", len(df_grouped))
            
            # ============================================================
            # FASE 4: ESTATÍSTICAS FINAIS
            # ============================================================
            self.end_time = time.time()
            execution_time = self.end_time - self.start_time
            
            # Consolidar estatísticas
            self.execution_stats = {
                'total_files': extract_stats['total_files'],
                'total_records': transform_stats['total_records'],
                'records_by_type': transform_stats['records_by_type'],
                'period_start': transform_stats.get('period_start'),
                'period_end': transform_stats.get('period_end'),
                'execution_time': execution_time
            }
            
            # Salvar estatísticas no banco
            self.db_loader.save_etl_statistics(
                self.execution_stats, 
                execution_time,
                status='success'
            )
            
            self.logger_manager.log_etl_end(
                "Alarmes de Formulação", 
                execution_time
            )
            
            # Resumo final
            self._print_final_summary()
            
            return True, self.execution_stats
            
        except Exception as e:
            self.logger.error(f"Erro durante execução do pipeline: {e}", exc_info=True)
            
            if self.start_time:
                execution_time = time.time() - self.start_time
                self.db_loader.save_etl_statistics(
                    {'total_records': 0},
                    execution_time,
                    status='failed'
                )
            
            return False, {}
        
        finally:
            self.db_loader.close()
    
    def _print_final_summary(self):
        """Imprime resumo final da execução"""
        print("\n" + "="*80)
        print("📊 RESUMO FINAL DA EXECUÇÃO")
        print("="*80)
        print(f"Arquivos processados: {self.execution_stats['total_files']}")
        print(f"Total de registros: {self.execution_stats['total_records']}")
        print(f"\nRegistros por tipo:")
        for alarm_type, count in self.execution_stats['records_by_type'].items():
            print(f"  {alarm_type}: {count}")
        
        if self.execution_stats.get('period_start'):
            print(f"\nPeríodo dos dados:")
            print(f"  Início: {self.execution_stats['period_start']}")
            print(f"  Fim: {self.execution_stats['period_end']}")
        
        print(f"\nTempo de execução: {self.execution_stats['execution_time']:.2f} segundos")
        print("="*80)
        print("✓ Pipeline ETL concluído com sucesso!")
        print("="*80 + "\n")
    
    def query_database(self, **kwargs) -> pd.DataFrame:
        """
        Consulta dados do banco
        
        Args:
            **kwargs: Parâmetros de consulta (alarm_type, pc_id, limit)
            
        Returns:
            DataFrame com resultados
        """
        return self.db_loader.query_alarms(**kwargs)
    
    def get_execution_history(self) -> pd.DataFrame:
        """
        Retorna histórico de execuções do ETL
        
        Returns:
            DataFrame com histórico
        """
        return self.db_loader.get_statistics_summary()


# Função helper para executar o pipeline
def run_etl_pipeline(source_directory: Optional[str] = None, 
                     clear_database: bool = False) -> Tuple[bool, dict]:
    """
    Executa o pipeline ETL
    
    Args:
        source_directory: Diretório fonte
        clear_database: Limpar dados antigos
        
    Returns:
        Tuple (success, statistics)
    """
    pipeline = ETLPipeline(source_directory)
    return pipeline.run(clear_database)


# Exemplo de uso
if __name__ == "__main__":
    print("\n" + "="*80)
    print("EXECUTANDO PIPELINE ETL")
    print("="*80 + "\n")
    
    # Executar pipeline
    success, stats = run_etl_pipeline(clear_database=False)
    
    if success:
        print("\n✓ Pipeline executado com sucesso!")
        
        # Criar nova instância para consultas
        pipeline = ETLPipeline()
        
        # Exemplo de consulta
        print("\n" + "-"*80)
        print("EXEMPLO DE CONSULTA AO BANCO")
        print("-"*80)
        df_result = pipeline.query_database(alarm_type='CFN', limit=5)
        print(df_result)
        
        # Histórico de execuções
        print("\n" + "-"*80)
        print("HISTÓRICO DE EXECUÇÕES")
        print("-"*80)
        df_history = pipeline.get_execution_history()
        print(df_history)
    else:
        print("\n✗ Pipeline falhou durante a execução")
        