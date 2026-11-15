# Blender 3D Vizualizacija Binarnog Stabla Traženja
Ovaj program, koji sam izradio za svoj završni rad, omogućuje 3D vizualizaciju izgradnje binarnog stabla traženja.
Klikom na _Generiraj_ u grafičkom sučelju (`GUI.py`), otvara se Blender i renderira se .mp4 video s navedenim postavkama. Rezultat će se pojaviti u folderu 'renders', koji bi se trebao nalaziti unutar istog foldera gdje se nalazi i `tree_vizualization.blend`.

Alternativno, moguće je i pokrenuti renderiranje bez grafičkog sučelja, ulaskom u .blend datoteku.
U Edit -> Preferences -> Save&Load, ako je postavka Auto Run Python Scripts uključena, renderiranje će se automatski pokrenuti. Ako je ta postavka isključena, Blender će tražiti potvrdu prije pokretanja skripte.

Ukoliko je potrebno napraviti neke izmjene u samoj insertion.py datoteci, to je moguće napraviti s isključenom Auto Run Python Scripts postavkom, i to tako da se insertion.py pokrene nakon ažuriranja promjena.
