from scapy.all import *
from scapy.layers.tls.all import *
import sys
# Проверяем, передал ли пользователь домен
if len(sys.argv) < 2:
    print("Ошибка: Вы не указали домен!")
    print("Использование: sudo python tls_trace.py <домен>")
    sys.exit(1)
target = sys.argv[1]
# Шаблон минимального TLS Client Hello
tls_payload = TLS(msg=[TLSClientHello(version="TLS 1.2")])

for ttl in range(1, 30):
    # Строим пакет: IP (с TTL) -> TCP (порт 443) -> TLS Payload
    pkt = IP(dst=target, ttl=ttl)/TCP(sport=RandShort(), dport=443, flags="PA")/tls_payload
    
    # Отправляем и ждем ответ 2 секунды
    reply = sr1(pkt, timeout=2, verbose=0)
    
    if reply is None:
        print(f"Hop {ttl}: * * * (Timeout)")
    elif reply.haslayer(ICMP):
        # Получен ответ от промежуточного роутера
        print(f"Hop {ttl}: {reply.src} (TTL Exceeded)")
    elif reply.haslayer(TCP):
        # Дошли до целевого сервера!
        print(f"Hop {ttl}: {reply.src} (Reached Target via TCP)")
        break
