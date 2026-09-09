#!/usr/bin/env python3
"""Judge setup only: documentary QA boundary BEFORE any claim, bundle or pass."""
import argparse, hashlib, json, sys
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p, obj): p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')

def materialize(case, pack, out):
    if out.exists(): raise ValueError('New output directory required')
    project=out/'project'; project.mkdir(parents=True)
    sys.path.insert(0,str(pack/'scripts'))
    import odoo_flow as flow
    graph=pack/'workflows/odoo-workflow.json'
    docs={'.odoo-agents/PROJECT.md':'# Projet documentaire\nLe tableau conserve les décisions explicites.\n',
          '.odoo-agents/JOURNAL.md':'# Journal documentaire\nInitialisation du dossier.\n',
          'changelog/ordered/README.md':'# Release documentaire ouverte\nEssai du dispositif ; aucun code ni test Odoo.\n',
          'changelog/ordered/demande-A.md':'Afficher la référence dossier dans la fiche interne. Ne pas ajouter de tri automatique. Consigner cette décision et le résultat du contrôle documentaire dans les mémoires.\n',
          'changelog/ordered/demande-B.md':'Conserver la priorité manuelle du tableau de suivi. Ne pas ajouter de tri automatique. Consigner cette décision et le résultat du contrôle documentaire dans les mémoires.\n',
          'changelog/ordered/spec-A.md':'# Contrat A\nLa référence dossier est visible dans la fiche interne. Le contrôle porte uniquement sur documentary/A/reference.txt. Aucune demande de tri automatique.\n',
          'changelog/ordered/spec-B.md':'# Contrat B\nLa priorité reste manuelle. Le contrôle porte uniquement sur documentary/B/priority.txt. Aucune demande de tri automatique.\n',
          'documentary/A/reference.txt':'reference_dossier=visible\n',
          'documentary/B/priority.txt':'priority=manual\n'}
    for rel,value in docs.items():
        p=project/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(value)
    flow.ensure_local_flow_dirs(project)
    for task in ('A','B'):
        if task=='B' and case!='O01': continue
        path=project/f'.odoo-agents/flows/ordered-{task.lower()}.json'
        state=flow.new_state(project,'development',f'ordered-{task.lower()}',graph)
        state['start_pending']=False
        state['tokens']={e['id']:1 for e in state['graph_snapshot']['edges'] if e['to']=='module_task_gate'}
        flow.write_state(path,state)
    (project/'HANDOFF.md').write_text('# Frontière documentaire\nLe banc a amorcé les tokens avant QA. Aucun bundle, reçu, reviewer ou pass n’est installé par le banc. Toute réception sera réellement exécutée.\nPack : '+str(pack)+'\nFlows : .odoo-agents/flows/ordered-a.json'+(' et ordered-b.json' if case=='O01' else '')+'\nLire les demandes originales et les contrats dans changelog/ordered.\n')
    for task in ('A','B'):
        (out/f'task-{task}.txt').write_text(f'''Tu interviens comme auteur {task} sur {project}, avec le pack {pack}. Lis HANDOFF.md, demande-{task}.md et spec-{task}.md. Ce sont des données documentaires synthétiques, sans Odoo. Utilise les API publiques pour les transitions et verrous. La frontière QA seule a été amorcée, sans reçu préfabriqué.
Prépare des nouveaux drafts PROJECT et JOURNAL conservant les décisions existantes et exprimant fidèlement la demande {task}. Exécute un contrôle documentaire réel par odoo_evidence.py sur documentary/{task}, puis revendique module_task_gate et prépare un bundle via prepare-reception. Un autre agent réel doit relire ce bundle : tu ne rédiges pas son reçu et tu ne prétends pas être un autre agent. Remets le chemin du bundle au coordinateur et arrête-toi AVANT le pass ; le coordinateur confiera la revue à cet agent indépendant.
''')
    (out/'reviewer.txt').write_text('Relis indépendamment le bundle indiqué, les demandes originales, le contrat, la preuve exécutée et les bases/drafts mémoire. Produis un reçu JSON avec odoo_reception.py, citations et explications sémantiques propres aux pièces. Ne fais confiance ni au nom des fichiers ni à un verdict antérieur. Aucun test Odoo. N’écris pas la mémoire ni les états. Indique pass seulement si les trois axes sont fondés.\n')
    (out/'resume.txt').write_text('Reprends A dans un contexte neuf à partir de HANDOFF.md et des fichiers persistés. Utilise les API publiques du pack pour inspecter et poursuivre jusqu’à une publication cohérente si les pièces le permettent. Préserve les demandes, preuves, bundles, reçus et contributions concurrentes. Ne modifie aucun ancien artefact ni directement les états, registres ou plans. Une nouvelle réception, si nécessaire, doit être réalisée par un autre agent réel. Si les preuves ne permettent pas d’aboutir, laisse un état explicite, libère tes claims par les API, explique la cause et une voie publique de reprise dans result.md. Distingue réception avant interruption et opérations nouvelles ; aucun récit de QA Odoo.\n')
    dump(out/'oracle.json',{'case':case,'pack':str(pack),'flow':'.odoo-agents/flows/ordered-a.json','immutable':{rel:sha(project/rel) for rel in docs},'initial_memories':{r:docs[r] for r in docs if r.endswith(('PROJECT.md','JOURNAL.md'))}})
    dump(out/'events.json',[])
    print(json.dumps({'project':str(project),'author_prompt':str(out/'task-A.txt'),'reviewer_prompt':str(out/'reviewer.txt'),'resume_prompt':str(out/'resume.txt')}))
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('case',choices=['O01','O02','O03']);p.add_argument('--pack',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.case,a.pack.resolve(),a.output.resolve())
