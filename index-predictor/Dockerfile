FROM node:23-alpine AS builder
WORKDIR /app

COPY package.json ./

RUN npm install

COPY . .

ARG NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
ENV NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=$NEXT_PUBLIC_GOOGLE_MAPS_API_KEY

RUN npm run build

FROM node:23-alpine AS runner
WORKDIR /app

RUN npm install -g next

ENV NODE_ENV=production

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "run", "start"]