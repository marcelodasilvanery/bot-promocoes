import requests
import os
import json
import random

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# SEUS IDs DE AFILIADO (Coloque isso nos Secrets do GitHub)
# Shopee: Apenas o número (ex: 1234567890)
SHOPEE_ID = os.getenv('SHOPEE_AFF_ID', '') 
# Magalu: Geralmente é um parâmetro na URL ou ID de parceiro. 
# Se não tiver, deixe vazio.
MAGALU_ID = os.getenv('MAGALU_PARTNER_ID', '')

# Headers para parecer navegador
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
        print("✅ Mensagem enviada ao Telegram.")
    except Exception as e:
        print(f"❌ Erro Telegram: {e}")

def buscar_magalu():
    print(">>> Tentando Magazine Luiza...")
    # API aberta de produtos mais vendidos da Magalu
    url = "https://api-produtos.magazineluiza.com.br/product/grid?sortType=relevance&limit=5"
    
    try:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            produtos = data.get('products', [])
            if produtos:
                item = random.choice(produtos)
                nome = item.get('title')
                preco = f"R$ {item.get('price', 0):.2f}".replace('.', ',')
                link = item.get('url')
                
                # TENTA AFILIAÇÃO MAGALU
                # Nota: A Magalu exige cadastro no programa de parceiros para gerar link.
                # Se tiver um ID de parceiro, tentamos adicionar, mas geralmente
                # o link correto vem do painel deles. Aqui usamos o link direto.
                return {
                    "loja": "Magazine Luiza",
                    "nome": nome,
                    "preco": preco,
                    "link": link
                }
    except Exception as e:
        print(f"Erro Magalu: {e}")
    return None

def buscar_shopee_mobile():
    print(">>> Tentando Shopee (Método Mobile)...")
    # Endpoint alternativo que simula busca de celular
    url = "https://shopee.com.br/api/v4/recommend/recommend?bundle=flash_sale_landing_page_card&limit=5"
    
    try:
        # Headers específicos de celular para evitar bloqueio
        mob_headers = HEADERS.copy()
        mob_headers['User-Agent'] = 'okhttp/4.9.2' 
        
        resp = requests.get(url, headers=mob_headers)
        
        if resp.status_code == 200:
            data = resp.json()
            # A estrutura da resposta da Shopee muda muito. 
            # Tentamos encontrar a lista de itens de forma genérica.
            if 'data' in data and 'sections' in data['data']:
                secoes = data['data']['sections'][0]
                itens = secoes.get('data', {}).get('item', [])
                
                if itens:
                    p = itens[0]
                    item_id = p.get('itemid')
                    shop_id = p.get('shopid')
                    nome = p.get('name')
                    preco = f"R$ {p.get('price_min', 0) / 100000:.2f}".replace('.', ',')
                    
                    link_base = f"https://shopee.com.br/product/{shop_id}/{item_id}"
                    
                    # GERA LINK DE AFILIADO SHOPEE
                    # O parâmetro 'af_siteid' é o padrão para afiliação básica
                    link_final = f"{link_base}?af_siteid={SHOPEE_ID}" if SHOPEE_ID else link_base
                    
                    return {
                        "loja": "Shopee",
                        "nome": nome,
                        "preco": preco,
                        "link": link_final
                    }
    except Exception as e:
        print(f"Erro Shopee: {e}")
    return None

if __name__ == "__main__":
    produto = None
    
    # Estratégia: Tenta Magalu primeiro (mais estável), depois Shopee
    produto = buscar_magalu()
    
    if not produto:
        produto = buscar_shopee_mobile()

    # Se encontrou algo
    if produto:
        msg = f"""
🛒 <b>{produto['loja']}</b>

📦 <b>{produto['nome']}</b>
💰 <b>Preço:</b> {produto['preco']}

👉 <a href="{produto['link']}">COMPRAR AGORA</a>

<i>Link gerado automaticamente.</i>
"""
        enviar_telegram(msg)
    else:
        enviar_telegram("🤖 Robô pesquisando, mas Shopee/Magalu bloquearam a requisição automática agora. Tentarei mais tarde.")
