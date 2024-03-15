### First stage ###

FROM node:21-alpine as base

RUN addgroup -g 1000 appuser \
    && adduser -u 1000 -G appuser -h /home/appuser -D appuser

WORKDIR /front
RUN chown -R appuser:appuser /front


### Second stage ###

FROM base as builder
COPY front/public /front/public
COPY front/src /front/src
COPY front/package.json front/postcss.config.js front/tailwind.config.js front/tsconfig.json \
    front/tsconfig.node.json front/vite.config.ts \
    /front/

# this needs to be moved
COPY .env.example .
WORKDIR /front
RUN mv ../.env.example ../.env && npm install && npm build

### Final stage ###

FROM base as final
COPY --from=builder /front/dist /front/dist
