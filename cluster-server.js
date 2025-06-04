const cluster = require('cluster');
const os = require('os');

if (cluster.isPrimary) {
  const numCPUs = os.cpus().length;
  console.log(`Master PID ${process.pid} corriendo`);
  console.log(`Lanzando ${numCPUs} workers...`);

  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} murió. Reiniciando...`);
    cluster.fork();
  });
} else {
  console.log(`Worker iniciado - PID ${process.pid}`);
  require('./worker');
}