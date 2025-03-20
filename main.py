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
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ENTREPRISES = {
    "BNP Paribas": "https://group.bnpparibas/en/careers/job-offers",
    "Total": "https://careers.totalenergies.com/",
    "Crédit Agricole": "https://jobs.credit-agricole.com/",
    "Amazon": "https://www.amazon.jobs/en/locations/france",
    "AXA": "https://www.axa.com/en/careers/job-offers",
    "Canal+": "https://groupe.canalplus.com/carrieres/",
    "FDJ": "https://www.groupefdj.com/fr/talents/nous-rejoindre.html",
    "Enedis": "https://www.enedis.fr/recrute",
    "CNP Assurances": "https://www.cnp.fr/recrutement",
    "SNCF": "https://www.emploi.sncf.com/",
    "Club Med": "https://www.clubmedjobs.com/en",
    "Lacoste": "https://jobs.lacoste.com/",
    "RATP": "https://www.ratp.fr/en/offres-demploi",
    "Vinci": "https://jobs.vinci.com/",
    "Nestlé": "https://www.nestle.com/jobs",
    "Danone": "https://careers.danone.com/",
    "Coca-Cola": "https://careers.coca-colacompany.com/",
    "Disney": "https://jobs.disneycareers.com/",
    "Ubisoft": "https://www.ubisoft.com/fr-fr/company/careers",
    "Warner Bros": "https://www.warnerbroscareers.com/",
    "Universal Studios": "https://www.nbcunicareers.com/",
    "Caisse d'Épargne": "https://recrutement.caisse-epargne.fr/",
    "Groupama": "https://www.groupama.com/fr/carrieres/"
}
MOTS_CLES = ["cybersecurity", "data security", "IT project management", "risk management", "compliance", 
             "cloud security", "cyber risk", "security governance", "ISO 27001", "GDPR", "NIST", 
             "identity and access management", "SIEM", "SOC", "network security", "penetration testing",
             "data privacy", "encryption", "firewall", "incident response", "vulnerability management",
             "ethical hacking", "DevSecOps", "forensics", "zero trust", "IAM", "threat intelligence",
             "IT governance", "IT program management", "PMO", "agile project management", "scrum master",
             "change management", "cloud transformation", "digital transformation", "process optimization"]
LOCALISATION = "France"
ANNONCES_ENVOYEES = set()

# Fonction pour rechercher chaque mot-clé sur LinkedIn, Glassdoor et les sites carrières
def scrape_jobs_from_keywords():
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for keyword in MOTS_CLES:
        linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location=France"
        glassdoor_url = f"https://www.glassdoor.fr/Emploi/france-{keyword}-emplois-SRCH_IL.0,6_IN86_KO7,20.htm"
        
        # Scraping LinkedIn
        try:
            response = requests.get(linkedin_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            for job in soup.find_all("a", href=True):
                title = job.text.strip()
                link = job["href"]
                jobs.append({"title": title, "company": "LinkedIn", "link": link})
        except Exception as e:
            logger.error(f"Erreur scraping LinkedIn pour {keyword}: {e}")
        
        # Scraping Glassdoor
        try:
            response = requests.get(glassdoor_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            for job in soup.find_all("a", href=True):
                title = job.text.strip()
                link = job["href"]
                jobs.append({"title": title, "company": "Glassdoor", "link": link})
        except Exception as e:
            logger.error(f"Erreur scraping Glassdoor pour {keyword}: {e}")
        
        # Scraping des sites carrières
        for company, url in ENTREPRISES.items():
            try:
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                for job in soup.find_all("a", href=True):
                    title = job.text.strip()
                    link = job["href"] if "http" in job["href"] else url + job["href"]
                    if any(k in title.lower() for k in MOTS_CLES):
                        jobs.append({"title": title, "company": company, "link": link})
            except Exception as e:
                logger.error(f"Erreur scraping {company}: {e}")
    return jobs

# Commande /list_company
def list_company(update: Update, context: CallbackContext):
    message = "\n".join([f"{company} - {url}" for company, url in ENTREPRISES.items()])
    update.message.reply_text(message)

# Commande /list_keywords
def list_keywords(update: Update, context: CallbackContext):
    message = "\n".join(MOTS_CLES)
    update.message.reply_text(message)

# Commande /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Bot activé ! Recherche des offres en cours...")
    offres = scrape_jobs_from_keywords()
    for offre in offres:
        if offre["link"] not in ANNONCES_ENVOYEES:
            msg = f"{offre['title']} - {offre['company']}\n{offre['link']}"
            update.message.reply_text(msg)
            ANNONCES_ENVOYEES.add(offre["link"])

# Main function
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("list_company", list_company))
    dp.add_handler(CommandHandler("list_keywords", list_keywords))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
