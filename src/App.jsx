import { motion } from 'motion/react'
import { QRCode } from './QRCode.jsx'

export default function App() {
  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', padding: '2rem' }}>
      <h1>Motion + QR demo</h1>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        style={{
          width: 160,
          height: 160,
          borderRadius: 16,
          background: 'linear-gradient(135deg, #6366f1, #ec4899)',
          marginTop: '1rem',
        }}
      />
      <div style={{ marginTop: '2rem' }}>
        <QRCode value="https://github.com/pc1970/Project1" size={220} />
      </div>
    </div>
  )
}
