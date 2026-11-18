from dataclasses import dataclass, replace
from datetime import date
from functools import reduce


@dataclass(frozen=True)
class Livro:
    id: int
    titulo: str
    autor: str


@dataclass(frozen=True)
class Usuario:
    id: int
    nome: str


@dataclass(frozen=True)
class Emprestimo:
    id: int
    usuario_id: int
    livro_id: int
    data_emprestimo: date
    data_prevista: date
    data_devolucao: date | None = None


def calcular_multa(data_prevista: date, data_referencia: date) -> int:
    return max(0, (data_referencia - data_prevista).days) * 2


def multa_emprestimo(emprestimo: Emprestimo, referencia: date) -> int:
    return calcular_multa(emprestimo.data_prevista, emprestimo.data_devolucao or referencia)


@dataclass(frozen=True)
class Biblioteca:
    livros: tuple[Livro, ...] = ()
    usuarios: tuple[Usuario, ...] = ()
    emprestimos: tuple[Emprestimo, ...] = ()

    def cadastrar_livro(self, titulo: str, autor: str) -> 'Biblioteca':
        if not titulo.strip() or not autor.strip():
            raise ValueError('Título e autor são obrigatórios.')
        livro = Livro(len(self.livros) + 1, titulo.strip(), autor.strip())
        return replace(self, livros=self.livros + (livro,))

    def cadastrar_usuario(self, nome: str) -> 'Biblioteca':
        if not nome.strip():
            raise ValueError('Nome é obrigatório.')
        usuario = Usuario(len(self.usuarios) + 1, nome.strip())
        return replace(self, usuarios=self.usuarios + (usuario,))

    def disponivel(self, livro_id: int) -> bool:
        if not any(livro.id == livro_id for livro in self.livros):
            raise ValueError('Livro não encontrado.')
        return not any(e.livro_id == livro_id and e.data_devolucao is None for e in self.emprestimos)

    def livros_disponiveis(self) -> tuple[Livro, ...]:
        return tuple(filter(lambda livro: self.disponivel(livro.id), self.livros))

    def titulos_disponiveis(self) -> tuple[str, ...]:
        return tuple(map(lambda livro: livro.titulo, self.livros_disponiveis()))

    def emprestar(self, usuario_id: int, livro_id: int, inicio: date, prevista: date) -> 'Biblioteca':
        if not any(usuario.id == usuario_id for usuario in self.usuarios):
            raise ValueError('Usuário não encontrado.')
        if prevista < inicio:
            raise ValueError('O prazo não pode ser anterior ao empréstimo.')
        if not self.disponivel(livro_id):
            raise ValueError('Livro indisponível.')
        if any(e.livro_id == livro_id and e.data_devolucao is not None and e.data_devolucao > inicio for e in self.emprestimos):
            raise ValueError('A data informada conflita com o histórico do livro.')
        emprestimo = Emprestimo(len(self.emprestimos) + 1, usuario_id, livro_id, inicio, prevista)
        return replace(self, emprestimos=self.emprestimos + (emprestimo,))

    def devolver(self, emprestimo_id: int, devolucao: date) -> 'Biblioteca':
        emprestimo = next((e for e in self.emprestimos if e.id == emprestimo_id), None)
        if emprestimo is None:
            raise ValueError('Empréstimo não encontrado.')
        if emprestimo.data_devolucao is not None:
            raise ValueError('Empréstimo já devolvido.')
        if devolucao < emprestimo.data_emprestimo:
            raise ValueError('Devolução anterior ao empréstimo.')
        atualizado = replace(emprestimo, data_devolucao=devolucao)
        registros = tuple(map(lambda e: atualizado if e.id == emprestimo_id else e, self.emprestimos))
        return replace(self, emprestimos=registros)

    def total_multas(self, referencia: date) -> int:
        return reduce(lambda total, e: total + multa_emprestimo(e, referencia), self.emprestimos, 0)

def formatar_reais(valor):
    return f"{valor},00"


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
                valor = formatar_reais(multa_emprestimo(emprestimo, devolucao))
                print(f'Devolução registrada. Multa: R$ {valor}')
            elif opcao == '6':
                referencia = ler_data('Data de referência para multas em aberto')
                for e in biblioteca.emprestimos:
                    estado = 'Devolvido' if e.data_devolucao else 'Em aberto'
                    valor = formatar_reais(multa_emprestimo(e, referencia))
                    print(f'{e.id} - Usuário {e.usuario_id} - Livro {e.livro_id} - {estado} - Multa: R$ {valor}')
                total = formatar_reais(biblioteca.total_multas(referencia))
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
