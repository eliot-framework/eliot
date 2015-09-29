Eliot Framework
=====

Uma abordagem leve para o desenvolvimento de soluções Web/Mobile responsiva!

![alt tag](https://github.com/eliot-framework/eliot/blob/master/static/img/dashboard.png)


Ambiente de Desenvolvimento Recomendado
------------------------

* Ubuntu 64 Bits -- http://www.ubuntu.com/download/desktop
* IDE -- https://eclipse.org/
* PyDev para Eclipse -- http://www.pydev.org/
* Python 3.4 -- https://www.python.org/downloads/
* Django 1.7.4 -- https://www.djangoproject.com/

Instalando as dependências do projeto e o framework
------------------------

* Python 3.4 (ou superior)
```
Python 3 é instalado por padrão em modernas versões do Ubuntu.
```


* Django
```
sudo pip3 install Django==1.8.4
```
* Suporte ao Mysql
```
sudo pip3 install pymysql
```
* Suporte ao Postgresql
```
sudo apt-get install python3-psycopg2
```

* Fazer download do eliot
```
git clone https://github.com/eliot-framework/eliot.git
```


Executando o dashboard do framework (Testado em Ubuntu 15.04)
------------------------

```
$ python3.4 manage.py syncdb
Iniciando deploy, aguarde...
Linha de comando: ['manage.py', 'syncdb']
Operations to perform:
  Synchronize unmigrated apps: adm, estoque, fpc, sae
  Apply all migrations: sessions, admin, contenttypes, auth
Synchronizing apps without migrations:
  Creating tables...
    Creating table fpc_fpc
    Creating table fpc_transacao
    Creating table fpc_fpccontrole
    Creating table Sistema
    Creating table Departamento
    Creating table adm_usuario
    Creating table Telefone
    Creating table Endereco
    Creating table estoque_grupoproduto
    Creating table estoque_subgrupoproduto
    Creating table estoque_produtocomposicao
    Creating table estoque_produto
    Creating table estoque_aliquota
    Creating table estoque_icms
    Creating table estoque_pis_cofins
    Creating table estoque_pessoa
  Installing custom SQL...
  Installing indexes...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying sessions.0001_initial... OK

You have installed Django's auth system, and don't have any superusers defined.
Would you like to create one now? (yes/no): yes
Username (leave blank to use 'everton'): agilar
Email address: 
Password: xxx

$ python3.4 manage.py runserver --noreload

Iniciando deploy, aguarde...
Linha de comando: ['manage.py', 'runserver', '--noreload']
Cadastra configuração padrão.
Cadastrando funcionalidades fixas do framework.
Cadastrando permissão view para todos os modelos.
Criando arquivo /home/everton/desenvolvimento/python/eliot/static/css/fpc_concat.css.gz.
Criando arquivo /home/everton/desenvolvimento/python/eliot/static/js/fpc_concat.js.gz.
Performing system checks...

System check identified no issues (0 silenced).
August 27, 2015 - 08:53:26
Django version 1.7.3, using settings 'eliot.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.

```


Documentação sobre programação Python/Django
------------------------
* http://www.djangobook.com/en/2.0/index.html


