# CONTEXT_RULES — Governança de Contexto para Agentes de IA

> Este arquivo deve ser fornecido **em toda interação** com o assistente de IA, junto com [specs/task_analyzer_spec.md](specs/task_analyzer_spec.md) e [tests/test_harness.py](tests/test_harness.py). Ele define **como** o código deve ser escrito; a especificação define **o que** ele deve fazer.
>
> **Versão 1.1 (Fase 3):** acrescenta a seção 3.5 (pipeline e entrega) e oficializa a estrutura final do repositório, com `.github/workflows/ci.yml`, `Dockerfile`, `docker-compose.yml`, `pytest.ini` e `specs/requirements.yaml`. As seções 3.1 a 3.4 continuam valendo sem alteração.

# 3. Governança de Contexto e Regras para Agentes de IA (CONTEXT_RULES)

As regras abaixo formam o arquivo CONTEXT_RULES.md, que será fornecido **em toda interação** com o assistente de IA. Elas são a fonte de verdade sobre **como** o código deve ser escrito; a especificação (Seções 1 e 2) define **o que** ele deve fazer.

## 3.1 Diretrizes arquiteturais (obrigatórias)

1.  **Python 3.11+** como versão mínima (uso de X \| None e list\[...\] nativos).

2.  **Type hints** em todas as funções, métodos, parâmetros e retornos.

3.  **Single Responsibility (SRP)**: validação, cálculo de métricas e montagem do relatório em funções separadas.

4.  Código limpo e aderente à **PEP 8** (nomes em snake_case, classes em PascalCase, linhas ≤ 88 caracteres).

5.  **Google style docstrings** em módulo, classes e funções, descrevendo Args, Returns e Raises.

6.  Funções **pequenas e coesas** (referência: até ~25 linhas) com um único propósito.

7.  **Tratamento de exceções específico**: apenas as exceções do contrato (1.3.4), com mensagens em português que citem id e campo.

8.  **Logs estruturados** com o módulo padrão logging (logger = logging.getLogger(\_\_name\_\_)), nunca print.

9.  Nomes de variáveis e funções **descritivos** em português, alinhados aos termos desta especificação.

10. Constantes para valores fixos (PRIORIDADES_VALIDAS, STATUS_VALIDOS), sem "números mágicos".

## 3.2 Proibições explícitas (regras restritivas)

1.  **Não** utilizar bibliotecas externas não autorizadas (ver 3.4).

2.  **Não** alterar, remover ou adaptar os cenários de teste fornecidos.

3.  **Não** modificar a estrutura de pastas definida na Seção 4.

4.  **Não** persistir dados em arquivos ou bancos de dados.

5.  **Não** alterar a assinatura (nome e parâmetros) de funções públicas sem autorização.

6.  **Não** gerar código sem testes correspondentes para novas funcionalidades.

7.  **Não** inserir código duplicado, morto ou sem necessidade.

8.  **Não** assumir comportamentos não especificados no contrato de negócio — em caso de dúvida, perguntar.

9.  **Não** usar except Exception genérico, except: vazio ou silenciar erros.

10. **Não** retornar campos, tipos ou valores diferentes dos definidos em 1.3.3.

11. **Não** comentar código em excesso: comentários explicam o "porquê", não o "o quê".

## 3.3 Regras de interação com a IA

- Todo prompt de geração deve incluir: CONTEXT_RULES.md + specs/task_analyzer_spec.md + tests/test_harness.py.

- Pedir **primeiro um plano** (funções e responsabilidades) e só depois o código.

- Gerar **uma funcionalidade por vez** (validação → cálculo → relatório), validando com pytest a cada passo.

- Exigir que a IA **pergunte** quando a especificação for ambígua, em vez de inventar regra.

- Rejeitar qualquer resposta que viole o contrato ou as proibições, mesmo que "funcione".

- Registrar no Pull Request os prompts relevantes e as correções feitas manualmente (rastreabilidade para a Fase 3).

## 3.4 Dependências autorizadas

| **Pacote**                             | **Onde pode ser usado** | **Motivo**                                                                        |
|----------------------------------------|-------------------------|-----------------------------------------------------------------------------------|
| dataclasses, typing, datetime, logging | src/ e tests/           | Biblioteca padrão do Python — modelos, tipos, datas e logs.                       |
| pytest                                 | Somente tests/          | Execução do Test Harness. Única dependência externa, listada em requirements.txt. |
| Qualquer outro                         | Proibido                | Exige nova versão desta especificação.                                            |

## 3.5 Regras de pipeline e entrega (Fase 3)

1.  A branch **main** só recebe código por Pull Request, com o workflow **CI** verde e homologação humana.

2.  O pipeline executa **exatamente** `pytest tests/test_harness.py -v`, em Python 3.11, sobre as dependências de `requirements.txt`.

3.  **Não** desativar, pular (`skip`, `xfail`, `continue-on-error`) ou filtrar testes para o pipeline passar.

4.  **Não** incluir segredos, tokens ou dados pessoais no workflow, no `Dockerfile` ou na imagem. O workflow roda com `permissions: contents: read`.

5.  O container usa a imagem base fixa `python:3.11-slim`, roda com usuário sem privilégios de root e só copia `src/`, `tests/`, `pytest.ini` e `requirements.txt`.

6.  Dependências com **versão fixada** em `requirements.txt`, para que o resultado seja igual na máquina local, no Docker e no GitHub Actions.

7.  Mudanças de infraestrutura geradas por IA seguem as mesmas regras do código: prompt com contexto, revisão humana e registro no Pull Request.
