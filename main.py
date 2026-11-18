from datetime import date

from biblioteca import Biblioteca, multa_emprestimo


def ler_data(mensagem: str) -> date:
    return date.fromisoformat(input(mensagem + ' (AAAA-MM-DD): ').strip())


def executar() -> None:
    biblioteca = Biblioteca()
    while True:
        print('\nSISTEMA DE BIBLIOTECA')
        print('1 - Cadastrar livro\n2 - Cadastrar usuário\n3 - Listar livros')
        print('4 - Emprestar\n5 - Devolver\n6 - Relatório de empréstimos\n0 - Sair')
        try:
            opcao = input('Opção: ').strip()
            if opcao == '0':
                print('Programa encerrado.')
                break
            if opcao == '1':
                biblioteca = biblioteca.cadastrar_livro(input('Título: '), input('Autor: '))
                print(f'Livro cadastrado. ID: {biblioteca.livros[-1].id}')
            elif opcao == '2':
                biblioteca = biblioteca.cadastrar_usuario(input('Nome: '))
                print(f'Usuário cadastrado. ID: {biblioteca.usuarios[-1].id}')
            elif opcao == '3':
                for livro in biblioteca.livros:
                    estado = 'Disponível' if biblioteca.disponivel(livro.id) else 'Emprestado'
                    print(f'{livro.id} - {livro.titulo} / {livro.autor} - {estado}')
                print('Títulos disponíveis:', ', '.join(biblioteca.titulos_disponiveis()) or 'Nenhum')
            elif opcao == '4':
                for usuario in biblioteca.usuarios:
                    print(f'{usuario.id} - {usuario.nome}')
                usuario_id = int(input('ID do usuário: '))
                livro_id = int(input('ID do livro: '))
                inicio = ler_data('Data do empréstimo')
                prevista = ler_data('Data prevista de devolução')
                biblioteca = biblioteca.emprestar(usuario_id, livro_id, inicio, prevista)
                print(f'Empréstimo registrado. ID: {biblioteca.emprestimos[-1].id}')
            elif opcao == '5':
                emprestimo_id = int(input('ID do empréstimo: '))
                devolucao = ler_data('Data da devolução')
                biblioteca = biblioteca.devolver(emprestimo_id, devolucao)
                emprestimo = next(e for e in biblioteca.emprestimos if e.id == emprestimo_id)
                valor = str(multa_emprestimo(emprestimo, devolucao)).replace('.', ',')
                print(f'Devolução registrada. Multa: R$ {valor}')
            elif opcao == '6':
                referencia = ler_data('Data de referência para multas em aberto')
                for e in biblioteca.emprestimos:
                    estado = 'Devolvido' if e.data_devolucao else 'Em aberto'
                    valor = str(multa_emprestimo(e, referencia)).replace('.', ',')
                    print(f'{e.id} - Usuário {e.usuario_id} - Livro {e.livro_id} - {estado} - Multa: R$ {valor}')
                total = str(biblioteca.total_multas(referencia)).replace('.', ',')
                print(f'Total de multas: R$ {total}')
            else:
                print('Opção inválida.')
        except ValueError as erro:
            print(f'Não foi possível realizar a operação: {erro}')
        except (EOFError, KeyboardInterrupt):
            print('\nPrograma encerrado.')
            break


if __name__ == '__main__':
    executar()
