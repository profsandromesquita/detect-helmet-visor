import cv2
import numpy as np
import winsound # Importa a biblioteca para tocar o som
import threading  # Importa a biblioteca para trabalhar com threads

# Inicializa um contador e define um limiar para mudança de estado
contador_viseira_fechada = 0
limiar_para_mudanca = 2  # Número de detecções consistentes para mudar o estado
area_minima_contorno = 500  # Define a área mínima que um contorno deve ter para ser considerado

class Alarme(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True  # Define a thread como um daemon para que ela termine quando o programa principal terminar
        self.playing = threading.Event()

    def run(self):
        while True:
            self.playing.wait()  # Espera até que o sinal para tocar seja dado
            winsound.Beep(1000, 200)  # Toca um bip

    def start_alarm(self):
        self.playing.set()  # Define o sinal para tocar

    def stop_alarm(self):
        self.playing.clear()  # Limpa o sinal para tocar

# Inicializa a thread de alarme
alarme = Alarme()
alarme.start()

def detect_lime_green(frame, contador_viseira_fechada):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Intervalo de cor HSV para detectar azul
    lower_blue = np.array([90, 100, 100])
    upper_blue = np.array([120, 255, 255])

    # Criar a máscara para detectar a cor azul
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Encontrar contornos na máscara
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filtra contornos que tenham uma área mínima
    contours = [c for c in contours if cv2.contourArea(c) > area_minima_contorno]
    print(len(contours))
    # Detecta a viseira aberta ou fechada com base no número de contornos
    if len(contours) >= 2:
        # Se dois ou mais contornos grandes são detectados, presume-se que a viseira está aberta
        contador_viseira_fechada = max(contador_viseira_fechada - 1, 0)
        if contador_viseira_fechada <= 0:
            cv2.putText(frame, "Helmet visor OPEN", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (45, 173, 238), 3)
            # Inicia a thread de som
            alarme.start_alarm()

    elif len(contours) == 1:
        cv2.putText(frame, "Helmet visor CLOSE", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        alarme.stop_alarm()  # Interrompe o alarme imediatamente quando a viseira é detectada como fechada
    else:
        cv2.putText(frame, "Helmet NOT DETECTED", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        alarme.stop_alarm()  # Interrompe o alarme imediatamente quando a viseira é detectada como fechada

    # Aplica a máscara na imagem original para mostrar apenas a cor detectada
    result = cv2.bitwise_and(frame, frame, mask=mask)
    return result, frame, contador_viseira_fechada

cap = cv2.VideoCapture(0)

# Cria uma janela nomeada que será usada para exibição
cv2.namedWindow("Detect Open Helmet Visor", cv2.WND_PROP_FULLSCREEN)

# Configura a janela para o modo de tela cheia
cv2.setWindowProperty("Detect Open Helmet Visor", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    detected_frame, original_frame, contador_viseira_fechada = detect_lime_green(frame.copy(), contador_viseira_fechada)
    cv2.imshow('Detect Open Helmet Visor', original_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

