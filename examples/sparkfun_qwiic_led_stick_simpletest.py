import board
import time
from rainbowio import colorwheel
from sparkfun_qwiic_led_stick import QwiicLEDStick

i2c = board.STEMMA_I2C()
pixels = QwiicLEDStick(i2c, brightness=0.1, auto_write=False)
# pixels.LED_off()

pixels.optimized_fill(0)

# while True:
#     pixels.fill(0)
#     pixels.show()
#     time.sleep(1)
#     pixels.optimized_fill(0x500050)
#     time.sleep(1)
#     pixels.fill(0x008000)
#     pixels.show()
#     time.sleep(1)
#     pixels.optimized_fill(0x808000)
#     time.sleep(1)
#     pixels.fill(0x008080)
#     pixels.show()
#     time.sleep(1)

while True:
    for n in range(0,256,4):
        for i in range(10):
            pixels[i] = colorwheel(n + 4 * i)
        pixels.show()
        time.sleep(0.1)
    print(pixels.retries)
