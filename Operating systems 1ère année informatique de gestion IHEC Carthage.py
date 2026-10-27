#!/usr/bin/env python3
"""
Systèmes d'exploitation — site d'apprentissage pour la 1ère année (semestre 1), IHEC Carthage.
Cours, schémas, exercices corrigés, quiz, simulateurs (ordonnancement CPU, pagination),
terminal Linux d'entraînement, glossaire et plan de révision. Tout est en français.

Lancer :     python systemes_exploitation.py      puis ouvrir http://localhost:8008
Exporter :   python systemes_exploitation.py --export     (crée index.html, hébergeable gratuitement)

NB : le plan des chapitres suit le programme classique d'un cours d'introduction aux SE.
Adaptez la liste CHAPITRES au plan exact de votre enseignant.
"""
import sys
import webbrowser
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8008

# ======================================================================
# CONTENU DES CHAPITRES
# ======================================================================
SCHEMA_COUCHES = """<div class="couches">
<div class="u">Applications <small>navigateur, Word, jeux…</small></div>
<div class="u">Shell / interface graphique</div>
<div class="u">Appels système <small>read, write, fork…</small></div>
<div class="k"><b>Noyau (kernel)</b> <small>processus, mémoire, fichiers, entrées/sorties</small></div>
<div class="h">Matériel <small>processeur, RAM, disque, périphériques</small></div>
</div><p class="legende">Les trois couches du haut tournent en <b>mode utilisateur</b>, le noyau en <b>mode noyau</b> (privilégié).</p>"""

SCHEMA_ETATS = """<svg viewBox="0 0 700 250" class="schema" role="img" aria-label="Diagramme des états d'un processus">
<defs><marker id="f" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0 0L9 4.5L0 9Z" fill="#14213D"/></marker></defs>
<g font-size="15" text-anchor="middle" fill="#14213D">
<g fill="#E8EEFC" stroke="#2B59C3" stroke-width="2"><rect x="10" y="100" width="100" height="44" rx="10"/><rect x="170" y="100" width="100" height="44" rx="10"/>
<rect x="370" y="100" width="110" height="44" rx="10" fill="#D6F5E5" stroke="#1F9D63"/><rect x="560" y="100" width="110" height="44" rx="10"/>
<rect x="270" y="196" width="110" height="44" rx="10" fill="#FFF0C2" stroke="#C99A00"/></g>
<text x="60" y="128">Nouveau</text><text x="220" y="128">Prêt</text><text x="425" y="128">Élu</text><text x="615" y="128">Terminé</text><text x="325" y="224">Bloqué</text>
<g stroke="#14213D" stroke-width="2" marker-end="url(#f)" fill="none"><path d="M110 122H168"/><path d="M270 112H368"/><path d="M370 134H272"/><path d="M480 122H558"/><path d="M415 144L350 194"/><path d="M290 196L235 146"/></g>
<g font-size="12" fill="#444"><text x="139" y="92">admission</text><text x="319" y="104">élection</text><text x="319" y="152">fin de quantum</text><text x="520" y="114">fin</text>
<text x="440" y="186">attente d'E/S</text><text x="200" y="190">E/S terminée</text></g></g></svg>"""

CHAPITRES = [
 dict(
  titre="Introduction aux systèmes d'exploitation",
  resume="Comprendre à quoi sert un système d'exploitation et comment il est organisé.",
  objectifs=["Définir un SE et citer ses deux rôles", "Retracer l'évolution : lots, multiprogrammation, temps partagé", "Distinguer les types de SE", "Expliquer mode noyau, mode utilisateur et appel système"],
  cours="""<h4>1. Qu'est-ce qu'un système d'exploitation ?</h4>
<p>Un <b>système d'exploitation (SE)</b> est le logiciel de base qui fait le lien entre le <b>matériel</b> (processeur, mémoire, disque, clavier…) et les <b>applications</b> (navigateur, Word, jeux…). Sans lui, chaque programme devrait savoir parler lui-même à chaque composant.</p>
<div class="image"><b>Image mentale :</b> le SE est le <b>directeur d'un hôtel</b>. Les clients sont les programmes, les chambres sont la mémoire, le personnel est le processeur. Le directeur attribue les chambres, organise le travail du personnel et empêche un client de déranger les autres.</div>
<h4>Les deux rôles du SE</h4>
<ul><li><b>Machine étendue :</b> il cache la complexité du matériel. Vous ouvrez un fichier sans connaître les secteurs du disque.</li>
<li><b>Gestionnaire de ressources :</b> il partage et protège le processeur, la mémoire et les périphériques entre plusieurs programmes ou utilisateurs.</li></ul>
<h4>2. Fonctions principales</h4>
<ul><li>Gestion des <b>processus</b> (qui utilise le processeur, et quand)</li><li>Gestion de la <b>mémoire</b> centrale</li><li>Gestion des <b>fichiers</b></li><li>Gestion des <b>entrées/sorties</b></li><li><b>Protection et sécurité</b></li><li><b>Interface</b> utilisateur (graphique ou ligne de commande)</li></ul>
<h4>3. Évolution historique</h4>
<table><tr><th>Génération</th><th>Période</th><th>Idée clé</th></tr>
<tr><td>Traitement par lots (batch)</td><td>années 1950-60</td><td>Les travaux (cartes perforées) s'exécutent l'un après l'autre, sans interaction.</td></tr>
<tr><td>Multiprogrammation</td><td>années 1960</td><td>Plusieurs programmes en mémoire : quand l'un attend une E/S, le processeur passe à un autre.</td></tr>
<tr><td>Temps partagé</td><td>années 1960-70</td><td>Le processeur est découpé en petites tranches : plusieurs utilisateurs interagissent en même temps (Unix).</td></tr>
<tr><td>Ordinateur personnel</td><td>années 1980</td><td>MS-DOS, Mac OS, Windows : un utilisateur, une machine.</td></tr>
<tr><td>Réseau, mobile, cloud</td><td>depuis 1990</td><td>Linux, Android, virtualisation, systèmes distribués.</td></tr></table>
<h4>4. Types de systèmes d'exploitation</h4>
<ul><li><b>Mono-tâche / multitâche</b> : un seul programme à la fois, ou plusieurs.</li><li><b>Mono-utilisateur / multi-utilisateur</b> : Linux et Windows Server gèrent plusieurs comptes.</li>
<li><b>Temps réel</b> : les réponses doivent respecter des échéances strictes (freinage ABS, avionique).</li><li><b>Distribué</b> : plusieurs machines qui se comportent comme une seule.</li><li><b>Embarqué</b> : dans une box internet, une voiture, une machine à laver.</li></ul>
<h4>5. Architecture : noyau, shell et appels système</h4>"""+SCHEMA_COUCHES+"""
<p>Le <b>noyau</b> (kernel) est le cœur du SE. Il s'exécute en <b>mode privilégié</b> et il est le seul à toucher directement au matériel. Une application tourne en <b>mode utilisateur</b> : pour obtenir un service (lire un fichier, créer un processus), elle fait un <b>appel système</b>, qui fait passer le processeur en mode noyau le temps du service. Le <b>shell</b> est l'interpréteur de commandes qui permet à l'utilisateur de parler au système.</p>
<p><b>Organisations possibles du noyau :</b> <i>monolithique</i> (tout dans le noyau, rapide : Linux), <i>micro-noyau</i> (noyau minimal, le reste en dehors, plus sûr), <i>en couches</i> (chaque couche s'appuie sur celle du dessous).</p>""",
  retenir=["Le SE est un intermédiaire entre applications et matériel, et un gestionnaire de ressources.", "Le noyau s'exécute en mode privilégié, les applications en mode utilisateur.", "Un appel système est la porte d'entrée vers le noyau.", "Multiprogrammation : le processeur ne reste plus inactif pendant une E/S.", "Temps partagé : plusieurs utilisateurs interactifs sur une même machine."],
  erreurs=["Confondre SE et interface graphique : l'interface n'est qu'une partie du SE.", "Dire que Word ou Chrome sont des SE : ce sont des applications. Windows, Linux, macOS, Android sont des SE.", "Confondre noyau et SE : le SE contient aussi le shell, les pilotes et les utilitaires."],
  exo=("Un programme veut lire un fichier. Décrivez les étapes entre le programme et le disque.",
       "<ol><li>Le programme (mode utilisateur) appelle <code>read()</code> : c'est un <b>appel système</b>.</li><li>Le processeur passe en <b>mode noyau</b> (interruption logicielle).</li><li>Le noyau vérifie les <b>droits</b> et localise le fichier grâce au système de fichiers.</li><li>Il demande la lecture au <b>pilote</b> du disque. Le processus devient <b>bloqué</b> et le processeur est donné à un autre processus.</li><li>Quand le disque a fini, il envoie une <b>interruption</b> : les données sont copiées en mémoire et le processus redevient <b>prêt</b>.</li><li>Retour en <b>mode utilisateur</b>.</li></ol>"),
  quiz=[("Quel est le rôle d'un système d'exploitation ?", ["Créer des documents texte", "Gérer les ressources et servir d'intermédiaire entre les applications et le matériel", "Remplacer le processeur", "Se connecter à Internet uniquement"], 1, "Le SE est à la fois machine étendue (il simplifie le matériel) et gestionnaire de ressources."),
        ("Un appel système sert à :", ["Redémarrer l'ordinateur", "Demander un service au noyau depuis une application", "Installer un logiciel", "Compiler un programme"], 1, "C'est le seul moyen, pour un programme en mode utilisateur, d'obtenir un service du noyau."),
        ("Quelle évolution évite que le processeur reste inactif pendant une E/S ?", ["Le traitement par lots", "La multiprogrammation", "Le mode texte", "La mémoire cache"], 1, "Avec plusieurs programmes en mémoire, le processeur passe à un autre pendant qu'un programme attend.")],
 ),
 dict(
  titre="Processus et threads",
  resume="Comprendre ce qu'est un processus, ses états, et la différence avec un thread.",
  objectifs=["Distinguer programme et processus", "Décrire le PCB et les états d'un processus", "Expliquer la commutation de contexte", "Comparer processus et threads", "Citer les moyens de communication entre processus"],
  cours="""<h4>1. Programme ou processus ?</h4>
<p>Un <b>programme</b> est un fichier sur le disque. Un <b>processus</b> est un programme <b>en cours d'exécution</b>.</p>
<div class="image"><b>Image mentale :</b> le programme est une <i>recette de cuisine</i>. Le processus est le <i>cuisinier en train de cuisiner</i>, avec ses ingrédients et là où il en est. Deux cuisiniers peuvent suivre la même recette : deux processus du même programme.</div>
<h4>2. Que contient un processus ?</h4>
<p>Le code, les données, le <b>tas</b> (mémoire dynamique), la <b>pile</b> (appels de fonctions), le <b>compteur ordinal</b> (la prochaine instruction), les registres et les fichiers ouverts. Le SE les résume dans le <b>PCB</b> (<i>Process Control Block</i>) : PID, état, compteur ordinal, registres, priorité, informations mémoire, fichiers ouverts.</p>
<h4>3. Les états d'un processus</h4>"""+SCHEMA_ETATS+"""
<ul><li><b>Prêt</b> : il attend le processeur.</li><li><b>Élu</b> (en exécution) : il utilise le processeur. Il y en a un seul par cœur.</li><li><b>Bloqué</b> : il attend un événement (fin d'une lecture disque, saisie clavier).</li></ul>
<p>Remarque : un processus bloqué ne peut pas passer directement à Élu. Il repasse d'abord par Prêt.</p>
<h4>4. Commutation de contexte</h4>
<p>Pour passer d'un processus à un autre, le SE <b>sauvegarde</b> le PCB de l'ancien et <b>charge</b> celui du nouveau. C'est du temps perdu (surcoût) : plus on change souvent, moins le processeur travaille vraiment.</p>
<h4>5. Création et fin</h4>
<p>Un processus peut en créer d'autres (ses <i>fils</i>), ce qui forme un arbre. Sous Unix, <code>fork()</code> crée une copie du processus et <code>exec()</code> remplace son programme. <code>exit()</code> termine un processus.</p>
<h4>6. Les threads</h4>
<p>Un <b>thread</b> (fil d'exécution) est un « mini-processus » à l'intérieur d'un processus. Les threads d'un même processus <b>partagent</b> le code, les données et les fichiers ouverts, mais chacun a sa <b>pile</b> et ses <b>registres</b>. Exemple : un navigateur utilise un thread pour l'affichage et d'autres pour télécharger.</p>
<table><tr><th></th><th>Processus</th><th>Thread</th></tr><tr><td>Mémoire</td><td>Espace séparé</td><td>Partagée avec les autres threads</td></tr><tr><td>Création</td><td>Lourde</td><td>Légère et rapide</td></tr><tr><td>Communication</td><td>Mécanismes dédiés (IPC)</td><td>Directe, via la mémoire commune</td></tr><tr><td>Risque</td><td>Isolation sûre</td><td>Accès concurrents (chapitre 4)</td></tr></table>
<h4>7. Communication entre processus (IPC)</h4>
<p>Les processus étant isolés, ils communiquent par : <b>tubes</b> (<i>pipes</i>), <b>files de messages</b>, <b>mémoire partagée</b>, <b>signaux</b> et <b>sockets</b> (réseau).</p>""",
  retenir=["Programme = fichier passif, processus = programme en exécution.", "États : Nouveau, Prêt, Élu, Bloqué, Terminé.", "Le PCB contient tout ce que le SE doit savoir pour reprendre un processus.", "Les threads partagent la mémoire du processus, mais pas la pile.", "La commutation de contexte a un coût."],
  erreurs=["Confondre Prêt et Bloqué : Prêt attend le processeur, Bloqué attend un événement.", "Penser qu'un processus Bloqué peut passer à Élu directement.", "Croire que les threads ont chacun leurs données : ils partagent celles du processus."],
  exo=("Un processus passe par : Nouveau → Prêt → Élu → Bloqué (lecture disque) → Prêt → Élu → Terminé. Nommez chaque transition.",
       "<ol><li>Nouveau → Prêt : <b>admission</b></li><li>Prêt → Élu : <b>élection</b> (l'ordonnanceur choisit le processus)</li><li>Élu → Bloqué : <b>attente d'une E/S</b> (lecture disque)</li><li>Bloqué → Prêt : <b>fin de l'E/S</b> (réveil)</li><li>Prêt → Élu : <b>élection</b> de nouveau</li><li>Élu → Terminé : <b>fin d'exécution</b></li></ol>"),
  quiz=[("Dans quel état est un processus qui attend la fin d'une lecture disque ?", ["Prêt", "Élu", "Bloqué", "Terminé"], 2, "Il attend un événement extérieur : il est bloqué, pas prêt."),
        ("Les threads d'un même processus partagent :", ["Leur pile", "Leurs registres", "Le code et les données", "Rien"], 2, "Chaque thread a sa propre pile et ses registres, mais le code et les données sont communs."),
        ("Que contient le PCB ?", ["Le code source du programme", "Les informations dont le SE a besoin pour gérer le processus", "La liste des utilisateurs", "Le contenu du disque"], 1, "PID, état, compteur ordinal, registres, priorité, mémoire, fichiers ouverts.")],
 ),
 dict(
  titre="Ordonnancement du processeur",
  resume="Savoir choisir quel processus s'exécute, et calculer les temps d'attente et de rotation.",
  objectifs=["Définir ordonnancement, préemptif et non préemptif", "Calculer temps de rotation, d'attente et de réponse", "Appliquer FCFS, SJF, SRT, Round Robin et priorités", "Dessiner un diagramme de Gantt"],
  cours="""<h4>1. Pourquoi ordonnancer ?</h4>
<p>Il y a plusieurs processus <b>prêts</b> mais un seul processeur. L'<b>ordonnanceur</b> (<i>scheduler</i>) choisit lequel s'exécute. Un algorithme est <b>préemptif</b> si le SE peut retirer le processeur à un processus en cours, <b>non préemptif</b> s'il doit attendre que le processus se termine ou se bloque.</p>
<h4>2. Les critères (formules à connaître)</h4>
<table><tr><th>Mesure</th><th>Formule</th></tr><tr><td>Temps de rotation (séjour)</td><td><b>fin − arrivée</b></td></tr><tr><td>Temps d'attente</td><td><b>rotation − durée d'exécution</b></td></tr><tr><td>Temps de réponse</td><td>premier passage sur le CPU − arrivée</td></tr><tr><td>Utilisation du CPU, débit</td><td>% de temps occupé, processus terminés par seconde</td></tr></table>
<h4>3. Les algorithmes</h4>
<table><tr><th>Algorithme</th><th>Principe</th><th>Avantage / inconvénient</th></tr>
<tr><td><b>FCFS</b> (premier arrivé, premier servi)</td><td>File d'attente simple, non préemptif</td><td>Simple, mais effet de convoi : un long processus fait attendre tous les courts</td></tr>
<tr><td><b>SJF</b> (plus court d'abord)</td><td>Choisit la plus petite durée, non préemptif</td><td>Minimise l'attente moyenne, mais il faut connaître les durées, et les longs processus risquent la famine</td></tr>
<tr><td><b>SRT</b> (temps restant le plus court)</td><td>Version préemptive de SJF</td><td>Très efficace, plus de commutations</td></tr>
<tr><td><b>Round Robin</b> (tourniquet)</td><td>Chaque processus reçoit un <b>quantum</b> q, puis retourne en fin de file</td><td>Équitable, bon temps de réponse. Si q est trop petit : trop de commutations. Si q est trop grand : on retombe sur FCFS</td></tr>
<tr><td><b>Priorités</b></td><td>On exécute le processus le plus prioritaire</td><td>Risque de <b>famine</b> pour les faibles priorités, résolu par le <b>vieillissement</b> (la priorité augmente avec l'attente)</td></tr></table>
<div class="image"><b>Image mentale :</b> à la caisse d'un supermarché, FCFS c'est la file normale. SJF, c'est laisser passer en premier celui qui n'a qu'un article. Round Robin, c'est servir tout le monde 2 minutes à tour de rôle.</div>
<h4>4. Exemple pas à pas</h4>
<p>Trois processus : P1 (arrive à 0, durée 5), P2 (arrive à 1, durée 3), P3 (arrive à 2, durée 1).</p>
<table><tr><th></th><th>Diagramme de Gantt</th><th>Attente (P1, P2, P3)</th><th>Attente moyenne</th></tr>
<tr><td><b>FCFS</b></td><td>P1 [0-5] P2 [5-8] P3 [8-9]</td><td>0, 4, 6</td><td>3,33</td></tr>
<tr><td><b>SJF</b></td><td>P1 [0-5] P3 [5-6] P2 [6-9]</td><td>0, 5, 3</td><td>2,67</td></tr></table>
<p>SJF fait mieux : en laissant passer P3 (très court), on réduit l'attente globale. <b>Vérifiez avec le simulateur d'ordonnancement</b> dans la section « Outils ».</p>""",
  retenir=["rotation = fin − arrivée ; attente = rotation − durée.", "SJF minimise l'attente moyenne (si les durées sont connues).", "Round Robin : le choix du quantum est un compromis.", "Priorités : attention à la famine, le vieillissement la corrige.", "Un processus ne peut pas démarrer avant son arrivée."],
  erreurs=["Confondre attente et rotation (la rotation inclut le temps d'exécution).", "Faire commencer un processus avant son instant d'arrivée.", "Pour Round Robin, oublier la convention : ici, un processus qui arrive pendant un quantum se place dans la file avant celui qui vient d'être préempté. Demandez la convention à votre enseignant."],
  exo=("Round Robin avec q = 2 : P1 (arrivée 0, durée 6), P2 (arrivée 1, durée 4), P3 (arrivée 2, durée 2). Donnez le Gantt, les temps de rotation et d'attente.",
       "<p><b>Gantt :</b> P1 [0-2] · P2 [2-4] · P3 [4-6] · P1 [6-8] · P2 [8-10] · P1 [10-12]</p><p><b>Fins :</b> P1 = 12, P2 = 10, P3 = 6.</p><p><b>Rotation</b> (fin − arrivée) : P1 = 12, P2 = 9, P3 = 4 → moyenne 8,33.</p><p><b>Attente</b> (rotation − durée) : P1 = 6, P2 = 5, P3 = 2 → moyenne <b>4,33</b>.</p><p><i>Astuce :</i> à t = 2, P3 arrive pendant que P1 est préempté : la file devient P2, P3, P1.</p>"),
  quiz=[("Quel algorithme minimise le temps d'attente moyen (durées connues) ?", ["FCFS", "SJF", "Round Robin avec q très petit", "Priorités"], 1, "SJF est optimal pour l'attente moyenne en non préemptif."),
        ("Le temps d'attente est égal à :", ["fin − arrivée", "rotation − durée d'exécution", "durée − arrivée", "arrivée + durée"], 1, "L'attente est le temps passé dans l'état Prêt : rotation moins le temps réellement passé sur le CPU."),
        ("Quel est le risque principal de l'ordonnancement par priorités ?", ["La famine", "L'interblocage", "La fragmentation", "Le thrashing"], 0, "Un processus peu prioritaire peut ne jamais être élu. Le vieillissement est la solution.")],
 ),
 dict(
  titre="Synchronisation et interblocage",
  resume="Éviter les erreurs d'accès concurrent et comprendre pourquoi des processus se bloquent mutuellement.",
  objectifs=["Expliquer une condition de concurrence", "Définir section critique, mutex et sémaphore", "Reconnaître le problème producteur/consommateur", "Citer les 4 conditions de Coffman", "Appliquer l'algorithme du banquier"],
  cours="""<h4>1. Le problème : la condition de concurrence</h4>
<p>Deux threads exécutent <code>compteur = compteur + 1</code>. Cette instruction se fait en 3 étapes : <i>lire, ajouter, écrire</i>. Si elles s'entrelacent :</p>
<table><tr><th>Étape</th><th>Thread 1</th><th>Thread 2</th><th>compteur</th></tr><tr><td>1</td><td>lit 5</td><td></td><td>5</td></tr><tr><td>2</td><td></td><td>lit 5</td><td>5</td></tr><tr><td>3</td><td>écrit 6</td><td></td><td>6</td></tr><tr><td>4</td><td></td><td>écrit 6</td><td>6 (au lieu de 7 !)</td></tr></table>
<p>Le résultat dépend de l'ordre d'exécution : c'est une <b>condition de concurrence</b> (<i>race condition</i>).</p>
<h4>2. Section critique</h4>
<p>La <b>section critique</b> est la partie du code qui accède à une ressource partagée. Une bonne solution respecte : <b>exclusion mutuelle</b> (un seul à la fois), <b>progression</b> (personne n'est bloqué sans raison) et <b>attente bornée</b> (pas de famine).</p>
<h4>3. Les outils</h4>
<ul><li><b>Mutex (verrou)</b> : <code>lock()</code> avant la section critique, <code>unlock()</code> après. Comme la clé des toilettes d'un café : une seule personne peut l'avoir.</li>
<li><b>Sémaphore</b> : un entier S avec deux opérations atomiques. <code>P(S)</code> (wait) : S ← S − 1, et si S &lt; 0 le processus se bloque. <code>V(S)</code> (signal) : S ← S + 1, et si S ≤ 0 on réveille un processus. Un sémaphore à 1 est un mutex. Un sémaphore à N compte N ressources identiques.</li>
<li><b>Moniteur</b> : mécanisme de plus haut niveau qui garantit l'exclusion mutuelle (synchronized en Java).</li></ul>
<h4>4. Problèmes classiques</h4>
<p><b>Producteur/consommateur</b> : un tampon de N cases. Le producteur ne peut pas ajouter si le tampon est plein, le consommateur ne peut pas retirer s'il est vide. Trois sémaphores : <code>mutex = 1</code>, <code>vide = N</code>, <code>plein = 0</code>.</p>
<pre>Producteur :                 Consommateur :
  P(vide)                      P(plein)
  P(mutex)                     P(mutex)
  ajouter(objet)               retirer(objet)
  V(mutex)                     V(mutex)
  V(plein)                     V(vide)</pre>
<p>Autres classiques : <b>lecteurs/rédacteurs</b> (plusieurs lecteurs OK, un seul rédacteur) et <b>dîner des philosophes</b> (risque d'interblocage si chacun prend sa fourchette gauche).</p>
<h4>5. L'interblocage (deadlock)</h4>
<p>Des processus s'attendent mutuellement pour toujours. Exemple : P1 détient la ressource A et attend B, P2 détient B et attend A. Il faut que <b>les 4 conditions de Coffman</b> soient réunies :</p>
<ol><li><b>Exclusion mutuelle</b> : une ressource n'est utilisée que par un processus à la fois.</li><li><b>Détention et attente</b> : on garde ce qu'on a en demandant autre chose.</li><li><b>Pas de réquisition</b> : on ne peut pas retirer de force une ressource.</li><li><b>Attente circulaire</b> : P1 attend P2, qui attend … qui attend P1.</li></ol>
<h4>6. Comment traiter l'interblocage</h4>
<ul><li><b>Prévention</b> : empêcher l'une des 4 conditions (ex. imposer un ordre dans les demandes pour supprimer l'attente circulaire).</li>
<li><b>Évitement</b> : l'<b>algorithme du banquier</b> n'accorde une ressource que si le système reste dans un <b>état sûr</b> (il existe un ordre dans lequel tous les processus peuvent finir).</li>
<li><b>Détection puis guérison</b> : repérer un cycle dans le graphe d'allocation, puis tuer un processus ou réquisitionner une ressource.</li>
<li><b>Ignorer</b> (« politique de l'autruche ») : choix de nombreux SE, car les interblocages sont rares.</li></ul>""",
  retenir=["Condition de concurrence : le résultat dépend de l'ordre d'exécution.", "Mutex = sémaphore binaire. P bloque, V réveille.", "Les 4 conditions de Coffman doivent être vraies en même temps.", "État sûr = il existe une séquence où tous les processus peuvent se terminer.", "Casser une seule condition suffit à empêcher l'interblocage."],
  erreurs=["Confondre famine (attente très longue) et interblocage (attente infinie mutuelle).", "Croire qu'un état non sûr est forcément un interblocage : c'est seulement un risque.", "Oublier d'inverser l'ordre des P dans producteur/consommateur : P(mutex) avant P(vide) provoque un interblocage."],
  exo=("Un système a 12 ressources identiques. P1 a besoin au maximum de 10 et en détient 5 ; P2 max 4, détient 2 ; P3 max 9, détient 2. Cet état est-il sûr ?",
       "<p><b>Disponible</b> = 12 − (5 + 2 + 2) = <b>3</b>.</p><p><b>Besoins restants</b> (max − détenu) : P1 = 5, P2 = 2, P3 = 7.</p><ol><li>P2 a besoin de 2 ≤ 3 : il termine et rend 2 → disponible = 5.</li><li>P1 a besoin de 5 ≤ 5 : il termine et rend 5 → disponible = 10.</li><li>P3 a besoin de 7 ≤ 10 : il termine.</li></ol><p><b>Séquence sûre : P2, P1, P3</b> → l'état est <b>sûr</b>.</p>"),
  quiz=[("Quelle condition de Coffman signifie qu'on ne peut pas retirer une ressource de force ?", ["Exclusion mutuelle", "Détention et attente", "Pas de réquisition", "Attente circulaire"], 2, "« Pas de réquisition » (non préemption) : seul le détenteur peut libérer la ressource."),
        ("Que fait P(S) quand le sémaphore vaut 0 ?", ["Il retourne une erreur", "Le processus se bloque", "Il passe quand même", "Il remet S à 1"], 1, "S devient négatif et le processus est mis en attente jusqu'à un V(S)."),
        ("Une condition de concurrence est :", ["Une panne matérielle", "Un résultat qui dépend de l'ordre d'exécution des processus", "Une file d'attente trop longue", "Un défaut de page"], 1, "Les accès non synchronisés à une donnée partagée donnent des résultats imprévisibles.")],
 ),
 dict(
  titre="Gestion de la mémoire",
  resume="Allocation, pagination, segmentation, mémoire virtuelle et remplacement de pages.",
  objectifs=["Distinguer adresse logique et physique", "Reconnaître les fragmentations interne et externe", "Calculer une traduction d'adresse en pagination", "Expliquer la mémoire virtuelle et le défaut de page", "Appliquer FIFO, LRU et OPT"],
  cours="""<h4>1. Le rôle du gestionnaire de mémoire</h4>
<p>Partager la RAM entre les processus, <b>isoler</b> chacun des autres et donner l'illusion de beaucoup de mémoire. Le programme manipule des <b>adresses logiques</b>. La <b>MMU</b> (unité matérielle) les convertit en <b>adresses physiques</b> dans la RAM.</p>
<h4>2. Allocation contiguë</h4>
<ul><li><b>Partitions fixes</b> : mémoire découpée à l'avance. Fragmentation <b>interne</b> : place perdue <i>dans</i> une partition trop grande.</li>
<li><b>Partitions variables</b> : une partition à la taille du processus. Fragmentation <b>externe</b> : beaucoup de petits trous inutilisables entre les partitions.</li>
<li>Stratégies de placement : <b>first fit</b> (premier trou suffisant), <b>best fit</b> (le plus petit trou suffisant), <b>worst fit</b> (le plus grand trou).</li>
<li><b>Compactage</b> : regrouper les trous. <b>Swapping</b> : mettre un processus sur le disque pour libérer la RAM.</li></ul>
<h4>3. La pagination</h4>
<p>La mémoire logique est découpée en <b>pages</b> et la RAM en <b>cadres</b> de même taille. La <b>table des pages</b> indique dans quel cadre se trouve chaque page. Une adresse logique est un couple (<b>n° de page</b>, <b>déplacement</b>).</p>
<div class="formule">n° de page = adresse <b>DIV</b> taille de page &nbsp;·&nbsp; déplacement = adresse <b>MOD</b> taille de page<br>adresse physique = n° de cadre × taille de page + déplacement</div>
<p><b>Exemple :</b> pages de 1 024 octets, adresse logique 3 500 → page 3 (3 × 1 024 = 3 072), déplacement 428. Si la page 3 est dans le cadre 7 : adresse physique = 7 × 1 024 + 428 = <b>7 596</b>.</p>
<p>La pagination supprime la fragmentation externe. Il reste un peu de fragmentation interne dans la dernière page. Le <b>TLB</b> est un petit cache qui accélère la consultation de la table des pages.</p>
<h4>4. La segmentation</h4>
<p>Découpage selon la logique du programme (code, données, pile). Chaque segment a une <b>base</b> et une <b>limite</b> (table des segments). Retour de la fragmentation externe.</p>
<h4>5. La mémoire virtuelle</h4>
<p>Seules les pages <b>utiles</b> sont en RAM, le reste reste sur le disque. Si le programme utilise une page absente, il y a un <b>défaut de page</b> : le SE charge la page depuis le disque (très lent) puis relance l'instruction. Trop de défauts de pages = <b>thrashing</b> : le système passe son temps à charger au lieu de calculer.</p>
<h4>6. Algorithmes de remplacement de pages</h4>
<p>Quand il n'y a plus de cadre libre, il faut choisir une page « victime » :</p>
<ul><li><b>FIFO</b> : la plus ancienne en mémoire. Simple, mais peut souffrir de l'<b>anomalie de Belady</b> (plus de cadres, plus de défauts).</li><li><b>LRU</b> : la page <b>la moins récemment utilisée</b>. Très bon, mais coûteux à suivre.</li><li><b>OPT</b> (optimal) : la page qui sera utilisée <b>le plus tard</b>. Donne le minimum de défauts, mais est irréalisable (il faut connaître l'avenir). Sert de référence.</li><li><b>Horloge</b> : approximation pratique de LRU.</li></ul>
<p>Utilisez le <b>simulateur de pagination</b> dans « Outils » pour voir les défauts étape par étape.</p>""",
  retenir=["Adresse physique = cadre × taille + déplacement.", "Fragmentation interne (dans la partition) ≠ externe (entre les partitions).", "Pagination : taille fixe, sans fragmentation externe. Segmentation : taille logique, avec fragmentation externe.", "Défaut de page = page absente de la RAM.", "OPT ≤ LRU ≤ FIFO en général, et OPT est la référence théorique."],
  erreurs=["Confondre page (mémoire logique) et cadre (RAM).", "Oublier le déplacement dans le calcul de l'adresse physique.", "Croire que LRU et FIFO donnent les mêmes résultats."],
  exo=("A) Pages de 1 Ko, table : page 0 → cadre 5, 1 → 2, 2 → 9, 3 → 7. Quelle est l'adresse physique de l'adresse logique 3 500 ?<br>B) Chaîne de références 7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1 avec 3 cadres : combien de défauts pour FIFO, LRU, OPT ?",
       "<p><b>A)</b> 3 500 = 3 × 1 024 + 428 → page 3, déplacement 428. Page 3 → cadre 7. Adresse physique = 7 × 1 024 + 428 = <b>7 596</b>.</p><p><b>B)</b> FIFO : <b>15</b> défauts · LRU : <b>12</b> défauts · OPT : <b>9</b> défauts. Vérifiez et observez chaque étape avec le simulateur.</p>"),
  quiz=[("La pagination découpe la mémoire en blocs de taille :", ["Variable selon le programme", "Fixe", "Aléatoire", "Égale à la taille du disque"], 1, "Pages et cadres ont la même taille fixe."),
        ("Que provoque l'accès à une page absente de la RAM ?", ["Un interblocage", "Un défaut de page", "Un arrêt du système", "Une commutation de contexte"], 1, "Le SE doit aller chercher la page sur le disque."),
        ("Quel algorithme de remplacement est optimal mais irréalisable en pratique ?", ["FIFO", "LRU", "OPT", "Horloge"], 2, "OPT nécessite de connaître les accès futurs.")],
 ),
 dict(
  titre="Systèmes de fichiers",
  resume="Comprendre comment les fichiers sont organisés, stockés et protégés sur le disque.",
  objectifs=["Définir fichier, répertoire et chemin", "Comparer les méthodes d'allocation", "Expliquer l'inode et la FAT", "Lire les droits rwx et utiliser chmod"],
  cours="""<h4>1. Le fichier</h4>
<p>Un <b>fichier</b> est un ensemble nommé d'informations conservées durablement. Ses <b>attributs</b> : nom, type, taille, emplacement sur le disque, droits d'accès, dates. Opérations : créer, ouvrir, lire, écrire, se positionner (<i>seek</i>), fermer, supprimer. L'accès peut être <b>séquentiel</b> (du début à la fin) ou <b>direct</b> (n'importe où).</p>
<h4>2. Les répertoires</h4>
<p>Les fichiers sont rangés dans des <b>répertoires</b> (dossiers) organisés en <b>arborescence</b>. Un <b>chemin absolu</b> part de la racine (<code>/home/etudiant/notes.txt</code> ou <code>C:\\Users\\Sami\\notes.txt</code>), un <b>chemin relatif</b> part du répertoire courant (<code>../notes.txt</code>). Un <b>lien symbolique</b> est un raccourci vers un autre fichier.</p>
<h4>3. Comment stocker un fichier sur le disque ?</h4>
<p>Le disque est découpé en <b>blocs</b> (clusters). Le SE doit retenir quels blocs appartiennent à quel fichier. Trois méthodes :</p>
<table><tr><th>Méthode</th><th>Principe</th><th>Avantages</th><th>Inconvénients</th></tr>
<tr><td><b>Contiguë</b></td><td>Les blocs se suivent</td><td>Simple, rapide, accès direct</td><td>Fragmentation externe, difficile d'agrandir un fichier</td></tr>
<tr><td><b>Chaînée</b></td><td>Chaque bloc pointe vers le suivant. <b>FAT</b> : les pointeurs sont dans une table à part</td><td>Pas de fragmentation externe</td><td>Accès direct lent : il faut suivre la chaîne</td></tr>
<tr><td><b>Indexée</b></td><td>Un bloc d'index (l'<b>inode</b> sous Unix) liste tous les blocs du fichier</td><td>Accès direct, pas de fragmentation externe</td><td>Espace pris par l'index</td></tr></table>
<p>L'<b>inode</b> contient les attributs du fichier (taille, droits, dates…) et les adresses de ses blocs, mais <b>pas son nom</b> : le nom est stocké dans le répertoire.</p>
<h4>4. Gestion de l'espace libre</h4>
<p><b>Bitmap</b> : 1 bit par bloc (0 = libre, 1 = occupé). Ou <b>liste chaînée</b> des blocs libres.</p>
<h4>5. Les droits Unix</h4>
<p>Trois groupes (<b>propriétaire, groupe, autres</b>) et trois droits : <b>r</b> (lire) = 4, <b>w</b> (écrire) = 2, <b>x</b> (exécuter) = 1. On additionne : <code>rwx</code> = 7, <code>r-x</code> = 5, <code>r--</code> = 4. Ainsi <code>chmod 754 fichier</code> donne <code>rwxr-xr--</code>.</p>
<h4>6. Systèmes de fichiers courants</h4>
<p><b>FAT32</b> (clés USB), <b>NTFS</b> (Windows), <b>ext4</b> (Linux), <b>APFS</b> (macOS).</p>""",
  retenir=["Contiguë = rapide mais fragmentation externe. Chaînée = accès direct lent. Indexée = bon compromis.", "L'inode contient les attributs et les adresses des blocs, pas le nom.", "r = 4, w = 2, x = 1.", "Chemin absolu (depuis la racine) ≠ chemin relatif (depuis le répertoire courant)."],
  erreurs=["Croire que le nom du fichier est dans l'inode.", "Confondre FAT (table de chaînage) et FAT32 (système de fichiers).", "Mal additionner les droits : rw- = 4 + 2 = 6, pas 5."],
  exo=("A) Que signifie chmod 640 notes.txt ? Que peut faire un autre utilisateur ?<br>B) Un fichier occupe 10 blocs. Combien de lectures pour atteindre le 8ᵉ bloc en allocation chaînée ? en allocation indexée ?",
       "<p><b>A)</b> 6 = rw- (propriétaire : lire et écrire), 4 = r-- (groupe : lire), 0 = --- (autres : <b>aucun accès</b>).</p><p><b>B)</b> Chaînée : il faut suivre la chaîne depuis le premier bloc, donc <b>8 lectures</b>. Indexée : 1 lecture de l'index + 1 lecture du bloc = <b>2 lectures</b>.</p>"),
  quiz=[("Que contient un inode ?", ["Le nom du fichier", "Les attributs et les adresses des blocs du fichier", "Le contenu du répertoire parent", "La liste des utilisateurs"], 1, "Le nom est stocké dans le répertoire, pas dans l'inode."),
        ("Quelle méthode d'allocation permet l'accès direct sans fragmentation externe ?", ["Contiguë", "Chaînée", "Indexée", "Aucune"], 2, "L'index donne directement l'adresse de chaque bloc."),
        ("Que vaut rwx en notation octale ?", ["5", "6", "7", "8"], 2, "4 + 2 + 1 = 7.")],
 ),
 dict(
  titre="Entrées/sorties et disques",
  resume="Comment le SE dialogue avec les périphériques et organise l'accès au disque.",
  objectifs=["Distinguer contrôleur et pilote", "Comparer scrutation, interruption et DMA", "Calculer un temps d'accès disque", "Appliquer FCFS et SSTF à une file de requêtes"],
  cours="""<h4>1. Périphériques, contrôleurs et pilotes</h4>
<p>Il y a des périphériques <b>blocs</b> (disque : données lues par blocs) et <b>caractères</b> (clavier : flux d'octets). Chaque périphérique a un <b>contrôleur</b> (matériel) et un <b>pilote</b> (<i>driver</i>), logiciel du SE qui sait le commander. Le pilote cache les différences entre fabricants.</p>
<h4>2. Comment le processeur dialogue avec un périphérique</h4>
<table><tr><th>Technique</th><th>Principe</th></tr><tr><td><b>Scrutation</b> (polling)</td><td>Le processeur vérifie en boucle si le périphérique a fini. Il gaspille du temps.</td></tr>
<tr><td><b>Interruptions</b></td><td>Le périphérique prévient le processeur quand il a fini. Le processeur fait autre chose entre-temps.</td></tr>
<tr><td><b>DMA</b> (accès direct à la mémoire)</td><td>Le contrôleur transfère les données directement entre le périphérique et la RAM, sans mobiliser le processeur. Une interruption signale la fin.</td></tr></table>
<h4>3. Tampons, cache et spooling</h4>
<p>Un <b>tampon</b> (buffer) compense les différences de vitesse. Un <b>cache</b> garde en mémoire les données récemment utilisées. Le <b>spooling</b> met les travaux en file d'attente (exemple : l'impression).</p>
<h4>4. Le disque dur</h4>
<p>Des <b>plateaux</b> divisés en <b>pistes</b> et <b>secteurs</b> ; l'ensemble des pistes situées au même rayon forme un <b>cylindre</b>.</p>
<div class="formule">Temps d'accès = temps de recherche (<i>seek</i>, déplacement du bras) + latence de rotation + temps de transfert</div>
<p>Le plus coûteux est le déplacement du bras. Le SSD n'a pas de pièces mobiles, donc il est beaucoup plus rapide.</p>
<h4>5. Ordonnancement des requêtes disque</h4>
<p>Pour réduire le déplacement du bras :</p>
<ul><li><b>FCFS</b> : dans l'ordre d'arrivée (simple, mouvements importants).</li><li><b>SSTF</b> : la piste la plus proche d'abord (efficace, mais risque de famine).</li><li><b>SCAN</b> (ascenseur) : le bras balaie le disque dans un sens jusqu'au bout, puis revient. <b>C-SCAN</b> : revient directement au début. <b>LOOK</b> : comme SCAN, mais s'arrête à la dernière requête.</li></ul>
<div class="image"><b>Image mentale :</b> SCAN, c'est un ascenseur qui monte en s'arrêtant à tous les étages demandés, puis redescend en faisant de même.</div>""",
  retenir=["Pilote = logiciel, contrôleur = matériel.", "Interruption : le périphérique prévient. DMA : le transfert se fait sans le CPU.", "Temps d'accès = seek + latence + transfert.", "SSTF peut affamer les requêtes lointaines."],
  erreurs=["Confondre scrutation et interruption.", "Oublier que le DMA a aussi besoin d'une interruption à la fin.", "Mal compter les distances en valeur absolue (|a − b|)."],
  exo=("Disque de pistes 0 à 199, tête en 53, requêtes : 98, 183, 37, 122, 14, 124, 65, 67. Calculez le déplacement total pour FCFS et SSTF.",
       "<p><b>FCFS</b> : 53→98 (45), →183 (85), →37 (146), →122 (85), →14 (108), →124 (110), →65 (59), →67 (2) = <b>640 pistes</b>.</p><p><b>SSTF</b> : 53→65 (12), →67 (2), →37 (30), →14 (23), →98 (84), →122 (24), →124 (2), →183 (59) = <b>236 pistes</b>.</p><p>SSTF réduit beaucoup le déplacement, mais peut retarder indéfiniment les requêtes éloignées.</p>"),
  quiz=[("Le DMA permet :", ["De remplacer le processeur", "De transférer des données entre périphérique et mémoire sans mobiliser le processeur", "D'augmenter la taille du disque", "De chiffrer les fichiers"], 1, "Le processeur est seulement prévenu à la fin du transfert."),
        ("Le temps d'accès à un disque dur est :", ["seek + latence de rotation + transfert", "seek × latence", "transfert seulement", "latence − seek"], 0, "Les trois composantes s'additionnent."),
        ("Quel risque présente SSTF ?", ["L'interblocage", "La famine de certaines requêtes", "La fragmentation", "Les défauts de page"], 1, "Les requêtes éloignées peuvent attendre longtemps si des requêtes proches arrivent sans cesse.")],
 ),
 dict(
  titre="Linux et le shell (travaux pratiques)",
  resume="Apprendre à utiliser le terminal : arborescence, commandes, redirections, droits et processus.",
  objectifs=["Se repérer dans l'arborescence Linux", "Utiliser les commandes de base", "Rediriger et enchaîner avec | > >>", "Gérer droits et processus", "Écrire un petit script shell"],
  cours="""<h4>1. Pourquoi Linux ?</h4>
<p>Libre, stable, très utilisé sur les serveurs et dans Android. Il existe en <b>distributions</b> (Ubuntu, Debian, Fedora…). Pour s'entraîner sans rien casser : une machine virtuelle (VirtualBox), WSL sous Windows, ou le <b>terminal d'entraînement</b> de ce site.</p>
<h4>2. L'arborescence</h4>
<table><tr><th>Dossier</th><th>Rôle</th></tr><tr><td><code>/</code></td><td>Racine de tout</td></tr><tr><td><code>/home</code></td><td>Dossiers personnels des utilisateurs</td></tr><tr><td><code>/etc</code></td><td>Fichiers de configuration</td></tr><tr><td><code>/bin</code>, <code>/usr</code></td><td>Programmes</td></tr><tr><td><code>/var</code></td><td>Données variables (journaux)</td></tr><tr><td><code>/tmp</code></td><td>Fichiers temporaires</td></tr><tr><td><code>/dev</code></td><td>Périphériques (« tout est fichier »)</td></tr></table>
<h4>3. Commandes de base</h4>
<table><tr><th>Commande</th><th>Rôle</th></tr><tr><td><code>pwd</code></td><td>Afficher le répertoire courant</td></tr><tr><td><code>ls</code>, <code>ls -l</code></td><td>Lister les fichiers (détaillé avec -l)</td></tr><tr><td><code>cd dossier</code></td><td>Changer de répertoire (<code>cd ..</code> remonte)</td></tr><tr><td><code>mkdir</code>, <code>touch</code></td><td>Créer un dossier, un fichier vide</td></tr><tr><td><code>cp</code>, <code>mv</code>, <code>rm</code></td><td>Copier, déplacer/renommer, supprimer</td></tr><tr><td><code>cat</code>, <code>less</code>, <code>head</code>, <code>tail</code></td><td>Afficher un fichier</td></tr><tr><td><code>echo</code></td><td>Afficher un texte</td></tr><tr><td><code>man commande</code></td><td>Lire l'aide</td></tr></table>
<h4>4. Redirections et tubes</h4>
<ul><li><code>commande &gt; fichier</code> écrit la sortie dans un fichier (écrase).</li><li><code>commande &gt;&gt; fichier</code> ajoute à la fin.</li><li><code>commande &lt; fichier</code> lit l'entrée depuis un fichier.</li><li><code>cmd1 | cmd2</code> (<b>tube</b>) envoie la sortie de cmd1 à l'entrée de cmd2. Exemple : <code>ls | wc -l</code> compte les fichiers.</li></ul>
<h4>5. Droits et utilisateurs</h4>
<p><code>whoami</code> (qui suis-je), <code>chmod 755 fichier</code> (changer les droits), <code>chown</code> (changer le propriétaire), <code>sudo</code> (exécuter en administrateur).</p>
<h4>6. Les processus</h4>
<p><code>ps</code> liste les processus, <code>top</code> affiche l'activité en direct, <code>kill PID</code> arrête un processus, <code>commande &amp;</code> la lance en arrière-plan, <code>jobs</code>, <code>fg</code> et <code>bg</code> gèrent les tâches.</p>
<h4>7. Un premier script shell</h4>
<pre>#!/bin/bash
for f in *.txt; do
  echo "Fichier : $f"
done</pre>
<p>Pour l'exécuter : <code>chmod +x script.sh</code> puis <code>./script.sh</code>.</p>""",
  retenir=["pwd, ls, cd, mkdir, touch, cat, cp, mv, rm : les 9 commandes de base.", "> écrase, >> ajoute, | enchaîne deux commandes.", "chmod 755 = rwxr-xr-x.", "Sous Linux, les périphériques sont des fichiers dans /dev."],
  erreurs=["Utiliser > au lieu de >> et écraser un fichier.", "Oublier ./ pour lancer un script du répertoire courant.", "Lancer rm sans réfléchir : il n'y a pas de corbeille."],
  exo=("Créez un dossier tp, placez-vous dedans, créez un fichier a.txt contenant Bonjour, puis affichez son contenu.",
       "<pre>mkdir tp\ncd tp\necho \"Bonjour\" &gt; a.txt\ncat a.txt</pre><p>Essayez ces commandes dans le <b>terminal d'entraînement</b> (section Outils).</p>"),
  quiz=[("Quelle commande affiche le répertoire courant ?", ["ls", "pwd", "cd", "whoami"], 1, "pwd signifie « print working directory »."),
        ("Le symbole | (tube) sert à :", ["Écrire dans un fichier", "Envoyer la sortie d'une commande vers l'entrée d'une autre", "Supprimer un fichier", "Lancer un programme en arrière-plan"], 1, "Exemple : ls | wc -l."),
        ("chmod 755 donne les droits :", ["rwxr-xr-x", "rw-r--r--", "rwxrwxrwx", "r-xr-xr-x"], 0, "7 = rwx, 5 = r-x, 5 = r-x.")],
 ),
]

FORMULES = [
    ("Temps de rotation", "fin − arrivée"), ("Temps d'attente", "rotation − durée d'exécution"),
    ("Temps de réponse", "premier passage sur le CPU − arrivée"), ("Page / déplacement", "page = adresse DIV taille ; déplacement = adresse MOD taille"),
    ("Adresse physique", "n° de cadre × taille de page + déplacement"), ("Temps d'accès disque", "seek + latence de rotation + transfert"),
    ("Disponible (banquier)", "total − somme des ressources détenues"), ("Besoin restant", "maximum − détenu"),
    ("Droits Unix", "r = 4, w = 2, x = 1 (rwx = 7, r-x = 5, rw- = 6)"), ("Déplacement disque", "somme des |piste suivante − piste actuelle|"),
]

GLOSSAIRE = [
    ("Appel système", "Demande de service faite par une application au noyau."), ("Attente circulaire", "Cycle de processus où chacun attend une ressource détenue par le suivant."),
    ("Banquier (algorithme)", "Méthode d'évitement d'interblocage qui n'accorde une ressource que si l'état reste sûr."), ("Bloqué", "État d'un processus qui attend un événement (E/S…)."),
    ("Cadre", "Bloc de mémoire physique qui reçoit une page."), ("Commutation de contexte", "Sauvegarde d'un processus et chargement d'un autre sur le processeur."),
    ("Condition de concurrence", "Situation où le résultat dépend de l'ordre d'exécution de processus."), ("Défaut de page", "Accès à une page absente de la RAM, qui doit être chargée depuis le disque."),
    ("DMA", "Transfert de données entre périphérique et mémoire sans mobiliser le processeur."), ("Élu", "État du processus qui utilise le processeur."),
    ("Famine", "Attente indéfinie d'un processus qui n'est jamais choisi."), ("FAT", "Table d'allocation de fichiers : chaînage des blocs dans une table."),
    ("Fragmentation externe", "Trous inutilisables entre les partitions."), ("Fragmentation interne", "Place perdue à l'intérieur d'une partition ou d'une page."),
    ("Inode", "Structure Unix contenant les attributs d'un fichier et les adresses de ses blocs."), ("Interblocage (deadlock)", "Blocage définitif de processus qui s'attendent mutuellement."),
    ("Interruption", "Signal qui avertit le processeur d'un événement."), ("Mémoire virtuelle", "Technique qui n'a en RAM que les pages utiles, le reste étant sur le disque."),
    ("MMU", "Matériel qui traduit les adresses logiques en adresses physiques."), ("Mode noyau", "Mode privilégié du processeur, réservé au noyau."),
    ("Mutex", "Verrou garantissant l'exclusion mutuelle."), ("Noyau (kernel)", "Cœur du SE, qui gère processus, mémoire, fichiers et E/S."),
    ("Page", "Bloc de taille fixe de la mémoire logique."), ("PCB", "Bloc de contrôle d'un processus : toutes les informations utiles au SE."),
    ("Pilote (driver)", "Logiciel du SE qui commande un périphérique."), ("Préemption", "Retrait du processeur à un processus en cours."),
    ("Processus", "Programme en cours d'exécution."), ("Quantum", "Durée maximale d'une tranche de temps en Round Robin."),
    ("Section critique", "Code qui accède à une ressource partagée."), ("Sémaphore", "Entier avec opérations atomiques P et V, pour synchroniser."),
    ("Shell", "Interpréteur de commandes."), ("Spooling", "Mise en file d'attente de travaux, comme l'impression."),
    ("Thrashing", "Surcharge de défauts de page : le système charge au lieu de calculer."), ("Thread", "Fil d'exécution à l'intérieur d'un processus."),
    ("TLB", "Cache matériel de la table des pages."),
]

PLAN = [
    ("Chaque chapitre (méthode en 5 étapes)", "1) Lisez le cours une fois sans vous arrêter. 2) Refaites les schémas à la main. 3) Faites l'exercice sans regarder la correction. 4) Passez le quiz. 5) Vérifiez avec l'outil de simulation."),
    ("Semaines 1 à 3", "Chapitres 1 et 2 (bases). Refaites le diagramme des états d'un processus."),
    ("Semaines 4 à 6", "Chapitre 3 (ordonnancement) : faites au moins 5 exercices de Gantt. Chapitre 8 : pratiquez le terminal chaque semaine."),
    ("Semaines 7 à 9", "Chapitre 4 (synchronisation, interblocage). Refaites l'algorithme du banquier 3 fois."),
    ("Semaines 10 à 12", "Chapitres 5, 6 et 7 : calculs d'adresses, pages, tête de disque."),
    ("Dernière semaine avant l'examen", "Relisez les « À retenir » et la fiche des formules, refaites les exercices ratés, passez tous les quiz, puis vérifiez le glossaire."),
]
LIVRES = ["A. Tanenbaum, « Systèmes d'exploitation » (référence en français)", "Silberschatz, Galvin, Gagne, « Operating System Concepts » (en anglais, très clair)",
          "Le polycopié et les TD de votre enseignant : ils priment toujours sur ce site"]

# ======================================================================
# STYLE
# ======================================================================
CSS = r"""
:root{--encre:#14213D;--papier:#FBFBF8;--bleu:#2B59C3;--jaune:#FFE066;--vert:#1F9D63;--rouge:#D1495B;--gris:#5A6478;--ligne:#DDE1EA}
*{box-sizing:border-box;margin:0}
[hidden]{display:none!important}
html{scroll-behavior:smooth;scroll-padding-top:20px}
body{background:var(--papier);color:var(--encre);font:17px/1.75 'Lexend',system-ui,sans-serif;display:grid;grid-template-columns:280px 1fr}
h1,h2,h3,h4{line-height:1.25}
code,pre,.mono{font-family:'JetBrains Mono',ui-monospace,monospace}
code{background:#EEF1F8;padding:1px 6px;border-radius:5px;font-size:.88em}
pre{background:var(--encre);color:#E8EEFC;padding:16px 18px;border-radius:10px;overflow-x:auto;font-size:.88rem;line-height:1.6;margin:12px 0}
a{color:var(--bleu)}
:focus-visible{outline:3px solid var(--bleu);outline-offset:2px}

aside{position:sticky;top:0;height:100vh;overflow-y:auto;background:var(--encre);color:#E8EEFC;padding:22px 18px}
.marque{font-weight:700;font-size:1.25rem;line-height:1.2;text-decoration:none;color:#fff;display:block;margin-bottom:4px}
.marque span{background:var(--jaune);color:var(--encre);padding:0 6px;border-radius:4px}
.ecole{font-size:.8rem;opacity:.7;margin-bottom:16px}
.prog{font-size:.8rem;margin-bottom:18px}.prog .barre{height:8px;background:#2A3A63;border-radius:6px;margin-top:6px;overflow:hidden}.prog .barre div{height:100%;width:0;background:var(--jaune);transition:width .4s}
aside h5{font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;color:#8FA2D1;margin:16px 0 6px}
aside a.nav{display:block;color:#E8EEFC;text-decoration:none;font-size:.92rem;padding:6px 10px;border-radius:8px;line-height:1.35}
aside a.nav:hover{background:#243662}
aside a.nav.ok:before{content:"✓ ";color:var(--jaune);font-weight:700}
#burger{display:none;position:fixed;top:10px;left:10px;z-index:50;background:var(--encre);color:#fff;border:0;border-radius:10px;padding:10px 14px;font:inherit;font-size:.9rem;cursor:pointer}

main{padding:0 clamp(18px,4vw,56px) 80px;max-width:980px}
section{padding:54px 0 10px;border-bottom:2px dashed var(--ligne)}
.accueil{padding-top:48px}
.accueil h1{font-size:clamp(2rem,5vw,3.2rem);margin-bottom:12px}
.accueil h1 mark{background:var(--jaune);padding:0 8px;border-radius:6px}
.accueil p.lead{font-size:1.1rem;color:var(--gris);max-width:60ch;margin-bottom:22px}
.note{background:#FFF8D6;border-left:5px solid #E0B800;padding:14px 18px;border-radius:8px;margin:18px 0;font-size:.95rem}
.demarrer{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin:22px 0 30px}
.demarrer a{display:block;text-decoration:none;color:var(--encre);background:#fff;border:2px solid var(--ligne);border-radius:14px;padding:16px;font-weight:600}
.demarrer a small{display:block;font-weight:400;color:var(--gris);margin-top:4px}
.demarrer a:hover{border-color:var(--bleu);transform:translateY(-2px)}
.etapes{counter-reset:e;list-style:none;padding:0}
.etapes li{counter-increment:e;position:relative;padding:8px 0 8px 46px}
.etapes li:before{content:counter(e);position:absolute;left:0;top:6px;width:32px;height:32px;border-radius:50%;background:var(--bleu);color:#fff;display:grid;place-items:center;font-weight:700}

.chap-tete .num{display:inline-block;background:var(--bleu);color:#fff;font-size:.82rem;font-weight:700;padding:3px 14px;border-radius:999px}
.chap-tete h2{font-size:clamp(1.7rem,4vw,2.4rem);margin:10px 0 6px}
.chap-tete .res{color:var(--gris);margin-bottom:14px}
.obj{background:linear-gradient(transparent 0,transparent 0),#FFF8D6;border-radius:10px;padding:14px 20px;margin-bottom:20px}
.obj b{display:block;margin-bottom:4px}.obj ul{margin:0 0 0 20px}
.cours h4{font-size:1.2rem;margin:26px 0 8px;color:var(--bleu)}
.cours p,.cours ul,.cours ol{margin:8px 0}.cours ul,.cours ol{padding-left:24px}.cours li{margin:4px 0}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:.92rem;display:block;overflow-x:auto}
th,td{border:1px solid var(--ligne);padding:8px 12px;text-align:left;vertical-align:top}
th{background:#EEF1F8}
.image{background:#E8F1FF;border-left:5px solid var(--bleu);padding:12px 18px;border-radius:8px;margin:14px 0}
.formule{background:#F3EEFF;border:2px solid #8B6CD9;padding:12px 18px;border-radius:10px;margin:14px 0;font-weight:500}
.schema{width:100%;max-width:700px;display:block;margin:14px auto;background:#fff;border:1px solid var(--ligne);border-radius:12px;padding:8px}
.couches{max-width:520px;margin:14px auto 4px;display:grid;gap:4px}
.couches div{padding:10px 16px;border-radius:8px;text-align:center;font-weight:600}.couches small{display:block;font-weight:400;font-size:.8rem}
.couches .u{background:#E8F1FF;border:2px solid var(--bleu)}.couches .k{background:#D6F5E5;border:2px solid var(--vert)}.couches .h{background:#EEE;border:2px solid #999}
.legende{text-align:center;font-size:.88rem;color:var(--gris)}
.bloc{border-radius:12px;padding:16px 22px;margin:20px 0}
.bloc h4{margin:0 0 6px}.bloc ul{margin:0 0 0 20px}
.retenir{background:#E2F7EC;border:2px solid var(--vert)}.retenir h4{color:#136E44}
.erreurs{background:#FDE8EB;border:2px solid var(--rouge)}.erreurs h4{color:#A8283A}
details{background:#fff;border:2px solid var(--ligne);border-radius:12px;padding:14px 20px;margin:20px 0}
summary{cursor:pointer;font-weight:700}
details .corr{margin-top:12px;padding-top:12px;border-top:1px dashed var(--ligne)}
.exo h4{margin:20px 0 6px}
.q{background:#fff;border:2px solid var(--ligne);border-radius:12px;padding:16px 20px;margin:12px 0}
.q p{font-weight:600;margin-bottom:8px}
.q button{display:block;width:100%;text-align:left;font:inherit;font-size:.95rem;background:#F4F6FB;border:2px solid transparent;border-radius:8px;padding:9px 14px;margin:6px 0;cursor:pointer;color:var(--encre)}
.q button:hover{border-color:var(--bleu)}
.q.fait button{cursor:default}.q button.bon{background:#D6F5E5;border-color:var(--vert)}.q button.mauvais{background:#FDE8EB;border-color:var(--rouge)}
.expl{font-size:.92rem;color:var(--gris);margin-top:6px}
.score{font-weight:700;color:var(--vert);min-height:1.5em}
.fini{display:flex;gap:10px;align-items:center;margin:18px 0 30px;font-weight:600;cursor:pointer}
.fini input{width:20px;height:20px;accent-color:var(--vert)}

h2.titre{font-size:clamp(1.7rem,4vw,2.3rem);margin-bottom:6px}
.carte{background:#fff;border:2px solid var(--ligne);border-radius:16px;padding:22px;margin:18px 0}
.carte h3{font-size:1.3rem;margin-bottom:6px}
.champs{display:flex;gap:12px;flex-wrap:wrap;align-items:end;margin:12px 0}
label{font-size:.85rem;font-weight:600;display:grid;gap:3px}
input[type=text],input[type=number],select{font:inherit;font-size:.92rem;padding:7px 10px;border:2px solid var(--ligne);border-radius:8px;background:#fff;color:var(--encre)}
input[type=number]{width:84px}
#refs{width:min(440px,78vw)}input[type=text]{max-width:100%}
.btn{font:inherit;font-weight:700;font-size:.92rem;background:var(--bleu);color:#fff;border:0;border-radius:10px;padding:9px 18px;cursor:pointer}
.btn:hover{background:#1F4399}.btn.clair{background:#E8EEFC;color:var(--bleu)}
.gantt{display:flex;margin:16px 0 28px;min-height:44px}
.gantt div{position:relative;display:grid;place-items:center;color:#fff;font-weight:700;font-size:.85rem;border:1px solid #fff;min-width:22px}
.gantt div span{position:absolute;left:-5px;bottom:-22px;font-size:.72rem;color:var(--gris);font-weight:500}
.gantt div.fin-t span.f{left:auto;right:-5px}
.gantt .idle{background:#CCD2E0!important;color:#555}
.pg{overflow-x:auto;margin:12px 0}.pg table{display:table;width:auto;font-size:.85rem}.pg td,.pg th{text-align:center;padding:6px 10px}
.pg td.f{background:#FDE8EB;font-weight:700}.pg td.h{background:#E2F7EC}.pg .ent{font-weight:700;background:#EEF1F8}
.resume{font-weight:600;margin:8px 0}
.terminal{background:#0E1730;color:#D6E2FF;border-radius:14px;padding:14px 16px;font-family:'JetBrains Mono',monospace;font-size:.86rem}
#term-out{white-space:pre-wrap;height:280px;overflow-y:auto;margin:0}
.ligne-cmd{display:flex;gap:8px;align-items:center;border-top:1px solid #243662;padding-top:10px;margin-top:8px}
.ligne-cmd span{color:#7DE0A6;white-space:nowrap}
.ligne-cmd input{flex:1;background:none;border:0;color:#fff;font:inherit;outline:0;min-width:0}
.formules{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:12px;margin:16px 0}
.formules div{background:#fff;border:2px solid var(--ligne);border-radius:12px;padding:12px 16px}.formules b{display:block;color:var(--bleu)}
.terme{padding:10px 0;border-bottom:1px solid var(--ligne)}.terme b{color:var(--bleu)}
footer{padding:36px 0 0;color:var(--gris);font-size:.9rem}

@media (max-width:900px){
  body{display:block}#burger{display:block}
  aside{position:fixed;z-index:40;width:280px;transform:translateX(-100%);transition:transform .25s}body.menu aside{transform:none}
  main{padding-top:56px}
}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}aside,.demarrer a{transition:none}}
"""

# ======================================================================
# JAVASCRIPT : quiz, progression, outils
# ======================================================================
JS = r"""
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const NCH = __NCH__, KEY = "se-ihec-progression";
let done = {}; try { done = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) {}
function majProg() {
  const n = Object.values(done).filter(Boolean).length;
  $("#prog-txt").textContent = `${n} / ${NCH} chapitres terminés`; $("#prog-bar").style.width = (n / NCH * 100) + "%";
  $$("[data-nav]").forEach(a => a.classList.toggle("ok", !!done[a.dataset.nav]));
  $$("input[data-done]").forEach(c => { c.checked = !!done[c.dataset.done]; });
}
$$("input[data-done]").forEach(c => c.onchange = () => { done[c.dataset.done] = c.checked; try { localStorage.setItem(KEY, JSON.stringify(done)); } catch (e) {} majProg(); });
majProg();
$("#burger").onclick = () => document.body.classList.toggle("menu");
$$("aside a.nav, aside a.marque").forEach(a => a.addEventListener("click", () => document.body.classList.remove("menu")));

/* ---- Quiz ---- */
$$(".q").forEach(q => {
  const ok = +q.dataset.ok, btns = [...q.querySelectorAll("button")];
  btns.forEach((b, i) => b.onclick = () => {
    if (q.classList.contains("fait")) return;
    q.classList.add("fait"); if (i === ok) q.dataset.res = "1";
    b.classList.add(i === ok ? "bon" : "mauvais"); btns[ok].classList.add("bon"); q.querySelector(".expl").hidden = false;
    const sec = q.closest("section"), qs = sec.querySelectorAll(".q");
    if (sec.querySelectorAll(".q.fait").length === qs.length) {
      const bons = sec.querySelectorAll(".q[data-res='1']").length;
      sec.querySelector(".score").textContent = `Score : ${bons} / ${qs.length}` + (bons === qs.length ? " — parfait !" : " — relisez les « À retenir » et refaites le quiz.");
    }
  });
});

/* ---- Ordonnanceur CPU ---- */
const COULEURS = ["#2B59C3", "#1F9D63", "#D1495B", "#C98A00", "#7B4FD1", "#0F8B8D", "#B5470F", "#5A6478"];
function ordonnancer(ps, algo, q) {
  const n = ps.length, rem = ps.map(p => p.d), fin = Array(n).fill(0), seen = Array(n).fill(false), tl = [], queue = [];
  let t = 0, cur = -1, qt = 0, left = n;
  const arrive = () => ps.forEach((p, i) => { if (!seen[i] && p.a <= t) { seen[i] = true; queue.push(i); } });
  const key = { fcfs: i => [ps[i].a, i], sjf: i => [ps[i].d, ps[i].a], prio: i => [ps[i].p, ps[i].a], srt: i => [rem[i], ps[i].a] }[algo];
  const mieux = (x, y) => { const a = key(x), b = key(y); return a[0] < b[0] || (a[0] === b[0] && a[1] < b[1]); };
  arrive();
  while (left > 0 && t < 3000) {
    if (algo === "rr") { if (cur < 0 && queue.length) { cur = queue.shift(); qt = 0; } }
    else if (cur < 0 || algo === "srt") {
      let best = -1;
      for (let i = 0; i < n; i++) if (seen[i] && rem[i] > 0 && (best < 0 || mieux(i, best))) best = i;
      if (cur < 0 || (best >= 0 && mieux(best, cur))) cur = best;
    }
    if (cur < 0) { tl.push(-1); t++; arrive(); continue; }
    tl.push(cur); rem[cur]--; t++; qt++; arrive();
    if (rem[cur] === 0) { fin[cur] = t; left--; cur = -1; }
    else if (algo === "rr" && qt >= q) { queue.push(cur); cur = -1; }
  }
  return { tl, fin };
}
let procs = [{ a: 0, d: 5, p: 2 }, { a: 1, d: 3, p: 1 }, { a: 2, d: 1, p: 3 }];
function dessinerProcs() {
  $("#procs").innerHTML = procs.map((p, i) => `<tr><td><b>P${i + 1}</b></td><td><input type="number" min="0" value="${p.a}" data-i="${i}" data-k="a" aria-label="Arrivée P${i + 1}"></td>
    <td><input type="number" min="1" value="${p.d}" data-i="${i}" data-k="d" aria-label="Durée P${i + 1}"></td><td><input type="number" min="1" value="${p.p}" data-i="${i}" data-k="p" aria-label="Priorité P${i + 1}"></td>
    <td><button class="btn clair" data-del="${i}" aria-label="Supprimer P${i + 1}">×</button></td></tr>`).join("");
  $$("#procs input").forEach(inp => inp.onchange = () => { procs[inp.dataset.i][inp.dataset.k] = Math.max(inp.dataset.k === "d" ? 1 : 0, +inp.value || 0); });
  $$("#procs [data-del]").forEach(b => b.onclick = () => { if (procs.length > 1) { procs.splice(+b.dataset.del, 1); dessinerProcs(); } });
}
function simuler() {
  const algo = $("#algo").value, q = Math.max(1, +$("#quantum").value || 2), { tl, fin } = ordonnancer(procs, algo, q);
  const segs = []; tl.forEach((x, t) => { const s = segs[segs.length - 1]; if (s && s.i === x) s.e = t + 1; else segs.push({ i: x, s: t, e: t + 1 }); });
  const total = tl.length;
  $("#gantt").innerHTML = segs.map(s => `<div class="${s.i < 0 ? "idle" : ""}" style="width:${(s.e - s.s) / total * 100}%;background:${COULEURS[s.i % 8]}">${s.i < 0 ? "—" : "P" + (s.i + 1)}<span>${s.s}</span></div>`).join("") +
    `<div style="width:0;border:0;min-width:0"><span>${total}</span></div>`;
  let sr = 0, sa = 0;
  const lignes = procs.map((p, i) => { const r = fin[i] - p.a, w = r - p.d; sr += r; sa += w; return `<tr><td><b>P${i + 1}</b></td><td>${p.a}</td><td>${p.d}</td><td>${fin[i]}</td><td>${r}</td><td>${w}</td></tr>`; }).join("");
  const f = x => (Math.round(x * 100) / 100).toString().replace(".", ",");
  $("#ordo-res").innerHTML = `<table><tr><th>Processus</th><th>Arrivée</th><th>Durée</th><th>Fin</th><th>Rotation (fin − arrivée)</th><th>Attente (rotation − durée)</th></tr>${lignes}</table>
    <p class="resume">Rotation moyenne : ${f(sr / procs.length)} · Attente moyenne : ${f(sa / procs.length)}</p>`;
}
$("#ajout").onclick = () => { if (procs.length < 8) { procs.push({ a: 0, d: 2, p: 1 }); dessinerProcs(); } };
$("#go-ordo").onclick = simuler;
$("#algo").onchange = () => { $("#bq").hidden = $("#algo").value !== "rr"; $("#note-prio").hidden = $("#algo").value !== "prio"; };
dessinerProcs(); simuler();

/* ---- Pagination ---- */
function paginer(refs, F, algo) {
  const fr = Array(F).fill(null), last = {}, cols = []; let faults = 0, ptr = 0;
  refs.forEach((r, k) => {
    const idx = fr.indexOf(r); let fault = idx < 0;
    if (!fault) last[r] = k;
    else {
      faults++; let v = fr.indexOf(null);
      if (v < 0) {
        if (algo === "fifo") { v = ptr; ptr = (ptr + 1) % F; }
        else if (algo === "lru") { v = 0; fr.forEach((x, i) => { if (last[x] < last[fr[v]]) v = i; }); }
        else { let far = -1; fr.forEach((x, i) => { let nx = refs.indexOf(x, k + 1); if (nx < 0) nx = 1e9; if (nx > far) { far = nx; v = i; } }); }
      } else if (algo === "fifo") ptr = (v + 1) % F;
      fr[v] = r; last[r] = k;
    }
    cols.push({ r, fr: [...fr], fault });
  });
  return { cols, faults };
}
function lancerPages() {
  const refs = $("#refs").value.split(/[\s,;]+/).filter(Boolean).map(Number).filter(x => !isNaN(x)), F = Math.min(8, Math.max(1, +$("#frames").value || 3)), algo = $("#palgo").value;
  if (!refs.length) { $("#pages-res").textContent = "Entrez une chaîne de références, par exemple 7,0,1,2,0,3."; return; }
  const { cols, faults } = paginer(refs, F, algo), noms = { fifo: "FIFO", lru: "LRU", opt: "OPT" };
  let h = `<div class="pg"><table><tr><th>Référence</th>${cols.map(c => `<th>${c.r}</th>`).join("")}</tr>`;
  for (let i = 0; i < F; i++) h += `<tr><td class="ent">Cadre ${i + 1}</td>${cols.map(c => `<td class="${c.fault ? "f" : "h"}">${c.fr[i] === null ? "" : c.fr[i]}</td>`).join("")}</tr>`;
  h += `<tr><td class="ent">Défaut ?</td>${cols.map(c => `<td>${c.fault ? "✗" : "✓"}</td>`).join("")}</tr></table></div>`;
  const tous = ["fifo", "lru", "opt"].map(a => `${noms[a]} : ${paginer(refs, F, a).faults}`).join(" · ");
  $("#pages-res").innerHTML = h + `<p class="resume">${noms[algo]} : ${faults} défauts sur ${refs.length} références (taux de défauts ${Math.round(faults / refs.length * 100)} %)</p><p>Comparaison avec ${F} cadres → ${tous}</p>
    <p class="expl">Rouge = défaut de page (✗), vert = la page était déjà en mémoire (✓).</p>`;
}
$("#go-pages").onclick = lancerPages; lancerPages();

/* ---- Terminal d'entraînement ---- */
const FS = { t: "d", c: { home: { t: "d", c: { etudiant: { t: "d", c: { "notes.txt": { t: "f", x: "Bienvenue en cours de systèmes d'exploitation !\n" } } } } }, tmp: { t: "d", c: {} } } };
let cwd = ["home", "etudiant"]; const hist = []; let hi = 0;
const get = parts => { let n = FS; for (const s of parts) { if (!n || n.t !== "d" || !(s in n.c)) return null; n = n.c[s]; } return n; };
const res = p => { const a = p.startsWith("/") ? [] : [...cwd]; for (const s of p.split("/")) { if (!s || s === ".") continue; if (s === "..") a.pop(); else a.push(s); } return a; };
const pwd = () => "/" + cwd.join("/"), sortie = $("#term-out");
const out = s => { sortie.textContent += s + "\n"; sortie.scrollTop = sortie.scrollHeight; };
function cmd(ligne) {
  $("#prompt").textContent = `etudiant@ihec:${pwd()}$`; out(`etudiant@ihec:${pwd()}$ ${ligne}`);
  let redir = null; const m = ligne.match(/^(echo\b.*?)\s*(>>?)\s*(\S+)\s*$/);
  if (m) { ligne = m[1]; redir = [m[2], m[3]]; }
  const a = (ligne.match(/"[^"]*"|\S+/g) || []).map(x => x.replace(/^"|"$/g, "")), c = a[0], opts = a.filter(x => x.startsWith("-") && c !== "echo"), args = a.slice(1).filter(x => c === "echo" || !x.startsWith("-"));
  const parentDe = p => { const r = res(p); return [get(r.slice(0, -1)), r[r.length - 1]]; };
  switch (c) {
    case undefined: break;
    case "help": out("Commandes : pwd, ls [-l], cd, mkdir, touch, cat, echo [> >>], rm [-r], whoami, ps, date, clear"); break;
    case "pwd": out(pwd()); break;
    case "ls": { const n = get(args[0] ? res(args[0]) : cwd); if (!n) out("ls: dossier introuvable"); else if (n.t === "f") out(args[0]);
      else { const ks = Object.keys(n.c).sort(); out(ks.length ? (opts.includes("-l") ? ks.map(k => `${n.c[k].t === "d" ? "drwxr-xr-x" : "-rw-r--r--"} etudiant ${k}`).join("\n") : ks.map(k => k + (n.c[k].t === "d" ? "/" : "")).join("  ")) : "(vide)"); } break; }
    case "cd": { const t = args[0] ? res(args[0]) : ["home", "etudiant"], n = get(t); if (n && n.t === "d") cwd = t; else out(`cd: ${args[0]}: dossier introuvable`); break; }
    case "mkdir": args.forEach(x => { const [p, nom] = parentDe(x); if (!p || p.t !== "d") out(`mkdir: ${x}: chemin invalide`); else if (nom in p.c) out(`mkdir: ${x}: existe déjà`); else p.c[nom] = { t: "d", c: {} }; }); break;
    case "touch": args.forEach(x => { const [p, nom] = parentDe(x); if (!p || p.t !== "d") out(`touch: ${x}: chemin invalide`); else if (!(nom in p.c)) p.c[nom] = { t: "f", x: "" }; }); break;
    case "cat": args.forEach(x => { const n = get(res(x)); out(!n ? `cat: ${x}: fichier introuvable` : n.t === "d" ? `cat: ${x}: c'est un dossier` : n.x.replace(/\n$/, "")); }); break;
    case "echo": { const txt = a.slice(1).join(" ");
      if (redir) { const [p, nom] = parentDe(redir[1]); if (!p || p.t !== "d") out("echo: chemin invalide"); else { const f = p.c[nom] || (p.c[nom] = { t: "f", x: "" }); f.x = redir[0] === ">" ? txt + "\n" : f.x + txt + "\n"; } } else out(txt); break; }
    case "rm": args.forEach(x => { const [p, nom] = parentDe(x); if (!p || !(nom in p.c)) out(`rm: ${x}: introuvable`); else if (p.c[nom].t === "d" && !opts.includes("-r")) out(`rm: ${x}: c'est un dossier (utilisez rm -r)`); else delete p.c[nom]; }); break;
    case "whoami": out("etudiant"); break;
    case "date": out(new Date().toLocaleString("fr-FR")); break;
    case "ps": out("  PID CMD\n    1 systemd\n  212 bash\n  245 ps"); break;
    case "clear": sortie.textContent = ""; break;
    default: out(`${c}: commande introuvable (tapez help)`);
  }
  $("#prompt").textContent = `etudiant@ihec:${pwd()}$`;
}
$("#term-in").addEventListener("keydown", e => {
  if (e.key === "Enter") { const v = e.target.value.trim(); if (v) { hist.push(v); hi = hist.length; } cmd(v); e.target.value = ""; }
  else if (e.key === "ArrowUp" && hist.length) { hi = Math.max(0, hi - 1); e.target.value = hist[hi]; e.preventDefault(); }
  else if (e.key === "ArrowDown") { hi = Math.min(hist.length, hi + 1); e.target.value = hist[hi] || ""; }
});
out("Terminal d'entraînement. Tapez help pour voir les commandes. Essayez : ls, cat notes.txt, mkdir tp");

/* ---- Glossaire ---- */
$("#recherche").addEventListener("input", e => { const v = e.target.value.toLowerCase(); $$(".terme").forEach(t => { t.hidden = !t.textContent.toLowerCase().includes(v); }); });
"""

# ======================================================================
# ASSEMBLAGE DE LA PAGE
# ======================================================================
def chapitre_html(i, c):
    objectifs = "".join(f"<li>{escape(o)}</li>" for o in c["objectifs"])
    retenir = "".join(f"<li>{escape(r)}</li>" for r in c["retenir"])
    erreurs = "".join(f"<li>{escape(e)}</li>" for e in c["erreurs"])
    quiz = ""
    for q, opts, bonne, expl in c["quiz"]:
        boutons = "".join(f"<button type='button'>{escape(o)}</button>" for o in opts)
        quiz += f"<div class='q' data-ok='{bonne}'><p>{escape(q)}</p>{boutons}<div class='expl' hidden>{escape(expl)}</div></div>"
    enonce, correction = c["exo"]
    n = i + 1
    return f"""<section id="ch{n}">
<div class="chap-tete"><span class="num">Chapitre {n}</span><h2>{escape(c['titre'])}</h2><p class="res">{escape(c['resume'])}</p></div>
<div class="obj"><b>À la fin de ce chapitre, vous saurez :</b><ul>{objectifs}</ul></div>
<div class="cours">{c['cours']}</div>
<div class="bloc retenir"><h4>À retenir</h4><ul>{retenir}</ul></div>
<div class="bloc erreurs"><h4>Erreurs fréquentes à éviter</h4><ul>{erreurs}</ul></div>
<div class="exo"><h4>Exercice corrigé</h4><p>{enonce}</p><details><summary>Voir la correction (essayez d'abord seul !)</summary><div class="corr">{correction}</div></details></div>
<h4>Quiz d'auto-évaluation</h4>{quiz}<p class="score"></p>
<label class="fini"><input type="checkbox" data-done="{n}"> J'ai terminé ce chapitre</label>
</section>"""


def page():
    nav = "".join(f"<a class='nav' data-nav='{i + 1}' href='#ch{i + 1}'>{i + 1}. {escape(c['titre'])}</a>" for i, c in enumerate(CHAPITRES))
    chapitres = "".join(chapitre_html(i, c) for i, c in enumerate(CHAPITRES))
    formules = "".join(f"<div><b>{escape(a)}</b>{escape(b)}</div>" for a, b in FORMULES)
    glossaire = "".join(f"<div class='terme'><b>{escape(t)}</b> : {escape(d)}</div>" for t, d in sorted(GLOSSAIRE))
    plan = "".join(f"<div class='terme'><b>{escape(t)}</b><br>{escape(d)}</div>" for t, d in PLAN)
    livres = "".join(f"<li>{escape(l)}</li>" for l in LIVRES)
    js = JS.replace("__NCH__", str(len(CHAPITRES)))
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Systèmes d'exploitation — 1ère année, semestre 1 — IHEC Carthage</title>
<meta name="description" content="Cours complet de systèmes d'exploitation en français : processus, ordonnancement, mémoire, fichiers, Linux. Exercices corrigés, quiz et simulateurs.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Lexend:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<button id="burger" type="button">☰ Menu</button>
<aside>
  <a class="marque" href="#accueil">Systèmes d'<span>exploitation</span></a>
  <div class="ecole">1ère année · Semestre 1 · IHEC Carthage</div>
  <div class="prog"><span id="prog-txt"></span><div class="barre"><div id="prog-bar"></div></div></div>
  <h5>Chapitres</h5>{nav}
  <h5>Outils</h5>
  <a class="nav" href="#ordo">Simulateur d'ordonnancement</a><a class="nav" href="#pagination">Simulateur de pagination</a><a class="nav" href="#terminal">Terminal Linux d'entraînement</a>
  <h5>Révision</h5>
  <a class="nav" href="#formules">Fiche des formules</a><a class="nav" href="#glossaire">Glossaire</a><a class="nav" href="#revision">Plan de révision</a>
</aside>
<main>
<section id="accueil" class="accueil">
  <h1>Comprendre les <mark>systèmes d'exploitation</mark>, pas à pas</h1>
  <p class="lead">Un cours complet en français pour la 1ère année (semestre 1) : explications simples, schémas, exercices corrigés, quiz et simulateurs pour pratiquer.</p>
  <div class="note"><b>À savoir :</b> ce plan en {len(CHAPITRES)} chapitres suit le programme classique d'un cours d'introduction aux systèmes d'exploitation. Je n'ai pas pu consulter le plan officiel de votre enseignant à l'IHEC Carthage : comparez avec votre polycopié et suivez-le en cas de différence.</div>
  <div class="demarrer"><a href="#ch1">Commencer le cours<small>Chapitre 1 : introduction</small></a><a href="#ordo">Simuler un ordonnancement<small>FCFS, SJF, SRT, Round Robin</small></a><a href="#terminal">Pratiquer Linux<small>sans rien installer</small></a><a href="#formules">Fiche des formules<small>pour réviser vite</small></a></div>
  <h3>Comment bien utiliser ce site ?</h3>
  <ol class="etapes"><li><b>Lisez</b> le cours du chapitre, avec les « images mentales » qui rendent les idées concrètes.</li><li><b>Refaites</b> les schémas à la main : c'est ce qui fixe la mémoire.</li><li><b>Faites l'exercice</b> sans regarder la correction, puis comparez.</li><li><b>Testez-vous</b> avec le quiz, puis cochez « terminé » : votre progression est enregistrée.</li><li><b>Vérifiez</b> vos calculs avec les simulateurs, avant l'examen.</li></ol>
</section>
{chapitres}
<section id="ordo">
  <h2 class="titre">Simulateur d'ordonnancement CPU</h2>
  <p>Modifiez les processus, choisissez un algorithme et comparez les résultats.</p>
  <div class="carte">
    <table><tr><th>Processus</th><th>Arrivée</th><th>Durée</th><th>Priorité</th><th></th></tr><tbody id="procs"></tbody></table>
    <div class="champs"><button class="btn clair" id="ajout" type="button">+ Ajouter un processus</button>
      <label>Algorithme<select id="algo"><option value="fcfs">FCFS</option><option value="sjf">SJF (non préemptif)</option><option value="srt">SRT (SJF préemptif)</option><option value="rr">Round Robin</option><option value="prio">Priorités (non préemptif)</option></select></label>
      <label id="bq" hidden>Quantum<input type="number" id="quantum" min="1" value="2"></label>
      <button class="btn" id="go-ordo" type="button">Simuler</button></div>
    <p class="expl" id="note-prio" hidden>Priorité : le plus petit nombre est le plus prioritaire.</p>
    <p class="expl">Round Robin : un processus qui arrive pendant un quantum se place dans la file avant celui qui vient d'être préempté.</p>
    <div class="gantt" id="gantt"></div><div id="ordo-res"></div>
  </div>
</section>
<section id="pagination">
  <h2 class="titre">Simulateur de remplacement de pages</h2>
  <p>Par défaut : la chaîne classique du chapitre 5 avec 3 cadres (FIFO : 15, LRU : 12, OPT : 9 défauts).</p>
  <div class="carte"><div class="champs">
    <label>Chaîne de références<input type="text" id="refs" value="7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1"></label>
    <label>Cadres<input type="number" id="frames" min="1" max="8" value="3"></label>
    <label>Algorithme<select id="palgo"><option value="fifo">FIFO</option><option value="lru">LRU</option><option value="opt">OPT (optimal)</option></select></label>
    <button class="btn" id="go-pages" type="button">Simuler</button></div><div id="pages-res"></div></div>
</section>
<section id="terminal">
  <h2 class="titre">Terminal Linux d'entraînement</h2>
  <p>Un faux terminal sécurisé : vous ne pouvez rien casser. Tapez <code>help</code>, puis essayez les commandes du chapitre 8.</p>
  <div class="terminal"><pre id="term-out" style="background:none;padding:0;margin:0"></pre><div class="ligne-cmd"><span id="prompt">etudiant@ihec:/home/etudiant$</span><input id="term-in" type="text" autocomplete="off" spellcheck="false" aria-label="Commande"></div></div>
</section>
<section id="formules"><h2 class="titre">Fiche des formules</h2><p>À relire la veille de l'examen.</p><div class="formules">{formules}</div></section>
<section id="glossaire"><h2 class="titre">Glossaire</h2><p>Tapez un mot pour filtrer.</p><p><input type="text" id="recherche" placeholder="Rechercher un terme…" aria-label="Rechercher dans le glossaire" size="30"></p>{glossaire}</section>
<section id="revision"><h2 class="titre">Plan de révision</h2>{plan}<h4 style="margin-top:20px">Pour aller plus loin</h4><ul>{livres}</ul>
<footer>Site d'aide à l'étude, non officiel. Le polycopié et les consignes de votre enseignant restent la référence.</footer></section>
</main>
<script>{js}</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] not in ("/", "/index.html"):
            self.send_error(404, "Page introuvable")
            return
        contenu = page().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(contenu)))
        self.end_headers()
        self.wfile.write(contenu)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    if "--export" in sys.argv:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(page())
        print("index.html créé : vous pouvez le mettre en ligne gratuitement (Netlify, GitHub Pages).")
    else:
        url = f"http://localhost:{PORT}"
        print(f"Le site est en ligne sur {url} (Ctrl+C pour arrêter)")
        webbrowser.open(url)
        try:
            HTTPServer(("", PORT), Handler).serve_forever()
        except KeyboardInterrupt:
            print("\nServeur arrêté.")