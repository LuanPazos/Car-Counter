import cv2
import numpy as np
from time import sleep
from constantes import *


def pega_centro(x, y, largura, altura):
    """
    :param x: x do objeto
    :param y: y do objeto
    :param largura: largura do objeto
    :param altura: altura do objeto
    :return: tupla que contém as coordenadas do centro de um objeto
    """
    x1 = largura // 2 
    y1 = altura // 2 
    cx = x + x1 # Pega o centro do objeto na cordenada x
    cy = y + y1 # Pega o centro do objeto na cordenada y
    return cx, cy # Retorna o centro do objeto


def set_info(detec):
    global carros 
    for (x, y) in detec: # Percorre a lista de objetos detectados
        if (pos_linha + offset) > y > (pos_linha - offset): # Se o objeto estiver na linha:
            carros += 1
            cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (0, 127, 255), 3) # Linha de contagem
            detec.remove((x, y)) # Para não contar o mesmo carro mais de uma vez
            print("Carros detectados até o momento: " + str(carros))


def show_info(frame1, dilatada): # Mostra as informações na tela
    text = f'Carros: {carros}' 
    cv2.putText(frame1, text, (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5) # Texto na tela
    cv2.imshow("Video Original", frame1) # Mostra o vídeo original
    cv2.imshow("Detectar", dilatada) # Mostra o vídeo com a subtração


carros =  0 
cap = cv2.VideoCapture('video.mp4')  # Pega o vídeo
subtracao = cv2.bgsegm.createBackgroundSubtractorMOG()  # Pega o fundo e subtrai do que está se movendo

while True:
    ret, frame1 = cap.read()  # Pega cada frame do vídeo
    tempo = float(1 / delay)
    sleep(tempo)  # Dá um delay entre cada processamento
    grey = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)  # Pega o frame e transforma para preto e branco
    blur = cv2.GaussianBlur(grey, (3, 3), 5)  # Faz um blur para tentar remover as imperfeições da imagem
    img_sub = subtracao.apply(blur)  # Faz a subtração da imagem aplicada no blur
    dilat = cv2.dilate(img_sub, np.ones((5, 5)))  # "Engrossa" o que sobrou da subtração
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (
        5, 5))  # Cria uma matriz 5x5, em que o formato da matriz entre 0 e 1 forma uma elipse dentro
    dilatada = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)  # Tenta preencher todos os "buracos" da imagem
    dilatada = cv2.morphologyEx(dilatada, cv2.MORPH_CLOSE, kernel)

    contorno, img = cv2.findContours(dilatada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (255, 127, 0), 3)
    for (i, c) in enumerate(contorno):
        (x, y, w, h) = cv2.boundingRect(c)
        validar_contorno = (w >= largura_min) and (h >= altura_min)
        if not validar_contorno:
            continue

        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
        centro = pega_centro(x, y, w, h)
        detec.append(centro)
        cv2.circle(frame1, centro, 4, (0, 0, 255), -1)

    set_info(detec)
    show_info(frame1, dilatada)

    if cv2.waitKey(1) == 27: # Tecla Esc para sair
        break

cv2.destroyAllWindows()
cap.release()

