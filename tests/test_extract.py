"""
Testes Unitários para o Módulo de Extração
"""
import pytest
import tempfile
from pathlib import Path
import sys

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extract.file_reader import FileReader, FileInfo


class TestFileReader:
    """Testes para a classe FileReader"""
    
    @pytest.fixture
    def temp_directory(self):
        """Cria diretório temporário para testes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def sample_files(self, temp_directory):
        """Cria arquivos de teste"""
        # Arquivo 1: UTF-8
        file1 = temp_directory / "test_file1.log"
        file1.write_text("2024-01-01 10:00:00,000 [PC001] ALARM_001 CFN\n", encoding='utf-8')
        
        # Arquivo 2: Latin-1
        file2 = temp_directory / "test_file2.log"
        file2.write_text("2024-01-01 11:00:00,000 [PC002] ALARM_002 OK\n", encoding='latin-1')
        
        # Arquivo com extensão diferente (não deve ser processado)
        file3 = temp_directory / "test_file3.cof"
        file3.write_text("Should not be processed\n", encoding='utf-8')
        
        return temp_directory
    
    def test_file_reader_initialization(self):
        """Testa inicialização do FileReader"""
        reader = FileReader()
        assert reader is not None
        assert reader.file_extension == '.log'
        assert len(reader.encodings) > 0
    
    def test_list_files(self, sample_files):
        """Testa listagem de arquivos"""
        reader = FileReader(source_directory=sample_files)
        files = reader.list_files()
        
        assert len(files) == 2  # Apenas .log
        assert all(f.suffix.upper() == '.LOG' for f in files)
    
    def test_read_file_utf8(self, sample_files):
        """Testa leitura de arquivo UTF-8"""
        reader = FileReader(source_directory=sample_files)
        file_path = sample_files / "test_file1.log"
        
        file_info = reader.read_file(file_path)
        
        assert file_info is not None
        assert isinstance(file_info, FileInfo)
        assert file_info.filename == "test_file1.log"
        assert file_info.line_count == 1
        assert file_info.encoding in ['utf-8', 'UTF-8']
    
    def test_read_file_latin1(self, sample_files):
        """Testa leitura de arquivo Latin-1"""
        reader = FileReader(source_directory=sample_files)
        file_path = sample_files / "test_file2.log"
        
        file_info = reader.read_file(file_path)
        
        assert file_info is not None
        assert file_info.filename == "test_file2.log"
        assert file_info.encoding in reader.encodings
    
    def test_read_all_files(self, sample_files):
        """Testa leitura de todos os arquivos"""
        reader = FileReader(source_directory=sample_files)
        file_infos = reader.read_all_files()
        
        assert len(file_infos) == 2
        assert all(isinstance(fi, FileInfo) for fi in file_infos)
        
        total_lines = sum(fi.line_count for fi in file_infos)
        assert total_lines == 2
    
    def test_get_statistics(self, sample_files):
        """Testa geração de estatísticas"""
        reader = FileReader(source_directory=sample_files)
        file_infos = reader.read_all_files()
        
        stats = reader.get_statistics(file_infos)
        
        assert 'total_files' in stats
        assert stats['total_files'] == 2
        assert 'total_lines' in stats
        assert stats['total_lines'] == 2
        assert 'encodings_used' in stats
        assert len(stats['encodings_used']) > 0
    
    def test_empty_directory(self, temp_directory):
        """Testa comportamento com diretório vazio"""
        reader = FileReader(source_directory=temp_directory)
        files = reader.list_files()
        
        assert files == []
    
    def test_nonexistent_directory(self):
        """Testa comportamento com diretório inexistente"""
        fake_path = Path("/fake/nonexistent/path")
        reader = FileReader(source_directory=fake_path)
        files = reader.list_files()
        
        assert files == []


class TestFileInfo:
    """Testes para a classe FileInfo"""
    
    def test_fileinfo_creation(self):
        """Testa criação de FileInfo"""
        file_info = FileInfo(
            filename="test.txt",
            filepath=Path("test.txt"),
            lines=["line1\n", "line2\n"],
            encoding="utf-8",
            line_count=2
        )
        
        assert file_info.filename == "test.txt"
        assert file_info.line_count == 2
        assert file_info.encoding == "utf-8"
    
    def test_fileinfo_repr(self):
        """Testa representação string de FileInfo"""
        file_info = FileInfo(
            filename="test.txt",
            filepath=Path("test.txt"),
            lines=["line1\n"],
            encoding="utf-8",
            line_count=1
        )
        
        repr_str = repr(file_info)
        assert "test.txt" in repr_str
        assert "utf-8" in repr_str
        assert "1" in repr_str


# Executar testes com pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
