import requests
import os
import json

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
# Se tiver ID de Afiliado do Mercado Livre, coloque nos Secrets como 'ML_AFF_ID'
ML_AFF_ID = os.getenv('ML_AFF_ID', '') 

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'application/json',
}

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, data=data)
        print(f"Telegram Resposta: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Erro Telegram: {e}")

def buscar_ofertas_mercado_livre():
    print(">>> Buscando no Mercado Livre...")
    # API pública de busca de ofertas/deals do ML
    url = "https://api.mercadolibre.com/sites/MLB/deals/search?limit=5"
    
    try:
        resp = requests.get(url, headers=HEADERS)
        print(f"Status ML: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('results', [])
            if results:
                # Pega o primeiro produto
                item = results[0]
                nome = item.get('title')
                preco = item.get('price')
                link = item.get('permalink')
                
                # Adiciona ID de afiliado se existir
                if ML_AFF_ID:
                    link = f"{link}?af_id={ML_AFF_ID}"

                return {
                    "nome": nome,
                    "preco": f"R$ {preco:.2f}",
                    "link": link
                }
            else:
                print("ML retornou lista vazia.")
                return None
        else:
            print(f"Erro ML: {resp.text}")
            return None
    except Exception as e:
        print(f"Erro excecão ML: {e}")
        return None

def buscar_ofertas_shopee_fallback():
    # Fallback desativado temporariamente devido ao bloqueio 404
    return None

if __name__ == "__main__":
    # Tenta Mercado Livre
    produto = buscar_ofertas_mercado_livre()
    
    # Se não achar no ML, tenta Shopee (desativado no código acima, mas estrutura pronta)
    if not produto:
        produto = buscar_ofertas_shopee_fallback()

    # RESULTADO
    if produto:
        msg = f"""
🤖 <b>OFERTA AUTOMÁTICA</b>

📦 <b>Produto:</b> {produto['nome']}
💰 <b>Preço:</b> {produto['preco']}

👉 <a href="{produto['link']}">COMPRE AQUI</a>
"""
        enviar_telegram(msg)
    else:
        # Mensagem de teste para saber que o robô está vivo, mas sem ofertas
        msg
