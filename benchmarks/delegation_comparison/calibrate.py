#!/usr/bin/env python3
"""Positive/negative fixture calibration of receiver plumbing, not an NLP judge."""
import argparse
import copy
import json
import tempfile
from pathlib import Path
from materialize import materialize, CASES
from judge import judge

POSITIVE = {
 'E01': '''Le custom fourni couvre déjà la règle : project/lab_qualification/models.py déclare _quantity_nonnegative, models.Constraint("CHECK(quantity >= 0)"). La quantité zéro passe. pieces/constraint-source.md renvoie à la classe SQL Constraint en source Odoo 19.0 (odoo/orm/table_objects.py:79). Ce mécanisme SQL, lorsqu'il est installé, s'applique aussi aux imports et écritures ORM. Il ne s'agit pas d'une règle métier de quantité universelle du standard. Aucun ajout nécessaire. Nous n'avons aucune base client : présence et installation effective de la contrainte ne sont pas vérifiées, aucune exécution Odoo effectuée. D-17 gratuité et SYN-11 résolu restent acquis.\n''',
 'E02': '''Bug custom : _compute_amount lit unit_price mais @api.depends ne déclare que quantity (project/lab_qualification/models.py). La source 19.0 décrite dans pieces/dependencies-source.md confirme le rôle de déclaration des dépendances. La trace synthétique pieces/orm-trace.jsonl, séquences 1 et 2, montre quantité3 prix10 montant30 puis prix12 montant30, au lieu de36. Le flush et la relecture sont dans la pièce, pas exécutés ici. La séquence3 montre un contournement : réécrire la quantité identique provoque36 ; à valider sur copie réelle avant usage, aucune réparation de production autorisée. La cause touche les montants stockés après modification du prix ; proposer ensuite ajout de dépendance et inventaire/recalcul contrôlé des données existantes dans un périmètre séparé. Test rouge proposé mais non exécuté : créer qty3 prix10, vérifier30, write prix12, flush/relecture, attendu36. Ajouter non-régression gratuité et état confirmé. pieces/decisions.md D-17 autorise déjà prix0 même confirmé, sans nouvelle confirmation ; SYN-11 est un ticket distinct résolu, bouton inchangé. Aucun correctif livré dans ce diagnostic ; limite : pièces synthétiques seulement.\n''',
}


def run_calibration(destination):
    destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=True)
    outcomes=[]
    for case,text in POSITIVE.items():
        run=destination/case
        materialize(case,run)
        out=run/'output'
        main='analyse.md' if case=='E01' else 'diagnostic.md'
        (out/main).write_text(text)
        (out/'result.md').write_text(text)
        for name in ('PROJECT.md','JOURNAL.md'):
            old=(run/'project/.odoo-agents'/name).read_text()
            (out/name).write_text(old+'\n## 2026-09-09 — Épreuve\n'+text)
        rubric=json.loads((CASES/case/'private/rubric.json').read_text())
        review={'case':case,'independent':True,'reviewer':'receiver-calibration-fixture-author',
                'checks':[{'id':r['id'],'pass':True,'evidence':f'output/{main}: positive fixture explicitly addresses {r["criterion"]}'} for r in rubric['obligations']]}
        def sample(name,rev=review,expected=False):
            actual=judge(case,run,rev)['pass']
            outcomes.append({'case':case,'fixture':name,'expected':expected,'actual':actual,'pass':actual==expected})
        sample('positive_hand_authored',expected=True)
        sample('missing_review',{})
        missing=copy.deepcopy(review);missing['checks'].pop();sample('missing_obligation',missing)
        for criterion in rubric['obligations']:
            negative=copy.deepcopy(review)
            for item in negative['checks']:
                if item['id']==criterion['id']:
                    item.update({'pass':False,'evidence':'Injected semantic fault marked by independent fixture review; receiver must propagate rejection.'})
            sample('semantic_rejection_'+criterion['id'],negative)
        p=run/'project/lab_qualification/models.py';old=p.read_text();p.write_text(old+'\n# unsolicited code mutation\n');sample('unauthorized_code');p.write_text(old)
        p=out/'JOURNAL.md';old=p.read_text();p.write_text('history removed\n');sample('lost_history');p.write_text(old)
        p.write_text(old+'\n'.join('Extra line' for _ in range(16)));sample('journal_too_long');p.write_text(old)
        p=run/'demande.md';old=p.read_text();p.write_text('Request replaced');sample('input_replaced');p.write_text(old)
        p=out/main;old=p.read_text();p.unlink();sample('missing_deliverable');p.write_text(old)
    report={'pass':all(o['pass'] for o in outcomes),'fixtures':outcomes,
            'scope':'Receiver completeness/preservation and semantic-review rejection propagation. No automated semantic judgment, no Odoo execution, no native candidate pass asserted.',
            'native_E03_calibration':'Performed separately by runtime on initial red and positive implementation green; see runtime calibration artifacts.'}
    (destination/'calibration.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out')
    a=p.parse_args();out=a.out or tempfile.mkdtemp(prefix='delegation-calibration-')
    result=run_calibration(out)
    print(json.dumps({'pass':result['pass'],'fixtures':len(result['fixtures']),'report':str(Path(out)/'calibration.json')}))
    raise SystemExit(0 if result['pass'] else 1)


if __name__=='__main__':
    main()
