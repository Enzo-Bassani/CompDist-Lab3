# CompDist-Lab3
alunos: Enzo Bassani e Rian Serena

Nossa implementacao consiste em um servidor web que recebe imagens de diversos clientes e 
envia ela em base64 por meio do middleware RabbitMQ para um programa em python, que faz
algumas alteracoes na imagem, após o processamento da imagem ela é retorna para os clientes.

o sistema tem uma limitacao de funcionar somente com imagens .png
é necessario ter o docker e o docker compose instalados para execução

para instalacao do docker compose basta executar os seguintes comandos:

1- sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
2- sudo chmod +x /usr/local/bin/docker-compose

para executar o sistema basta estar no diretorio dos arquivos e executar o seguinte comando no terminal:
docker compose up --build

apos as conexoes serem efetuados em outro terminal o cliente envia a imagem da seguinte maneira:

curl --location --request POST 'http://localhost:8080/processImage?op=inv' \
--header 'Content-Type: image/png' \
--data-binary '@{diretorio da imagem aqui}'

após o @ é inserido o diretorio da imagem e no final da url do POST 'http://localhost:8080/processImage?op=inv'
na "op=" podemos alterer o "inv" para fazer diferentes modificacoes na imagem
"inv" inverte as cores da imagem
"pb" deixa a imagem em preto e branco
"blur" bora a imagem

apos a execucao do primeiro comando ele irá retornar uma mensagem de sucesso juntamente com um ID, 
para conseguir transformar a imagem em um arquivo, basta executar o seguinte comando pelo mesmo terminal
que foi enviado a imagem:

curl --location --request GET 'http://localhost:8080/getImage?id={aqui vai o ID retornado no terminas do server}' \
--output{nome da imagem para ser salva}

a imagem sera salva com o nome escolhido seguido de .png no mesmo diretorio da imagem enviada

Foi desenvolvido também um cliente em Python. Para utilizá-lo:

```
python pythonClient.py pb teste1.png teste2.png
```

O primeiro argumento é a operacão desejada; os demais são os arquivos a serem enviados.