### Base node stage ###

FROM node:21-alpine as base

RUN adduser -h /home/appuser -D appuser

WORKDIR /application
RUN chown -R appuser:appuser /application


### Development and build stage ###

# Copy vite project files
FROM base as builder
COPY public /application/public
COPY src /application/src
COPY package.json postcss.config.js tailwind.config.js tsconfig.json \
    tsconfig.node.json vite.config.ts index.html \
    ./

# Install dependencies
RUN npm install

# Optionally build for production
ARG BUILD_PRODUCTION
RUN if [ "$BUILD_PRODUCTION" = "true" ]; then npm run build; fi

### Production Nginx stage ###

FROM nginx:alpine as production
COPY nginx.conf /etc/nginx/nginx.conf
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /application/dist /usr/share/nginx/html/front
EXPOSE 5173

CMD ["nginx", "-g", "daemon off;"]
