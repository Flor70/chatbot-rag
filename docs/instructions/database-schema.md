# Esquema do Banco de Dados - Chatbot para Aulas

## Visão Geral

Este documento descreve o esquema simplificado do banco de dados para o protótipo do chatbot de aulas. O banco de dados será hospedado no Supabase e consiste em duas tabelas que armazenam informações sobre os cursos e suas respectivas aulas com transcrições.

## Tabelas

### 1. `courses` (Cursos)

Esta tabela armazena informações gerais sobre os cursos.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | Identificador único do curso (chave primária) |
| `pilar` | TEXT | Nome do pilar/área de conhecimento |
| `tipo` | TEXT | Tipo do curso |
| `nome` | TEXT | Nome do curso |
| `created_at` | TIMESTAMP | Data e hora de criação do registro |

### 2. `lessons` (Aulas)

Esta tabela armazena as aulas e suas transcrições, mantendo a referência ao curso.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | UUID | Identificador único da aula (chave primária) |
| `course_id` | UUID | Referência ao curso correspondente (chave estrangeira) |
| `modulo` | TEXT | Nome do módulo ao qual a aula pertence |
| `nome` | TEXT | Nome da aula |
| `youtube_link` | TEXT | Link do vídeo no YouTube |
| `transcription` | TEXT | Texto completo da transcrição da aula |
| `video_summary` | TEXT | Resumo do conteúdo do vídeo |
| `created_at` | TIMESTAMP | Data e hora de criação do registro |

## Relacionamentos

- Um curso pode ter várias aulas (`courses` 1:N `lessons`)

## Script SQL de Criação

```sql
-- Criação da tabela de cursos
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pilar TEXT NOT NULL,
    tipo TEXT NOT NULL,
    nome TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(pilar, tipo, nome)
);

-- Criação da tabela de aulas
CREATE TABLE lessons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    modulo TEXT NOT NULL,
    nome TEXT NOT NULL,
    youtube_link TEXT,
    transcription TEXT,
    video_summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(course_id, modulo, nome)
);

-- Índice para otimizar consultas por course_id
CREATE INDEX idx_lessons_course_id ON lessons(course_id);
```

## Consultas Comuns

### Obter lista de aulas para o dropdown

```sql
SELECT 
    l.id AS lesson_id,
    c.pilar,
    c.tipo,
    c.nome AS curso,
    l.modulo,
    l.nome AS aula
FROM 
    lessons l
JOIN 
    courses c ON l.course_id = c.id
ORDER BY 
    c.pilar, c.tipo, c.nome, l.modulo, l.nome;
```

### Obter transcrição de uma aula específica

```sql
SELECT 
    l.transcription,
    l.video_summary,
    l.nome AS aula_nome,
    l.modulo,
    c.nome AS curso_nome,
    c.pilar,
    c.tipo
FROM 
    lessons l
JOIN 
    courses c ON l.course_id = c.id
WHERE 
    l.id = '[ID_DA_AULA]';
```

## Processo de Importação da Planilha

Para importar os dados da planilha `cursos_classplay.csv` para este esquema:

1. Filtrar a planilha para incluir APENAS as entradas cujo campo `transcription` não está vazio
2. A partir dos dados filtrados, extrair combinações únicas de Pilar, Tipo e Nome para criar registros na tabela `courses`
3. Para cada linha filtrada da planilha, encontrar o `course_id` correspondente e inserir os dados da aula na tabela `lessons`

## Observações

1. Esta estrutura simplificada em duas tabelas mantém todos os metadados necessários enquanto prioriza a simplicidade para o protótipo.

2. Os campos essenciais para a funcionalidade do chatbot são o `id` da aula (para seleção no dropdown) e a `transcription` (para fornecer contexto ao agente).

3. A restrição de unicidade na tabela `courses` (pilar, tipo, nome) e na tabela `lessons` (course_id, modulo, nome) garante que não haja duplicação de dados durante a importação.

4. Para o propósito deste protótipo, priorizamos a simplicidade sobre a normalização completa do banco de dados.