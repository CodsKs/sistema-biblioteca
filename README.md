# Sistema de Biblioteca

Projeto acadêmico em Python com todo o sistema em um único arquivo `main.py`, interface de terminal, orientação a objetos e programação funcional. Não utiliza banco de dados nem dependências externas. O código Python não contém comentários.

## Executar

Requer Python 3.10 ou superior. Abra o terminal na pasta do projeto e execute:

```bash
python main.py
```

No Windows, também é possível usar `py main.py`.

## Funcionalidades

- Cadastro de livros e usuários com identificadores automáticos.
- Consulta de disponibilidade e listagem de títulos disponíveis.
- Empréstimos com datas de início e prazo informados pelo operador.
- Devoluções com liberação imediata do exemplar.
- Multa de R$ 2,00 por dia corrido de atraso.
- Relatório de empréstimos e soma das multas.
- Validação de campos vazios, identificadores, datas e devoluções duplicadas.

Cada livro cadastrado representa um exemplar físico. Exemplares do mesmo título podem ser cadastrados separadamente. Um exemplar admite apenas um empréstimo ativo. O prazo é informado em cada operação, pois o enunciado não define um prazo fixo.

Os dados ficam na memória e são descartados ao encerrar o programa. Todas as datas usam o formato `DD/MM/AAAA`. No relatório, a data de referência calcula as multas dos empréstimos em aberto; as multas de empréstimos devolvidos ficam fixadas na data da devolução. O total agrega esses valores e não representa controle de pagamentos.

## Exemplo de uso

1. Na opção 1, cadastre `Dom Casmurro`, de `Machado de Assis` (livro 1).
2. Na opção 2, cadastre `Ana` (usuário 1).
3. Na opção 4, informe usuário 1, livro 1, início `01/11/2026` e prazo `08/11/2026`.
4. Na opção 3, o livro aparecerá como emprestado.
5. Na opção 5, devolva o empréstimo 1 em `11/11/2026`.
6. O sistema informa multa de `R$ 6,00` e disponibiliza o livro novamente.

## Requisitos de programação

| Requisito | Aplicação |
| --- | --- |
| POO | Classes Livro, Usuario, Emprestimo e Biblioteca |
| Funções puras | calcular_multa e multa_emprestimo recebem explicitamente as datas e não alteram estado externo |
| Imutabilidade | dataclasses congeladas, coleções em tuplas e novas instâncias produzidas com replace |
| map | Transformação de livros em títulos e substituição imutável de um empréstimo devolvido |
| filter | Seleção dos livros disponíveis |
| reduce | Soma das multas |

As operações de cadastro, empréstimo e devolução retornam uma nova Biblioteca. O terminal atribui esse resultado à variável local, preservando as instâncias anteriores. Como a multa é sempre um múltiplo de R$ 2,00, os cálculos usam números inteiros em reais.

## Testes

```bash
python -m unittest discover -v
```

Os testes cobrem cadastro, imutabilidade, disponibilidade, empréstimos duplicados, referências inválidas, datas inconsistentes, devolução, histórico, multa antes/no prazo e com atraso, congelamento da multa após devolução, map, filter e reduce. O GitHub Actions também executa os testes a cada push e pull request.

## Arquivos

- `main.py`: sistema completo, com classes, regras de negócio e menu de terminal.
- `test_biblioteca.py`: testes automatizados.

## Entrega

Grupo de até quatro alunos. Preencha os nomes dos integrantes abaixo antes da entrega:

- Integrante 1: Luís Eduardo Freire Linhares        
- Integrante 2: Pedro Henrique Mendes Albuquerque 



