### First stage ###

FROM node:21-alpine as base

RUN addgroup -g 1000 appuser \
    && adduser -u 1000 -G appuser -h /home/appuser -D appuser

WORKDIR /front
RUN chown -R appuser:appuser /front


### Second stage ###

FROM base as builder
COPY public /front/public
COPY src /front/src
COPY package.json postcss.config.js tailwind.config.js tsconfig.json tsconfig.node.json \
    vite.config.ts \
    /front/

# this needs to be moved
COPY .env.example /front/
RUN mv .env.example .env

RUN npm install && npm run build


### Final stage ###

FROM base as final
COPY --from=builder /front/dist /front/dist
