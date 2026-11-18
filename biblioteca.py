from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
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


def calcular_multa(data_prevista: date, data_referencia: date) -> Decimal:
    return Decimal(max(0, (data_referencia - data_prevista).days)) * Decimal('2.00')


def multa_emprestimo(emprestimo: Emprestimo, referencia: date) -> Decimal:
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

    def total_multas(self, referencia: date) -> Decimal:
        return reduce(lambda total, e: total + multa_emprestimo(e, referencia), self.emprestimos, Decimal('0.00'))
