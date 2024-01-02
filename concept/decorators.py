"""Decoradores en python"""
import functools


def deco(fn):
    '''Un decorator es una función que devuelve una función que contiene a otra
    dada como parámetro (fn en este caso) para añadir operaciones previas o 
    posteriores a su ejecución'''
    # wraps sirve para que la función apunte a fn y no a wrapper
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):  # Para pasarle los parámetros a la función
        print('decorating function')  # Paso previo añadido a la ejecución
        fn(*args, **kwargs)  # Ejecución de la función pasada como parámetro
        print('decorated function')  # Paso posterior añadido a la ejecución
    return wrapper


@deco
def say_hi():
    '''Función de ejemplo'''
    print('Hola')


# Al ejecutar esta función lo hará aplicando el decorador
say_hi()


@deco
def say_hi_to(name):
    """Ejemplo de decorador en funciones con parámetros"""
    print(f'hola {name}')


# Como en el decorador pasamos los parámetros, podremos ejecutar la función correctamente
say_hi_to('jlop')
