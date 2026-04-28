# Project1

A small Vite + React demo wired up with [`motion`](https://motion.dev) for
animations and a custom SVG QR code component.

## Stack

- [Vite](https://vitejs.dev) 5
- [React](https://react.dev) 18
- [`motion`](https://www.npmjs.com/package/motion) — the React/JS flavor of
  Framer Motion (`import { motion } from 'motion/react'`)
- [`qrcode`](https://www.npmjs.com/package/qrcode) — used to compute the QR
  module matrix; rendering is hand-rolled SVG

## Quick start

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # production build to dist/
npm run preview  # serve the production build
```

## Layout

```
src/
  main.jsx       React entry
  App.jsx        Demo page (motion gradient + QR code)
  QRCode.jsx     SVG QR code component (rounded finder eyes, dotted modules)
index.html       Vite entry
vite.config.js   Vite + @vitejs/plugin-react
```

## QR component

`QRCode` accepts `value`, `size`, `fgColor`, `bgColor`, and
`errorCorrectionLevel` (`'L' | 'M' | 'Q' | 'H'`). Colors default to CSS
variables (`--foreground` / `--background`) with `#111` / `#fff` fallbacks.

```jsx
import { QRCode } from './QRCode.jsx'

<QRCode value="https://example.com" size={220} />
```

## Claude Code

The `.claude/skills/` directory contains agent skills used during development;
they are not runtime dependencies of the app.
