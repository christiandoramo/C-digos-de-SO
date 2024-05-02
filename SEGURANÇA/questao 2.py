# aluno: Christian Oliveira
# atividade: Prática Sistemas de arquivos

# RAID 0 - simples

from datetime import datetime
import getpass
import hashlib
import os
import time

def criptografar_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

class Disk:
    def __init__(self, id, blocks):
        self.id = id
        self.blocks = blocks

class Block:
    def __init__(self, id, size):
        self.id = id
        self.size = size
        self.next = None
        self.status = "livre"
        self.free_space = size
    def __str__(self):
        next_id = self.next.id if self.next else None
        return f'id:{self.id} next: {next_id} status: {self.status} free_space: {self.free_space}'

class File:
    def __init__(self, name, size):
        self.name = name
        self.password = None
        self.size = size
        self.creation_date = datetime.now()
        self.user_creator = None
        self.permissions = ["root"]
        self.blocks = []
        ext = name.split('.')[-1] if '.' in name else 'desconhecido'
        if(ext == 'desconhecido'):
            self.type = "Arquivo"
        elif ext=="txt":
            self.type = "Documento de texto (.txt)"
        else:
            self.type = f'Arquivo {ext.upper()} (.{ext})'

class Directory:
    def __init__(self, name):
        self.name = name
        self.password = None
        self.creation_date = datetime.now()
        self.type = 'Pasta de Arquivos'
        self.user_creator = None
        self.permissions = ["root"]
        self.contents = []
    def size(self):
        return sum(item.size for item in self.contents)

class FileSystem:
    def __init__(self, max_size, block_size, user, num_disks):
        self.max_size = max_size
        self.block_size = block_size
        self.root = Directory("/")
        self.root.permissions.append(user)
        self.user = user
        self.num_disks = num_disks
        self.disks = [Disk(i, [Block(i * (max_size // block_size) + j + 1, block_size) for j in range(max_size // block_size)]) for i in range(num_disks)]
    
    def set_password_file(self, path, name,user):
        file = self.find_file(path, name)
        if file and user in file.permissions:
            password = getpass.getpass("Digite uma senha para este arquivo: ")
            file.password = criptografar_senha(password)

    def check_password_file(self, path, name):
        file = self.find_file(path, name)
        if file:
            password = getpass.getpass("Digite a senha para acessar este arquivo: ")
            print(file.password == criptografar_senha(password))
            return file.password == criptografar_senha(password)
        return False  # Se o arquivo não existir, retorna False

    def add_permission_file(self, path, name,user):
        file = self.find_file(path, name)
        if file and user in file.permissions:
            if user not in file.permissions:
                file.permissions.append(user)

    def remove_permission_file(self, path, name, user):
        file = self.find_file(path, name)
        if file and user in file.permissions:
            if user in file.permissions:
                file.permissions.remove(user)

    def set_password_directory(self, path, name,user):
        directory = self.find_directory(path, name)
        if directory and user in directory.permissions:
            password = getpass.getpass("Digite uma senha para este arquivo: ")
            directory.password = criptografar_senha(password)

    def check_password_directory(self, path, name):
        file = self.find_directory(path, name)
        if file:
            password = getpass.getpass("Digite a senha para acessar este arquivo: ")
            print(file.password == criptografar_senha(password))
            return file.password == criptografar_senha(password)
        return False  # Se oarquivo não existir, retorna False

    def add_permission_directory(self, path, name,user):
        file = self.find_directory(path, name)
        if file and user in file.permissions:
            if user not in file.permissions:
                file.permissions.append(user)

    def remove_permission_directory(self, path, name, user):
        file = self.find_directory(path, name)
        if file and user in file.permissions:
            if user in file.permissions:
                file.permissions.remove(user)

    def allocate_blocks(self, size):
        num_blocks = size // self.block_size
        if size % self.block_size != 0:
            num_blocks += 1
        all_blocks = []
        for disk in self.disks:
            for disk_block in disk.blocks:
                all_blocks.append(disk_block)    
        disk_size = self.max_size // self.block_size
        sorted_blocks = sorted(all_blocks, key=lambda block: (block.id-1) % disk_size * len(self.disks) + block.id // disk_size)
        # distribuindo alocação entre os discos para RAID 0
        for x in sorted_blocks:
            print("sorted_blocks: ", x)
        blocks = [block for block in sorted_blocks if block.status == "livre"][:num_blocks]
        for x in blocks:
            print("blocks: ", x)
        if len(blocks) < num_blocks:
            return None
        for i in range(len(blocks) - 1): # não roda até o ultimo bloco pois é preenchido de outra forma
            blocks[i].next = blocks[i + 1]
            blocks[i].status = "ocupado"
            blocks[i].free_space = 0
        if blocks:
            blocks[-1].status = "ocupado"
        if size <= self.block_size:
            free_space = self.block_size - size
            print('condicional 1')
        elif (size % self.block_size == 0):
            free_space = 0
            print('condicional 2')
        elif (size % self.block_size != 0):
            freespace = size - (size % self.block_size)
        blocks[-1].free_space = free_space
        sorted_blocks_2 = sorted(blocks, key=lambda block: block.id) # reorganizando por id
        for x in sorted_blocks_2:
            print("sorted_blocks 2: ", x)
        return sorted_blocks_2

    def create_file(self, path, name, size):
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        if any(char in name for char in invalid_chars):
            print("Nome inválido. Não deve conter os seguintes caracteres: < > : \" / \\ | ? *")
            return
        dir = self.find_directory(path)
        blocks = None
        if dir and not any(item.name == name for item in dir.contents):
            blocks = self.allocate_blocks(size)
        else:
            print(f"Já existe um item com o nome {name} no diretório {path}.")
            return
        if blocks:
            file = File(name, size)
            file.blocks = blocks
            file.user_creator = self.user
            file.permissions.append(self.user)
            dir.contents.append(file)
        else:
            print("Não há blocos suficientes para criar o arquivo.")
    def create_directory(self, path, name):
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        if any(char in name for char in invalid_chars):
            print("Nome inválido. Não deve conter os seguintes caracteres: < > : \" / \\ | ? *")
            return
        else:
            dir = self.find_directory(path)
            if dir is None:
                print(f"O diretório {path} não foi encontrado.")
                return
            if any(item.name == name for item in dir.contents):
                print(f"Já existe um item com o nome {name} no diretório {path}.")
                return
            new_dir = Directory(name)
            new_dir.user_creator = self.user
            new_dir.permissions.append(self.user)
            dir.contents.append(new_dir)
    def delete_file(self, path, name,user):
        dir = self.find_directory(path)
        if dir:
            if user not in dir.permissions:
                print("voce nao tem acesso - diretorio\n")
                return
            if dir.password != None:
                comparacao = self.check_password_directory(path,name)
                if not comparacao:
                    print("Senha incorreta\n")
                    return
            achou = False
            for item in dir.contents:
                if item.name == name and isinstance(item, File):
                    achou = True
                if user not in dir.permissions:
                    print("voce nao tem acesso\n")
                    if dir.password != None:
                        comparacao = self.check_password_file(path,name)
                    if not comparacao:
                        print("Senha incorreta\n")
                    dir.contents.remove(item)
                    for block in item.blocks:
                        block.status = "livre"
                        block.free_space = self.block_size
                        block.next = None
                    break
            if(achou):
                print("arquivo removido com sucesso\n")
            else:
                print("arquivo não encontrado\n")
        else:
            print("pasta não encontrada")
    def delete_directory(self, path, name,user):
        dir = self.find_directory(path)
        if dir:
            if user not in dir.permissions:
                print("voce nao tem acesso\n")
                return
            if dir.password != None:
                comparacao = self.check_password_directory(path,name)
                if not comparacao:
                    print("Senha incorreta\n")
                    return
            print("diretório removido com sucesso\n")
            for item in dir.contents:
                if item.name == name and isinstance(item, Directory):
                    dir.contents.remove(item)
                    for subitem in item.contents:
                        if isinstance(subitem, File):
                            for disk in self.disks:
                                for block in disk.blocks:
                                    if block in subitem.blocks:
                                        block.status = "livre"
                                        block.free_space = self.block_size
                                        block.next = None
                    break
        else:
            print("diretório não encontrado\n")
    def count_subdirectories(self, directory):
        count = sum(1 for item in directory.contents if isinstance(item, Directory))
        for item in directory.contents:
            if isinstance(item, Directory):
                count += self.count_subdirectories(item)
        return count
    def total_directory_size(self, directory):
        total_size = sum(file.size for file in directory.contents if isinstance(file, File))
        for item in directory.contents:
            if isinstance(item, Directory):
                total_size += self.total_directory_size(item)
        return total_size
    def list_directory(self, path):
        dir = self.find_directory(path)
        print("\n")
        if dir:
            #contents = []
            for item in dir.contents:
                if isinstance(item, File):
                    #contents.append((item.name, item.size,item.user_creator,item.creation_date, item.permissions[0], item.permissions[1], item.type))
                    print(f"arquivo: {item.name} | criado por: {item.user_creator} | data de criação: {item.creation_date} | permissões: {item.permissions[0]} {item.permissions[1]}\n"+ 
                f" | tipo do arquivo: {item.type} | tamanho: {item.size}\nID(s) do(s) bloco(s) ocupado(s): {[block.id for block in item.blocks]}")
                elif isinstance(item, Directory):
                    total_size = self.total_directory_size(item)
                    num_subdirectories = self.count_subdirectories(item)
                    print(f"arquivo: {item.name} | criado por: {item.user_creator} | data de criação: {item.creation_date} | permissões: {item.permissions[0]} {item.permissions[1]}\n"+ 
                f" | tipo do arquivo: {item.type} | tamanho: {total_size} | subdiretorios: {num_subdirectories}")
        else:
            print("diretório vazio\n")
    def find_directory(self, path):
        parts = path.split("/")
        dir = self.root
        for part in parts:
            if part == "":
                continue
            for item in dir.contents:
                if isinstance(item, Directory) and item.name == part:
                    dir = item
                    break
            else:
                return None
        return dir
    
    def find_file(self, path, name):
        dir = self.find_directory(path)
        if dir:
            for item in dir.contents:
                if isinstance(item, File) and item.name == name:
                    return item
        return None


    def list_low_level(self, count):
        print("Sistema de arquivos em baixo nível\nBlocos:\n\n")
        for disk in self.disks:
            print(f"Disco: {disk.id}")
            for block in disk.blocks:
                print(f"id do bloco: {block.id} | status: {block.status}  | {f"aponta para o bloco com id {block.next.id}" if block.next else "aponta para nenhum bloco"} | espaço desocupado: {block.free_space} KB")
        time.sleep(count)
        print('\n\n')

    def show_files_and_directories(self, dir, path):
        print("\n")
        for item in dir.contents:
            if isinstance(item, File):
                print(f"nome: {item.name}\ncaminho: {path}/{item.name}\ncriado por: {item.user_creator}\ndata de criação: {item.creation_date}\npermissões: {item.permissions[0]} {item.permissions[1]}\n"+ 
                f"tipo do arquivo: {item.type}\ntamanho: {item.size}\nblocos ocupados: {[block.id for block in item.blocks]}")
            elif isinstance(item, Directory):
                total_size = sum(file.size for file in item.contents if isinstance(file, File))
                print(f"nome: {item.name}caminho: {path}/{item.name}\ncriada por: {item.user_creator}\ndata de criação: {item.creation_date}\npermissões: {item.permissions[0]} {item.permissions[1]}\n"+ 
                f"tipo do arquivo: {item.type}\ntamanho: {total_size}")
                self.show_files_and_directories(item, f'{path}/{item.name}')
            print("\n")
    def check_fragmentation(self):
        # Verifica a fragmentação interna
        total_size = sum(self.get_sizes(self.root))
        print("tamanho usado: ",total_size)
        total_blocks = total_size // self.block_size
        if total_size % self.block_size != 0:
            total_blocks += 1
        print("blocos usados: ",total_blocks)
        internal_frag = "Com fragmentação Interna" if total_blocks * self.block_size > total_size else "Sem fragmentação Interna"
        # Verifica a fragmentação externa
        external_frag = "Sem fragmentação Externa"
        for disk in self.disks:
            for i in range(len(disk.blocks) - 1):
                if disk.blocks[i].status == "livre" and disk.blocks[i+1].status == "ocupado":
                    external_frag = "Com fragmentação Externa"
                    break
        return internal_frag, external_frag

    def get_sizes(self, dir):
        sizes = []
        for item in dir.contents:
            if isinstance(item, File):
                sizes.append(item.size)
            else:
                sizes.extend(self.get_sizes(item))
        return sizes

def menu():
    fs = None
    user = input("Insira o nome do usuário: ")
    max_size = int(input("Digite o tamanho máximo de memória física em KB: "))
    block_size = int(input("Digite o tamanho dos blocos em KB: "))
    num_disks = int(input("Digite o número de discos: "))  # Solicita ao usuário o número 
    fs = FileSystem(max_size, block_size, user,num_disks)
    print('\n')
    while True:
        print("1. Criar arquivo")
        print("2. Excluir arquivo")
        print("3. Criar diretório")
        print("4. Excluir diretório")
        print("5. Listar arquivos e subdiretórios de uma pasta")
        print("6. Listar todos os arquivos e diretórios do sistema")
        print("7. Verificar fragmentação")
        print("8. Mostar baixo nível")
        print("9. Definir senha para um arquivo")
        print("10. Definir senha para um diretório")
        print("11. Adicionar permissão a um arquivo")
        print("12. Adicionar permissão a um diretório")
        print("13. Remover permissão a um arquivo")
        print("14. Remover permissão a um diretório")
        print("15. Sair")
        choice = input("Escolha uma opção: ")
        print("\n")
        if choice == "1":
            path = input("Digite o caminho do diretório: ")
            name = input("Digite o nome do arquivo: ")
            invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
            if any(char in name for char in invalid_chars):
                print("Arquivos e diretórios não devem conter os seguintes caracteres: < > : \" / \\ | ? *")
                print("\n")
                return
            size = int(input("Digite o tamanho do arquivo em KB: "))
            print("\n")
            fs.create_file(path, name, size)
            print("\n")
            fs.list_low_level(5)
        elif choice == "2":
            path = input("Digite o caminho do diretório: ")
            name = input("Digite o nome do arquivo: ")
            fs.delete_file(path, name,user)
            print("\n")
            fs.list_low_level(5)
        elif choice == "3":
            path = input("Digite o caminho do diretório: ")
            name = input("Digite o nome do diretório: ")
            print("\n")
            invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
            if any(char in name for char in invalid_chars):
                print("Arquivos e diretórios não devem conter os seguintes caracteres: < > : \" / \\ | ? *")
                return
            fs.create_directory(path, name)
            print("\n")
        elif choice == "4":
            path = input("Digite o caminho do diretório: ")
            name = input("Digite o nome do diretório: ")
            print("\n")
            fs.delete_directory(path, name,user)
        elif choice == "5":
            path = input("Digite o caminho do diretório: ")
            print("\n")
            fs.list_directory(path)
            print("\n")
        elif choice == "6":
            fs.show_files_and_directories(fs.root,"/")
            print("\n")
        elif choice == "7":
            print(fs.check_fragmentation())
            print("\n")
        elif choice == "8":
            fs.list_low_level(0)
        elif choice == "9":
            path = input("Digite o caminho do diretório: ")
            name = input("Digite o nome do arquivo: ")
            print('/')
            fs.set_password_file(path,name,user)
        elif choice == "10":
            path = input("Digite o caminho do diretório: ")
            name = input("Digite o nome do diretório: ")
            fs.set_password_directory(path,name,user)
        # ajustar aqui
        elif choice == "11":
            path = input("Digite o caminho do diretório: ")
            name = input("Digite o nome do arquivo: ")
            fs.add_permission_file(path,name,user)
        elif choice == "12":
            path = input("Digite o caminho do diretório: ")
            name = input("Digite o nome do diretório: ")
            fs.add_permission_directory(path,name,user)
        elif choice == "13":
            path = input("Digite o caminho do diretório: ")
            name = input("Digite o nome do arquivo: ")
            fs.remove_permission_file(path,name,user)
        elif choice == "14":
            path = input("Digite o caminho do diretório: ")
            name = input("Digite o nome do diretório: ")
            fs.remove_permission_directory(path,name,user)
        elif choice == "15":
            print("\n")
            print("Encerrando o Sistema...")
            time.sleep(0.33)
            print(".")
            time.sleep(.33)
            print("..")
            time.sleep(.33)
            print("...")
            time.sleep(1)
            print("Sistema de arquivos encerrado!")
            time.sleep(1)
            os.system("cls")
            # os.system("clear") linux
            break
        else:
            print("Escolha uma opção válida")

menu()
os.system("cls")