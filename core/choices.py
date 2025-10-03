# core/choices.py
# Este arquivo contém todas as listas de 'choices' para padronização e reutilização.



PERIODICIDADE_CHOICES = [
    ('unica', 'Única'),
    ('diaria', 'Diária'),
    ('semanal', 'Semanal'),
    ('mensal', 'Mensal'),
    ('anual', 'Anual'),
]

TIPO_CONTA_CHOICES = [
    ('corrente', 'Conta Corrente'),
    ('poupanca', 'Conta Poupança'),
    ('credito', 'Cartão de Crédito'),
    ('debito', 'Cartão de Débito'),
    ('alimentacao', 'Cartão Alimentação'),
]

THEME_CHOICES = [
    ('light', 'Modo Claro'),
    ('dark', 'Modo Escuro'),
    ('auto', 'Automático'),
]

# Nova estrutura de instituições financeiras
INSTITUICOES_FINANCEIRAS = {
    "Bancos": [
        ('001', 'Banco do Brasil'),
        ('003', 'Banco da Amazônia'),
        ('004', 'Banco do Nordeste'),
        ('007', 'BNDES'),
        ('010', 'Credicoamo'),
        ('011', 'Credit Suisse Brasil'),
        ('012', 'Banco Inbursa'),
        ('014', 'Natixis Brasil'),
        ('015', 'UBS Brasil'),
        ('016', 'Coop. Créd. Desp. Trânsito'),
        ('017', 'BNY Mellon Brasil'),
        ('018', 'Banco Tricury'),
        ('021', 'Banestes'),
        ('024', 'Banco Bandepe'),
        ('025', 'Banco Alfa'),
        ('029', 'Itaú Consignado'),
        ('033', 'Santander Brasil'),
        ('036', 'Bradesco BBI'),
        ('037', 'Banco do Pará'),
        ('040', 'Banco Cargill'),
        ('041', 'Banrisul'),
        ('047', 'Banese'),
        ('060', 'Confidence Câmbio'),
        ('062', 'Hipercard Banco'),
        ('063', 'Bradescard'),
        ('064', 'Goldman Sachs Brasil'),
        ('065', 'Banco AndBank'),
        ('066', 'Morgan Stanley'),
        ('069', 'Banco Crefisa'),
        ('070', 'BRB'),
        ('074', 'Banco Safra'),
        ('075', 'ABN Amro Brasil'),
        ('076', 'Banco KDB Brasil'),
        ('077', 'Banco Inter'),
        ('078', 'Haitong Brasil'),
        ('079', 'Original Agronegócio'),
        ('080', 'BT Corretora'),
        ('081', 'Bancorbrás'),
        ('082', 'Banco Topázio'),
        ('083', 'Banco da China Brasil'),
        ('084', 'Uniprime Norte PR'),
        ('085', 'Ailos'),
        ('089', 'Cred. Rural Mogiana'),
        ('091', 'CCECM/RS'),
        ('092', 'BRK S.A.'),
        ('093', 'Pólocred'),
        ('094', 'Banco Finaxis'),
        ('095', 'Travelex'),
        ('096', 'Banco B3'),
        ('097', 'CCNB'),
        ('098', 'Credialiança'),
        ('099', 'Uniprime Central'),
        ('104', 'Caixa Econômica'),
        ('107', 'Banco Bocom BBM'),
        ('108', 'PortoCred'),
        ('111', 'Banco Oliveira Trust'),
        ('113', 'Magliano Corretora'),
        ('114', 'CCCE/ES'),
        ('117', 'Advanced Câmbio'),
        ('119', 'Western Union Brasil'),
        ('120', 'Banco Rodobens'),
        ('121', 'Banco Agibank'),
        ('122', 'Bradesco BERJ'),
        ('124', 'Woori Bank Brasil'),
        ('125', 'Brasil Plural'),
        ('126', 'BR Partners'),
        ('127', 'Codepe Câmbio'),
        ('128', 'MS Bank'),
        ('129', 'UBS Investimento'),
        ('130', 'Caruana S.A.'),
        ('131', 'Tullett Prebon'),
        ('132', 'ICBC Brasil'),
        ('133', 'Conf. Nac. Cooper. Centrais'),
        ('134', 'BGC Liquidez'),
        ('135', 'Gradual Corretora'),
        ('136', 'Unicred'),
        ('137', 'Multimoney Câmbio'),
        ('138', 'Get Money Câmbio'),
        ('139', 'Intesa Sanpaolo Brasil'),
        ('140', 'Easynvest'),
        ('142', 'Broker Brasil'),
        ('143', 'Treviso Câmbio'),
        ('144', 'Bexs Câmbio'),
        ('145', 'Levycam Corretora'),
        ('146', 'Guitta Câmbio'),
        ('149', 'Facta Financeira'),
        ('157', 'ICAP Brasil'),
        ('159', 'Casa do Crédito'),
        ('163', 'Commerzbank Brasil'),
        ('169', 'Banco Olé Bonsucesso'),
        ('173', 'BRL Trust'),
        ('174', 'Pernambucanas Financ.'),
        ('177', 'Guide Investimentos'),
        ('180', 'CM Capital Markets'),
        ('182', 'Dacasa Financeira'),
        ('183', 'Socred'),
        ('184', 'Itaú BBA'),
        ('188', 'Ativa Investimentos'),
        ('189', 'HS Financeira'),
        ('190', 'Servicoop'),
        ('191', 'Nova Futura'),
        ('194', 'Parmetal'),
        ('196', 'Fair Câmbio'),
        ('197', 'Stone Pagamentos'),
        ('204', 'Bradesco Cartões'),
        ('208', 'BTG Pactual'),
        ('212', 'Banco Original'),
        ('213', 'Banco Arbi'),
        ('217', 'John Deere'),
        ('218', 'Banco BS2'),
        ('222', 'Credit Agrícole Brasil'),
        ('224', 'Banco Fibra'),
        ('233', 'Banco Cifra'),
        ('237', 'Bradesco'),
        ('241', 'Banco Classico'),
        ('243', 'Banco Máxima'),
        ('246', 'ABC Brasil'),
        ('249', 'Investcred Unibanco'),
        ('250', 'BCV'),
        ('253', 'Bexs Corretora'),
        ('254', 'Paraná Banco'),
        ('259', 'Banco Modal'),
        ('260', 'Nubank'),
        ('265', 'Banco Fator'),
        ('266', 'Banco Cédula'),
        ('268', 'Barigui'),
        ('269', 'HSBC Investimento'),
        ('270', 'Sagitur Câmbio'),
        ('271', 'IB Corretora'),
        ('272', 'AGK Câmbio'),
        ('273', 'CCR São Miguel Oeste'),
        ('274', 'Money Plus'),
        ('276', 'Senff'),
        ('278', 'Genial Investimentos'),
        ('279', 'CCR Primavera do Leste'),
        ('280', 'Avista'),
        ('281', 'Coopavel'),
        ('283', 'RB Capital'),
        ('285', 'Frente Câmbio'),
        ('286', 'CCR Ouro Sul'),
        ('288', 'Carol DTVM'),
        ('289', 'EFX Câmbio'),
        ('290', 'Pago Seguro'),
        ('292', 'BS2 DTVM'),
        ('293', 'Lastro RDV'),
        ('296', 'Vision Câmbio'),
        ('298', 'Vips Câmbio'),
        ('299', 'Sorocred'),
        ('300', 'Banco Nacion Argentina'),
        ('301', 'BPP IP'),
        ('306', 'Portopar DTVM'),
        ('307', 'Terra Investimentos'),
        ('309', 'CAMBIONET'),
        ('310', 'VORTX DTVM'),
        ('311', 'Dourada Câmbio'),
        ('312', 'HSCM'),
        ('313', 'Amazônia Câmbio'),
        ('315', 'PI DTVM'),
        ('318', 'Banco BMG'),
        ('319', 'OM DTVM'),
        ('320', 'China Construction Bank'),
        ('321', 'Crefaz'),
        ('322', 'CCR Abelardo Luz'),
        ('323', 'Mercado Pago'),
        ('324', 'Cartos'),
        ('325', 'Órama DTVM'),
        ('326', 'Parati'),
        ('329', 'Qi Sociedade'),
        ('330', 'Banco Bari'),
        ('331', 'Fram Capital'),
        ('332', 'Acesso Pagamentos'),
        ('335', 'Banco Digio'),
        ('336', 'C6 Bank'),
        ('340', 'Super Pagamentos'),
        ('341', 'Itaú'),
        ('342', 'Creditas'),
        ('343', 'FFA'),
        ('348', 'XP Investimentos'),
        ('349', 'AL5'),
        ('350', 'CCR Peq. Agricultores'),
        ('352', 'Torra Corretora'),
        ('354', 'Necton Investimentos'),
        ('355', 'Ótimo'),
        ('358', 'Mercantil do Brasil'),
        ('359', 'Zema'),
        ('360', 'Trinus Capital'),
        ('362', 'Cielo'),
        ('363', 'Singulare'),
        ('364', 'Gerencianet'),
        ('365', 'Solidus'),
        ('366', 'Societe Generale'),
        ('367', 'Vitreo DTVM'),
        ('368', 'Banco CSF'),
        ('370', 'Mizuho Brasil'),
        ('371', 'Warren'),
        ('373', 'UP.P'),
        ('374', 'Realize'),
        ('376', 'JP Morgan'),
        ('377', 'MS Sociedade'),
        ('378', 'BBC'),
        ('379', 'Cooperforte'),
        ('380', 'PicPay'),
        ('381', 'Mercedes-Benz'),
        ('382', 'Fidúcia'),
        ('383', 'BoletoBancário'),
        ('384', 'Global Finanças'),
        ('385', 'CCR Ibiam'),
        ('386', 'Nu Financeira'),
        ('387', 'Toyota Brasil'),
        ('388', 'Original Agronegócio'),
        ('389', 'Mercantil Brasil'),
        ('390', 'GM'),
        ('391', 'CCR Palmitos'),
        ('392', 'Volkswagen'),
        ('393', 'Honda'),
        ('394', 'Bradesco Financiamentos'),
        ('395', 'CCR Ouro'),
        ('396', 'Hub Pagamentos'),
        ('397', 'Listo'),
        ('398', 'Ideal Corretora'),
        ('399', 'Kirton Bank'),
        ('626', 'C6 Consignado'),
        ('630', 'Letsbank'),
        ('633', 'Rendimento'),
        ('634', 'Triângulo'),
        ('637', 'Sofisa'),
        ('643', 'Pine'),
        ('652', 'Itaú Holding'),
        ('653', 'Voiter'),
        ('654', 'Digimais'),
        ('655', 'Votorantim'),
        ('707', 'Daycoval'),
        ('712', 'Ourinvest'),
        ('739', 'Cetelem'),
        ('741', 'Ribeirão Preto'),
        ('743', 'Semear'),
        ('745', 'Citibank'),
        ('746', 'Modal'),
        ('747', 'Rabobank'),
        ('748', 'Sicredi'),
        ('751', 'Scotiabank'),
        ('752', 'BNP Paribas'),
        ('753', 'Novo Banco Continental'),
        ('754', 'Banco Sistema'),
        ('755', 'Bank of America'),
        ('756', 'Sicoob'),
        ('757', 'KEB Hana Brasil'),
    ],
    
    "Cartoes de Credito": [
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
        ('AMEX', 'American Express'),
        ('ELO', 'Elo'),
        ('HIPERCARD', 'Hipercard'),
        ('DINERS', 'Diners Club'),
        ('DISCOVER', 'Discover'),
        ('JCB', 'JCB'),
        ('AURA', 'Aura'),
        ('CABAL', 'Cabal'),
        ('BANESCARD', 'Banescard'),
        ('CREDSYSTEM', 'Credsystem'),
        ('CREDZ', 'Credz'),
        ('FORTBRASIL', 'FortBrasil'),
        ('GRENCARD', 'Grencard'),
        ('PERSONALCARD', 'PersonalCard'),
        ('POLICARD', 'Policard'),
        ('SOROCRED', 'Sorocred'),
        ('VEROCHEQUE', 'Verocheque'),
        ('CREDISHOP', 'Credishop'),
        ('AGICARD', 'Agicard'),
        ('AVISTA', 'Avista'),
        ('CARDOBOM', 'Cardobom'),
        ('UPBRASIL', 'UpBrasil'),
        ('BIGCARD', 'BigCard'),
    ],
    
    "Cartoes de Alimentacao": [
        ('VALECARD', 'Valecard'),
        ('RAIO', 'Raio'),
        ('ALELO', 'Alelo'),
        ('SODEXO', 'Sodexo'),
        ('TICKET', 'Ticket'),
        ('VR', 'VR'),
        ('BANESCARD', 'Banescard'),
        ('GREENCARD', 'Green Card'),
        ('UP', 'UP'),
        ('PLURECARD', 'Plurecard'),
        ('VEROCARD', 'Verocard'),
        ('CABAL', 'Cabal'),
        ('GOODCARD', 'Goodcard'),
        ('FLEX', 'Flex'),
        ('SUPERCARD', 'Supercard'),
        ('FACILCARD', 'Facilcard'),
        ('PERSONALCARD', 'PersonalCard'),
        ('NUTRICASH', 'Nutricash'),
        ('MAISCARD', 'Maiscard'),
        ('FESTACARD', 'Festacard'),
        ('QUALICARD', 'Qualicard'),
        ('PESCARD', 'Pescard'),
        ('SOCIALCARD', 'Socialcard'),
        ('REFEICARD', 'Refeicard'),
        ('HORTIFRUTI', 'Hortifruti'),
        ('ACOUGUE', 'Açougue'),
        ('FEIRA', 'Feira'),
    ]
}

# Unifica todas as escolhas de instituições financeiras em uma única lista para BANCO_CHOICES
BANCO_CHOICES = []
for category_choices in INSTITUICOES_FINANCEIRAS.values():
    BANCO_CHOICES.extend(category_choices)


FORMA_RECEBIMENTO_CHOICES = [
    ('dinheiro', 'Dinheiro (Caixa)'),
    ('pix', 'PIX'),
    ('ted_doc', 'TED/DOC'),
    ('cartao', 'Cartão (Crédito/Débito)'),
    ('boleto', 'Boleto'),
    ('outros', 'Outros'),
]

FORMA_PAGAMENTO_CHOICES = [
    ('dinheiro', 'Dinheiro'),
    ('cartao_credito', 'Cartão de Crédito'),
    ('cartao_debito', 'Cartão de Débito'),
    ('pix', 'PIX'),
    ('boleto', 'Boleto'),
    ('cheque', 'Cheque'),
    ('outros', 'Outros'),
]

TIPO_PAGAMENTO_DETALHE_CHOICES = [
    ('avista', 'À vista'),
    ('parcelado', 'Parcelado'),
]

SITUACAO_CHOICES = [
    ('pago', 'Pago'),
    ('pendente', 'Pendente'),
]

FORMA_RECEBIMENTO_CHOICES = [
    ('dinheiro', 'Dinheiro (Caixa)'),
    ('pix', 'PIX'),
    ('ted_doc', 'TED/DOC'),
    ('cartao', 'Cartão (Crédito/Débito)'),
    ('boleto', 'Boleto'),
    ('outros', 'Outros'),
]



# ================================================================
# CATEGORIAS PRINCIPAIS
# ================================================================
CATEGORIA_CHOICES = [
    ('moradia', 'Moradia'),
    ('alimentacao', 'Alimentação'),
    ('transporte', 'Transporte'),
    ('saude', 'Saúde'),
    ('educacao', 'Educação'),
    ('lazer', 'Lazer'),
    ('seguros', 'Seguros'),
    ('pessoais', 'Despesas Pessoais'),
    ('familia', 'Família'),
    ('contas', 'Contas e Serviços'),
    ('investimentos', 'Investimentos'),
    ('impostos', 'Impostos'),
]

# ================================================================
# SUBCATEGORIAS (Formato correto: (valor, label))
# ================================================================
SUBCATEGORIA_CHOICES = [
    # Moradia
    ('moradia_aluguel', 'Aluguel'),
    ('moradia_financiamento', 'Financiamento Imobiliário'),
    ('moradia_condominio', 'Condomínio'),
    ('moradia_iptu', 'IPTU'),
    ('moradia_energia', 'Energia Elétrica'),
    ('moradia_agua', 'Água e Esgoto'),
    ('moradia_gas', 'Gás'),
    ('moradia_internet', 'Internet'),
    ('moradia_manutencao', 'Manutenção/Reparos'),
    
    # Alimentação
    ('alimentacao_supermercado', 'Supermercado'),
    ('alimentacao_hortifruti', 'Hortifruti'),
    ('alimentacao_padaria', 'Padaria'),
    ('alimentacao_restaurante', 'Restaurante'),
    ('alimentacao_lanches', 'Lanches'),
    
    # Transporte
    ('transporte_combustivel', 'Combustível'),
    ('transporte_manutencao', 'Manutenção Veicular'),
    ('transporte_seguro', 'Seguro Veicular'),
    ('transporte_estacionamento', 'Estacionamento'),
    ('transporte_publico', 'Transporte Público'),
    ('transporte_app', 'Táxi/App de Transporte'),
    
    # Saúde
    ('saude_plano', 'Plano de Saúde'),
    ('saude_medicamentos', 'Medicamentos'),
    ('saude_consultas', 'Consultas Médicas'),
    ('saude_exames', 'Exames'),
    ('saude_odontologia', 'Odontologia'),
    
    # Educação
    ('educacao_mensalidade', 'Mensalidade Escolar/Faculdade'),
    ('educacao_cursos', 'Cursos/Treinamentos'),
    ('educacao_materiais', 'Livros/Material Didático'),
    
    # Lazer
    ('lazer_cinema', 'Cinema/Teatro'),
    ('lazer_shows', 'Shows/Eventos'),
    ('lazer_viagens', 'Viagens'),
    ('lazer_entretenimento', 'Salão de Jogos/Entretenimento'),

    # Seguros
    ('seguros_vida', 'Seguro de Vida'),
    ('seguros_residencial', 'Seguro Residencial'),
    ('seguros_viagem', 'Seguro Viagem'),

    # Despesas Pessoais
    ('pessoais_academia', 'Academia/Atividade Física'),
    ('pessoais_estetica', 'Estética/Beleza'),
    ('pessoais_vestuario', 'Vestuário'),
    ('pessoais_calcados', 'Calçados'),
    ('pessoais_acessorios', 'Acessórios'),

    # Família
    ('familia_mesada', 'Mesada para Filhos'),
    ('familia_presentes', 'Presentes'),
    ('familia_pets', 'Cuidados com Pets'),

    # Contas e Serviços
    ('contas_telefone', 'Telefone'),
    ('contas_assinaturas', 'Assinaturas'),
    ('contas_tv', 'TV por Assinatura/Streaming'),

    # Investimentos
    ('investimentos_poupanca', 'Poupança'),
    ('investimentos_fundos', 'Fundos de Investimento'),
    ('investimentos_acoes', 'Ações'),
    ('investimentos_cripto', 'Criptomoedas'),

    # Impostos
    ('impostos_irpf', 'IRPF'),
    ('impostos_inss', 'INSS'),
    ('impostos_taxas', 'Taxas/Tributos'),
]

# ================================================================
# DICIONÁRIO PARA MAPEAR SUBCATEGORIAS → CATEGORIAS
# (Para uso no JavaScript)
# ================================================================
SUBCATEGORIA_PARA_CATEGORIA = {
    # Moradia
    'moradia_aluguel': 'moradia',
    'moradia_financiamento': 'moradia',
    'moradia_condominio': 'moradia',
    'moradia_iptu': 'moradia',
    'moradia_energia': 'moradia',
    'moradia_agua': 'moradia',
    'moradia_gas': 'moradia',
    'moradia_internet': 'moradia',
    'moradia_manutencao': 'moradia',
    
    # Alimentação
    'alimentacao_supermercado': 'alimentacao',
    'alimentacao_hortifruti': 'alimentacao',
    'alimentacao_padaria': 'alimentacao',
    'alimentacao_restaurante': 'alimentacao',
    'alimentacao_lanches': 'alimentacao',
    
    # Transporte
    'transporte_combustivel': 'transporte',
    'transporte_manutencao': 'transporte',
    'transporte_seguro': 'transporte',
    'transporte_estacionamento': 'transporte',
    'transporte_publico': 'transporte',
    'transporte_app': 'transporte',
    
    # Saúde
    'saude_plano': 'saude',
    'saude_medicamentos': 'saude',
    'saude_consultas': 'saue',
    'saude_exames': 'saude',
    'saude_odontologia': 'saude',
    
    # Educação
    'educacao_mensalidade': 'educacao',
    'educacao_cursos': 'educacao',
    'educacao_materiais': 'educacao',
    
    # Lazer
    'lazer_cinema': 'lazer',
    'lazer_shows': 'lazer',
    'lazer_viagens': 'lazer',
    'lazer_entretenimento': 'lazer',

    # Seguros
    'seguros_vida': 'seguros',
    'seguros_residencial': 'seguros',
    'seguros_viagem': 'seguros',

    # Despesas Pessoais
    'pessoais_academia': 'pessoais',
    'pessoais_estetica': 'pessoais',
    'pessoais_vestuario': 'pessoais',
    'pessoais_calcados': 'pessoais',
    'pessoais_acessorios': 'pessoais',

    # Família
    'familia_mesada': 'familia',
    'familia_presentes': 'familia',
    'familia_pets': 'familia',

    # Contas e Serviços
    'contas_telefone': 'contas',
    'contas_assinaturas': 'contas',
    'contas_tv': 'contas',

    # Investimentos
    'investimentos_poupanca': 'investimentos',
    'investimentos_fundos': 'investimentos',
    'investimentos_acoes': 'investimentos',
    'investimentos_cripto': 'investimentos',

    # Impostos
    'impostos_irpf': 'impostos',
    'impostos_inss': 'impostos',
    'impostos_taxas': 'impostos',
}


FORMA_PAGAMENTO_CHOICES = [
    ('dinheiro', 'Dinheiro'),
    ('cartao_credito', 'Cartão de Crédito'),
    ('cartao_debito', 'Cartão de Débito'),
    ('pix', 'PIX'),
    ('boleto', 'Boleto'),
    ('cheque', 'Cheque'),
    ('outros', 'Outros'),
]

TIPO_PAGAMENTO_DETALHE_CHOICES = [
    ('avista', 'À vista'),
    ('parcelado', 'Parcelado'),
]

SITUACAO_CHOICES = [
    ('pago', 'Pago'),
    ('pendente', 'Pendente'),
]

PERIODICIDADE_CHOICES = [
    ('unica', 'Única'),
    ('diaria', 'Diária'),
    ('semanal', 'Semanal'),
    ('mensal', 'Mensal'),
    ('anual', 'Anual'),
]


# Nova lista de choices para o tipo de operação de empréstimos
TIPO_OPERACAO_CHOICES = [
        ('SAQUE_ANIVERSARIO', 'Saque Aniversário FGTS'),
        ('ANTECIPACAO_13', 'Antecipação do 13º Salário'),
        ('CREDITO_CONSIGNADO', 'Crédito Consignado'),
        
        ('emprestimo_pessoal', 'Empréstimo Pessoal'),
        ('emprestimo_consignado', 'Empréstimo Consignado'),
        ('emprestimo_cartao_consignado', 'Empréstimo Cartão Consignado'),
        ('financiamento_veiculo', 'Financiamento de Veículo'),
        ('financiamento_imobiliario', 'Financiamento Imobiliário'),
        ('credito_rural', 'Crédito Rural'),
        ('outros', 'Outros'),
]



# ================================================================
# FUNÇÕES ÚTEIS
# ================================================================

def get_categoria_display(codigo):
    """Retorna o nome da categoria baseado no código"""
    return dict(CATEGORIA_CHOICES).get(codigo, 'Sem Categoria')

def get_subcategoria_display(codigo):
    """Retorna o nome da subcategoria baseado no código"""
    return dict(SUBCATEGORIA_CHOICES).get(codigo, '')

def get_subcategorias_por_categoria(categoria):
    """Retorna todas as subcategorias de uma categoria específica"""
    return [(codigo, nome) for codigo, nome in SUBCATEGORIA_CHOICES 
            if SUBCATEGORIA_PARA_CATEGORIA.get(codigo) == categoria]

def validar_categoria_subcategoria(categoria, subcategoria):
    """Valida se a subcategoria pertence à categoria"""
    if not categoria or not subcategoria:
        return True
    return SUBCATEGORIA_PARA_CATEGORIA.get(subcategoria) == categoria