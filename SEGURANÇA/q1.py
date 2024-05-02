# Importando as bibliotecas necessárias
import hashlib
import time
import itertools
import string

def criptografar_senha(senha):
    # A biblioteca hashlib fornece algoritmos de hash para criptografia
    # O método sha256() retorna um objeto de hash usando o algoritmo SHA-256
    # O método encode() converte a string em bytes para ser usado pelo algoritmo de hash
    # O método hexdigest() retorna a string codificada em hexadecimal
    return hashlib.sha256(senha.encode()).hexdigest()

#Quebrar a senha
def quebrar_senha(senha_criptografada, max_length, timeout):
    # Guarda o tempo inicial
    start_time = time.time()
    # Define os caracteres a serem usados na tentativa de força bruta
    chars = string.ascii_lowercase + string.digits
    # Tenta todas as combinações possíveis de caracteres
    for password_length in range(1, max_length + 1):
        for guess in itertools.product(chars, repeat=password_length):
            guess = ''.join(guess)
            # Se a senha criptografada for igual à tentativa criptografada, a senha foi quebrada
            if criptografar_senha(guess) == senha_criptografada:
                return guess, time.time() - start_time
            # Se o tempo limite for atingido, interrompe a tentativa
            if time.time() - start_time > timeout:
                return None, time.time() - start_time
    return None, time.time() - start_time


def main():
    # Solicita ao usuário que insira uma senha
    senha = input("Digite sua senha (máximo de 8 caracteres): ")
    # Verifica se a senha tem mais de 8 caracteres
    if len(senha) > 8:
        print("A senha deve ter no máximo 8 caracteres.")
        return

    # Criptografa a senha
    senha_criptografada = criptografar_senha(senha)
    print(f"A senha criptografada é: {senha_criptografada}")

    # Tenta quebrar a senha
    senha_quebrada, tempo_gasto = quebrar_senha(senha_criptografada, len(senha), 10)
    if senha_quebrada is None:
        print(f"Não foi possível quebrar a senha em 10 segundos.")
    else:
        print(f"A senha foi quebrada: {senha_quebrada}")
    print(f"Tempo gasto: {tempo_gasto} segundos")

# Executa a função principal
if __name__ == "__main__":
    main()
