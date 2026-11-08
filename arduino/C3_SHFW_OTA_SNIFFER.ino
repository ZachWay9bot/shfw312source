/* Passive G30D 3-Cap UART collector: ESP32-C3 GPIO20 RX only.
 * USB CDC/JTAG forwards binary bytes; never connects a UART TX to the scooter.
 * Requires 3.3-V compatible levels and common GND.
 * ESP32C3 Dev Module; USB CDC On Boot ENABLED; USB Mode hardware USB CDC/JTAG.
 */
#include <Arduino.h>
#include <driver/uart.h>
#include <esp_idf_version.h>
#if !defined(CONFIG_IDF_TARGET_ESP32C3)
#error "Select an ESP32-C3 board"
#endif
#if !defined(ARDUINO_USB_CDC_ON_BOOT) || !ARDUINO_USB_CDC_ON_BOOT
#error "USB CDC On Boot must be enabled"
#endif

static const uart_port_t U=UART_NUM_1;
static const int RX_PIN=20;
static uint8_t rx[1024];

void setup() {
  Serial.begin(115200);
  uart_config_t cfg={};
  cfg.baud_rate=115200;
  cfg.data_bits=UART_DATA_8_BITS;
  cfg.parity=UART_PARITY_DISABLE;
  cfg.stop_bits=UART_STOP_BITS_1;
  cfg.flow_ctrl=UART_HW_FLOWCTRL_DISABLE;
#if ESP_IDF_VERSION_MAJOR >= 5
  cfg.source_clk=UART_SCLK_DEFAULT;
#else
  cfg.source_clk=UART_SCLK_APB;
#endif
  if(uart_param_config(U,&cfg)!=ESP_OK) while(1) delay(1000);
  if(uart_set_pin(U,UART_PIN_NO_CHANGE,RX_PIN,UART_PIN_NO_CHANGE,UART_PIN_NO_CHANGE)!=ESP_OK) while(1) delay(1000);
  if(uart_driver_install(U,16384,0,0,nullptr,0)!=ESP_OK) while(1) delay(1000);
  while(!Serial) delay(5);
}
void loop() {
  int n=uart_read_bytes(U,rx,sizeof(rx),pdMS_TO_TICKS(5));
  int offset=0;
  while(offset<n){
    if(!Serial) return;
    size_t sent=Serial.write(rx+offset,(size_t)(n-offset));
    if(!sent) delay(1);
    else offset+=(int)sent;
  }
}
