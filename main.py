import logging
import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables d’environnement
TOKEN = os.getenv("7440786076:AAEU6twrOXsZ0qKiOjiedAL-59Rube2K4Ek")
ENTREPRISES = ["BNP Paribas", "Total", "Crédit Agricole", "Amazon", "AXA", "Canal+", "FDJ", "Enedis", 
               "CNP Assurances", "SNCF", "Club Med", "Lacoste", "RATP", "Vinci", "Nestlé", "Danone", 
               "Coca-Cola", "Disney", "Ubisoft", "Warner Bros", "Universal Studios", "Caisse d'Épargne", "Groupama"]
MOTS_CLES = ["cybersecurity", "data security", "IT project management", "risk management", "compliance", 
             "cloud security", "cyber risk", "security governance", "ISO 27001", "GDPR", "NIST", 
             "identity and access management", "SIEM", "SOC", "network security", "penetration testing",
             "data privacy", "encryption", "firewall", "incident response", "vulnerability management",
             "ethical hacking", "DevSecOps", "forensics", "zero trust", "IAM", "threat intelligence",
             "IT governance", "IT program management", "PMO", "agile project management", "scrum master",
             "change management", "cloud transformation", "digital transformation", "process optimization"]
LOCALISATION = "France"
ANNONCES_ENVOYEES = set()

# URLs des sites carrière + plateformes générales
SITES_EMPLOI = {
    "LinkedIn": "https://www.linkedin.com/jobs/search/?keywords=cybersecurity&location=France",
    "Glassdoor": "https://www.glassdoor.fr/Emploi/france-cybersecurity-emplois-SRCH_IL.0,6_IN86_KO7,20.htm",
    "WelcomeToTheJungle": "https://www.welcometothejungle.com/fr/jobs?refinementList%5Bcontract_type_names.fr%5D%5B%5D=CDI",
    "Coca-Cola": "https://careers.coca-colacompany.com/",
    "Amazon": "https://www.amazon.jobs/en/locations/france",
    "Ubisoft": "https://www.ubisoft.com/fr-fr/company/careers",
    "Disney": "https://jobs.disneycareers.com/",
    "Nestlé": "https://www.nestle.com/jobs",
    "Danone": "https://careers.danone.com/",
    "AXA": "https://www.axa.com/en/careers/job-offers",
    "BNP Paribas": "https://group.bnpparibas/en/careers/job-offers",
    "Total": "https://careers.totalenergies.com/",
    "SNCF": "https://www.emploi.sncf.com/",
    "Vinci": "https://jobs.vinci.com/",
    "Lacoste": "https://jobs.lacoste.com/",
    "Club Med": "https://www.clubmedjobs.com/en",
    "RATP": "https://www.ratp.fr/en/offres-demploi",
    "Canal+": "https://groupe.canalplus.com/carrieres/",
}

# Fonction de scraping des sites
def scrape_sites():
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for company, url in SITES_EMPLOI.items():
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            for job in soup.find_all("a", href=True):  # Exemple basique, peut être affiné selon le site
                title = job.text.strip()
                link = url + job["href"] if "http" not in job["href"] else job["href"]
                if any(k in title.lower() for k in MOTS_CLES):
                    jobs.append({"title": title, "company": company, "link": link})
        except Exception as e:
            logger.error(f"Erreur scraping {company}: {e}")
    return jobs

# Commande /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Bot activé ! Recherche des offres en cours...")
    offres = scrape_sites()
    for offre in offres:
        if offre["link"] not in ANNONCES_ENVOYEES:
            msg = f"{offre['title']} - {offre['company']}\n{offre['link']}"
            update.message.reply_text(msg)
            ANNONCES_ENVOYEES.add(offre["link"])

# Commandes pour ajouter/supprimer des entreprises
def add_company(update: Update, context: CallbackContext):
    if context.args:
        entreprise = " ".join(context.args)
        ENTREPRISES.append(entreprise)
        update.message.reply_text(f"Entreprise ajoutée : {entreprise}")

def remove_company(update: Update, context: CallbackContext):
    if context.args:
        entreprise = " ".join(context.args)
        if entreprise in ENTREPRISES:
            ENTREPRISES.remove(entreprise)
            update.message.reply_text(f"Entreprise supprimée : {entreprise}")

# Commande pour définir des mots-clés
def set_keywords(update: Update, context: CallbackContext):
    global MOTS_CLES
    if context.args:
        MOTS_CLES = context.args
        update.message.reply_text(f"Mots-clés mis à jour : {', '.join(MOTS_CLES)}")

# Main function
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add_company", add_company))
    dp.add_handler(CommandHandler("remove_company", remove_company))
    dp.add_handler(CommandHandler("set_keywords", set_keywords))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
