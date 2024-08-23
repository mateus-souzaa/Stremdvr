import random

def gerar_cnpj():
    def calcular_digito(cnpj, peso):
        soma = sum(int(digito) * peso[i] for i, digito in enumerate(cnpj))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    def formatar_cnpj(cnpj):
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

    # Gerar a base do CNPJ
    base = ''.join([str(random.randint(0, 9)) for _ in range(8)])  # 8 primeiros dígitos
    cnpj = base + '0001'  # Adiciona o "0001" (4 dígitos para o número da filial)

    # Calcula o primeiro dígito verificador
    peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito1 = calcular_digito(cnpj, peso1)
    cnpj += str(digito1)

    # Calcula o segundo dígito verificador
    peso2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito2 = calcular_digito(cnpj, peso2)
    cnpj += str(digito2)

    return formatar_cnpj(cnpj)

# Exemplo de uso
cnpj_gerado = gerar_cnpj()
print(cnpj_gerado)
