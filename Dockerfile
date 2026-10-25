# Imagem base leve e fixa: mesmo Python 3.11 do pipeline de CI.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Usuário sem privilégios de root para executar os testes.
RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin appuser \
    && chown appuser:appuser /app

# Dependências primeiro: a camada fica em cache enquanto requirements.txt não mudar.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=appuser:appuser pytest.ini ./
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser tests/ ./tests/

USER 10001

# Comando de entrada principal: executa o Test Harness completo.
CMD ["pytest", "tests/test_harness.py", "-v"]
