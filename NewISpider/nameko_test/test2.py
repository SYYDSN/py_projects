
# _*_coding:utf-8_*_
__author__ = 'Alex Li'
import pika

credentials = pika.PlainCredentials('remote_client','NewSpider-123')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    '192.168.2.154',5672,'/',credentials))
channel = connection.channel()

# You may ask why we declare the queue again ‒ we have already declared it in our previous code.
# We could avoid that if we were sure that the queue already exists. For example if send.py program
# was run before. But we're not yet sure which program to run first. In such cases it's a good
# practice to repeat declaring the queue in both programs.
channel.queue_declare(queue='balance')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


channel.basic_consume(callback,
                      queue='balance',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()