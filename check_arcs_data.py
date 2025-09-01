#!/usr/bin/env python3
"""
Vérifier les données des arcs pour comprendre la distribution des segments
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app, GrapheArc
from sqlalchemy import func

def check_arcs_data():
    """Vérifier les données des arcs"""
    with app.app_context():
        print("🔍 Vérification des données des arcs...")
        
        # Compter le nombre total d'arcs
        total_arcs = GrapheArc.query.count()
        print(f"📊 Total des arcs: {total_arcs}")
        
        # Compter les axes uniques
        axes_count = db.session.query(func.count(func.distinct(GrapheArc.nom_axe))).scalar()
        print(f"📊 Axes uniques: {axes_count}")
        
        # Afficher tous les axes uniques avec leur nombre de segments
        axes_stats = db.session.query(
            GrapheArc.nom_axe,
            func.count(GrapheArc.id).label('segment_count')
        ).group_by(GrapheArc.nom_axe).order_by(func.count(GrapheArc.id).desc()).all()
        
        print(f"\n📋 Distribution des segments par axe:")
        for axe, count in axes_stats:
            print(f"   {axe}: {count} segments")
        
        # Afficher les détails des premiers axes
        print(f"\n🔍 Détails des premiers axes:")
        for axe, count in axes_stats[:5]:
            print(f"\n📍 Axe: {axe} ({count} segments)")
            segments = GrapheArc.query.filter_by(nom_axe=axe).all()
            for i, segment in enumerate(segments[:3]):  # Afficher les 3 premiers segments
                print(f"   Segment {i+1}: ID={segment.id}, PK_Debut={segment.pk_debut}, PK_Fin={segment.pk_fin}")
                if segment.geometrie:
                    print(f"      Géométrie: {segment.geometrie[:100]}...")
                else:
                    print(f"      Géométrie: NULL")

if __name__ == "__main__":
    from app import db
    check_arcs_data()
