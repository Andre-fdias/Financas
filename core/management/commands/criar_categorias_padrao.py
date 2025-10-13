# management/commands/criar_categorias_padrao.py
from django.core.management.base import BaseCommand
from core.models import Categoria, Subcategoria

class Command(BaseCommand):
    help = 'Cria categorias e subcategorias padrão do sistema'
    
    def handle(self, *args, **options):
        categorias_padrao = [
            ('Moradia', [
                'Aluguel', 'Condomínio', 'IPTU', 'Energia Elétrica', 
                'Água', 'Gás', 'Internet', 'Manutenção'
            ]),
            ('Alimentação', [
                'Supermercado', 'Restaurante', 'Lanches', 'Hortifruti'
            ]),
            # ... adicione outras categorias conforme CATEGORIA_CHOICES
        ]
        
        for cat_nome, subcats in categorias_padrao:
            categoria, created = Categoria.objects.get_or_create(
                nome=cat_nome,
                eh_padrao=True,
                defaults={'usuario': None}
            )
            
            for sub_nome in subcats:
                Subcategoria.objects.get_or_create(
                    nome=sub_nome,
                    categoria=categoria,
                    eh_padrao=True,
                    defaults={'usuario': None}
                )
        
        self.stdout.write(self.style.SUCCESS('Categorias padrão criadas com sucesso!'))