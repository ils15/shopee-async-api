import os; from dotenv import load_dotenv; load_dotenv(); print('SHOPEE_APP_ID is set' if os.getenv('SHOPEE_APP_ID') else 'Missing SHOPEE_APP_ID')
