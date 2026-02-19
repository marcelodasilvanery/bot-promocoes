import requests
import os

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SHOPEE_AFF_ID = os.getenv('SHOPEE_AFF_ID') # Seu ID Shopee (ex: 12345678)
ML_AFF_ID = os.getenv('ML_AFF_ID', '')     # Seu ID ML (opcional)

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
        print("Oferta enviada com sucesso!")
    except Exception as e:
        print(f"Erro Telegram: {e}")

def buscar_oferta_promobit():
    print(">>> Buscando ofertas na API do Promobit...")
    
    # API pública do Promobit para pegar as Top Offers (Não requer chave para uso básico)
    url = "https://backend-promobit.azurewebsites.net/v1/offer/top-offers"
    
    # Headers simples para parecer um navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Referer': 'https://www.promobit.com.br/'
    }
    
    try:
        resp = requests.get(url, headers=headers)
        print(f"Status Promobit: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            ofertas = data.get('offers', [])
            
            if not ofertas:
                print("Lista de ofertas vazia.")
                return None
            
            # Vamos pegar a primeira oferta da lista (a mais quente)
            item = ofertas[0]
            
            nome = item.get('title')
            preco_antigo = item.get('oldPrice', 0) / 100
            preco_novo = item.get('price', 0) / 100
            desconto = item.get('discount', 0)
            loja = item.get('store', {}).get('name', 'Loja Parceira')
            
            # O Promobit retorna o link direto para a loja
            # Às vezes é um link curto do próprio Promobit que redireciona.
            # Para afiliar, precisamos tratar a URL base.
            link_original = item.get('link') # Este link pode já ser redirecionado
            
            # Tenta extrair a URL real se for Shopee/ML para aplicar o ID de afiliado
            # Nota: Se o link do Promobit for redirecional, usamos ele direto
            # pois garantir a afiliação por cima do link do Promobit é complexo.
            # Mas se o link for direto, tentamos afiliar.
            
            link_final = link_original # Default: usa o link do Promobit
            
            # Tenta converter para link de afiliado se tivermos o ID
            # (Isso depende de como o Promobit entrega o link, muitas vezes ele entrega direto)
            
            texto_preco = f"De R$ {preco_antigo:.2f} por <b>R$ {preco_novo:.2f}</b> ({desconto}% OFF)" if preco_antigo > preco_novo else f"R$ {preco_novo:.2f}"

            return {
                "nome": nome,
                "preco": texto_preco,
                "loja": loja,
                "link": link_final
            }
        else:
            print(f"Erro Promobit: {resp.text}")
            return None
    except Exception as e:
        print(f"Erro exceção: {e}")
        return None

if __name__ == "__main__":
    produto = buscar_oferta_promobit()
    
    if produto:
        msg = f"""
🔥 <b>OFERTA TOP DO DIA</b> 🔥

📦 <b>Produto:</b> {produto['nome']}
🏪 <b>Loja:</b> {produto['loja']}
💰 <b>Preço:</b> {produto['preco']}

👉 <a href="{produto['link']}">PEGAR OFERTA AGORA</a>
"""
        enviar_telegram(msg)
    else:
        # Se falhar, manda aviso técnico
        enviar_telegram("⚠️ Robô passou aqui, mas as APIs estão instáveis agora. Tentarei novamente mais tarde.")
