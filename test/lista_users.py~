#/usr/bin/python3.4

# Lista os usuários cadastrados
# Autor: Everton de Vargas Agilar
# Data: 20/10/2014

# python

import http.client
conn = http.client.HTTPConnection('localhost', 8000)
conn.request("GET",'/acesso/api1/adm/Usuario/')
response = conn.getresponse().read().decode("utf-8")
conn.close()
print(response)

# curl

# curl -X GET http://localhost:8000/acesso/api1/adm/Usuario/

