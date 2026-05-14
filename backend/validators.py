import re


def validate_rut(rut: str) -> bool:
    """
    Valida un RUT chileno completo.
    Retorna True si el formato es válido y el dígito verificador coincide,
    False en caso contrario.
    """
    if not isinstance(rut, str):
        return False
    # Normalizar: remover puntos, guiones y espacios; pasar a mayúsculas
    rut = rut.strip().upper().replace('.', '').replace('-', '')
    # El RUT debe tener entre 7 y 8 dígitos en el cuerpo
    if not re.match(r'^\d{7,8}[0-9K]$', rut):
        return False
    cuerpo = rut[:-1]
    dv = rut[-1]
    # Cálculo del dígito verificador (módulo 11)
    suma = 0
    multiplicador = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador == 8:
            multiplicador = 2
    resto = 11 - (suma % 11)
    if resto == 11:
        dv_calculado = '0'
    elif resto == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(resto)
    return dv == dv_calculado
