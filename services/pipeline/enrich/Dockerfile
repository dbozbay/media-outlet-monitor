FROM ghcr.io/astral-sh/uv:0.11.15 AS uv

FROM public.ecr.aws/lambda/python:3.13 AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_INSTALLER_METADATA=1
ENV UV_LINK_MODE=copy

RUN --mount=from=uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv export --frozen --no-emit-workspace --no-dev --no-editable -o requirements.txt && \
    uv pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

FROM public.ecr.aws/lambda/python:3.13

ENV NLTK_DATA=/opt/nltk_data

COPY --from=builder ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}

RUN mkdir -p /opt/nltk_data && \
    python -c "import nltk; nltk.download('punkt', download_dir='/opt/nltk_data'); nltk.download('punkt_tab', download_dir='/opt/nltk_data'); nltk.download('stopwords', download_dir='/opt/nltk_data'); nltk.download('vader_lexicon', download_dir='/opt/nltk_data')"

RUN python -m spacy download en_core_web_sm

COPY main.py ${LAMBDA_TASK_ROOT}

CMD ["main.handler"]