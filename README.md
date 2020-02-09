
[![Build Status](https://travis-ci.org/b2wdigital/async-worker.svg?branch=master)](https://travis-ci.org/b2wdigital/async-worker)
[![codecov](https://codecov.io/gh/b2wdigital/async-worker/branch/master/graph/badge.svg?flag=unittest)](https://codecov.io/gh/b2wdigital/async-worker)
[![codecov](https://codecov.io/gh/b2wdigital/async-worker/branch/master/graph/badge.svg?flag=typehint)](https://codecov.io/gh/b2wdigital/async-worker)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![PyPI version](https://badge.fury.io/py/async-worker.svg)](https://badge.fury.io/py/async-worker)


# O projeto

O projeto tem como objetivo ser um framework para escrever workers assíncronos em python. Por worker entende-se qualquer aplicação que rode por tempo indeterminado e que receba estímulos de várias origens diferentes. Essas orignes podem ser:

 - Uma mensagem em um broker, como RabbitMQ;
 - Um evento vindo se um servidor HTTP, como server side events;
 - Um evento recorrente gerado em um intervalo fixo de tempo;
 - Uma requisição HTTP
 - ...

 Documentação: https://b2wdigital.github.io/async-worker/
