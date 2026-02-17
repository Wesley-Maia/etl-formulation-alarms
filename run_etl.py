"""
Script Principal para Execução do Pipeline ETL
Alarmes de Formulação - Análise e Processamento
"""
import sys
import argparse
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.etl_pipeline import ETLPipeline


def parse_arguments():
    """Parse argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description='Pipeline ETL para Análise de Alarmes de Formulação',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_etl.py                          # Execução padrão
  python run_etl.py --clear                  # Limpar banco antes de carregar
  python run_etl.py --source /path/to/logs   # Especificar diretório fonte
  python run_etl.py --query --type CFN       # Consultar alarmes tipo CFN
  python run_etl.py --history                # Ver histórico de execuções
        """
    )
    
    parser.add_argument(
        '--source',
        type=str,
        help='Diretório fonte dos arquivos de log',
        default=None
    )
    
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Limpar dados antigos do banco antes de carregar'
    )
    
    parser.add_argument(
        '--query',
        action='store_true',
        help='Modo consulta: apenas consultar dados do banco'
    )
    
    parser.add_argument(
        '--type',
        type=str,
        choices=['CFN', 'OK', 'ACK'],
        help='Filtrar por tipo de alarme (usar com --query)'
    )
    
    parser.add_argument(
        '--pc-id',
        type=str,
        help='Filtrar por PC ID (usar com --query)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Número máximo de registros na consulta (padrão: 100)'
    )
    
    parser.add_argument(
        '--history',
        action='store_true',
        help='Exibir histórico de execuções do ETL'
    )
    
    return parser.parse_args()


def run_query_mode(args):
    """Executa modo de consulta"""
    print("\n" + "="*80)
    print("MODO CONSULTA - BANCO DE DADOS")
    print("="*80 + "\n")
    
    pipeline = ETLPipeline()
    
    # Consultar dados
    df = pipeline.query_database(
        alarm_type=args.type,
        pc_id=args.pc_id,
        limit=args.limit
    )
    
    if not df.empty:
        print(f"Encontrados {len(df)} registros:\n")
        print(df.to_string(index=False))
    else:
        print("Nenhum registro encontrado com os filtros especificados.")
    
    print("\n" + "="*80 + "\n")


def show_execution_history():
    """Mostra histórico de execuções"""
    print("\n" + "="*80)
    print("HISTÓRICO DE EXECUÇÕES DO PIPELINE ETL")
    print("="*80 + "\n")
    
    pipeline = ETLPipeline()
    df_history = pipeline.get_execution_history()
    
    if not df_history.empty:
        print(df_history.to_string(index=False))
    else:
        print("Nenhuma execução registrada ainda.")
    
    print("\n" + "="*80 + "\n")


def run_etl_mode(args):
    """Executa modo ETL completo"""
    print("\n" + "="*80)
    print("🚀 INICIANDO PIPELINE ETL - ALARMES DE FORMULAÇÃO")
    print("="*80)
    
    if args.source:
        print(f"Diretório fonte: {args.source}")
    
    if args.clear:
        print("⚠ ATENÇÃO: Dados antigos serão removidos do banco")
        response = input("Confirmar? (s/n): ")
        if response.lower() != 's':
            print("Operação cancelada.")
            return
    
    print("\n")
    
    # Executar pipeline
    pipeline = ETLPipeline(source_directory=args.source)
    success, stats = pipeline.run(clear_database=args.clear)
    
    if success:
        print("\n✅ Pipeline executado com SUCESSO!")
        
        # Oferecer consulta rápida
        print("\n" + "-"*80)
        print("Deseja visualizar alguns registros? (s/n): ", end="")
        if input().lower() == 's':
            df_sample = pipeline.query_database(limit=10)
            print("\nPrimeiros 10 registros:")
            print(df_sample.to_string(index=False))
    else:
        print("\n❌ Pipeline FALHOU durante a execução")
        print("Verifique os logs em 'logs/etl_pipeline.log' para mais detalhes")
        sys.exit(1)


def main():
    """Função principal"""
    args = parse_arguments()
    
    try:
        # Determinar modo de operação
        if args.history:
            show_execution_history()
        elif args.query:
            run_query_mode(args)
        else:
            run_etl_mode(args)
            
    except KeyboardInterrupt:
        print("\n\n⚠ Operação cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
