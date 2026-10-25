Terme			Définition simple							Dans le code
Entrée			Unité de base du journal. Trois types possibles.			Classe abstraite Entry
Tâche			Quelque chose à faire. Elle a un état.					Task
Événement		Quelque chose qui se passe à une date (et éventuellement une heure).	Event
Note			Une information à retenir, sans action ni date.				Note
État d’une tâche	À faire •, terminée ×, migrée >, planifiée <, abandonnée (barrée).	Enum des états
Migration		Reporter une tâche non terminée vers un autre jour ou mois.		Méthode du journal
Planifier		Envoyer une tâche dans le Future Log, pour un mois lointain.		Niveau 3
Abandonner		Renoncer à une tâche devenue sans objet.				État de la tâche
Daily Log		Page d’un jour : ses entrées, ajoutées au fil de l’eau.			DailyLog
Monthly Log		Page d’un mois : calendrier et tâches du mois.				MonthlyLog
Future Log		Vue des mois à venir.							Niveau 3
Signifiant		Marque ajoutée à une entrée : * priorité, ! idée.			Attribut optionnel
Rapid logging		La notation courte par symboles.					Affichage
Identifiant unique	Numéro propre à chaque entrée, même si deux ont le même nom.		Attribut id