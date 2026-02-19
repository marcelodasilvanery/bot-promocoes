import requests
import os
import random
import time

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
# SEU ID DE AFILIADO SHOPEE (O número que você acabou de pegar)
SHOPEE_AFF_ID = os.getenv('SHOPEE_AFF_ID') 

# Headers para parecer um navegador real (evita bloqueio)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
}

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
        print("Enviado para o Telegram!")
    except Exception as e:
        print(f"Erro Telegram: {e}")

def buscar_ofertas_shopee_scraping():
    """
    Busca ofertas na API interna da Shopee (usada pelo celular/site).
    Método robusto que não precisa de Partner Key.
    """
    print("Buscando ofertas na Shopee...")
    
    # API interna da Shopee para buscar "Flash Sale" (Ofertas do Dia)
    # O 'limit=5' busca 5 ofertas. Pegaremos 1 aleatória.
    url_api = "https://shopee.com.br/api/v4/recommend/recommend?bundle=flash_sale_landing_page_card&limit=10"
    
    try:
        # Faz a requisição disfarçado de navegador
        resp = requests.get(url_api, headers=HEADERS)
        data = resp.json()
        
        # Navega na estrutura do JSON para achar os produtos
        # A estrutura pode mudar, mas geralmente está em 'data' -> 'sections'
        # Vamos tentar achar os itens direto na resposta principal para simplificar
        items = data.get('data', {}).get('sections', [{}])[0].get('data', {}).get('item', {})
        
        if not items:
             # Se achar vazio, tentamos outra estrutura comum
             items = data.get('data', {}).get('sections', [{}])[0].get('data', {}).get('items', [])

        if items:
            # Escolhe um produto aleatório
            produto_raw = random.choice(items)
            
            # Extrai dados
            nome = produto_raw.get('name', 'Produto Incrível')
            preco_centavos = produto_raw.get('price_min', 0) / 100000
            preco_formatado = f"R$ {preco_centavos:.2f}".replace('.', ',')
            
            item_id = produto_raw.get('itemid')
            shop_id = produto_raw.get('shopid')
            
            # Monta o link direto
            link_direto = f"https://shopee.com.br/product/{shop_id}/{item_id}"
            
            # ADICIONA SEU ID DE AFILIADO (A Mágica)
            # Adiciona o parâmetro ?af_siteid=SEU_ID
            link_afiliado = f"{link_direto}?af_siteid={SHOPEE_AFF_ID}"
            
            return {
                "nome": nome,
                "preco": preco_formatado,
                "link": link_afiliado
            }
        else:
            print("Estrutura do JSON mudou ou sem produtos.")
            return None
            
    except Exception as e:
        print(f"Erro ao buscar Shopee: {e}")
        return None

if __name__ == "__main__":
    produto = buscar_ofertas_shopee_scraping()
    
    if produto:
        msg = f"""
🔥 <b>OFERTA AUTOMÁTICA SHOPEE</b> 🔥

📦 <b>Produto:</b> {produto['nome']}
💰 <b>Preço:</b> {produto['preco']}

👉 <a href="{produto['link']}">COMPRE AQUI</a>

<i>(Link de afiliado gerado automaticamente)</i>
"""
        enviar_telegram(msg)
    else:
        print("Nenhuma oferta encontrada hoje.")
