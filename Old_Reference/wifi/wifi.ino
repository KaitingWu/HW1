#include <WiFi.h> 
#include <MySQL_Connection.h>
#include <MySQL_Cursor.h>
#include <SimpleDHT.h> //DHT11 的標頭檔 

const char *ssid     = "alvin"; //ssid:網路名稱
const char *password = "20050423"; //pasword：網路密碼

IPAddress server_addr(192,168,137,254); //輸入你的 WIFI 的 IP Address

int MYSQLPort = 3306; //輸入 MySQL 使用的 port 號(預設為 3306)
char user[] = "test123"; //MySQL 使用者的帳號
char pass[] = "test123"; //MySQL 使用者的密碼
WiFiClient client;
MySQL_Connection conn((Client *)&client);
int pinDHT11 = 4; //把 DHT11 的 Data 腳位接在 GPIO 4
SimpleDHT11 dht11(pinDHT11); 

void setup() {
 Serial.begin(115200);
 delay(10);
 //連線你輸入的 WIFI
 WiFi.begin(ssid, password);
 while (WiFi.status() != WL_CONNECTED) {
 delay(500);
 Serial.print(".");
 }
 Serial.println("");
 Serial.println("WiFi connected");
 Serial.println("IP address: ");
 Serial.println(WiFi.localIP());

 //連線至 MySQL
 if (conn.connect(server_addr, 3306, user, pass))
 delay(1000);
else
 Serial.println("Connection failed.");
 delay(2000);
}
void loop() {
 //讀取 DHT11
 byte temperature = 0;
 byte humidity = 0;
 int err = SimpleDHTErrSuccess;
 if ((err = dht11.read(&temperature, &humidity, NULL)) !=
SimpleDHTErrSuccess) {
 Serial.print("Read DHT11 failed, err="); Serial.println(err);
delay(1000);
 return;
 }
Serial.print("Sample OK: ");
 Serial.print((int)temperature); Serial.print(" *C, ");
 Serial.print((int)humidity); Serial.println(" H");
 //將 DHT11 讀到的溫度與濕度傳至 MySQL
 String INSERT_SQL = "INSERT INTO tempandhumd.datalog (temp,humd) VALUES('" + String((int)temperature) + "','" + String((int)humidity) + "')";
//SQL 的語法
 MySQL_Cursor *cur_mem = new MySQL_Cursor(&conn);
 cur_mem->execute(INSERT_SQL.c_str()); //執行剛剛的 SQL 語法
 delete cur_mem; //因為已執行完 SQL 語法，不需要了，所以刪掉它
 Serial.println("Data Saved.");
 delay(6000);
}
