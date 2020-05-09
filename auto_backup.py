#!/usr/bin/python3.7
# -*- coding: utf-8 -*-

# Victor De Faria 2020-04-27 2020-05-xx
# Algorythme du programme
#   |
#   |-> Générer le nom de la sauvevarde  <- Source fichier data.yml
#   |-> Sauvegarder les données sur le serveur local
#      |-> Récupérer la liste des fichiers sauvegarde du serveur FTP
#      |-> Supprimer la plus ancienne sauvegarde

# IMPORTATION DES MODULES
import os
import datetime
import re
import glob
import netrc
import ftplib
#from ftplib import FTP
import yaml

# DEFINITION DES FONCTIONS
def nom(texte, base_name):
    # Fonction qui génère un nom de fichier en fonction de la date et heure de la sauvegarde
    date = datetime.datetime.now()
    texte = f'backup-{base_name}-{texte}-{date.strftime("%Y-%m-%d-%H-%M")}.tar.gz'
    return texte


def fichiers(texte, base_name, dir_back):
    '''
    Fonction qui récupère la liste des fichiers du répertoire backup
    et ne renvoie que ceux dont le nom contient 'backup'- expression régulière.
    Si 8 fichiers dans le répertoire, alors le plus ancien est supprimé.
    '''
    fichiers = glob.glob(dir_back + "*")
    fichiers.sort(key=os.path.getmtime)
    backup_files = []
    for file in fichiers:
        reg = re.search(rf'backup-{base_name}-{texte}(-[0-9]+)+', file)
        if reg is not None:
            backup_files.append(file)
    if len(backup_files) > 7:
        os.remove(backup_files[0])
        backup_files.remove(backup_files[0])
    return(backup_files)    

# Fonction qui charge la liste des fichiers du serveur FTP
def list_ftp_files(host, user, passwd, path):
    with ftplib.FTP(host, user, passwd) as ftp:
        try:
            print(ftp.getwelcome())
            ftp.cwd(path)
            files = []
            ftp.dir(files.append)
            print(files)
        except ftplib.all_errors as e:
            print('FTP error: ', e)
    return(files)


with open('data_backup.yml') as f:
    try:
        data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print("Ouverture YAML Error :", e)
globals().update(data)

'''
# Définition des constantes des répertoires et noms des bases
dir_wordpress = "/var/www/html/wordpress/"
dir_backup = "/home/administrateur/backup/"
base_name = "wordpress"
nom_user_base = "wp_user"
backup_type = ["files", "bases"]
virtual_host = "/etc/apache2/sites-available/wordpress.conf"
ftp_host = "P9-DB-FTP"
dir_ftp = '/home/testftp/depot'
'''
#  //  MAIN PROGRAM // PROGRAMME PRINCIPAL //

# Définition du nom de la sauvegarde du jour
nom_backup_file = nom(backup_type[0], base_name)
nom_backup_base = nom(backup_type[1], base_name)

# Sauvegarde de la base de donnée Wordpress
os.system(f"mysqldump -h localhost -u {nom_user_base} --databases {base_name} | gzip > {dir_backup}{nom_backup_base}")
# Création du fichier de sauvegarde qui copie tous les fichiers du répertoire wordpress
os.system(f"tar czf {dir_backup}{nom_backup_file} {dir_wordpress}*")

# On récupère les informations de connexion du serveur ftp
netrc = netrc.netrc()
auth_ftp = netrc.authenticators(ftp_host)

# Recupération de la liste des fichiers du serveur FTP
fichier_ftp = list_ftp_files(ftp_host, auth_ftp[0], auth_ftp[2], dir_ftp)
print("\t FICHIERS : ", fichier_ftp)

# Récupération de la liste des fichiers  de sauvegarde
backup_files = fichiers(backup_type[0], base_name, dir_backup)
backup_bases = fichiers(backup_type[1], base_name, dir_backup)

# Partie de connexion au serveur FTP 
with ftplib.FTP(host= ftp_host, user=auth_ftp[0], passwd=auth_ftp[2]) as ftp:
    try:
        print(ftp.getwelcome())
        ftp.cwd(dir_ftp)
        ftp.storbinary('STOR ' + nom_backup_file, open(dir_backup + nom_backup_file , 'rb'))
        ftp.storbinary('STOR ' + nom_backup_base, open(dir_backup + nom_backup_base , 'rb'))
        ftp.quit()
    except ftplib.all_errors as e:
        print('FTP erreur : ', e)


