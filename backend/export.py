import pandas as pd
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import create_engine
from config import Config

class DataExporter:
    def __init__(self):
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        
    def get_data(self, query, params=None):
        """Récupère les données depuis la base de données"""
        return pd.read_sql(query, self.engine, params=params)
    
    def export_csv(self, data, filename=None):
        """Exporte les données en CSV"""
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output = io.StringIO()
        data.to_csv(output, index=False, encoding='utf-8-sig')
        return output.getvalue(), filename
    
    def export_excel(self, data, filename=None):
        """Exporte les données en Excel"""
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            data.to_excel(writer, index=False, sheet_name='Données')
            workbook = writer.book
            worksheet = writer.sheets['Données']
            
            # Formatage
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#D9E1F2',
                'border': 1
            })
            
            # Appliquer le formatage
            for col_num, value in enumerate(data.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15)
        
        return output.getvalue(), filename
    
    def export_pdf(self, data, title="Rapport de données", filename=None):
        """Exporte les données en PDF"""
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Titre
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Spacer(1, 20))
        
        # Tableau de données
        table_data = [data.columns.tolist()] + data.values.tolist()
        table = Table(table_data)
        
        # Style du tableau
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(table_style)
        elements.append(table)
        
        # Générer le PDF
        doc.build(elements)
        return buffer.getvalue(), filename

    def export_product_data(self, region=None, product_type=None):
        """Exporte les données des produits avec filtres"""
        query = """
        SELECT p.nom, p.region, p.qualite_score, p.est_bio, pr.nom as producteur
        FROM produit p
        JOIN producteur pr ON p.producteur_id = pr.id
        """
        params = {}
        
        if region:
            query += " WHERE p.region = :region"
            params['region'] = region
        if product_type:
            query += " AND " if "WHERE" in query else " WHERE "
            query += "p.nom = :product_type"
            params['product_type'] = product_type
            
        data = self.get_data(query, params)
        return data 