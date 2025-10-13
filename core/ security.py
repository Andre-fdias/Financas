# core/security.py
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import re
from .models import RegistroTentativa, BloqueioCadastro

class ProtecaoCadastro:
    def __init__(self, request):
        self.request = request
        self.email = None
        self.ip_address = self._get_client_ip()
        self.user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    def _get_client_ip(self):
        """Obtém o IP real do cliente"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def registrar_tentativa(self, email, sucesso=False):
        """Registra uma tentativa de cadastro"""
        try:
            self.email = email.lower().strip() if email else None
            
            RegistroTentativa.objects.create(
                email=self.email,
                ip_address=self.ip_address,
                user_agent=self.user_agent,
                sucesso=sucesso
            )
        except Exception as e:
            # Log do erro sem interromper o fluxo
            print(f"Erro ao registrar tentativa: {e}")
    
    def verificar_bloqueio_email(self, email):
        """Verifica se o email está bloqueado"""
        try:
            self.email = email.lower().strip() if email else None
            
            if not self.email:
                return {'bloqueado': False}

            # Verifica bloqueio permanente por email
            bloqueio = BloqueioCadastro.objects.filter(
                email=self.email,
                expira_em__gt=timezone.now()
            ).first()
            
            if bloqueio:
                return {
                    'bloqueado': True,
                    'motivo': bloqueio.motivo,
                    'expira_em': bloqueio.expira_em,
                    'tipo': 'email'
                }
        except Exception as e:
            print(f"Erro ao verificar bloqueio email: {e}")
        
        return {'bloqueado': False}
    
    def verificar_bloqueio_ip(self):
        """Verifica se o IP está bloqueado"""
        try:
            # Verifica bloqueio por IP
            bloqueio = BloqueioCadastro.objects.filter(
                ip_address=self.ip_address,
                expira_em__gt=timezone.now()
            ).first()
            
            if bloqueio:
                return {
                    'bloqueado': True,
                    'motivo': bloqueio.motivo,
                    'expira_em': bloqueio.expira_em,
                    'tipo': 'ip'
                }
        except Exception as e:
            print(f"Erro ao verificar bloqueio IP: {e}")
        
        return {'bloqueado': False}
    
    def verificar_taxa_tentativas(self, email, limite_tentativas=5, periodo_minutos=60):
        """Verifica taxa de tentativas por email e IP"""
        try:
            self.email = email.lower().strip() if email else None
            periodo_atras = timezone.now() - timedelta(minutes=periodo_minutos)
            
            # Tentativas por email
            tentativas_email = RegistroTentativa.objects.filter(
                email=self.email,
                timestamp__gte=periodo_atras
            ).count() if self.email else 0
            
            # Tentativas por IP
            tentativas_ip = RegistroTentativa.objects.filter(
                ip_address=self.ip_address,
                timestamp__gte=periodo_atras
            ).count()
            
            # Verifica se excedeu os limites
            if tentativas_email >= limite_tentativas:
                # Bloqueia o email
                BloqueioCadastro.bloquear(
                    email=self.email,
                    ip_address=self.ip_address,
                    motivo=f"Excedeu {limite_tentativas} tentativas em {periodo_minutos} minutos",
                    horas=24
                )
                return {
                    'bloqueado': True,
                    'motivo': f'Muitas tentativas para este email. Tente novamente em 24 horas.',
                    'tipo': 'taxa_email'
                }
            
            if tentativas_ip >= limite_tentativas * 2:  # Limite maior para IP
                # Bloqueia o IP
                BloqueioCadastro.bloquear(
                    email=self.email,
                    ip_address=self.ip_address,
                    motivo=f"Excedeu {limite_tentativas * 2} tentativas do IP em {periodo_minutos} minutos",
                    horas=24
                )
                return {
                    'bloqueado': True,
                    'motivo': f'Muitas tentativas deste IP. Tente novamente em 24 horas.',
                    'tipo': 'taxa_ip'
                }
        except Exception as e:
            print(f"Erro ao verificar taxa tentativas: {e}")
        
        return {'bloqueado': False}
    
    def verificar_padrao_suspeito(self, email):
        """Verifica padrões suspeitos de cadastro"""
        try:
            self.email = email.lower().strip() if email else None
            
            if not self.email:
                return {'bloqueado': False}

            # Padrões suspeitos de email
            padroes_suspeitos = [
                r'.*@(temp|fake|spam)\.',
                r'.*@(mailinator|guerrillamail|10minutemail)\.',
                r'^[a-z0-9]+@[a-z0-9]+\.[a-z]{2,3}$',  # Emails muito genéricos
            ]
            
            for padrao in padroes_suspeitos:
                if re.match(padrao, self.email):
                    return {
                        'bloqueado': True,
                        'motivo': 'Padrão de email suspeito detectado',
                        'tipo': 'padrao_suspeito'
                    }
        except Exception as e:
            print(f"Erro ao verificar padrão suspeito: {e}")
        
        return {'bloqueado': False}
    
    def verificar_tudo(self, email):
        """Executa todas as verificações de segurança"""
        try:
            verificacoes = [
                self.verificar_bloqueio_email(email),
                self.verificar_bloqueio_ip(),
                self.verificar_taxa_tentativas(email),
                self.verificar_padrao_suspeito(email)
            ]
            
            # Retorna o primeiro bloqueio encontrado
            for verificacao in verificacoes:
                if verificacao['bloqueado']:
                    return verificacao
        except Exception as e:
            print(f"Erro ao executar verificações de segurança: {e}")
        
        return {'bloqueado': False}