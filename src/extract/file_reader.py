"""
Módulo de Extração - File Reader
Responsável por ler arquivos de log do diretório fonte
"""
import os
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
import sys

# Adiciona a raiz do projeto ao sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.config import EXTRACT_CONFIG
from src.utils.logger import get_logger


@dataclass
class FileInfo:
    """Informações sobre um arquivo lido"""
    filename: str
    filepath: Path
    lines: List[str]
    encoding: str
    line_count: int
    
    def __repr__(self):
        return f"FileInfo(filename={self.filename}, lines={self.line_count}, encoding={self.encoding})"


class FileReader:
    """Classe para leitura de arquivos de log"""
    
    def __init__(self, source_directory: Optional[Path] = None):
        """
        Inicializa o FileReader
        
        Args:
            source_directory: Diretório fonte dos arquivos (opcional)
        """
        self.source_directory = source_directory or EXTRACT_CONFIG['source_directory']
        self.logger = get_logger('etl_pipeline.extract')
        self.logger.info(f"Diretório de leitura configurado: {self.source_directory}")
        self.logger.info(f"Diretório existe? {self.source_directory.exists()}")

        self.file_extension = EXTRACT_CONFIG['file_extension']
        self.encodings = EXTRACT_CONFIG['encodings_to_try']
        self.logger = get_logger('etl_pipeline.extract')
        
    def list_files(self) -> List[Path]:
        """
        Lista todos os arquivos com a extensão especificada
        
        Returns:
            Lista de Path objects dos arquivos encontrados
        """
        try:
            if not self.source_directory.exists():
                self.logger.error(f"Diretório não encontrado: {self.source_directory}")
                return []
            
            files = [
                f for f in self.source_directory.iterdir() 
                if f.is_file() and f.suffix.upper() == self.file_extension.upper()
            ]
            
            # Ordenar alfabeticamente
            files.sort()
            
            self.logger.info(f"Encontrados {len(files)} arquivo(s) {self.file_extension}")
            for f in files:
                self.logger.debug(f"  - {f.name}")
                
            return files
            
        except Exception as e:
            self.logger.error(f"Erro ao listar arquivos: {e}", exc_info=True)
            return []
    
    def read_file(self, filepath: Path) -> Optional[FileInfo]:
        """
        Lê um arquivo testando diferentes encodings
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            FileInfo object ou None se falhar
        """
        for encoding in self.encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                
                file_info = FileInfo(
                    filename=filepath.name,
                    filepath=filepath,
                    lines=lines,
                    encoding=encoding,
                    line_count=len(lines)
                )
                
                self.logger.info(
                    f"✓ Arquivo lido: {filepath.name} "
                    f"({len(lines)} linhas, encoding: {encoding})"
                )
                
                return file_info
                
            except (UnicodeDecodeError, Exception) as e:
                if encoding == self.encodings[-1]:
                    self.logger.error(
                        f"Falha ao ler {filepath.name} com todos os encodings"
                    )
                continue
        
        return None
    
    def read_all_files(self) -> List[FileInfo]:
        """
        Lê todos os arquivos do diretório fonte
        
        Returns:
            Lista de FileInfo objects
        """
        files = self.list_files()
        
        if not files:
            self.logger.warning("Nenhum arquivo para processar")
            return []
        
        file_infos = []
        
        for filepath in files:
            file_info = self.read_file(filepath)
            if file_info:
                file_infos.append(file_info)
        
        total_lines = sum(fi.line_count for fi in file_infos)
        self.logger.info(
            f"Total: {len(file_infos)} arquivo(s) processado(s), "
            f"{total_lines} linhas"
        )
        
        return file_infos
    
    def get_statistics(self, file_infos: List[FileInfo]) -> dict:
        """
        Gera estatísticas sobre os arquivos lidos
        
        Args:
            file_infos: Lista de FileInfo objects
            
        Returns:
            Dicionário com estatísticas
        """
        if not file_infos:
            return {}
        
        stats = {
            'total_files': len(file_infos),
            'total_lines': sum(fi.line_count for fi in file_infos),
            'encodings_used': list(set(fi.encoding for fi in file_infos)),
            'files_by_size': sorted(
                [(fi.filename, fi.line_count) for fi in file_infos],
                key=lambda x: x[1],
                reverse=True
            )
        }
        
        return stats


# Exemplo de uso e testes
if __name__ == "__main__":
    # Criar instância do FileReader
    reader = FileReader()
    
    # Listar arquivos
    print("\n" + "="*80)
    print("TESTE DO FILE READER")
    print("="*80)
    
    files = reader.list_files()
    print(f"\nArquivos encontrados: {len(files)}")
    
    # Ler todos os arquivos
    file_infos = reader.read_all_files()
    
    # Exibir estatísticas
    if file_infos:
        stats = reader.get_statistics(file_infos)
        print("\n" + "-"*80)
        print("ESTATÍSTICAS")
        print("-"*80)
        print(f"Total de arquivos: {stats['total_files']}")
        print(f"Total de linhas: {stats['total_lines']}")
        print(f"Encodings utilizados: {', '.join(stats['encodings_used'])}")
        print("\nArquivos por tamanho:")
        for filename, line_count in stats['files_by_size'][:5]:
            print(f"  {filename}: {line_count} linhas")
