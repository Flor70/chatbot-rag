chatbot-aulas/
│
├── README.md                           # Documentação geral do projeto
├── pyproject.toml                      # Configuração do Poetry e dependências Python
├── .env.example                        # Template de variáveis de ambiente
│
├── frontend/                           # Interface do usuário
│   ├── public/                         # Arquivos estáticos
│   ├── src/
│   │   ├── App.jsx                     # Componente principal
│   │   ├── components/                 # Componentes React reutilizáveis
│   │   │   ├── ChatInterface.jsx       # Interface de chat
│   │   │   └── ClassSelector.jsx       # Dropdown de seleção de aulas
│   │   ├── services/                   # Serviços de comunicação
│   │   │   ├── api.js                  # Funções para comunicação com o backend
│   │   │   └── supabase.js             # Cliente Supabase para o frontend
│   │   └── index.jsx                   # Ponto de entrada da aplicação
│   ├── .env.example                    # Template de variáveis de ambiente para o frontend
│   └── package.json                    # Dependências do frontend
│
├── backend/                            # Serviços de backend
│   ├── src/                            # Implementação JavaScript do backend
│   │   ├── index.js                    # Ponto de entrada do servidor
│   │   ├── routes/                     # Rotas da API
│   │   │   └── chat.js                 # Endpoints do chat
│   │   ├── services/                   # Serviços do backend
│   │   │   ├── agent.js                # Implementação do agente (OpenAI SDK)
│   │   │   └── database.js             # Funções para acesso ao Supabase
│   │   └── config/                     # Configurações
│   │       └── environment.js          # Variáveis de ambiente
│   ├── package.json                    # Dependências do backend JavaScript
│   │
│   ├── python_modules/                 # Implementação Python do backend
│   │   ├── README.md                   # Documentação do módulo Python
│   │   ├── src/                        # Código fonte Python
│   │   │   ├── __init__.py             # Inicialização do módulo Python
│   │   │   ├── main.py                 # Ponto de entrada para teste do ambiente
│   │   │   ├── config/                 # Configurações
│   │   │   │   ├── __init__.py         # Inicialização do módulo de configuração
│   │   │   │   └── environment.py      # Gerenciamento de variáveis de ambiente
│   │   │   ├── services/               # Serviços do backend
│   │   │   │   ├── __init__.py         # Inicialização do módulo de serviços
│   │   │   │   └── database.py         # Cliente Supabase e funções de acesso ao banco
│   │   │   ├── migrations/             # Scripts SQL para criação do banco de dados
│   │   │   │   ├── README.md           # Documentação sobre os scripts de migração
│   │   │   │   ├── 001_initial_schema.sql # Script SQL para criação inicial das tabelas
│   │   │   │   └── apply_migrations.py # Script Python para aplicação das migrações
│   │   │   └── tools/                  # Ferramentas utilitárias
│   │   │       ├── __init__.py         # Inicialização do módulo de ferramentas
│   │   │       ├── README.md           # Documentação do diretório de ferramentas
│   │   │       ├── data_processor.py   # Processamento de dados CSV
│   │   │       └── data_importer.py    # Importação de dados para Supabase
│   │   ├── tests/                      # Testes unitários
│   │   │   ├── __init__.py             # Inicialização do módulo de testes
│   │   │   ├── test_environment.py     # Testes para validação do ambiente
│   │   │   ├── test_migration_sql.py   # Testes para validação da sintaxe SQL
│   │   │   └── test_data_processor.py  # Testes para processamento de dados
│   │   ├── data_importer.py            # Script wrapper para importação de dados
│   │   ├── execute_migration.py        # Script para execução da migração SQL
│   │   └── verify_tables.py            # Script para verificação das tabelas no Supabase
│
├── data/                               # Dados para o projeto
│   └── processed/                      # Dados processados para importação
│       ├── courses.json                # Dados processados de cursos
│       └── lessons.json                # Dados processados de aulas
│
├── tasks/                              # Gestão de tarefas do projeto
│   ├── tasks.json                      # Definição estruturada das tarefas
│   ├── task_001.txt                    # Detalhes da tarefa 1
│   ├── task_002.txt                    # Detalhes da tarefa 2
│   │   // ... outros arquivos de tarefas
│   ├── task_001_log.txt                # Log de implementação da tarefa 1
│   ├── task_002_log.txt                # Log de implementação da tarefa 2
│   │   // ... outros logs de tarefas
│   └── database_plan_logs.txt          # Documento de onboarding do banco de dados
│
└── docs/                               # Documentação
    └── instructions/                   # Instruções do projeto
        ├── project_briefing.md         # Briefing do projeto
        ├── database-schema.md          # Esquema do banco de dados
        └── project_structure.md        # Estrutura do projeto (este arquivo)