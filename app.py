from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import difflib
import re

app = Flask(__name__)
app.secret_key = "replace_this_with_a_secure_random_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ---------- 50 structured FAQs ----------
banking_faq = [
    {"question": "what is my account balance", "keywords": ["balance", "account balance", "how much money"], "answer": "Your account balance is $5,000."},
    {"question": "how do i apply for a credit card", "keywords": ["apply credit card", "credit card", "get credit card"], "answer": "You can apply for a credit card online or by visiting your nearest branch."},
    {"question": "how do i request a new checkbook", "keywords": ["new checkbook", "request checkbook", "cheque book"], "answer": "You can request a new checkbook through your online banking account or by visiting a branch."},
    {"question": "how can i reset my password", "keywords": ["reset password", "forgot password", "change password"], "answer": "You can reset your password by clicking on 'Forgot Password' on the login page."},
    {"question": "where is the nearest branch", "keywords": ["nearest branch", "branch near me", "bank location"], "answer": "Please provide your location to find the nearest branch."},
    {"question": "how do i apply for a loan", "keywords": ["apply loan", "loan application", "get loan"], "answer": "You can apply for a loan through our mobile app or by visiting a branch."},
    {"question": "what is the interest rate for savings accounts", "keywords": ["interest rate", "savings interest", "savings rate"], "answer": "The current interest rate for savings accounts is 1.5% per annum."},
    {"question": "can i view my recent transactions", "keywords": ["recent transactions", "transaction history", "transactions"], "answer": "You can view your recent transactions in the 'Transaction History' section of your online account."},
    {"question": "how can i block my lost card", "keywords": ["block card", "lost card", "card block"], "answer": "You can block your card immediately through our mobile app or by calling our customer support."},
    {"question": "how do i reactivate my dormant account", "keywords": ["reactivate account", "dormant account", "activate account"], "answer": "Please visit your nearest branch with a valid ID to reactivate your account."},
    {"question": "what is the daily atm withdrawal limit", "keywords": ["atm limit", "withdrawal limit", "daily limit"], "answer": "The daily ATM withdrawal limit is $500."},
    {"question": "how do i update my contact information", "keywords": ["update contact", "change phone number", "update email"], "answer": "You can update your contact information in the 'Profile Settings' section of your online account."},
    {"question": "how do i open a new savings account", "keywords": ["open savings account", "new account", "open account"], "answer": "You can open a new savings account online or by visiting your nearest branch with required documents."},
    {"question": "what are the current foreign exchange rates", "keywords": ["forex rates", "currency rates", "exchange rates"], "answer": "The current foreign exchange rates can be found on our website or mobile app under the 'Forex' section."},
    {"question": "how do i register for online banking", "keywords": ["register online banking", "sign up online banking", "register"], "answer": "You can register for online banking by visiting our website and following the registration process."},
    {"question": "do you offer overdraft protection", "keywords": ["overdraft protection", "overdraft"], "answer": "Yes, we offer overdraft protection. Please contact us to learn more about terms and fees."},
    {"question": "how do i apply for a mortgage", "keywords": ["apply mortgage", "mortgage loan", "home loan"], "answer": "You can apply for a mortgage through our website or by visiting a branch to speak with a mortgage specialist."},
    {"question": "how can i deposit a check", "keywords": ["deposit check", "check deposit", "cheque deposit"], "answer": "You can deposit a check using our mobile app, at an ATM (if supported), or by visiting a branch."},
    {"question": "how can i get a copy of my account statement", "keywords": ["account statement", "bank statement", "statement copy"], "answer": "You can download or request a copy of your account statement through your online banking account."},
    {"question": "how do i update my account beneficiary", "keywords": ["update beneficiary", "change beneficiary"], "answer": "You can update your beneficiary by visiting your nearest branch with a valid ID."},
    {"question": "how do i make a loan repayment", "keywords": ["loan repayment", "pay loan", "repay loan"], "answer": "You can make a loan repayment online, through our mobile app, or at a branch."},
    {"question": "how do i close my account", "keywords": ["close account", "delete account", "account closure"], "answer": "To close your account, please visit your nearest branch with a valid ID and complete the closure form."},
    {"question": "what investment options do you offer", "keywords": ["investment options", "mutual funds", "fixed deposit", "fd"], "answer": "We offer mutual funds, fixed deposits, and retirement accounts. Visit our website for details."},
    {"question": "how can i make an international wire transfer", "keywords": ["international transfer", "wire transfer", "send money abroad"], "answer": "You can make an international wire transfer through your online banking account or by visiting a branch; fees may apply."},
    {"question": "how do i update my mailing address", "keywords": ["update address", "change address", "mailing address"], "answer": "You can update your mailing address in 'Profile Settings' or by visiting your nearest branch."},
    {"question": "how can i apply for an auto loan", "keywords": ["auto loan", "car loan", "vehicle loan"], "answer": "You can apply for an auto loan online or by visiting your nearest branch."},
    {"question": "where can i download the mobile banking app", "keywords": ["download app", "mobile app", "banking app"], "answer": "You can download our mobile banking app from the App Store (iOS) or Google Play Store (Android)."},
    {"question": "how do i dispute a transaction", "keywords": ["dispute transaction", "unauthorized transaction", "chargeback"], "answer": "You can dispute a transaction by contacting customer support or using the 'Dispute' option in your online account."},
    {"question": "how do i change my atm pin", "keywords": ["change atm pin", "reset pin", "change pin"], "answer": "You can change your ATM PIN at an ATM or through your online banking account if supported."},
    {"question": "what are the current fixed deposit rates", "keywords": ["fixed deposit rates", "fd rates", "deposit rates"], "answer": "The current fixed deposit rates are available on our website or via customer support."},
    {"question": "how can i check my credit score", "keywords": ["credit score", "cibil", "credit report"], "answer": "You can check your credit score through our mobile app or via partner credit bureau portals."},
    {"question": "what insurance products do you offer", "keywords": ["insurance products", "life insurance", "health insurance"], "answer": "We offer life, health, and auto insurance. Visit our website for product pages."},
    {"question": "how do i report fraud or suspicious activity", "keywords": ["report fraud", "fraud", "suspicious activity"], "answer": "Please contact our fraud department immediately via the support number or use the online fraud-reporting tool."},
    {"question": "how do i set up direct deposit", "keywords": ["direct deposit", "salary deposit"], "answer": "Set up direct deposit by providing your employer with your account and routing numbers."},
    {"question": "how do i notify the bank of my travel plans", "keywords": ["travel notification", "travel plans", "notify travel"], "answer": "You can notify us via the 'Travel Notification' section in your online banking or mobile app."},
    {"question": "what are the differences between your account types", "keywords": ["account types", "types of accounts", "compare accounts"], "answer": "Compare our account types on the 'Accounts' page on our website—each has different benefits and fees."},
    {"question": "how can i get pre-approved for a loan", "keywords": ["pre approved loan", "preapproval"], "answer": "You can submit an online application for pre-approval or speak to a loan advisor at a branch."},
    {"question": "how do i replace my debit card", "keywords": ["replace card", "new debit card", "card replacement"], "answer": "Request a replacement debit card through online banking, mobile app, or at a branch."},
    {"question": "how do i deposit a check using the mobile app", "keywords": ["mobile check deposit", "deposit check app"], "answer": "Open the mobile app, choose 'Deposit Check', capture images, and follow instructions."},
    {"question": "how do i open a business account", "keywords": ["business account", "open business account", "business banking"], "answer": "Visit a branch with required documents to open a business account or start online if available."},
    {"question": "how do i activate my new debit credit card", "keywords": ["activate card", "card activation"], "answer": "Activate your new card via the activation number, mobile app, or online banking 'Card Services' option."},
    {"question": "how can i set savings goals", "keywords": ["savings goals", "goals"], "answer": "Set savings goals via the 'Savings Goals' feature in the mobile app or online banking."},
    {"question": "how do i send a secure message to customer support", "keywords": ["secure message", "contact support", "message support"], "answer": "Send a secure message under 'Support' in online banking or use the secure messaging feature in the app."},
    {"question": "how can i check my loan payment due dates", "keywords": ["loan due date", "payment due", "due date"], "answer": "Check loan due dates in the 'Loan Details' section of your online account."},
    {"question": "how do i set up recurring payments", "keywords": ["recurring payments", "auto pay", "standing instructions"], "answer": "Set up recurring payments in online banking under 'Payments' -> 'Recurring'."},
    {"question": "how can i increase my credit card limit", "keywords": ["increase credit limit", "credit limit increase"], "answer": "Request a credit limit increase in online banking or contact customer support."},
    {"question": "how secure is your mobile banking app", "keywords": ["app security", "security"], "answer": "Our app uses industry-standard encryption and multi-factor authentication to secure accounts."},
    {"question": "can i exchange currency at a branch", "keywords": ["currency exchange", "exchange currency"], "answer": "Yes — currency exchange is available at selected branches; check availability before visiting."},
    {"question": "how can i view my tax documents", "keywords": ["tax documents", "tax forms", "form"], "answer": "View tax documents in the 'Documents' section of online banking or request via branch."},
    {"question": "how do i enroll in the rewards program", "keywords": ["rewards program", "rewards"], "answer": "Enroll in the rewards program via online banking or contact customer support to sign up."}
]
# ---------- end FAQs ----------

# Precompute phrase list for fuzzy matching
phrase_to_answer = {}
all_phrases = []
for item in banking_faq:
    q = item["question"]
    phrase_to_answer[q] = item["answer"]
    all_phrases.append(q)
    for kw in item.get("keywords", []):
        phrase_to_answer[kw] = item["answer"]
        all_phrases.append(kw)

def normalize(text):
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text

def find_answer(user_input):
    user_input_norm = normalize(user_input)

    # 1) direct keyword presence
    for phrase in all_phrases:
        if phrase in user_input_norm:
            return {"answer": phrase_to_answer[phrase], "method": "keyword", "match": phrase}

    # 2) fuzzy matching using difflib
    matches = difflib.get_close_matches(user_input_norm, all_phrases, n=1, cutoff=0.35)
    if matches:
        m = matches[0]
        return {"answer": phrase_to_answer[m], "method": "fuzzy", "match": m}

    # 3) no confident answer
    return {"answer": None, "method": "none", "match": None}

@app.route("/")
def home():
    if "chat_history" not in session:
        session["chat_history"] = []
    return render_template("index.html", chat_history=session["chat_history"])

@app.route("/get_response", methods=["POST"])
def get_response():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "Please type a question."}), 400

    result = find_answer(user_message)
    answer = result["answer"]

    # store last topic / match for simple follow-ups (optional)
    if result["method"] != "none":
        session["last_match"] = result["match"]

    # fallback if no answer
    if not answer:
        fallback = ("Sorry, I couldn't find an exact answer. "
                    "Try rephrasing or pick a suggested question below.")
        answer = fallback

    # store chat history in session
    hist = session.get("chat_history", [])
    hist.append({"user": user_message, "bot": answer})
    session["chat_history"] = hist
    session.modified = True

    # top suggestions (first 6 questions)
    suggestions = [item["question"] for item in banking_faq[:6]]
    return jsonify({"response": answer, "method": result["method"], "suggestions": suggestions})

@app.route("/new_chat", methods=["POST"])
def new_chat():
    session["chat_history"] = []
    session.modified = True
    return jsonify({"status": "ok"})

@app.route("/faqs", methods=["GET"])
def faqs_route():
    # return list of questions for frontend to show as quick replies
    questions = [item["question"] for item in banking_faq]
    return jsonify({"faqs": questions})

if __name__ == "__main__":
    app.run(debug=True)
