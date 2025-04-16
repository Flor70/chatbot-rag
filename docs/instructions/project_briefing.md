# Briefing: Protótipo de Chatbot para Responder Perguntas Baseadas em Transcrições de Aulas

## Visão Geral do Projeto

Este projeto consiste no desenvolvimento de um protótipo de chatbot capaz de responder perguntas com base em transcrições de aulas. O sistema permitirá que usuários selecionem uma aula específica e façam perguntas relacionadas ao conteúdo dessa aula, com o chatbot respondendo a partir do contexto da transcrição.

## Objetivos do Projeto

1. Desenvolver um protótipo funcional com ênfase na simplicidade
2. Testar a viabilidade da funcionalidade principal (responder perguntas sobre o conteúdo de aulas)
3. Criar uma base para validação do conceito

## Princípios Norteadores

- **Simplicidade**: Todas as decisões devem priorizar soluções simples e diretas
- **Funcionalidade**: O foco é garantir que o sistema funcione conforme esperado, não em otimizações
- **Prototipagem rápida**: Este é um MVP para validação de conceito, não um produto final

## Tecnologias e Recursos

- **LLM/Agent**: OpenAI SDK para desenvolvimento do agente
  - Framework de código aberto que facilita a construção de agents
  - Permite implementar a lógica de processamento de perguntas e geração de respostas

- **OpenRouter**: Roteador de provedores de LLMs
  - Permite a escolha de diferentes modelos de linguagem
  - Requer apenas uma chave de API do OpenRouter para acesso aos diversos LLMs disponíveis

- **Banco de Dados**: Supabase
  - Armazenamento das informações sobre aulas
  - Armazenamento das transcrições das aulas

- **Frontend**: Interface baseada no template de UI
  - Clone do repositório github.com/ChristophHandschuh/chatbot-ui
  - Adaptação para inclusão de seletor de aulas

## Estrutura do Projeto

O projeto será desenvolvido em três etapas principais:

1. **Etapa 1**: Criação e configuração do banco de dados
   - Definição do esquema para armazenar aulas e transcrições
   - Configuração do projeto no Supabase

2. **Etapa 2**: Desenvolvimento do agente e integração com o banco de dados
   - Utilização do OpenAI SDK para construção do agent
   - Integração com OpenRouter para acesso aos LLMs
   - Conexão com o banco de dados para recuperação das transcrições

3. **Etapa 3**: Desenvolvimento da interface e conexão com o agente e banco de dados
   - Adaptação do template de UI para incluir seletor de aulas
   - Implementação da comunicação entre frontend, agent e banco de dados

## Fluxo de Funcionamento

1. O usuário acessa a aplicação
2. O sistema carrega a lista de aulas disponíveis no dropdown
3. O usuário seleciona uma aula específica
4. O sistema carrega a transcrição da aula selecionada
5. O usuário digita uma pergunta relacionada à aula
6. O sistema envia a pergunta e a transcrição para o agente LLM
7. O agente processa a pergunta considerando o contexto da transcrição
8. A resposta é exibida na interface para o usuário

## Limitações do Protótipo

- **Sem otimização de performance**: Pode haver lentidão no processamento de transcrições muito longas
- **Segurança básica**: Não implementa autenticação ou proteções avançadas
- **Sem persistência de conversas**: Histórico de conversas não é salvo entre sessões
- **UI simplificada**: Interface funcional, mas sem recursos avançados

## Recursos Necessários

- Conta no Supabase
- Chave de API do OpenRouter
- Ambiente de desenvolvimento para React
- Repositório Git para controle de versão

Este briefing serve como visão geral para o desenvolvimento do protótipo, fornecendo uma compreensão de alto nível do projeto. As decisões específicas de implementação, tarefas detalhadas e plano de execução serão definidos em documentos posteriores.