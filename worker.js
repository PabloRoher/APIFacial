const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');

const app = express();
const upload = multer();
const PORT = 3000;

app.post('/api/detector', upload.single('image'), (req, res) => {
  const imagePath = path.join(__dirname, 'temp.jpg');
  fs.writeFileSync(imagePath, req.file.buffer);

  execFile('python', ['predict.py', 'temp.jpg'], { cwd: __dirname }, (error, stdout, stderr) => {
    if (error) {
      console.error('Error ejecutando modelo:', error);
      return res.status(500).send('Error en el modelo');
    }

    try {
      const result = JSON.parse(stdout.trim().split('\n').pop());
      res.json({ predictions: result });
    } catch {
      res.status(500).send('Error al interpretar la salida');
    }
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Worker ${process.pid} escuchando en puerto ${PORT}`);
});