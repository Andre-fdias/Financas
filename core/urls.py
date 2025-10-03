from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    # Páginas principais
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    # Reset de senha
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='core/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), name='password_reset_complete'),
    path('profile/change-password/', views.password_change_view, name='password_change_view'),


    # Perfil do usuário (URLs simplificadas)
    path('profile/', views.profile_update_view, name='profile'),  # Página principal do perfil
    path('profile/update/', views.profile_update_view, name='profile_update'),
    path('profile/change-password/', views.password_change_view, name='password_change'),
    path('profile/delete-account/', views.delete_account, name='delete_account'),
    path('profile/remove-photo/', views.remove_profile_photo, name='remove_profile_photo'),
    
    # APIs para perfil (AJAX)
    path('api/profile/update-info/', views.update_profile_info, name='update_profile_info'),
    path('api/profile/update-photo/', views.update_profile_photo, name='update_profile_photo'),
    path('api/profile/statistics/', views.user_statistics, name='user_statistics'),
    path('api/profile/track-login/', views.track_login, name='track_login'),

    # Contas Bancárias
    path('contas/', views.conta_list, name='conta_list'),
    path('contas/nova/', views.conta_create, name='conta_create'),
    path('contas/nova_modal/', views.conta_create_modal, name='conta_create_modal'),
    path('contas/<int:pk>/editar/', views.conta_update, name='conta_update'),
    path('contas/<int:pk>/excluir/', views.conta_delete, name='conta_delete'),
    path('get_banco_code/', views.get_banco_code, name='get_banco_code'),
    path('contas/buscar-titular/', views.buscar_contas_por_titular, name='buscar_contas_titular'),
    path('contas/estatisticas/', views.estatisticas_contas, name='estatisticas_contas'),


    # Entradas (Receitas)
    path('entradas/', views.entrada_list, name='entrada_list'),
    path('entradas/nova/', views.entrada_create, name='entrada_create'),
    path('entradas/<int:pk>/editar/', views.entrada_update, name='entrada_update'),
    path('entradas/<int:pk>/excluir/', views.entrada_delete, name='entrada_delete'),

    # Saídas (Despesas)
    path('saidas/', views.saida_list, name='saida_list'),
    path('saidas/criar/', views.saida_create, name='saida_create'),
    path('saidas/editar/<int:pk>/', views.saida_update, name='saida_update'),
    path('saidas/<int:pk>/marcar_pago/', views.marcar_como_pago, name='marcar_como_pago'),
    path('saidas/excluir/<int:pk>/', views.saida_delete, name='saida_delete'),
    path('saidas/debug/<int:pk>/', views.debug_saida_update, name='debug_saida_update'),
    
    # Relatórios e Extratos
    path('extrato/', views.extrato_completo, name='extrato_completo'),
    path('extrato/modal-selecao/', views.modal_selecao_extrato, name='modal_selecao_extrato'),
    path('extrato/gerar-pdf/', views.gerar_extrato_bancario_pdf, name='gerar_extrato_pdf'),
    path('saldo/', views.saldo_atual, name='saldo_atual'),
    # Nova rota para a API de insights
      path('api/insights/', views.financial_insights_api, name='financial_insights_api'),

    
    # APIs para transações
    path('api/transacao/<int:pk>/detalhes/', views.transacao_detalhes, name='transacao_detalhes'),
    path('api/transacao/<int:pk>/marcar-pago/', views.marcar_como_pago, name='marcar_como_pago'),

    # Transferências
    path('transferencias/', views.transferencia_list, name='transferencia_list'),
    path('transferencias/criar/', views.transferencia_create, name='transferencia_create'),
    path('transferencias/editar/<int:pk>/', views.transferencia_update, name='transferencia_update'),
    path('transferencias/excluir/<int:pk>/', views.transferencia_delete, name='transferencia_delete'),
    path('get-account-balance/<int:pk>/', views.get_account_balance, name='get_account_balance'),


  # Lembretes
# URLs para Lembretes

    path('lembretes/', views.lembrete_list, name='lembrete_list'),
    path('lembretes/criar/', views.lembrete_create, name='lembrete_create'),
    path('lembretes/editar/<int:pk>/', views.lembrete_update, name='lembrete_update'),
    path('lembretes/excluir/<int:pk>/', views.lembrete_delete, name='lembrete_delete'),
    path('lembretes/toggle/<int:pk>/', views.lembrete_toggle, name='lembrete_toggle'),
    path('lembretes/alternar-status/', views.alternar_status_lembrete, name='alternar_status_lembrete'),
   
    # Operações de Saque
    path('operacoes-saque/', views.operacao_saque_list, name='operacao_saque_list'),
    path('operacoes-saque/nova/', views.operacao_saque_create, name='operacao_saque_create'),
    path('operacoes-saque/<int:pk>/', views.operacao_saque_detail, name='operacao_saque_detail'),
    path('operacoes-saque/<int:pk>/excluir/', views.operacao_saque_delete, name='operacao_saque_delete'),


    #Oraculo Financeiro
   path('oraculo/', views.oraculo_financeiro, name='oraculo_financeiro'),    

    # APIs para categorias/subcategorias
    path('api/categorias/', views.api_categorias, name='api_categorias'),
    path('api/categorias/criar/', views.api_criar_categoria, name='api_criar_categoria'),
    path('api/subcategorias/<int:categoria_id>/', views.api_subcategorias_por_categoria, name='api_subcategorias'),
    path('api/subcategorias/criar/', views.api_criar_subcategoria, name='api_criar_subcategoria'),
]