-- Les tables --
CREATE TABLE Personne (id_pers INT PRIMARY KEY, nom VARCHAR(50) not null, prenom VARCHAR(50), date_naiss DATE, adr VARCHAR(60), num VARCHAR(10), mail VARCHAR(50), pays VARCHAR(50) ); 

CREATE TABLE Projet (id_proj INT PRIMARY KEY, titre VARCHAR(100)); 

CREATE TABLE Don (id_don INT PRIMARY KEY, montant DECIMAL(10, 2) not null, type_reglem VARCHAR(40), id_pers INT, id_proj INT, FOREIGN KEY (id_pers) REFERENCES Personne(id_pers), FOREIGN KEY (id_proj) REFERENCES Projet(id_proj) ); 

CREATE TABLE Lieu (coord VARCHAR(255) PRIMARY KEY, pays VARCHAR(50), ville VARCHAR(70)); 

CREATE TABLE Action (id_act INT PRIMARY KEY, nom_act VARCHAR(100), date_realisat DATE, cout DECIMAL(10, 2), id_proj INT, act_dep VARCHAR(100), FOREIGN KEY (id_proj) REFERENCES Projet(id_proj) ); 

CREATE TABLE Intervention (id_int INT PRIMARY KEY, date_int DATE, duree VARCHAR(4), qte VARCHAR(3) not null, id_etat INT, id_act INT, etat VARCHAR(10) not null, coord VARCHAR(255), FOREIGN KEY (id_act) REFERENCES Action(id_act), FOREIGN KEY (coord) REFERENCES Lieu(coord) ); 

CREATE TABLE Personne_Intervention ( id_pers INT, id_int INT, role VARCHAR(50), PRIMARY KEY (id_pers, id_int), FOREIGN KEY (id_pers) REFERENCES Personne(id_pers), FOREIGN KEY (id_int) REFERENCES Intervention(id_int) ); 

CREATE TABLE Personne_Don ( id_pers INT, id_don INT, statut_don VARCHAR(50), PRIMARY KEY (id_pers, id_don), FOREIGN KEY (id_pers) REFERENCES Personne(id_pers), FOREIGN KEY (id_don) REFERENCES Don(id_don) );

alter table action add constraint fk_act_dep FOREIGN KEY (id_act_dep) references action(id_act);

-- action1 ne doit pas dépendre de action1 -- 
alter table action add constraint fk_unique_act CHECK (id_act <> id_act_dep);

-- Don entre 1 et 9999... -- 
ALTER TABLE Don ADD CONSTRAINT chk_montant CHECK (montant >= 1 AND montant <= 9999999999.99);

-- Triggers/Procedures --
-- Verification des dons, si un don est superieur à la sommes des dons qu'il nous faut pour l'action alors on n'accepte pas le don
CREATE OR REPLACE TRIGGER trg_verif_dons BEFORE INSERT ON Don FOR EACH ROW 
DECLARE 
v_montant_total_dons DECIMAL(10, 2); 
v_cout_total_actions DECIMAL(10, 2); 
BEGIN 
SELECT SUM(montant) INTO v_montant_total_dons FROM Don WHERE id_proj = :NEW.id_proj; 
SELECT SUM(cout) INTO v_cout_total_actions FROM Action WHERE id_proj = :NEW.id_proj; 
IF 
		v_montant_total_dons + :NEW.montant > v_cout_total_actions THEN RAISE_APPLICATION_ERROR (-20001, 'Vous depassez le montant necessaire.'); 
END IF; 
END; 
/

-- Actualise les statuts, si le don est en espece alors le statut sera valide (car on possede deja l'argent dans la entreprise humainitaire) sinon on le mets en attente le temps d'un changement futur (en le comptant pour d'autres requetes)
CREATE TRIGGER trg_statut_don AFTER INSERT ON Don FOR EACH ROW 
BEGIN     
IF 
:NEW.type_reglem = 'espece' THEN         
INSERT INTO Personne_Don (id_pers, id_don, statut_don) VALUES (:NEW.id_pers, :NEW.id_don, 'valide');     
ELSE        
INSERT INTO Personne_Don (id_pers, id_don, statut_don) VALUES (:NEW.id_pers, :NEW.id_don, 'en attente');     
END IF; 
END;
/

-- Actualise automatiquement le role d'une personne, si on souhaite le changer il faudra le faire manuellement /!\ Possibilité de le faire avec un check /!\
CREATE TRIGGER trg_role BEFORE INSERT ON Personne_Intervention FOR EACH ROW 
BEGIN     
	SET :NEW.role = "intervenant"; 
END;
/

-- Procedure de recapitulation des dons d'une personne
CREATE OR REPLACE PROCEDURE pro_recap_don(v_id_pers Personne.id_pers%type) IS 
BEGIN 
FOR tuple IN (select * from don where id_pers = v_id_pers) 
	LOOP 
		dbms_output.put_line('Donation :' || tuple.montant || '.'); 
	END LOOP; 
END; 
/

-- Pour une intervention liée à une action, si la date de l'action à lieu après l'intervention, on nous renvoie un message d'erreur
CREATE OR REPLACE TRIGGER trg_date_int_act BEFORE INSERT ON Intervention FOR EACH ROW
DECLARE 
	act_date DATE; 
BEGIN 
SELECT date_realisat INTO act_date FROM Action WHERE id_act = :NEW.id_act; 
	IF action_date > :NEW.date_int THEN 
		RAISE_APPLICATION_ERROR(-20001, 'Attention ! La date de l intervention est antérieur à la date de l action.'); 
	END IF; 
END; 
/

-- Inserts --
-- Voir la partie python pour la creation des données --
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (364, 'John', 'Gillespie', DATE "1988-6-25", '318 Nicole Glen Suite 738 Blackland, SD 03871', '0676526607', 'dunnpamela@example.org', 'Liberia'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (183, 'Brian', 'Olsen', DATE "1984-10-19", '39109 Webb Islands Suite 586 Cardenasfort, OR 43799', '0679231814', 'rachel38@example.org', 'Dominica'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (261, 'Jane', 'Brown', DATE "1997-09-11", '9037 Tiffany Ridges North Kara, PA 42086', '0694171815', 'cooperjulie@example.net', 'Uganda'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (128, 'Brooke', 'Rosales', DATE "2000-01-01", '162 Short Row Abbotthaven, NE 14471', '0672948562', 'chernandez@example.com', 'Chad'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (513, 'Kelsey', 'Johnson', DATE "1997-03-11", '1515 Sandra Points Apt. 937 Kaitlynton, MD 81399', '0635596007', 'teresahull@example.org', 'Fiji'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (203, 'Bailey', 'Ross', DATE "1982-08-12", '0843 Young Lakes Port Shawn, DC 71776', '0628294891', 'dicksontiffany@example.com', 'Lebanon'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (695, 'Craig', 'Grant', DATE "1999-07-06", '352 Rice Landing Apt. 288 Johnsonland, FM 63894', '0627327797', 'briannafrazier@example.net', 'Belize'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (458, 'Mario', 'Hawkins', DATE "1985-05-12", '3660 Becker Walk Apt. 113 East Chad, AL 60002', '0618607949', 'bsteele@example.org', 'Germany'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (462, 'Wayne', 'Foster', DATE "2002-12-09", '38190 John Flats Apt. 856 Brandonton, UT 46429', '0679289387', 'efisher@example.net', 'Liberia'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (788, 'Christopher', 'Arroyo', DATE "1992-07-06", '87458 Amanda Plain Port Angela, KS 85979', '0646220291', 'wiseandrew@example.org', 'Swaziland'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (425, 'Ricky', 'Johnson', DATE "1980-05-28", '33205 Rachel Oval Suite 401 Laurafort, ND 73789', '0696968939', 'zmoreno@example.net', 'Namibia'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (692, 'Bryan', 'Braun', DATE "1996-12-13", '513 Wise Lodge New Amanda, MO 25545', '0614528577', 'hufflisa@example.org', 'United Arab Emirates'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (557, 'Paul', 'Ballard', DATE "1994-10-01", '9375 Ortiz Springs Dicksonview, AZ 47891', '0690726255', 'thomasnicole@example.com', 'New Caledonia'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (708, 'Ashley', 'Hawkins', DATE "2002-12-03", '265 Derek Pines Suite 957 New Barbarafurt, MH 74599', '0630964713', 'websterdanny@example.com', 'Lao People s Democratic Republic');
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (712, 'Lori', 'White', DATE "1987-05-18", '6044 Taylor Harbor Suite 937 Olsonshire, WV 51304', '0671825539', 'wardamanda@example.net', 'Argentina');
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (3, 'Johnson', 'Robert', DATE '1978-03-10', '789 Pine St', '5551112222', 'robert.johnson@email.com', 'UK'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (4, 'Garcia', 'Maria', DATE '1982-11-08', '234 Elm St', '3334445555', 'maria.garcia@email.com', 'Spain'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (5, 'Kim', 'Sung', DATE '1995-07-30', '567 Maple St', '9998887777', 'sung.kim@email.com', 'South Korea'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (6, 'MÃ¼ller', 'Anna', DATE '1989-04-18', '890 Birch St', '1112223333', 'anna.muller@email.com', 'Germany'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (7, 'Li', 'Wei', DATE '1973-12-05', '123 Pineapple St', '7776665555', 'wei.li@email.com', 'China'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (8, 'Abdullah', 'Ahmed', DATE '1980-08-20', '456 Orange St', '4445556666', 'ahmed.abdullah@email.com', 'Saudi Arabia'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (9, 'Martinez', 'Luis', DATE '1992-01-25', '789 Banana St', '8889990000', 'luis.martinez@email.com', 'Mexico'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (10, 'Yamamoto', 'Yuki', DATE '1987-06-12', '234 Cherry St', '2223334444', 'yuki.yamamoto@email.com', 'Japan'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (11, 'Dubois', 'Sophie', DATE '1984-09-28', '567 Lemon St', '6667778888', 'sophie.dubois@email.com', 'France'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (12, 'Chen', 'Wei', DATE '1975-02-15', '890 Grape St', '3334445555', 'wei.chen@email.com', 'China'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (13, 'Singh', 'Raj', DATE '1990-07-03', '123 Plum St', '9998887777', 'raj.singh@email.com', 'India'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (14, 'Abe', 'Takashi', DATE '1986-04-20', '456 Mango St', '1112223333', 'takashi.abe@email.com', 'Japan'); 
INSERT INTO Personne (id_pers, nom, prenom, date_naiss, adr, num, mail, pays) VALUES (15, 'Wang', 'Mei', DATE '1981-11-10', '789 Avocado St', '7776665555', 'mei.wang@email.com', 'China');


INSERT INTO Lieu (coord, pays, ville) VALUES ('-14.3619265/-66.763923', 'Comoros', 'Sanderschester'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('-31.281493/43.021202', 'Ukraine', 'Alexport'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('71.135852/-14.959615', 'Sao Tome and Principe', 'Wilsonborough'); INSERT INTO Lieu (coord, pays, ville) VALUES ('-32.219290/-66.052052', 'Azerbaijan', 'West Georgebury'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('79.8584055/-133.839916', 'Liechtenstein', 'New James'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('-8.862733/-145.496915', 'Serbia', 'Hernandezbury'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('34.523602/-80.374691', 'Guatemala', 'East Michaelland'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('53.9629765/-102.738309', 'Colombia', 'North Elizabeth'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('-68.7828295/-26.747994', 'Finland', 'Nicholsonborough'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('7.970871/-122.069819', 'Guinea-Bissau', 'South Travisville'); INSERT INTO Lieu (coord, pays, ville) VALUES ('31.7462785/-50.268228', 'Uganda', 'Michealstad'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('-69.5213115/-166.638712', 'Honduras', 'Jonathanfort'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('-5.116573/76.226394', 'French Polynesia', 'East Lindsayborough'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('-78.023568/-65.660733', 'Kyrgyz Republic', 'South Michaelmouth'); INSERT INTO Lieu (coord, pays, ville) VALUES ('43.328520/-97.706764', 'United States Virgin Islands', 'North Keithview'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('73.8077015/-176.276428', 'Sao Tome and Principe', 'Myersborough'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('74.691157/-91.446139', 'Norway', 'Lake James'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('38.656811/99.841890', 'Tokelau', 'East Jamesshire'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('77.905672/-140.689026', 'Paraguay', 'Wallerhaven'); 
INSERT INTO Lieu (coord, pays, ville) VALUES ('-70.1584575/177.153962', 'Somalia', 'New Nathan');

INSERT INTO Projet (id_proj, titre) VALUES (1, 'Construction d écoles'); 
INSERT INTO Projet (id_proj, titre) VALUES (2, 'Fourniture de soins médicaux'); 
INSERT INTO Projet (id_proj, titre) VALUES (3, 'Programme d alimentation pour les enfants'); 
INSERT INTO Projet (id_proj, titre) VALUES (4, 'Réhabilitation des infrastructures'); 
INSERT INTO Projet (id_proj, titre) VALUES (5, 'Assistance aux réfugiés'); 
INSERT INTO Projet (id_proj, titre) VALUES (6, 'Projet d eau potable au Cambodge'); 
INSERT INTO Projet (id_proj, titre) VALUES (7, 'Sensibilisation à la santé publique'); 
INSERT INTO Projet (id_proj, titre) VALUES (8, 'Construction de logements durables'); 
INSERT INTO Projet (id_proj, titre) VALUES (9, 'Éducation des filles en Afghanistan'); 
INSERT INTO Projet (id_proj, titre) VALUES (10, 'Lutte contre la famine'); 
INSERT INTO Projet (id_proj, titre) VALUES (11, 'Soutien aux communautés autochtones'); 
INSERT INTO Projet (id_proj, titre) VALUES (12, 'Projet de microcrédit'); 
INSERT INTO Projet (id_proj, titre) VALUES (13, 'Réduction des déchets plastiques'); 
INSERT INTO Projet (id_proj, titre) VALUES (14, 'Soutien aux victimes de catastrophes naturelles au Mexique'); 
INSERT INTO Projet (id_proj, titre) VALUES (15, 'Programme d agriculture durable'); 
INSERT INTO Projet (id_proj, titre) VALUES (16, 'Réhabilitation des zones touchées par les feux de forêt en Californie'); 
INSERT INTO Projet (id_proj, titre) VALUES (17, 'Projet de santé maternelle'); 
INSERT INTO Projet (id_proj, titre) VALUES (18, 'Aide aux personnes déplacées'); 
INSERT INTO Projet (id_proj, titre) VALUES (19, 'Lutte contre la malnutrition infantile'); 
INSERT INTO Projet (id_proj, titre) VALUES (20, 'Projet de reboisement en Amazonie'); 
INSERT INTO Projet (id_proj, titre) VALUES (21, 'Sensibilisation au VIH/SIDA en Afrique'); 
INSERT INTO Projet (id_proj, titre) VALUES (22, 'Promotion de l''éducation environnementale en Norvège'); 
INSERT INTO Projet (id_proj, titre) VALUES (23, 'Aide aux personnes sans-abri aux États-Unis'); 
INSERT INTO Projet (id_proj, titre) VALUES (24, 'Soutien aux orphelins'); 
INSERT INTO Projet (id_proj, titre) VALUES (25, 'Programme de vaccination'); 
INSERT INTO Projet (id_proj, titre) VALUES (26, 'Projet d énergie renouvelable'); 
INSERT INTO Projet (id_proj, titre) VALUES (27, 'Assistance aux personnes âgées'); 
INSERT INTO Projet (id_proj, titre) VALUES (28, 'Soutien psychosocial aux survivants de violences'); 
INSERT INTO Projet (id_proj, titre) VALUES (29, 'Programme de prévention du paludisme'); 
INSERT INTO Projet (id_proj, titre) VALUES (30, 'Projet d accès à l eau potable');

INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (4, 'Réparation infrastructures éducatives', DATE '2023-04-10', 200.00, 1, NULL); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (1, 'Formation enseignants', DATE '2023-01-15', 1000.00, 1, 4); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (2, 'Renovation des salles de classe', DATE '2023-02-20', 500.00, 1, 4); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (3, 'Distribution de fournitures scolaires', DATE '2023-03-25', 300.25, 1, 4); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (5, 'Cours d alphabétisation', DATE '2023-05-05', 540.00, 1, 1); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (6, 'Sensibilisation hygiène', DATE '2023-06-12', 600.00, 2, NULL); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (7, 'Récolte de fonds', DATE '2023-07-20', 800.00, 5, NULL); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (10, 'Mise en place bibliothèque', DATE '2023-10-30', 850.00, 5, NULL); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (11, 'Formation professionnelle', DATE '2023-11-05', 2550.00, 5, NULL); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (15, 'Programme d orientation', DATE '2024-03-30', 1500.00, 5, NULL); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (12, 'Soutien psychologique', DATE '2024-01-18', 900.00, 3, NULL); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (13, 'Éducation nutritionnelle', DATE '2023-12-12', 200.00, 3, 12); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (19, 'Formation informatique', DATE '2024-07-25', 300.00, 5, NULL); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (20, 'Atelier jardinage', DATE '2024-08-30', 150.00, 7, NULL);
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (14, 'Mission d exploration médicale en zone reculée', '2023-01-10', 900.00, 11, NULL);
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (21, 'Projet de reforestation dans le désert', DATE '2023-02-15', 800.00, 12, NULL), 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (22, 'Éducation environnementale pour tribus isolées', '2023-03-20', 600.00, 13, NULL), 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (23, 'Soutien aux communautés isolés', DATE '2023-04-25', 900.00, 14, NULL);
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (24, 'Initiative d énergie solaire en zone arctique', DATE '2023-05-05', 650.00, 15, 23);
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (25, 'Programme de préservation marine unique', DATE '2023-06-10', 750.00, 16, NULL);
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (26, 'Sauvegarde des langues indigènes en voie de disparition', DATE '2023-07-15', 550.00, 17, NULL),;
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (27, 'Projet d alimentation durable pour les populations nomades', DATE '2023-08-20', 1850.00, 18, NULL); 
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (28, 'Aide aux victimes de phénomènes météorologiques extrêmes', DATE '2023-09-25', 720.00, 19, NULL);
INSERT INTO Action (id_act, nom_act, date_realisat, cout, id_proj, act_dep) VALUES (29, 'Soutien aux populations tribales en territoire isolé', DATE '2023-10-30', 680.00, 20, NULL);

INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (1, 50.00, 'carte bleue', 15, 1); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (2, 30.00, 'carte bleue', 1, 2); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (3, 25.50, 'carte bleue', 3, 3); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (4, 60.00, 'carte bleue', 2, 4); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (5, 35.50, 'carte bleue', 2, 1); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (6, 40.00, 'espece', 3, 3); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (7, 50.00, 'espece', 2, 4); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (8, 175.00, 'cheque', 4, 8); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (9, 165.00, 'cheque', 10, 9); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (10, 170.00, 'cheque', 5, 10); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (11, 285.00, 'cheque', 11, 11); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (12, 55.43, 'espece', 1, 1); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (13, 60.00, 'espece', 12, 3); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (14, 65.00, 'espece', 7, 2); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (15, 75.00, 'espece', 13, 3); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (16, 80.00, 'paypal', 8, 6); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (17, 20.00, 'paypal', 14, 17); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (18, 5.00, 'paypal', 9, 8);
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (19, 50.00, 'carte bleue', 15, 1), 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (20, 70.00, 'cheque', 16, 2); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (21, 30.00, 'espece', 17, 3); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (22, 80.00, 'paypal', 18, 4);
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (23, 40.00, 'carte bleue', 19, 5); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (24, 600.00, 'cheque', 20, 6);
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (25, 25.00, 'espece', 21, 7); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (26, 90.00, 'paypal', 22, 8);
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (27, 155.00, 'carte bleue', 23, 9); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (28, 75.00, 'cheque', 24, 10);
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (29, 300.00, 'espece', 25, 11); 
INSERT INTO Don (id_don, montant, type_reglem, id_pers, id_proj) VALUES (30, 85.00, 'paypal', 26, 12);


INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (1, DATE '2023-01-10', 24, 10, 1, 'en cours', '-32.219290/-66.052052');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (2, DATE '2023-02-15', 32, 7, 2, 'en cours', '-31.281493/43.021202');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (3, DATE '2023-03-20', 1, 3, 3, 'en attente', '71.135852/-14.959615');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (4, DATE '2023-04-25', 4, 2, 4, 'en cours', '-8.862733/-145.496915');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (5, DATE '2023-05-05', 2, 1, 5, 'en cours', '-68.7828295/-26.747994');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (6, DATE '2023-06-10', 30, 1, 6, 'en cours', '31.7462785/-50.268228');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (7, DATE '2023-07-15', 2, 2, 7, 'en attente', '-14.3619265/-66.763923');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (8, DATE '2023-08-20', 3, 5, 8, 'en cours', '31.7462785/-50.268228');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (9, DATE '2023-09-25', 1, 2, 9, 'en cours', '-14.3619265/-66.763923');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (10, DATE '2023-10-30', 4, 1, 10, 'en cours', '73.8077015/-176.276428');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (11, DATE '2024-01-01', 1, 1, 5, 'en cours', '79.8584055/-133.839916'); 
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (12, DATE '2024-04-10', 8, 4, 6, 'en cours', '-8.862733/-145.496915');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (13, DATE '2024-06-12', 1, 4, 7, 'en cours', '34.523602/-80.374691');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (14, DATE '2024-12-10', 1, 1, 10, 'en cours', '53.9629765/-102.738309'); 
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (15, DATE '2024-02-19', 1, 1, 11, 'en cours', '-68.7828295/-26.747994'); 
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (16, DATE '2024-06-22', 7, 3, 12, 'en cours', '7.970871/-122.069819');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (17, DATE '2024-06-10', 8, 1, 13, 'en cours', '31.7462785/-50.268228'); 
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (18, DATE '2024-09-23', 1, 1, 19, 'en cours', '-69.5213115/-166.638712');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (19, DATE '2024-02-03', 1, 1, 20, 'en cours', '-5.116573/76.226394');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (20, DATE '2024-10-16', 2, 2, 5, 'en cours', '-78.023568/-65.660733'); 
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (21, DATE '2024-01-24', 2, 2, 6, 'en cours', '43.328520/-97.706764');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (22, DATE '2024-01-10', 3, 1, 7, 'en cours', '73.8077015/-176.276428'); 
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (23, DATE '2024-04-10', 2, 2, 10, 'en cours', '74.691157/-91.446139');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (24, DATE '2024-01-26', 2, 1, 11, 'en cours', '38.656811/99.841890');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (25, DATE '2024-01-09', 3, 1, 15, 'en cours', '77.905672/-140.689026'); 
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (26, DATE '2024-02-03', 2, 1, 12, 'en cours', '-70.1584575/177.153962'); 
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (27, DATE '2024-06-27', 8, 2, 13, 'en cours', '79.8584055/-133.839916'); 
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (28, DATE '2024-06-10', 2, 1, 19, 'en cours', '-8.862733/-145.496915');
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (29, DATE '2024-08-10', 1, 1, 20, 'en cours', '34.523602/-80.374691'); 
INSERT INTO Intervention (id_int, date_int, duree, qte, id_act, etat, coord) VALUES (30, DATE '2024-11-31', 1, 1, 5, 'en cours', '53.9629765/-102.738309');

-- Requetes SQL --
-- Quelles sont les personnes ayant fait des dons aux projets auquel elles participent ?
SELECT DISTINCT p.nom, p.prenom FROM Personne p, Don d, Projet pr WHERE p.id_pers = d.id_pers AND d.id_proj = pr.id_proj;

-- Quels sont le mail et le numéro téléphone de toutes les personnes de l’intervention ’x’ ?
SELECT p.mail, p.num FROM Personne p, Personne_Intervention pi, Intervention i WHERE p.id_pers = pi.id_pers AND pi.id_int = i.id_int AND i.nom_intervention = 'x';

-- Pour le tresorier voir pour tous, savoir le total des dons et le cout total
SELECT d.id_proj, p.titre AS titre_projet, SUM(d.montant) AS montant_obtenu, SUM(a.cout) AS cout_du_projet FROM Don d, Projet p, Action a WHERE d.id_proj = p.id_proj and d.id_proj = a.id_proj GROUP BY d.id_proj, p.titre;

-- Quelles sont les prénoms et noms des personnes ayant fait des dons par carte bleu ?
SELECT p.nom, p.prenom FROM Personne p, Personne_Don pers_d, Don d WHERE p.id_pers = pers_d.id_pers and pers_d.id_don = d.id_don AND d.type_reglem = 'carte bleue';

-- Donation maximal (la plus élévé par projet)
SELECT pr.titre, MAX(d.montant) AS donation_max FROM Projet pr, Don d WHERE pr.id_proj = d.id_proj GROUP BY pr.titre;

-- Les 5 personnes ayant fait les plus gros dons 
SELECT p.nom, p.prenom, SUM(d.montant) AS total_dons FROM Personne p, Don d WHERE p.id_pers = d.id_pers GROUP BY p.nom, p.prenom ORDER BY total_dons DESC LIMIT 5;

-- Dons moyen par personne excluant les dons inferieur à 999 euros 
SELECT p.nom, p.prenom, AVG(d.montant) AS don_moyen FROM Personne p, Personne_Don pers_d, Don d WHERE p.id_pers = pers_d.id_pers AND pers_d.id_don = d.id_don WHERE d.montant > 999.00 GROUP BY p.nom, p.prenom;

-- La liste des personnes ayant participé à des interventions d’une durée supérieure à 3 jours.
`SELECT DISTINCT pi.id_pers 
FROM Personne_Intervention pi, Intervention I 
WHERE pi.id_int = I.id_int AND I.duree > 3;`

-- Quels sont les projets non terminées ?
SELECT * FROM Projet 
WHERE id_proj NOT IN ( 
	SELECT DISTINCT id_proj 
	FROM Action 
	WHERE etat = 'terminée' 
	);

-- Les personnes qui ont fait 2 donations avec une valeur supérieure à 500 euros avec les 2 dons
SELECT id_pers, SUM(montant) AS montant_total
FROM Don 
GROUP BY id_pers 
HAVING COUNT(*) = 2 AND montant_total > 500.00;

-- Les interventions non terminées 
SELECT * FROM Intervention WHERE etat != 'terminée';

-- Les personnes qui ont fait que des actions ensemble
SELECT pi1.id_pers 
FROM Personne_Intervention pi1, Personne_Intervention pi2
WHERE pi1.id_pers != pi2.id_pers AND pi1.id_int = pi2.id_int;

-- Dons moyens par personne, en excluant les dons inférieurs à un montant spécifique (ici 15 euros)
SELECT id_pers, AVG(montant) AS moyenne 
FROM Don 
WHERE montant > 15.00 
GROUP BY id_pers;

-- Contacts des adhérents ayant effectué des dons supérieurs à un montant spécifique mais n'ayant pas participé à une intervention
SELECT DISTINCT p.nom, p.prenom, p.mail, p.num 
FROM Personne p, Don d, Personne_Intervention pi
WHERE d.montant > 99.00 AND not exist(select * in Personne_Intervention where id_pers = p.id_pers) AND p.id_pers = d.id_pers AND d.id_pers = pi.id_pers;
-- OR
SELECT DISTINCT p.nom, p.prenom, p.mail, p.num 
FROM Personne p, Don d, Personne_Intervention pi
WHERE d.montant > 99.00 AND pi.id_pers IS NULL AND p.id_pers = d.id_pers AND d.id_pers = pi.id_pers;

-- Liste des pays ordonnée par coût total de donation
SELECT l.pays, SUM(d.montant) AS total_donation 
FROM Personne p, Personne_Don pers_d, Don d, Lieu l
WHERE p.id_pers = pers_d.id_pers AND pers_d.id_proj = d.id_proj AND p.pays = l.pays
GROUP BY l.pays 
ORDER BY total_donation DESC;

-- Les projets avec le ratio le plus élevé de coût total des actions au nombre total d’interventions
SELECT id_proj, SUM(cout) / COUNT(DISTINCT id_act) AS ratio 
FROM Action 
GROUP BY id_proj 
ORDER BY ratio DESC;

-- Statut chef de projet dans 3 actions differentes
SELECT id_pers, COUNT(DISTINCT id_act) 
FROM Personne_Intervention 
WHERE role = 'chef de projet' 
GROUP BY id_pers 
HAVING COUNT(DISTINCT id_act) >= 3;

-- Droits d'acces --
CREATE ROLE Admin; 
CREATE ROLE President; 
CREATE ROLE Tresorier; 
CREATE ROLE Adherents; 
CREATE ROLE Anonyme; 

GRANT ALL PRIVILEGES ON Personne TO Admin; 
GRANT ALL PRIVILEGES ON Projet TO Admin; 
GRANT ALL PRIVILEGES ON Don TO Admin; 
GRANT ALL PRIVILEGES ON Intervention TO Admin; 
GRANT ALL PRIVILEGES ON Action TO Admin; 
GRANT ALL PRIVILEGES ON Lieu TO Admin; 
GRANT ALL PRIVILEGES ON Personne_Intervention TO Admin; 
GRANT ALL PRIVILEGES ON Personne_Don TO Admin; 
-- Nous laissons le choix au President de pouvoir agir dans tout les cas. 
GRANT ALL PRIVILEGES ON Personne TO President; 
GRANT ALL PRIVILEGES ON Projet TO President; 
GRANT ALL PRIVILEGES ON Action TO President; 
GRANT ALL PRIVILEGES ON Intervention TO President; 
GRANT ALL PRIVILEGES ON Lieu TO President;
GRANT ALL PRIVILEGES ON Personne_Intervention TO President; 
GRANT ALL PRIVILEGES ON Personne_Don TO President; 

GRANT SELECT, INSERT, UPDATE ON Don TO Tresorier; 
GRANT SELECT ON Action TO Tresorier; 
GRANT SELECT ON Intervention TO Tresorier; 

GRANT SELECT ON view_personne TO Adherents; 
GRANT SELECT ON Projet TO Adherents; 
GRANT SELECT ON Action TO Adherents; 
GRANT SELECT ON Intervention TO Adherants;
GRANT SELECT ON Lieu TO Adherents;


GRANT SELECT ON view_intervention TO Anonyme;
GRANT SELECT ON view_anonyme TO Anonyme;
GRANT SELECT ON view_anonyme_personne TO Anonyme;

-- View(s) --
-- View de chaque dons avec la somme et le nom 
CREATE VIEW view_anonyme AS 
SELECT D.montant AS somme, P.titre AS nom_du_projet 
FROM Don D, Projet P ON D.id_proj = P.id_proj;

CREATE VIEW view_anonyme_personne AS SELECT nom, prenom FROM Personne;

-- View sur les personnes intervenant sur une action consernant un projet
CREATE VIEW view_intervention AS 
SELECT P.nom, P.prenom, A.nom_act, Pr.titre
FROM Personne P, Personne_Intervention PI, Action A, Projet Pr
WHERE P.id_pers = PI.id_pers AND PI.id_act = A.id_act AND Pr.id_proj = A.id_proj;
