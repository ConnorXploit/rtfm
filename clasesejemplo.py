
class Coche():

    def __init__(self, marca, matricula):
        self.marca = marca
        self.matricula = matricula
        self.andando = False

    def andar_parar(self):
        self.andando = not self.andando

    def pitar(self):
        print('Piiiii - {nom} - {mat} - Estado: {est}'.format(nom=self.marca, mat=self.matricula, est='Andando' if self.andando else 'Parado'))

class Concesionario():

    def __init__(self):
        self.coches = []

    def nuevo_coche(self, coche):
        self.coches.append(coche)

    def vender(self, coche):
        self.coches.remove(coche)

    def stock(self):
        if self.coches:
            for coche in self.coches:
                coche.pitar()
        else:
            print('No nos quedan coches')

coche1 = Coche('seat', '0000AAA')
coche2 = Coche('lambo', '1111AAA')

conc = Concesionario()

conc.nuevo_coche(coche1)
conc.nuevo_coche(coche2)

conc.stock()

print('-----------------------')

conc.vender(coche2)
coche1.andar_parar()

print('-----------------------')

conc.stock()