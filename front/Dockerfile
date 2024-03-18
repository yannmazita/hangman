### First stage ###

FROM node:21-alpine as node-base

#RUN addgroup -g 1000 appuser && adduser -u 1000 -G appuser -h /home/appuser -D appuser
RUN adduser -h /home/appuser -D appuser

WORKDIR /front
RUN chown -R appuser:appuser /front


### Second stage ###

FROM node-base as node-builder
COPY front/public /front/public
COPY front/src /front/src
COPY front/package.json front/postcss.config.js front/tailwind.config.js front/tsconfig.json \
    front/tsconfig.node.json front/vite.config.ts front/index.html \
    /front/

# this needs to be moved
COPY .env.example /.
WORKDIR /front
RUN tree
RUN mv ../.env.example ../.env && npm install && npm run build

### Final stage ###

FROM node-base as node-final
COPY --from=node-builder /front/dist /front/dist
