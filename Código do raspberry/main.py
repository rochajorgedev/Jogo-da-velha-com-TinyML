from machine import Pin, ADC
import neopixel
import time

# ===== Configurações =====
WIDTH, HEIGHT      = 5, 5
LED_PIN            = 7
BUTTON_PIN         = 22
ADC_X_PIN, ADC_Y_PIN = 27, 26

BLINK_INTERVAL_MS  = 500

# cores
RED    = (255, 0, 0)
BLUE   = (0, 0, 255)
OFF    = (0, 0, 0)
GRID   = (50, 50, 50)

# posições das linhas da grade
VERT_LINES   = [1, 3]
HORIZ_LINES  = [1, 3]

# ===== Inicializações =====
np    = neopixel.NeoPixel(Pin(LED_PIN), WIDTH * HEIGHT)
btn   = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
adc_x = ADC(Pin(ADC_X_PIN))
adc_y = ADC(Pin(ADC_Y_PIN))

adc_min, adc_max = 300, 65535

# armazena {índice_led: cor_fixa}
fixed_marks = {}

# cor que será usada na próxima marcação
next_color = RED

# controle do piscar do cursor
last_toggle = time.ticks_ms()
blink_on    = False

def idx(x, y):
    return y * WIDTH + x

def map_adc(val):
    raw = int((val - adc_min) / (adc_max - adc_min + 1) * WIDTH)
    return min(max(raw, 0), WIDTH - 1)

def draw_grid():
    # apaga tudo
    for i in range(WIDTH * HEIGHT):
        np[i] = OFF
    # desenha linhas verticais
    for x in VERT_LINES:
        for y in range(HEIGHT):
            np[idx(x, y)] = GRID
    # desenha linhas horizontais
    for y in HORIZ_LINES:
        for x in range(WIDTH):
            np[idx(x, y)] = GRID

# ===== Loop principal =====
while True:
    # atualiza estado do piscar
    now = time.ticks_ms()
    if time.ticks_diff(now, last_toggle) > BLINK_INTERVAL_MS:
        blink_on    = not blink_on
        last_toggle = now

    # lê joystick e converte em 0..4
    x = WIDTH - 1 - map_adc(adc_x.read_u16())
    y = map_adc(adc_y.read_u16())
    pos = idx(x, y)

    # desenha grade e marcas fixas
    draw_grid()
    for m_idx, color in fixed_marks.items():
        np[m_idx] = color

    # faz o cursor piscar na cor da próxima marca
    if pos not in fixed_marks and blink_on:
        np[pos] = next_color

    np.write()

    # ao pressionar botão, fixa a cor e alterna para a próxima
    if btn.value() == 0:
        # debounce – espera o botão soltar
        while btn.value() == 0:
            time.sleep_ms(10)
        # só marca se não houver nada ali
        if pos not in fixed_marks:
            fixed_marks[pos] = next_color
            # alterna cor para a próxima seleção
            next_color = BLUE if next_color == RED else RED
    print(fixed_marks)

    time.sleep_ms(20)

