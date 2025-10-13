# management/commands/limpar_tentativas_antigas.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import RegistroTentativa, BloqueioCadastro

class Command(BaseCommand):
    help = 'Limpa tentativas de cadastro e bloqueios expirados'
    
    def handle(self, *args, **options):
        # Remove tentativas com mais de 30 dias
        limite_tentativas = timezone.now() - timedelta(days=30)
        tentativas_removidas, _ = RegistroTentativa.objects.filter(
            timestamp__lt=limite_tentativas
        ).delete()
        
        # Remove bloqueios expirados
        bloqueios_removidos, _ = BloqueioCadastro.objects.filter(
            expira_em__lt=timezone.now()
        ).delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Removidos: {tentativas_removidas} tentativas, {bloqueios_removidos} bloqueios'
            )
        )