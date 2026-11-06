def calcula_subtracao(x,y):
    return x - y

def calcula_percentual(x,y):
    return(x/100)*y

def calcula_soma(x,y):
    return x+y

def calcula_radiciacao(x,y):
    return x**(1/y)

def calcula_multiplicacao(x,y):
    return x*y

def calcula_divisao_inteira(x,y):
    return x // y

def calcula_divisao(x,y):
    return x / y

def calcula_resto(x,y):
    return x % y

def calcula_exponenciacao(x, y):
    return x ** y

opcao = 1

while opcao != 0:
    print("\nEscolha uma das opções abaixo:")
    print("1 - Adição")
    print("2 - Subtração")
    print("3 - Multiplicação")
    print("4 - Divisão")
    print("5 - Exponenciação")
    print("6 - Radiciação")
    print("7 - Divisão inteira")
    print("8 - Resto")
    print("9 - Percentual")
    print("0 - Sair do programa")

    opcao = int(input("Digite a opção desejada: "))

    if opcao >= 1 and opcao <= 9:
        x = float(input("Digite o valor de x: "))
        y = float(input("Digite o valor de y: "))

        if opcao == 1:
            resultado = calcula_soma(x, y)

        elif opcao == 2:
            resultado = calcula_subtracao(x, y)

        elif opcao == 3:
            resultado = calcula_multiplicacao(x, y)

        elif opcao == 4:
            resultado = calcula_divisao(x, y)

        elif opcao == 5:
            resultado = calcula_exponenciacao(x, y)

        elif opcao == 6:
            resultado = calcula_radiciacao(x, y)

        elif opcao == 7:
            resultado = calcula_divisao_inteira(x, y)

        elif opcao == 8:
            resultado = calcula_resto(x, y)

        elif opcao == 9:
            resultado = calcula_percentual(x, y)

        print("Resultado:", resultado)

    elif opcao != 0:
        print("Opção inválida.")

print("Programa encerrado.")
