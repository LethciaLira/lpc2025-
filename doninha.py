import random

#frase alvo
alvo = "methinks it is like a weasel"

#alterando a frase
numfrases = 100 
mutacao = 0.05 # a chance de mutação por caractere não são especificados no livro do Dawkins

#delimitando o alfabeto
alfa = "".join(chr(i)for i in range(65,91)) + " "

#frase aleatoria
def frase_ale(length):
    return"".join(random.choice(alfa) for _ in range(length))

#comparando as frases 
def acuracia(candidate):
    iguais = 0
    for c, t in zip(candidate, alvo):
        if c == t:
            iguais += 1
    return iguais