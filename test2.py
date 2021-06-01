from rpc_client import RpcClient
import json

host='amqps://hcdfnopi:QrnJs_rKX_kGxmgMFHoSevUTgrsqIPuh@roedeer.rmq.cloudamqp.com/hcdfnopi'
#host='amqps://ppapnglh:anS8VpRjtAenIzJqaRN6MYLTBoiH16zm@whale.rmq.cloudamqp.com/ppapnglh'
rpc = RpcClient(host,'test1')
dict1={"ID": 338719585, "Account": "DUC00074", "Symbol": "EAGG", "SecurityType": "STK", "Position": 1280.0, "Amount": 53.3022901, "Currency": "USD"}




response = rpc.call('test1',json.dumps(dict1))

print(response)
