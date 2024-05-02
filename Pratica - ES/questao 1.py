# aluno: Christian Oliveira
# atividade: Prática Sistemas de arquivos

# alg. de escalonamento de braço - SCAN

import random

class Block:
    def __init__(self, id, size):
        self.id = id
        self.status = "livre"
        
class DiskScheduler:
    def __init__(self, start, end, armPosition):
        self.start = start
        self.end = end
        self.requests = []
        self.total_seek_time = 0
        if armPosition is None:
            self.current_position = random.randint(start, end)
        else:
            self.current_position = armPosition
            
        if armPosition is None:
            self.blocks = [Block(i, size=1) for i in range(self.end+ 1)]
        else:
            self.blocks = [Block(i, size=1) for i in range(max(self.end, armPosition) + 1)]
        
            

    def generate_requests(self, eu_quero, quantidade):
        if eu_quero is not None:
                inputrequests = input('digte a sequencia dividido por virgula "," ex: "4,5,10,8,6,9,7"')
                self.requests = inputrequests.split(',')
        elif quantidade is not None:
            if(quantidade != ""):
                self.requests = random.sample(range(self.start, self.end), quantidade)


    def scan_algorithm(self): # SCAN - O BRACO VAI DE PONTA A PONTA
        seek_count = 0
        visited_order = []

        # Vamos supor que o braço inicia em movimento para o intervalo maximo 
        # trantando inicio
        if(self.current_position  > self.end):
            seek_count = self.current_position - self.end
            self.current_position = self.end
        elif(self.current_position  < self.start):
            seek_count = self.start - self.current_position
            self.current_position = self.start
            
            
        found = 0
        if(self.blocks[self.current_position].id == self.requests[found]):
            print(f"Requisição achada: {self.requests[found]}")
            print(f"Tempo de seek parcial: {seek_count} u.t.")
            seek_count = 0
            found += 1
            visited_order.append(self.blocks[self.current_position])
        while(found < len(self.requests)):
            while(self.current_position <= self.end):# indo de bloco em bloco ate o ultimo
                print("posição atual: ", self.current_position)
                if(self.blocks[self.current_position ].id == self.requests[found]):
                    visited_order.append(self.requests[found])
                    self.total_seek_time += seek_count
                    print(f"Requisição achada: {self.requests[found]}")
                    print(f"Tempo de seek parcial: {seek_count} u.t.")
                    seek_count = 0
                    visited_order.append(self.blocks[self.current_position])
                    found += 1
                    if(found >= len(self.requests)):
                        break
                seek_count+=1
                if(self.current_position == self.end): break
                self.current_position += 1
                    
            if(found < len(self.requests)): # inicia descrendo do bloco de maior posição até o de menor
                while(self.current_position >= self.start):# indo de bloco em bloco ate o primeiro do intervalo
                    print("posição atual: ", self.current_position)
                    if(self.blocks[self.current_position].id == self.requests[found]):
                        visited_order.append(self.requests[found])
                        self.total_seek_time += seek_count
                        print(f"Requisição achada: {self.requests[found]}")
                        print(f"Tempo de seek parcial: {seek_count} u.t.\n")
                        seek_count = 0
                        visited_order.append(self.blocks[self.current_position])    
                        found += 1     
                        if(found >= len(self.requests)):
                            break
                    seek_count+=1
                    if(self.current_position == self.start): break
                    self.current_position -= 1
        block_ids = [f'block id: {block}' for block in visited_order]
        print(f'Blocos requisitados ordenados por visita: ')
        for block_id in block_ids:
            print(block_id)
        print(f"Tempo total de seek: {self.total_seek_time} u.t.")

def main(): 
    ds = None

    while True:
        print(' \n')
        print("1. Informe o intervalo de blocos mínimo e máximo em disco, e a posição inicial do braço")
        print("2. Gerar requisições")
        print("3. Executar algoritmo SCAN")
        print("10. Sair")
        opcao = int(input("Escolha uma opção: "))
        print(' \n')

        if opcao == 1:
            start = int(input("Informe o bloco mínimo: "))
            end = int(input("Informe o bloco máximo: "))
            print('deseja que o braço tenha uma posição inicial aleatória?')
            op = input('Caso queira escolher uma posição aperte (s): ')
            if(op =='s'):
                armPosition = int(input("Informe a posição inicial do braço: "))
                ds = DiskScheduler(start, end, armPosition)
            else:
                ds = DiskScheduler(start, end, None)
                print('Posição aleatória inicial do braço: ',ds.current_position)
        elif opcao == 2:
            if ds is not None:
                print('Deseja inserir um sequencia de blocos para visitar, ou deseja ter uma sequencia aleatória?')
                eu_quero = input("Caso queira digite 'eu quero': ")
                if(eu_quero != "eu quero"):
                    quantidade = int(input("Como você não quis escolher a sequência,\nDigite a quantidade de requisições aleatorias: "))
                    ds.generate_requests(None,quantidade)
                else:
                    ds.generate_requests(eu_quero,None)
                print("Requisições geradas: ", ds.requests)
            else:
                print("Por favor, informe o intervalo de blocos primeiro.")
        elif opcao == 3:
            if ds is not None:
                ds.scan_algorithm()
            else:
                print("Por favor, informe o intervalo de blocos e gere as requisições primeiro.")
        elif opcao == 10:
            print("Sistema encerrado.")
            break
        else:
            print("Opção inválida. Tente novamente.")
            

main()
