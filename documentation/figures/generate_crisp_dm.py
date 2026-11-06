"""Editable scientific figures; no project code imports, training or data writes.
Run: python documentation/figures/generate_crisp_dm.py
Only files in this script's directory are generated. SVG keeps editable text.
"""
import json
from pathlib import Path
import textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib import font_manager
from PIL import ImageFont

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'crisp_dm_content.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','font.size':14})
INK='#1d3440'; MINT='#247d73'; LINE='#9a9fa1'
CHECKS=[]


def canvas(w,h):
    fig=plt.figure(figsize=(w/100,h/100),dpi=100,facecolor='white')
    ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,w),ylim=(h,0));ax.axis('off')
    return fig,ax


def wrapped(text,size,width,bold=False):
    font=ImageFont.truetype(font_manager.findfont(font_manager.FontProperties(family='DejaVu Sans',weight='bold' if bold else 'normal')),round(size*100/72))
    lines=[]
    for paragraph in text.split('\n'):
        line=''
        for word in paragraph.split():
            if font.getlength((line+' '+word).strip())>width and line:
                lines.append(line);line=word
            else:line=(line+' '+word).strip()
            assert font.getlength(line)<=width,('Unbreakable text',line)
        lines.append(line)
    return '\n'.join(lines)


def put(ax,x,y,text,size=14,width=420,bold=False,color=INK):
    t=ax.text(x,y,wrapped(text,size,width,bold),fontsize=size,weight='bold' if bold else 'normal',
        va='top',ha='left',color=color,linespacing=1.32)
    return t


def bottom(fig,ax,t):
    fig.canvas.draw()
    return ax.transData.inverted().transform(t.get_window_extent(fig.canvas.get_renderer()).get_points())[0,1]


def save(fig,stem):
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    texts=[t for ax in fig.axes for t in ax.texts]
    boxes=[t.get_window_extent(renderer) for t in texts]
    for i,box in enumerate(boxes):
        assert box.x0>=0 and box.y0>=0 and box.x1<=fig.bbox.width and box.y1<=fig.bbox.height,(stem,'text outside canvas',texts[i].get_text())
        for j in range(i):
            assert not box.overlaps(boxes[j]),(stem,'overlapping text',texts[i].get_text(),texts[j].get_text())
    CHECKS.append({'figure':stem,'text_elements':len(texts),'text_intersections':0,'outside_canvas':0})
    fig.savefig(ROOT/(stem+'.svg'),metadata={'Creator':'MOVA – editable scientific figure'})
    fig.savefig(ROOT/(stem+'.png'),dpi=150)
    plt.close(fig)


def detail(cycle):
    w,h=3300,1900
    fig,ax=canvas(w,h)
    put(ax,36,25,f'CRISP-DM – MOVA · Zyklus {cycle}',26,3000,True)
    put(ax,36,82,'Sechs Phasen und 24 Arbeitsschritte · Sechsspaltiges Layout nach der bereitgestellten Originalvorlage von Prof. Schieder',14,3100)
    x0=32;cw=538;top=150;end=1700;items=DATA[f'cycle{cycle}'];n=0
    for i,phase in enumerate(DATA['phases']):
        x=x0+i*cw
        ax.plot([x-8,x-8],[top-12,end],color=LINE,lw=1)
        # Original's raised rectangular phase label with offset black shadow.
        ax.add_patch(Rectangle((x+7,top+7),cw-28,92,facecolor='#252525',edgecolor='none'))
        ax.add_patch(Rectangle((x,top),cw-28,92,facecolor='white',edgecolor='#777',lw=1.2))
        heading=f"{i+1:02d}  "+phase['name'].replace(' ','\n',1)
        ax.text(x+(cw-28)/2,top+46,heading,fontsize=17,weight='bold',ha='center',va='center',color='#151515',linespacing=1.15)
        y=top+136
        for step in phase['steps']:
            title=put(ax,x+3,y,f'{n+1:02d}  {step}',16,cw-47,True,color='#171717')
            y=bottom(fig,ax,title)+14
            body=put(ax,x+3,y,items[n],16,cw-47)
            y=bottom(fig,ax,body)+42
            assert y<end-5,(cycle,step,y)
            n+=1
        CHECKS.append({'figure':f'cycle{cycle}','phase':phase['name'],'last_text_plus_gap':round(y,1),'column_end':end})
    ax.plot([x0+6*cw-8]*2,[top-12,end],color=LINE,lw=1)
    note=('Zyklus 1: Inhalte nach der bereitgestellten ausgefüllten MOVA-Grafik; historische AP-1–8-Abschlussangaben. '
          'Test: 400 Fälle, Zielwochen 23–26. Schwäche bei zukünftigen Nullwochen motiviert Zyklus 2.' if cycle==1 else
          'Zyklus 2: verbindlich freigegebene Zuordnung. 1.200 interne Validierungsfälle; ursprüngliche 400 Testfälle ausgeschlossen. '
          'Ergebnis: Zusatzmerkmal verworfen; ursprüngliches Modell bleibt bestehen.')
    put(ax,36,1745,note,15,3200)
    put(ax,36,1834,'Layout nach bereitgestellter Lehrvorlage · Projektinhalte: MOVA · Synthetische Daten; kein Nachweis realer Übertragbarkeit',12,3200,color='#5b6266')
    assert n==24
    save(fig,f'0{cycle+1}_crisp_dm_zyklus_{cycle}')


def box(fig,ax,x,y,w,h,title,body):
    ax.add_patch(Rectangle((x,y),w,h,facecolor='#f4f8f7',edgecolor='#8daca5',lw=1.2))
    t=put(ax,x+20,y+18,title,17,w-40,True,color=MINT)
    b=put(ax,x+20,bottom(fig,ax,t)+18,body,15,w-40)
    assert bottom(fig,ax,b)<y+h-12,(title,bottom(fig,ax,b),y+h)


def arrow(ax,a,b,color=MINT,connectionstyle='arc3,rad=0'):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=20,lw=2,color=color,connectionstyle=connectionstyle))


def overview():
    fig,ax=canvas(2700,1710)
    put(ax,40,24,'MOVA – Zwei vollständige CRISP-DM-Zyklen',27,2600,True)
    put(ax,40,80,'Erkenntnis → neue Hypothese → neues Merkmal → erneute Modellierung → Evaluation → Entscheidung',17,2600)
    cw=420;gap=22;x0=35;xs=[x0+i*(cw+gap) for i in range(6)]
    put(ax,40,142,'ZYKLUS 1 · Aktivitätsanalyse und erste Prognose',20,2600,True)
    first=[('Ziele und Rahmen','Aktivitätssegmente, Folgewochenprognose und nachvollziehbare Angebote.'),
        ('Daten verstehen','Synthetische Aktivitätsdaten prüfen; auffällig breite Sportrepertoires erkennen.'),
        ('Daten aufbereiten','V2: 100 Nutzer × 26 Wochen. Neun K-Means- und zwei Regressionseingänge.'),
        ('Modelle erstellen','K-Means k = 2 und globale OLS; chronologischer Split 1.800 / 400.'),
        ('Ergebnisse bewerten','Test-MAE: OLS 1,489877; Persistenz 1,710000. Schwäche bei zukünftigen Nullwochen.'),
        ('Demonstrator übergeben','User View, Analytics Lab, Ergebnisartefakte und kritischer Abschlussbericht.')]
    second=[('Neue Hypothese','Historische Nullwochen könnten zusätzliche Prognoseinformation liefern.'),
        ('Bestand wiederverwenden','1.800 Entwicklungsfälle; keine neuen Daten; Wochenhistorie 1–22.'),
        ('Merkmal ergänzen','zero_weeks_last_4_weeks: Nullzählung aus t−3 bis t; Werte 0–4.'),
        ('Erneut modellieren','Drei chronologische Folds; zwei OLS-Varianten, sechs Fits; Persistenz als Referenz.'),
        ('Intern validieren','1.200 Fälle: MAE 1,522613 (2 Merkmale), 1,523105 (3); kein Gesamtgewinn.'),
        ('Entscheidung übergeben','Zusatzmerkmal verwerfen; bisheriges Modell erhalten; Befund im Lab zeigen.')]
    for y,rows in [(195,first),(1060,second)]:
        for i,((title,body),phase) in enumerate(zip(rows,DATA['phases'])):
            box(fig,ax,xs[i],y,cw,300,f"{i+1:02d} {phase['name']}\n{title}",body)
            if i<5:arrow(ax,(xs[i]+cw+2,y+150),(xs[i+1]-2,y+150))
    # Explicit, localized early iteration; no claim that a generator change is a second modeling cycle.
    box(fig,ax,420,555,1580,195,'Rücksprung in Zyklus 1 · Datengenerierung',
        'Data Understanding → Data Preparation / Construct Data → erneute Qualitätsprüfung. '
        'Sportgewichte mit Exponent 1,3 verstärkt; technische Kontrolle mit 1,0. '
        'Gepaarter Vergleich Kontrolle → V2: Top-2-Anteil +6,507 Prozentpunkte; V2 übernommen.')
    arrow(ax,(xs[1]+cw/2,495),(640,555))
    arrow(ax,(1840,555),(xs[2]+cw/2,495),connectionstyle='arc3,rad=-0.15')
    put(ax,450,772,'Frühe Dateniteration innerhalb von Zyklus 1 – noch kein zusätzlicher vollständiger Modellierungszyklus.',14,2100)
    box(fig,ax,430,850,2100,148,'Übergang von Zyklus 1 zu Zyklus 2',
        'Nullzielschwäche → vorab begrenzte Hypothese → Prüfung auf historischen Entwicklungsdaten. '
        'Die ursprünglichen 400 Testfälle bleiben von Entwicklung und Modellentscheidung ausgeschlossen.')
    arrow(ax,(xs[4]+cw/2,495),(2340,850),connectionstyle='arc3,rad=-0.16')
    ax.plot([430,15,15],[924,924,1210],color=MINT,lw=2)
    arrow(ax,(15,1210),(35,1210))
    put(ax,40,1010,'ZYKLUS 2 · Gezielter Merkmalsvergleich',20,2300,True)
    box(fig,ax,40,1420,2580,143,'Vorab definierte Entscheidung: beide Bedingungen erforderlich',
        'Niedrigerer gepoolter MAE UND MAE-Gewinn in mindestens 2 von 3 Folds. '
        'Zwei Foldgewinne reichen nicht: Der gepoolte MAE ist höher → Erweiterung verworfen.')
    put(ax,40,1600,'Abgrenzung: Zyklus 1 berichtet historische Testleistung; Zyklus 2 interne zeitliche Validierung. Kennzahlen nicht direkt als Fortschrittsmaß vergleichen.',14,2600)
    put(ax,40,1650,'Synthetische V2 · bekannte Nutzer · Hypothese nach Zyklus 1 entwickelt · keine unabhängige Testbestätigung für Zyklus 2',13,2600,color='#5b6266')
    save(fig,'01_crisp_dm_gesamtprozess')


if __name__=='__main__':
    assert sum(len(p['steps']) for p in DATA['phases'])==24
    assert len(DATA['cycle1'])==len(DATA['cycle2'])==24
    detail(1);detail(2);overview()
    (ROOT/'layout_checks.json').write_text(json.dumps({'step_count_per_detail':24,'phase_count_per_detail':6,'column_checks':CHECKS,'status':'all measured text blocks fit'},indent=2)+'\n')
    print('Created three SVG/PNG pairs; six phases and 24 steps per detail verified.')
