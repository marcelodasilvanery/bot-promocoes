import requests
import os
import random

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SHOPEE_AFF_ID = os.getenv('SHOPEE_AFF_ID')

# Headers cruciais para não ser bloqueado
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Referer': 'https://shopee.com.br/',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json',
}

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, data=data)
        print(f"Telegram Resposta: {resp.status_code}")
    except Exception as e:
        print(f"Erro Telegram: {e}")

def buscar_ofertas_shopee():
    print(">>> Iniciando busca na Shopee...")
    
    # API de busca da Shopee (procurando por "oferta" ou "promocao")
    # Isso é mais confiável do que tentar achar "Flash Sale" especifico
    termo_busca = "oferta%20imperdivel" # Termo de busca
    url_api = f"https://shopee.com.br/api/v4/search/search_item?by=relevancy&keyword={termo_busca}&limit=10&newest=0&order=desc&page_type=search"
    
    try:
        resp = requests.get(url_api, headers=HEADERS)
        print(f"Status Shopee: {resp.status_code}")
        
        # Se a Shopee bloquear (403 ou 404), avisamos no log
        if resp.status_code != 200:
            print(f"Erro ao acessar Shopee: {resp.text}")
            return None

        data = resp.json()
        
        # A estrutura padrão da busca é 'items'
        items = data.get('items', [])

        if not items:
            print("Lista de itens vazia.")
            return None

        # Pega um item aleatório
        produto_raw = random.choice(items)['item_basic']
        
        nome = produto_raw.get('name')
        item_id = produto_raw.get('itemid')
        shop_id = produto_raw.get('shopid')
        
        # Preço (Shopee manda em centavos, dividimos por 100000)
        preco_raw = produto_raw.get('price', 0) / 100000
        preco = f"R$ {preco_raw:.2f}".replace('.', ',')
        
        # Monta link com seu ID de afiliado
        link_produto = f"https://shopee.com.br/product/{shop_id}/{item_id}"
        link_afiliado = f"{link_produto}?af_siteid={SHOPEE_AFF_ID}"
        
        return {
            "nome": nome,
            "preco": preco,
            "link": link_afiliado
        }

    except Exception as e:
        print(f"Erro no processamento: {e}")
        return None

if __name__ == "__main__":
    produto = buscar_ofertas_shopee()
    
    if produto:
        msg = f"""
🔥 <b>OFERTA ENCONTRADA!</b>

📦 <b>Produto:</b> {produto['nome']}
💰 <b>Preço:</b> {produto['preco']}

👉 <a href="{produto['link']}">COMPRE AQUI</a>
"""
        enviar_telegram(msg)
    else:
        print("Falha ao buscar produto. Verifique os logs acima.")
