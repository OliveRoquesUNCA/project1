from node:lts
COPY ./src/ui /ui
WORKDIR /ui
RUN npm run build

from python:3.11
ARG GID=1001
ARG UID=1001
COPY ./src /app
COPY --from=0 /ui/dist /app/ui/dist
WORKDIR /app
RUN getent group ${GID} || groupadd -g ${GID} dev
RUN getent passwd ${UID} || useradd -m -u ${UID} -g ${GID} -s /bin/bash dev
RUN pip install poetry

RUN apt-get update && apt-get install -y jq

RUN poetry install

CMD ["poetry", "run", "uvicorn", "server:app", "--host", "0.0.0.0"]

