import pika
credentials = pika.PlainCredentials('remote_client', 'NewSpider-123')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    '192.168.2.154',5672,'/',credentials))
channel = connection.channel()

# 声明queue
channel.queue_declare(queue='balance')

# n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
channel.basic_publish(exchange='',
                      routing_key='balance',
                      body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()