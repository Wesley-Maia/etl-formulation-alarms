"""
Sistema de Logging para o Pipeline ETL
"""
import logging
import logging.config
from pathlib import Path
from datetime import datetime
import sys

# Adiciona a raiz do projeto ao sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.config import LOGGING_CONFIG, LOGS_DIR


class ETLLogger:
    """Classe para gerenciar logging do pipeline ETL"""
    
    def __init__(self, name='etl_pipeline'):
        """
        Inicializa o logger
        
        Args:
            name: Nome do logger
        """
        self.name = name
        self._setup_logging()
        self.logger = logging.getLogger(name)
        
    def _setup_logging(self):
        """Configura o sistema de logging"""
        # Garantir que o diretório de logs existe
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Configurar logging
        logging.config.dictConfig(LOGGING_CONFIG)
        
    def get_logger(self):
        """Retorna instância do logger"""
        return self.logger
    
    def log_etl_start(self, pipeline_name):
        """Log do início do pipeline"""
        self.logger.info("=" * 80)
        self.logger.info(f"INICIANDO PIPELINE ETL: {pipeline_name}")
        self.logger.info(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 80)
        
    def log_etl_end(self, pipeline_name, duration):
        """Log do fim do pipeline"""
        self.logger.info("=" * 80)
        self.logger.info(f"PIPELINE ETL FINALIZADO: {pipeline_name}")
        self.logger.info(f"Duração total: {duration:.2f} segundos")
        self.logger.info("=" * 80)
        
    def log_phase_start(self, phase_name):
        """Log do início de uma fase"""
        self.logger.info("-" * 80)
        self.logger.info(f"FASE: {phase_name}")
        self.logger.info("-" * 80)
        
    def log_phase_end(self, phase_name, records_count):
        """Log do fim de uma fase"""
        self.logger.info(f"✓ {phase_name} concluída: {records_count} registros")
        
    def log_error(self, error_msg, exception=None):
        """Log de erro"""
        self.logger.error(f"✗ ERRO: {error_msg}")
        if exception:
            self.logger.exception(exception)
            
    def log_warning(self, warning_msg):
        """Log de aviso"""
        self.logger.warning(f"⚠ AVISO: {warning_msg}")
        
    def log_info(self, info_msg):
        """Log de informação"""
        self.logger.info(f"ℹ {info_msg}")
        
    def log_debug(self, debug_msg):
        """Log de debug"""
        self.logger.debug(f"🔍 {debug_msg}")
        
    def log_stats(self, stats_dict):
        """Log de estatísticas"""
        self.logger.info("📊 Estatísticas:")
        for key, value in stats_dict.items():
            self.logger.info(f"   {key}: {value}")


def get_logger(name='etl_pipeline'):
    """
    Função helper para obter um logger
    
    Args:
        name: Nome do logger
        
    Returns:
        Logger instance
    """
    etl_logger = ETLLogger(name)
    return etl_logger.get_logger()


# Exemplo de uso
if __name__ == "__main__":
    # Criar logger
    logger_manager = ETLLogger('test_logger')
    
    # Testar diferentes níveis de log
    logger_manager.log_etl_start("Pipeline de Teste")
    logger_manager.log_phase_start("Extração")
    logger_manager.log_info("Processando arquivo teste.txt")
    logger_manager.log_debug("Detalhes da operação")
    logger_manager.log_warning("Arquivo pode estar incompleto")
    logger_manager.log_phase_end("Extração", 150)
    logger_manager.log_stats({
        'Total de arquivos': 5,
        'Registros processados': 150,
        'Erros': 0
    })
    logger_manager.log_etl_end("Pipeline de Teste", 2.5)
