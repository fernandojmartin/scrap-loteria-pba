import fitz
import json
from fitz.fitz import Document

doc = fitz.open('QuinielaMatutina.pdf')
page = doc[0]
blocks = list(block[4] for block in page.get_text('blocks'))
# for i, p in enumerate(blocks):
    # print(i,' => ',p)

fecha = blocks[0]
sorteo = blocks[10]
distrito1 = blocks[12]
turno1 = blocks[13]
premios1 = blocks[16:36]
numeros1 = [premio.strip().split('\n', 1)[1] for premio in premios1]
numeros1 = {puesto: numero for puesto, numero in enumerate(numeros1,1)}

# print(fecha, sorteo, distrito1, turno1, premios1)
print("Fecha:", fecha.strip())
print("Sorteo:", sorteo.strip())
print("Quiniela", distrito1.strip().upper(), '- Turno:', turno1.strip())
print('Numeros:', numeros1)
json.dumps(numeros1)



