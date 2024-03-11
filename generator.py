# Une partie des données est généré ici
import random 
from faker import Faker 
def creer_personne(): 
	fake = Faker() 
		tel = "\'" + "06" + str(random.randint(00000000, 99999999)) + "\'" date_naiss = "DATE \"" + str(random.randint(1980, 2003)) + "-" + str(random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])) + "-" + str(random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28])) + "\"" return [str(random.randint(100, 800)),"\'" + fake.first_name() +"\'", "\'" + fake.last_name() +"\'", date_naiss, "\'" + fake.address().replace("\n", " ") + "\'", str(tel), "\'" + fake.email() + "\'", "\'" +fake.country() + "\'"]

def creer_lieu(): 
	fake = Faker() coord = "\'" + str(fake.latitude()) + "/" + str(fake.longitude()) + "\'" 
	return [coord, "\'" + fake.country() + "\'", "\'" + fake.city() + "\'"] 
	
	def insert_personne(): 
	data = ', '.join(creer_personne()) return "INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES ("+ data + ");\n" 
	
	def insert_lieu(): data = ', '.join(creer_lieu()) return "INSERT INTO Lieu (coord, pays, ville) VALUES ("+ data + ");\n" 
	
# Notre but est de generer une partie des données avec la librairie python "Faker" afin d'avoir un jeu de donnée tres libre 
# Le fichier "datas.txt" contiendra des données que l'on écrira comme commandes 

with open('datas.txt', 'w') as f: 
for i in range(15): 
f.write(insert_personne()) 

f.write("\n")

for i in range(20): 
f.write(insert_lieu())
