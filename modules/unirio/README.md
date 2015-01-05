API
===

Python module for the API provided by the Universidade Federal do Estado do Rio de Janeiro (UNIRIO)
Please visit http://sistemas.unirio.br/api for futher information.

UNIRIOAPIRequest takes 2 arguments:
* A valid APIKey that will be used for future requests
* An integer identifier for the server used to perform requests. Default=0 (Production Server)

The main method signature for performing syncronous API GET requests is defined by the signature 
```python 
performGETRequest( path, params=None, fields=None )
```
* path = The API endpoint to use for the request, for example "ALUNOS"
* params = The parameters for the request. A value of None sends the automatic API parameters
* fields = The return fields for the request. A value of None is equal do requesting ALL the fields

Usage example:
```python
from unirio.api import *

APIKey = "62e1c0e9b6be2387e01e6f8d101786a9c8f04dc7c81e178822daa5ffc5b609da5bd3c828df0d8f939d6e409a77d65c9a"
uAPi = UNIRIOAPIRequest( APIKey )

path = "ALUNOS"
params = {"LMIN" : 0,
          "LMAX" : 1000,
          "SEXO" : "F"
          "ETNIA_ITEM" : 1}
fields = ["ID_ALUNO", "ID_PESSOA", "SEXO"]

ret = uAPi.performGETRequest( path, params, fields )

```

A method call to `UNIRIOAPIRequest.performGETRequest` will return an `APIResultObject` wich is a model object and have the following attributes:
* content = A list of dictionaries with the result of the API Query
* lmin = The offset of the request result
* lmax = The limit of the request result
* count = The total ammount of results if the request wasnt limited by lmin and lmax

For default value references, check the API documentation.