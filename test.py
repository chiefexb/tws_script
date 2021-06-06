import pika
import json
#host='amqps://hcdfnopi:QrnJs_rKX_kGxmgMFHoSevUTgrsqIPuh@roedeer.rmq.cloudamqp.com/hcdfnopi'
host='amqps://ppapnglh:anS8VpRjtAenIzJqaRN6MYLTBoiH16zm@whale.rmq.cloudamqp.com/ppapnglh'

# url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672/%2f')amqps://hcdfnopi:QrnJs_rKX_kGxmgMFHoSevUTgrsqIPuh@roedeer.rmq.cloudamqp.com/hcdfnopi

# params = pika.URLParameters(url)
connection = pika.BlockingConnection(

pika.URLParameters(host)
)
channel = connection.channel()
channel.queue_declare(queue='test1')
dict1={"ID": 338719585, "Account": "DUC00074", "Symbol": "EAGG", "SecurityType": "STK", "Position": 1280.0, "Amount": 53.3022901, "Currency": "USD"}
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=json.dumps(dict1))
print(" [x] Sent 'Hello World!'")
connection.close()
#pika.ConnectionParameters(host)
# pika.URLParameter(host)
