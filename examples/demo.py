import asyncio
import os
from dotenv import load_dotenv

from shopee_async_api.client import ShopeeAffiliateClient

async def main():
    # Load environment variables from .env file
    load_dotenv()
    
    app_id = os.getenv("SHOPEE_APP_ID", "")
    secret = os.getenv("SHOPEE_SECRET", "")
    
    if not app_id or not secret:
        print("Erro: SHOPEE_APP_ID ou SHOPEE_SECRET não encontrados no arquivo .env.")
        print("Por favor, preencha suas credenciais no arquivo .env e tente novamente.")
        return

    print("🔑 Credenciais carregadas com sucesso. Testando a API do Shopee...\n")
    
    async with ShopeeAffiliateClient(app_id=app_id, secret=secret) as client:
        try:
            print("1️⃣ Testando Endpoint: generate_short_link")
            # Link fornecido pelo usuário para teste
            test_url = "https://shopee.com.br/Xiaomi-S40-Pro-Rob%C3%B4-Aspirador-15000Pa-Bra%C3%A7o-Extens%C3%ADvel-Mop-Inteligente-Bivolt-Original-Lan%C3%A7amento-2026-i.1200876177.22194837125" 
            result = await client.generate_short_link(origin_url=test_url, sub_ids=["test1", "demo2"])
            print(f"✅ Link curto gerado: {result.shortLink}")
            
            print("\n2️⃣ Testando Endpoint: get_shopee_offer_list (Top 3 Ofertas)")
            offer_list = await client.get_shopee_offer_list(limit=3)
            for idx, offer in enumerate(offer_list.nodes, 1):
                print(f"  - Oferta {idx}: {offer.offerName} (Comissão: {offer.commissionRate})")
            
            print("\n🚀 Todos os testes preliminares concluídos com sucesso!")
            
        except Exception as e:
            print(f"\n❌ Ocorreu um erro durante o teste da API: {e}")

if __name__ == "__main__":
    asyncio.run(main())
