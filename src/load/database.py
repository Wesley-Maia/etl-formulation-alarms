"""
Módulo de Carga - Database Loader
Responsável por carregar dados no banco SQLite
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Index
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
import pandas as pd
from typing import Optional
from datetime import datetime as dt, timezone

from config.config import DATABASE_CONFIG, PERFORMANCE_CONFIG
from src.utils.logger import get_logger

Base = declarative_base()


class AlarmLog(Base):
    """Modelo da tabela de logs de alarmes"""
    
    __tablename__ = 'alarm_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    arquivo_origem = Column(String(255), nullable=False)
    timestamp = Column(String(50), nullable=False)
    datetime = Column(DateTime, nullable=True, index=True)
    pc_id = Column(String(100), nullable=False, index=True)
    alarm = Column(String(255), nullable=False, index=True)
    type = Column(String(20), nullable=False, index=True)
    linha_original = Column(Text)
    created_at = Column(DateTime, default=lambda: dt.now(timezone.utc))  # Timezone-aware
    
    # Índices compostos para otimizar queries
    __table_args__ = (
        Index('idx_pc_alarm', 'pc_id', 'alarm'),
        Index('idx_type_datetime', 'type', 'datetime'),
        Index('idx_arquivo_datetime', 'arquivo_origem', 'datetime'),
    )
    
    def __repr__(self):
        return f"<AlarmLog(id={self.id}, alarm={self.alarm}, type={self.type})>"


class ETLStatistics(Base):
    """Modelo da tabela de estatísticas de execução ETL"""
    
    __tablename__ = 'etl_statistics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_date = Column(DateTime, default=lambda: dt.now(timezone.utc), nullable=False)  # Timezone-aware
    total_files = Column(Integer)
    total_records = Column(Integer)
    cfn_count = Column(Integer)
    ok_count = Column(Integer)
    ack_count = Column(Integer)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    execution_time_seconds = Column(Integer)
    status = Column(String(50))
    
    def __repr__(self):
        return f"<ETLStatistics(date={self.execution_date}, records={self.total_records})>"


class DatabaseLoader:
    """Classe para gerenciar operações de banco de dados"""
    
    def __init__(self):
        """Inicializa o DatabaseLoader"""
        self.database_path = DATABASE_CONFIG['database_path']
        self.batch_size = PERFORMANCE_CONFIG['batch_size']
        self.logger = get_logger('etl_pipeline.load')
        
        # Criar engine
        self.engine = self._create_engine()
        
        # Criar sessão
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Criar tabelas
        self._create_tables()
    
    def _create_engine(self):
        """Cria engine do SQLAlchemy"""
        connection_string = f"sqlite:///{self.database_path}"
        
        engine = create_engine(
            connection_string,
            echo=DATABASE_CONFIG['echo'],
            connect_args={'check_same_thread': False},
            poolclass=StaticPool
        )
        
        self.logger.info(f"Engine criada: {self.database_path}")
        return engine
    
    def _create_tables(self):
        """Cria tabelas no banco de dados"""
        Base.metadata.create_all(self.engine)
        self.logger.info("Tabelas criadas/verificadas no banco de dados")
    
    def load_dataframe(self, df: pd.DataFrame, table_name: str = 'alarm_logs',
                       if_exists: str = 'append') -> bool:
        """
        Carrega DataFrame no banco de dados
        
        Args:
            df: DataFrame a ser carregado
            table_name: Nome da tabela
            if_exists: 'append' ou 'replace'
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            if df.empty:
                self.logger.warning("DataFrame vazio, nada para carregar")
                return False
            
            # Converter datetime para formato apropriado
            df_copy = df.copy()
            if 'datetime' in df_copy.columns:
                df_copy['datetime'] = pd.to_datetime(df_copy['datetime'])
            
            # Adicionar coluna created_at
            df_copy['created_at'] = dt.now(timezone.utc)
            
            # Carregar em batches para melhor performance
            total_records = len(df_copy)
            self.logger.info(f"Iniciando carga de {total_records} registros...")
            
            df_copy.to_sql(
                table_name,
                self.engine,
                if_exists=if_exists,
                index=False,
                chunksize=self.batch_size,
                method='multi'
            )
            
            self.logger.info(
                f"✓ {total_records} registros carregados na tabela '{table_name}'"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}", exc_info=True)
            return False
    
    def save_etl_statistics(self, stats: dict, execution_time: float, 
                           status: str = 'success') -> bool:
        """
        Salva estatísticas da execução do ETL
        
        Args:
            stats: Dicionário com estatísticas
            execution_time: Tempo de execução em segundos
            status: Status da execução
            
        Returns:
            True se sucesso
        """
        try:
            etl_stat = ETLStatistics(
                total_files=stats.get('total_files', 0),
                total_records=stats.get('total_records', 0),
                cfn_count=stats.get('records_by_type', {}).get('CFN', 0),
                ok_count=stats.get('records_by_type', {}).get('OK', 0),
                ack_count=stats.get('records_by_type', {}).get('ACK', 0),
                period_start=stats.get('period_start'),
                period_end=stats.get('period_end'),
                execution_time_seconds=int(execution_time),
                status=status
            )
            
            self.session.add(etl_stat)
            self.session.commit()
            
            self.logger.info("✓ Estatísticas de ETL salvas")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar estatísticas: {e}", exc_info=True)
            self.session.rollback()
            return False
    
    def query_alarms(self, alarm_type: Optional[str] = None, 
                    pc_id: Optional[str] = None,
                    limit: int = 100) -> pd.DataFrame:
        """
        Consulta alarmes no banco de dados
        
        Args:
            alarm_type: Filtrar por tipo de alarme
            pc_id: Filtrar por PC ID
            limit: Número máximo de registros
            
        Returns:
            DataFrame com resultados
        """
        query = "SELECT * FROM alarm_logs WHERE 1=1"
        
        if alarm_type:
            query += f" AND type = '{alarm_type}'"
        if pc_id:
            query += f" AND pc_id = '{pc_id}'"
        
        query += f" ORDER BY datetime DESC LIMIT {limit}"
        
        try:
            df = pd.read_sql(query, self.engine)
            self.logger.info(f"Consulta retornou {len(df)} registros")
            return df
        except Exception as e:
            self.logger.error(f"Erro na consulta: {e}")
            return pd.DataFrame()
    
    def get_statistics_summary(self) -> pd.DataFrame:
        """
        Retorna resumo das estatísticas de execuções
        
        Returns:
            DataFrame com estatísticas
        """
        try:
            df = pd.read_sql("SELECT * FROM etl_statistics ORDER BY execution_date DESC", 
                           self.engine)
            return df
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return pd.DataFrame()
    
    def clear_table(self, table_name: str = 'alarm_logs') -> bool:
        """
        Limpa dados de uma tabela
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            True se sucesso
        """
        try:
            self.session.execute(f"DELETE FROM {table_name}")
            self.session.commit()
            self.logger.info(f"Tabela '{table_name}' limpa")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao limpar tabela: {e}")
            self.session.rollback()
            return False
    
    def close(self):
        """Fecha conexões com o banco"""
        self.session.close()
        self.engine.dispose()
        self.logger.info("Conexões com banco fechadas")


# Exemplo de uso e testes
if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTE DO DATABASE LOADER")
    print("="*80)
    
    # Criar loader
    loader = DatabaseLoader()
    
    # Criar dados de teste
    test_data = pd.DataFrame({
        'arquivo_origem': ['2025-10-05_formulation.log'] * 3,
        'timestamp': ['2024-01-01 10:00:00,000'] * 3,
        'datetime': pd.to_datetime(['2024-01-01 10:00:00'] * 3),
        'pc_id': ['PC001', 'PC002', 'PC003'],
        'alarm': ['ALARM_001', 'ALARM_002', 'ALARM_003'],
        'type': ['CFN', 'OK', 'ACK'],
        'linha_original': ['test line 1', 'test line 2', 'test line 3']
    })
    
    # Testar carga
    success = loader.load_dataframe(test_data)
    
    if success:
        # Consultar dados
        df_result = loader.query_alarms(limit=10)
        print(f"\nRegistros no banco: {len(df_result)}")
        print(df_result.head())
    
    # Fechar conexão
    loader.close()
    