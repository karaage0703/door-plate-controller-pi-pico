from machine import Pin, SPI, PWM
import framebuf
import time
import os
import network
import urequests

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

# WiFi設定
WIFI_SSID = "your_ssid"
WIFI_PASSWORD = "your_password"


# ステータスURL
URLS = {
    "working": "http://192.168.xxx.xxx/child.html?status=working_for_child",
    "meeting": "http://192.168.xxx.xxx/child.html?status=meeting_for_child",
    "rest": "http://192.168.xxx.xxx/child.html?status=rest_for_child",
}


def connect_wifi():
    """WiFiに接続する関数"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("WiFiに接続中...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print("WiFi接続完了")
    print("IPアドレス:", wlan.ifconfig()[0])
    return wlan


def fetch_data(url):
    """指定されたURLからデータを取得する関数"""
    try:
        response = urequests.get(url)
        print("status_code = %d" % response.status_code)
    except Exception as e:
        print("エラー:", e)
        return None


class LCD_1inch3(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 240
        self.height = 240

        self.cs = Pin(CS, Pin.OUT)
        self.rst = Pin(RST, Pin.OUT)

        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1, 1000_000)
        self.spi = SPI(1, 100000_000, polarity=0, phase=0, sck=Pin(SCK), mosi=Pin(MOSI), miso=None)
        self.dc = Pin(DC, Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()

        self.red = 0x07E0
        self.green = 0x001F
        self.blue = 0xF800
        self.white = 0xFFFF

    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize dispaly"""
        self.rst(1)
        self.rst(0)
        self.rst(1)

        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A)
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35)

        self.write_cmd(0xBB)
        self.write_data(0x19)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x12)

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F)

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)

        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)

        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xEF)

        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xEF)

        self.write_cmd(0x2C)

        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)


if __name__ == "__main__":
    # バックライトの設定
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)  # max 65535

    # WiFi接続
    wlan = connect_wifi()

    # LCDの初期化
    LCD = LCD_1inch3()
    LCD.fill(LCD.white)
    LCD.show()

    # ボタンの設定
    keyA = Pin(15, Pin.IN, Pin.PULL_UP)
    keyB = Pin(17, Pin.IN, Pin.PULL_UP)
    keyC = Pin(19, Pin.IN, Pin.PULL_UP)

    while True:
        if keyA.value() == 0:  # keyAが押されたら緑色と作業中状態
            LCD.fill(LCD.green)
            fetch_data(URLS["working"])
        elif keyB.value() == 0:  # keyBが押されたら赤色と会議中状態
            LCD.fill(LCD.red)
            fetch_data(URLS["meeting"])
        elif keyC.value() == 0:  # keyCが押されたら青色と休憩中状態
            LCD.fill(LCD.blue)
            fetch_data(URLS["rest"])

        LCD.show()
        time.sleep(0.1)  # チャタリング防止
