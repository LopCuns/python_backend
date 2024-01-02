'''Clases en python'''


class Persona:
    '''Clase de ejemplo'''

    def __init__(self, name: str, surname: str, nation: str, postcode: int):
        self.name = name
        self.surname = surname
        self.nation = nation
        # Propiedad privada (no puede ser leida ni modificada desde el exterior)
        self.__postcode = postcode

    def greeting(self):
        '''Método de la clase'''
        print(
            f'Hola, me llamo {self.name} {self.surname}, soy de {self.nation}')

    def get_postcode(self):
        '''Método para leer una propiedad privada'''
        return self.__postcode

    def set_postcode(self, postcode: int):
        '''Método para modificar una propiedad privada'''
        self.__postcode = postcode


# Crear una instancia de la clase
jlop = Persona('jlop', 'cuns', 'España', 1808)
# Llamar a un método de la clase
jlop.greeting()
# Obtener un atributo privado
print(jlop.get_postcode())
# Modificar un atributo privado
jlop.set_postcode(1812)
print(jlop.get_postcode())

# Crear una clase que hereda de otra


class Spanish(Persona):
    '''Ejemplo de herencia'''

    def __init__(self, name, surname, postcode):
        super().__init__(name, surname, 'España', postcode)

    def greeting(self):
        print(f'Arriba España, soy {self.name} {self.surname}')


jlop_spanish = Spanish('jlop', 'cuns', 1808)
print(jlop_spanish.get_postcode())

# Uso de los métodos dunder (double underscore methods)


class PersonalizedNumber:
    '''Ejemplo de uso de los métodos dunder (double underscore methods) 
    para crear comportamientos personalizados'''

    def __init__(self, value):
        self.value = value

    def __abs__(self):
        # Creamos el método __abs__ para que python utilize este comportamiento personalizado
        # al llamar a la funcións abs()
        return f'el valor absoluto de {self.value} es {abs(self.value)}'


myPersoNumber = PersonalizedNumber(-5)
print(abs(myPersoNumber))
