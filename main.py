import requests
import os

# --- CONFIGURAÇÕES (Pegando os segredos do GitHub) ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') # Vamos adicionar isso no próximo passo

def enviar_telegram(mensagem):
    """Envia mensagem para o canal do Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML" # Permite usar negrito, links, etc.
    }
    try:
        requests.post(url, data=data)
        print("Mensagem enviada com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar: {e}")

def buscar_promocoes():
    # AQUI Entrará a lógica da Shopee/Mercado Livre no futuro
    # Por enquanto, vamos retornar uma oferta teste
    return {
        "nome": "Fone Bluetooth Teste - Promoção Relâmpago",
        "preco": "R$ 49,90",
        "link": "https://shopee.com.br/exemplo"
    }

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    print("Iniciando o robô...")
    
    # Busca a oferta
    produto = buscar_promocoes()
    
    # Formata a mensagem bonitinha
    msg = f"""
🔥 <b>OFERTA IMPERDÍVEL!</b> 🔥

📱 <b>Produto:</b> {produto['nome']}
💰 <b>Preço:</b> {produto['preco']}

👉 <a href="{produto['link']}">CLIQUE AQUI PARA COMPRAR</a>
"""
    
    # Envia para o Telegram
    enviar_telegram(msg)
