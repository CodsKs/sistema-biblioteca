import unittest
from dataclasses import FrozenInstanceError
from datetime import date

from main import Biblioteca, calcular_multa, multa_emprestimo


class TestBiblioteca(unittest.TestCase):
    def setUp(self):
        self.base = Biblioteca().cadastrar_livro('Dom Casmurro', 'Machado de Assis').cadastrar_usuario('Ana')
        self.inicio = date(2026, 11, 1)
        self.prazo = date(2026, 11, 8)
        self.ativa = self.base.emprestar(1, 1, self.inicio, self.prazo)

    def test_cadastro_preserva_estado_original(self):
        nova = self.base.cadastrar_livro('O Cortiço', 'Aluísio Azevedo')
        self.assertEqual(len(self.base.livros), 1)
        self.assertEqual(nova.livros[-1].id, 2)

    def test_objetos_sao_imutaveis(self):
        with self.assertRaises(FrozenInstanceError):
            self.base.livros[0].titulo = 'Outro'

    def test_cadastro_rejeita_campos_vazios(self):
        for titulo, autor in [(' ', 'Autor'), ('Título', '')]:
            with self.subTest(titulo=titulo, autor=autor):
                with self.assertRaises(ValueError):
                    self.base.cadastrar_livro(titulo, autor)
        with self.assertRaises(ValueError):
            self.base.cadastrar_usuario(' ')

    def test_emprestimo_bloqueia_livro_sem_alterar_base(self):
        self.assertTrue(self.base.disponivel(1))
        self.assertFalse(self.ativa.disponivel(1))
        with self.assertRaises(ValueError):
            self.ativa.emprestar(1, 1, self.inicio, self.prazo)

    def test_ids_inexistentes(self):
        for usuario, livro in [(99, 1), (1, 99)]:
            with self.subTest(usuario=usuario, livro=livro):
                with self.assertRaises(ValueError):
                    self.base.emprestar(usuario, livro, self.inicio, self.prazo)
        with self.assertRaises(ValueError):
            self.base.disponivel(99)
        with self.assertRaises(ValueError):
            self.ativa.devolver(99, self.prazo)

    def test_prazo_invalido(self):
        with self.assertRaises(ValueError):
            self.base.emprestar(1, 1, self.prazo, self.inicio)

    def test_devolucao_libera_livro_e_preserva_historico(self):
        devolvida = self.ativa.devolver(1, self.prazo)
        self.assertTrue(devolvida.disponivel(1))
        self.assertIsNone(self.ativa.emprestimos[0].data_devolucao)
        nova = devolvida.emprestar(1, 1, self.prazo, date(2026, 11, 15))
        self.assertEqual(len(nova.emprestimos), 2)
        self.assertFalse(nova.disponivel(1))

    def test_devolucao_duplicada(self):
        with self.assertRaises(ValueError):
            self.ativa.devolver(1, self.prazo).devolver(1, self.prazo)

    def test_devolucao_anterior_ao_emprestimo(self):
        with self.assertRaises(ValueError):
            self.ativa.devolver(1, date(2026, 10, 31))

    def test_emprestimo_nao_sobrepoe_historico(self):
        devolvida = self.ativa.devolver(1, self.prazo)
        with self.assertRaises(ValueError):
            devolvida.emprestar(1, 1, self.inicio, self.prazo)

    def test_multas_antes_no_prazo_e_atrasada(self):
        for referencia, esperado in [(date(2026, 11, 7), 0), (self.prazo, 0), (date(2026, 11, 9), 2), (date(2026, 11, 11), 6)]:
            with self.subTest(referencia=referencia):
                self.assertEqual(calcular_multa(self.prazo, referencia), esperado)

    def test_multa_para_de_crescer_apos_devolucao(self):
        devolvida = self.ativa.devolver(1, date(2026, 11, 11))
        self.assertEqual(multa_emprestimo(devolvida.emprestimos[0], date(2026, 12, 1)), 6)

    def test_map_filter_selecionam_disponiveis(self):
        biblioteca = self.ativa.cadastrar_livro('O Cortiço', 'Aluísio Azevedo')
        self.assertEqual(biblioteca.titulos_disponiveis(), ('O Cortiço',))
        self.assertEqual(tuple(livro.id for livro in biblioteca.livros_disponiveis()), (2,))

    def test_reduce_soma_multas_abertas_e_encerradas(self):
        biblioteca = self.ativa.devolver(1, date(2026, 11, 9))
        biblioteca = biblioteca.cadastrar_livro('O Cortiço', 'Aluísio Azevedo')
        biblioteca = biblioteca.emprestar(1, 2, self.inicio, self.prazo)
        self.assertEqual(biblioteca.total_multas(date(2026, 11, 11)), 8)
        self.assertEqual(Biblioteca().total_multas(self.prazo), 0)


if __name__ == '__main__':
    unittest.main()
