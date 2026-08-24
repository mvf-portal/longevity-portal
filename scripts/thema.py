#!/usr/bin/env python3
"""Alles Themenspezifische der taeglichen Studienauswahl — und sonst nichts.

Diese Datei ist die EINZIGE unter scripts/, die sich von Portal zu Portal
inhaltlich unterscheidet. `update_studies.py` bleibt in allen Portalen
wortgleich und importiert von hier. Wer die Auswahl aendern will, aendert
Text in dieser Datei — keinen Code.

Erzeugt von neues-portal.py aus dem Themenprofil `themen/longevity.json`.
Weiterentwickelt wird danach hier, nicht im Profil.
"""
from __future__ import annotations

import os

# --------------------------------------------------------------- Kennungen
# NCBI bittet bei automatisierten Zugriffen um eine Tool-Kennung.
NCBI_TOOL = "longevity-portal"

# ----------------------------------------------------------- Die Suchabfrage
# Zwei Bloecke, die BEIDE zutreffen muessen. Ohne den zweiten spuelt die Abfrage
# Arbeiten herein, die das Thema nur streifen; ohne den ersten kommt beliebige
# Versorgungsliteratur.
#
# Zur Feldwahl: [MeSH Terms] fasst breit, [Majr] verlangt das Haupt-Schlagwort,
# [Title/Abstract] fasst am breitesten, [Title] am engsten. Faustregel aus den
# Schwesterportalen: Steht ein Begriff in fremden Abstracts als blosses Werkzeug
# oder Beiwerk, ist [Title/Abstract] untauglich — dann [Majr]/[Title]. Im
# KI-Portal sank die Trefferzahl dadurch von 605.000 auf 321.000, und erst die
# kleinere Menge handelte tatsaechlich vom Thema.
#
# Vor dem Livegang die Trefferzahl in PubMed nachsehen und hier notieren, damit
# spaetere Aenderungen messbar bleiben.
_THEMA = (
    '(("Longevity"[Majr] OR "Healthy Aging"[Majr] OR "Aging"[Majr] '
    'OR "Cellular Senescence"[Majr] OR "Life Expectancy"[Majr] '
    'OR "Geriatrics"[Majr] OR "Frailty"[Majr] '
    'OR "Health Services for the Aged"[Majr]) '
    'OR (longevity[Title] OR healthspan[Title] OR "healthy ag*ing"[Title] '
    'OR "life expectancy"[Title] OR "biological age"[Title] '
    'OR "epigenetic clock*"[Title] OR senolytic*[Title] '
    'OR geroprotect*[Title] OR geroscience[Title] OR centenarian*[Title] '
    'OR "successful aging"[Title] OR frailty[Title]))'
)
_KONTEXT = (
    '("Delivery of Health Care"[MeSH Terms] OR "Health Services"[MeSH Terms] '
    'OR "Quality of Health Care"[MeSH Terms] OR "Patient Care"[MeSH Terms] '
    'OR "Health Policy"[MeSH Terms] OR "Public Health"[MeSH Terms] '
    'OR "health care"[Title/Abstract] OR "health services"[Title/Abstract] '
    'OR "patient outcome*"[Title/Abstract] OR "clinical practice"[Title/Abstract] '
    'OR implementation[Title/Abstract] OR patients[Title/Abstract])'
)
# "Humans"[MeSH] haelt Tier-, Labor- und reine Modellarbeiten heraus.
TERM = os.environ.get(
    "SEARCH_TERM",
    f'(({_THEMA} AND {_KONTEXT}) AND "Humans"[MeSH Terms])',
)
# Zweite Abfrage, damit Arbeiten mit Deutschland- und Europabezug den
# Kandidatenpool sicher erreichen. Ueber MeSH und Autorenadresse, nicht ueber
# Journalnamen - deutschsprachige Journale liefern kaum Treffer.
TERM_DE = os.environ.get(
    "SEARCH_TERM_DE",
    f"{TERM} AND (Germany[MeSH Terms] OR Germany[Affiliation] "
    "OR Europe[MeSH Terms] OR Europe[Affiliation])",
)

# Groesse des Kandidatenpools. Europa steht vorn und stellt die Mehrheit -
# ein Sprachmodell gewichtet, was es zuerst liest. Wer das umdreht, bekommt
# eine Auswahl ohne Bezug zu hiesigen Verhaeltnissen; im Klima-Portal ist
# genau das passiert.
POOL_EUROPA = 30
POOL_ALLGEMEIN = 25
# Welche Abfrage vorn steht. True ist der Regelfall und die Lehre aus dem
# Klima-Portal: Steht die allgemeine Abfrage vorn, kommt eine Auswahl ohne
# Bezug zu hiesigen Verhaeltnissen heraus. Das Versorgungsforschungs-Portal
# arbeitet historisch andersherum (40 allgemein + 15 deutsch) - dort steht
# hier False, damit der Anschluss an die Vorlage nichts an seiner taeglichen
# Auswahl geaendert hat. Umstellen ist eine redaktionelle Entscheidung.
EUROPA_ZUERST = True

# Wie viele Studien taeglich erscheinen. SOLL wird im Prompt verlangt und beim
# Kappen verwendet; ueber MAX wird gekappt, unter MIN bricht der Lauf ab.
# **Nicht ins JSON-Schema schreiben** - die Anthropic-API lehnt minItems > 1
# und maxItems ab (am 17.08.2026 zweimal mit HTTP 400 belegt).
ANZAHL_SOLL = 6
ANZAHL_MAX = 7
ANZAHL_MIN = 5
# True: zu viele Studien werden auf ANZAHL_SOLL gekuerzt (die Auswahl ist nach
# Relevanz geordnet, die vorderen sind brauchbar). False: zu viele lassen den
# Lauf scheitern - so hielt es das Versorgungsforschungs-Portal von Anfang an.
KAPPEN = True

# ------------------------------------------------------------------- Prompts
SYSTEM = (
    "Du bist Fachredakteur fuer gesundes Altern und Alternsforschung. Aus "
    "einer Liste von PubMed-Abstracts waehlst du die relevantesten aktuellen "
    "Studien aus und fasst sie praezise auf Deutsch zusammen. Deine "
    "Leserschaft arbeitet im deutschen Gesundheitswesen: Kliniken und "
    "geriatrische Abteilungen, Praxen, Kostentraeger, Selbstverwaltung, "
    "Praevention, Gesundheitspolitik und Alternsforschung. Sie will wissen, "
    "was eine Massnahme fuer die verbleibenden Lebensjahre und deren "
    "Qualitaet bewirkt - nicht, welcher Biomarker am staerksten mit dem "
    "Alter korreliert."
)

USER_TEMPLATE = """Unten stehen aktuelle PubMed-Abstracts (nach Datum sortiert).

Waehle 6 Studien aus - nur wenn nicht genug taugliche Kandidaten dabei sind, duerfen es 5 sein. Gesucht sind Studien, die (a) das Altern, die Lebenserwartung oder die Versorgung aelterer Menschen untersuchen UND (b) im
Abstract ein BENENNBARES ERGEBNIS berichten. Bei quantitativen Arbeiten heisst
das: konkrete Zahlen (Prozentwerte, Effektstaerken, Odds/Hazard Ratios, Zeit-
oder Kostenwirkungen, Fallzahlen, p-Werte) - und die gehoeren dann auch in die
Zusammenfassung. Qualitative Studien (Interviews, Fokusgruppen) und
Expertenpapiere sind ausdruecklich zugelassen; bei ihnen tritt an die Stelle
der Zahl die klar benannte Kernaussage - welche Faktoren, welche Bedingungen,
welche Empfehlung. Was NICHT genuegt, ist ein Abstract, der nur ankuendigt,
was untersucht wurde, ohne zu sagen, was dabei herauskam.
Ueberspringe Studien ohne Abstract oder ohne benennbares Ergebnis. Achte auf
thematische Vielfalt und mische quantitative und qualitative Arbeiten.

THEMATISCHE RANGFOLGE - in dieser Reihenfolge bevorzugen:
  1. Gewonnene Jahre und gewonnene Gesundheit: Massnahmen mit gemessener
     Wirkung auf Sterblichkeit, gesunde Lebensjahre, Funktionsfaehigkeit,
     Selbststaendigkeit oder Lebensqualitaet im Alter.
  2. Praevention und Verlauf: koerperliche Aktivitaet, Ernaehrung, Impfungen,
     Sturzprophylaxe, Absetzen ueberfluessiger Arzneimittel, kognitive
     Gesundheit - jeweils mit Endpunkt, nicht mit blossem Zwischenwert.
  3. Geriatrische Versorgung: Assessment, Rehabilitation, Delirprophylaxe,
     sektorenuebergreifende Versorgung, Versorgung am Lebensende.
  4. Bevoelkerung und System: Entwicklung der Lebenserwartung, Kompression
     der Morbiditaet, soziale Unterschiede in der Lebenserwartung,
     Krankheitslast und Kosten der Alterung.
  5. Biologie des Alterns nur dann, wenn sie am Menschen untersucht wurde
     UND einen klinischen oder Versorgungsbezug hat - etwa ein
     Alternsbiomarker, der ein Behandlungsergebnis vorhersagt.

NICHT in die Auswahl gehoeren:
reine Grundlagenforschung an Modellorganismen (Wurm, Fliege, Maus) ohne Bezug
zum Menschen, Assoziationsstudien ohne Endpunkt ("Biomarker X korreliert mit
dem Alter"), Studien zu Nahrungsergaenzungsmitteln oder Anti-Aging-Angeboten
ohne gemessenes Ergebnis, Querschnittsbefragungen ohne Bezugsgroesse, Arbeiten,
die aeltere Menschen nur als Stichprobe fuer eine ganz andere Fragestellung
verwenden, sowie Uebersichten, die nichts Eigenes berichten.

HARTE REGELN ZUR ZUSAMMENSETZUNG (sie gehen der thematischen Rangfolge vor):
  1. MINDESTENS DREI der sechs Studien muessen aus Europa stammen oder ein
     europaeisches Gesundheitssystem betreffen. Liegen weniger als drei solche
     Arbeiten vor, nimm die verbleibenden Plaetze aus dem Rest - aber schoepfe
     die europaeischen zuerst aus.
  2. HOECHSTENS EINE der sechs darf aus der Biologie des Alterns kommen
     (Biomarker, Seneszenz, epigenetisches Alter, Geroprotektoren). Dieses Feld
     publiziert viel und schnell und wuerde die Auswahl sonst dominieren,
     waehrend die Versorgungsfrage unbeantwortet bliebe.
  3. HOECHSTENS ZWEI duerfen sich auf Demenz beziehen. Demenz ist das
     meistpublizierte Einzelthema des Feldes und verdraengt sonst Sturz,
     Ernaehrung, Multimorbiditaet und Arzneimitteltherapie.
  4. MINDESTENS ZWEI der sechs muessen eine geriatrische Versorgungsfrage
     behandeln - Arzneimitteltherapie im Alter (Polypharmazie, Absetzen,
     unangemessene Verordnung), geriatrisches Assessment, Delir, Sturz,
     Frailty und Sarkopenie in der Versorgung, geriatrische Rehabilitation,
     Ueberleitung zwischen Klinik, Praxis und Pflege. Ohne diese Untergrenze
     kippt der Hub in Richtung Alternsforschung: Am 24.08.2026 gemessen,
     stammen 39,9 Prozent des Suchraums aus dem geriatrischen Feld, in der
     Auswahl kamen sie aber kaum vor. Die Quote ist der Grund, warum es
     keinen eigenen Geriatrie-Hub gibt - die Frage wird hier beantwortet.

ZWEITES AUSWAHLKRITERIUM - Übertragbarkeit auf Deutschland:
Bei sonst gleicher Qualität hat die übertragbare Studie IMMER Vorrang vor der
aktuelleren.

  Hoch:    Deutschland und deutschsprachiger Raum, vergleichbare Sozial-
           versicherungssysteme.
  Mittel:  Übriges Europa, Kanada, Australien - andere Ausgangslage,
           ähnlicher Versorgungsauftrag.
  Gering:  USA und Länder mit grundlegend anderer Finanzierung oder
           Ressourcenlage. Nur nehmen, wenn die Fragestellung davon
           unabhängig ist.

Besonderheit dieses Themenfeldes: Lebenserwartung und Versorgung im Alter
haengen staerker als anderswo an Sozialsystem und Wohlstand. Eine Studie aus
einem Land mit anderer Rentensicherung, anderer Pflegefinanzierung oder
deutlich anderer Lebenserwartung laesst sich nicht ohne Weiteres uebertragen.
Ordne die Systeme nach Vergleichbarkeit: hoch bei DACH, Niederlanden, Belgien
und Frankreich, mittel bei Skandinavien, Grossbritannien, Kanada, Australien
und Japan, gering bei den USA und bei Laendern mit deutlich niedrigerer
Lebenserwartung. Nenne im Feld transfer, was uebertragbar ist und was nicht -
und wenn die Altersstruktur oder die Finanzierung den Unterschied macht, sage
das ausdruecklich.

Fuer jede Studie:
- journal: Journalname genau so, wie er in der Kopfzeile des Abstracts steht -
  Abkuerzung nicht aufloesen, nichts ergaenzen. (Wird ohnehin durch die Angabe
  aus PubMed ersetzt; rate hier nichts.)
- year: Erscheinungsjahr, z. B. "2026"
- pmid: die PubMed-ID
- title: praegnanter deutscher Titel, **hoechstens 160 Zeichen**. Der
  Torwaechter lehnt alles ueber 200 Zeichen ab und stoppt damit die ganze
  Ausgabe - Methode und Population gehoeren nicht in den Titel, sie stehen
  in sum und transfer.
  **Er MUSS mit der Alterns- bzw. versorgungsbezogenen Fragestellung beginnen,
  nicht mit der Erkrankung, an der sie untersucht wurde.** Fast jede Arbeit in
  diesem Feld haengt an einem klinischen Traegerfall - Herzinsuffizienz,
  Hueftfraktur, Diabetes -, und die Abstracts sind danach betitelt. Uebernimmt
  der Titel das, liest sich der Hub wie eine beliebige Sammlung
  internistischer Studien. Nicht "Herzinsuffizienz bei Aelteren: ...",
  sondern "Geriatrisches Assessment vor Klinikaufnahme senkt ...".
- sum: 1 Satz auf Deutsch, was die Studie untersucht hat. Wenn der genannte
  Anlassfall nur das Material ist, an dem gerechnet wurde, sage das
  ausdruecklich - sonst haelt die Leserschaft ihn fuer den Gegenstand.
- result: Deutsch, die konkreten Zahlen/Befunde + ein kurzer Einordnungssatz.
  Deutsches Zahlenformat mit Komma (z. B. 0,63). **Der Einordnungssatz darf
  nicht behaupten, was die Autoren selbst ablehnen.** Wo ein Abstract eine
  Deutung ausdruecklich zurueckweist, diese Einschraenkung uebernehmen statt
  sie zu ueberschreiben. Ein Rechercheportal referiert, es wertet nicht auf.
- transfer: EIN Halbsatz (höchstens 12 Wörter), warum das Ergebnis für Deutschland
  taugt - oder wo die Grenze liegt. Nenne Land bzw. System und Datengrundlage.
  Keine ganzen Sätze, keine Wiederholung des Titels.
  Gut:      "Deutsche Klinikdaten, vergleichbare Dokumentationspflichten"
            "Niederlande, vergleichbares Versicherungssystem"
            "USA - nur der Sicherheitsbefund ist übertragbar"
  Schlecht: "Diese Studie ist gut übertragbar." (sagt nichts)

WICHTIG - Fachterminologie: Etablierte englische Fachbegriffe NICHT eindeutschen.
Sie sind auch im deutschen Fachdeutsch stehende Begriffe; eine woertliche
Uebersetzung wirkt unprofessionell und erschwert das Wiederfinden.
Beispiele fuer Begriffe, die englisch bleiben: Frailty (neben Gebrechlichkeit),
Healthspan, Geroscience, Deprescribing, Assessment, Screening, Odds Ratio,
Hazard Ratio. Uebersetze dagegen, was im Deutschen eine gaengige Entsprechung
hat: aus "life expectancy" wird Lebenserwartung, aus "healthy life years"
gesunde Lebensjahre, aus "nursing home" Pflegeheim.
Faustregel: Wuerde eine deutsche Fachzeitschrift wie Monitor Versorgungsforschung
den Begriff englisch stehen lassen, dann tue es auch. Im Zweifel englisch
belassen und bei Bedarf eine kurze deutsche Erlaeuterung in Klammern ergaenzen.

Gib ausschliesslich das geforderte JSON zurueck.

=== ABSTRACTS ===
{abstracts}
"""
