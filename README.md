# Gesundes Altern & Longevity · Rechercheportal

Ein Rechercheportal zum Themenfeld **Gesundes Altern & Longevity**: 91 Datenbanken in 11 Rubriken,
davon 48 mit Live-Suche, dazu eine täglich aus PubMed kuratierte Studienauswahl mit
deutschen Zusammenfassungen.

Ein Angebot von **Monitor Versorgungsforschung** (eRelation AG – Content in Health, Bonn).

https://longevity.m-vf.de/

## Wie es funktioniert

Ein Suchbegriff, eingegeben an einer Stelle, stellt sämtliche Datenbankkacheln darauf ein;
ein Klick führt direkt in die Trefferliste der jeweiligen Datenbank. Deutsche Fachbegriffe
werden für internationale Datenbanken automatisch in den Ausdruck übersetzt, unter dem sie
dort indexiert sind (211 Begriffe).

| | |
|---|---|
| Datenbanken | 91 in 11 Rubriken |
| Live-Suche | 48 |
| Portal (feste URL) | 37 |
| Lizenz nötig | 6 |
| Suchglossar | 211 Begriffe |
| Studienauswahl | täglich 6 Uhr aus PubMed, KI-kuratiert |

## Aufbau

| Datei | Zweck |
|---|---|
| `index.html` | die gesamte Anwendung (CSS + HTML + JS inline) |
| `ueber.html`, `newsletter.html` | Begleitseiten |
| `scripts/thema.py` | **alles Themenspezifische** der Studienauswahl |
| `scripts/update_studies.py` | PubMed → Claude → Marker-Block (in allen Portalen gleich) |
| `scripts/build_newsletter.py` | RSS-Feed und Download-Dateien aus dem Archiv |
| `scripts/mailchimp_entwurf.py` | Kampagnen-Entwurf zur Freigabe |
| `studien-archiv.json` | vollständige Historie aller gezeigten Studien |
| `portal.json` | die Werte dieses Portals — Grundlage des Vorlagen-Abgleichs |

Dieses Portal ist aus der Vorlage `mvf-portal/portal-vorlage` entstanden. Änderungen an der
Mechanik gehören dorthin und werden von dort in alle Portale eingespielt.

## Betrieb

Kein Build, kein Framework. Commit auf `main` → GitHub Pages baut automatisch.

Secrets im Repository: `LONGEVITYHUB` (Claude-API) und `LONGEVITYHUBMC` (Mailchimp).
