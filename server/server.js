import { connect } from 'amqplib'
import express from 'express'
import { sleep } from './utils.js'
import { createClient } from 'redis';
import { randomUUID } from 'crypto'

// ------------------------------------
// Connect to RabbitMQ
// ------------------------------------
const amqpUrl = 'amqp://rabbitmq:5672'
let connection
while (true) {
    console.log('Trying connection to RabbitMQ')
    await sleep(1000)
    try {
        connection = await connect(amqpUrl)
        break
    } catch {
        continue
    }
}
console.log('Succesfully connected to RabbitMQ')

const channel = await connection.createChannel()
const queue = 'image_processing'
await channel.assertQueue(queue, { durable: true })


// ------------------------------------
// Connect to Redis
// ------------------------------------
const client = createClient({ url: 'redis://redis' });
// const client = createClient();
client.on('error', err => console.log('Redis Client Error', err));
while (true) {
    console.log('Trying connection to Redis')
    await sleep(1000)
    try {
        await client.connect();
        break
    } catch {
        continue
    }
}
console.log('Succesfully connected to Redis')

// Initialize expressJS
const app = express();
const port = 8080;
app.use(express.raw({ type: 'image/png', limit: '10mb' }));

// Listen to requests
app.post("/processImage", async function (req, res) {
    if (!req.body || !req.body.length) {
        res.status(400).json({ error: 'No image file provided' });
        return;
    }

    const op = req.query.op

    const imageBuffer = req.body;
    const base64Image = imageBuffer.toString('base64');

    const requestID = randomUUID()

    // Save request to DB
    const requestEntry = {
        status: 'queue',
        image: '',
        date: Date()
    }
    await client.hSet(requestID, requestEntry)

    // Put job on workers queue
    const job = {
        image: base64Image,
        id: requestID,
        op: op
    }
    channel.sendToQueue(queue, Buffer.from(JSON.stringify(job)))
    res.json({ requestID })
});

app.get('/getImage', async function (req, res) {
    const id = req.query.id
    const requestEntry = await client.hGetAll(id);
    if (requestEntry.status != 'done') {
        res.status(400).json({ error: 'Request status: ' + requestEntry.status });
        return
    }

    const image = Buffer.from(requestEntry.image, 'base64')

    res.set('Content-Type', 'image/jpeg');
    res.send(image);
})

app.get('/getStatus', async function (req, res) {
    const id = req.query.id
    const requestEntry = await client.hGetAll(id);
    res.json(requestEntry)
})

app.listen(port, function () {
    console.log(`Server listening on port ${port}!`);
});
