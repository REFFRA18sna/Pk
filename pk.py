import requests
import telebot

# Initialize the bot with your token
bot = telebot.TeleBot("7034550037:AAH9iEaGBHbZRvfNKWj1OKzjySvqKhPglsg")
r = requests.Session()

# Initialize variables
pk = None
secretpi = None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome to the Payment Checker Bot!")

@bot.message_handler(commands=['pk'])
def set_pk(message):
    global pk
    pk = message.text.split()[1] if len(message.text.split()) > 1 else None
    bot.reply_to(message, f"PK set to: {pk}")

@bot.message_handler(commands=['pi'])
def set_pi(message):
    global secretpi
    secretpi = message.text.split()[1] if len(message.text.split()) > 1 else None
    bot.reply_to(message, f"Secret PI set to: {secretpi}")

def process_card(cc, mes, ano, cvv, pk, secretpi):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        "Pragma": "no-cache",
        "Accept": "/"
    }

    response = r.post("https://m.stripe.com/6", headers=headers)
    json_data = response.json()
    m = json_data.get("muid")
    s = json_data.get("sid")
    g = json_data.get("guid")

    index = secretpi.find('_secret_')
    pi = secretpi[:index] if index != -1 else None

    data = f'payment_method_data[type]=card&payment_method_data[billing_details][name]=skibidi+sigma+csub&payment_method_data[card][number]={cc}&payment_method_data[card][exp_month]={mes}&payment_method_data[card][exp_year]={ano}&payment_method_data[guid]={g}&payment_method_data[muid]={m}&payment_method_data[sid]={s}&payment_method_data[pasted_fields]=number&expected_payment_method_type=card&use_stripe_sdk=true&key={pk}&client_secret={secretpi}'
    response = r.post(f'https://api.stripe.com/v1/payment_intents/{pi}/confirm', headers=headers, data=data)

    response_json = response.json()
    code = response_json.get("error", {}).get("code")
    decline_code = response_json.get("error", {}).get("decline_code")
    message = response_json.get("error", {}).get("message")

    if '"status": "succeeded"' in response.text:
        return f"Payment successful for {cc}|{mes}|{ano}|{cvv}"
    else:
        return f"Declined for {cc}|{mes}|{ano}|{cvv} - {code} | {decline_code} | {message}"

@bot.message_handler(func=lambda message: True)
def check_cards(message):
    global pk, secretpi
    if not pk or not secretpi:
        bot.reply_to(message, "Please set PK and Secret PI first.")
        return

    cards = message.text.splitlines()
    results = []

    for card in cards:
        cc, mes, ano, cvv = card.split('|')
        result = process_card(cc, mes, ano, cvv, pk, secretpi)
        results.append(result)
        bot.reply_to(message, result)

# Start polling
if __name__ == '__main__':
    bot.polling()
