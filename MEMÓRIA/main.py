import random

class Process:
    def __init__(self, name, process_id, size):
        self.name = name
        self.process_id = process_id
        self.size = size
        self.pages = []

class Page:
    def __init__(self, page_id, process_id):
        self.page_id = page_id
        self.process_id = process_id

class Memory:
    def __init__(self, physical_size, virtual_size, page_size):
        self.physical_size = physical_size
        self.virtual_size = virtual_size
        self.page_size = page_size
        self.physical_memory = [None] * (physical_size // page_size)
        self.virtual_memory = [None] * (virtual_size // page_size)

    def allocate_page(self, process):
        if process.size > self.virtual_size:
            print(f"Error: Process {process.name} size exceeds virtual memory size.")
            return

        required_pages = (process.size // self.page_size) + (1 if process.size % self.page_size != 0 else 0)

        if required_pages > self.get_free_pages():
            self.page_replacement_algorithm()

        for i in range(len(self.virtual_memory)):
            if self.virtual_memory[i] is None:
                page = Page(i, process.process_id)
                process.pages.append(page)
                self.virtual_memory[i] = page
                self.allocate_physical_memory(page)
                break

    def allocate_physical_memory(self, page):
        for i in range(len(self.physical_memory)):
            if self.physical_memory[i] is None:
                self.physical_memory[i] = page
                break

    def get_free_pages(self):
        return self.virtual_memory.count(None)

    def page_replacement_algorithm(self):
        # Implement your page replacement algorithm here (e.g., FIFO, LRU, Clock, etc.)
        pass

def main():
    # Configurações
    physical_size = 1024  # Tamanho máximo de memória física (em KB)
    virtual_size = 2048   # Tamanho máximo de memória virtual (em KB)
    page_size = 64        # Tamanho das páginas (em KB)

    # Criação de processos
    processes = [
        Process("Process1", 1, 128),
        Process("Process2", 2, 256),
        Process("Process3", 3, 192),
        # Adicione mais processos conforme necessário
    ]

    # Criação de memória
    memory = Memory(physical_size, virtual_size, page_size)

    # Alocação de páginas para processos
    for process in processes:
        memory.allocate_page(process)

    # Simulação de referências às páginas (FIFO)
    for i in range(100):
        random_process = random.choice(processes)
        random_page = random.choice(random_process.pages)
        # Simule a referência à página aqui

    # Ao final, calcule e exiba a quantidade de "page miss" para cada algoritmo de substituição de página
    # Implemente essa parte conforme a lógica do seu algoritmo de substituição de página escolhido

if __name__ == "__main__":
    main()

