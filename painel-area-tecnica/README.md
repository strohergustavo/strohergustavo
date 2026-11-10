# Painel Área Técnica — Dashboard

Dashboard web para análise de indicadores da área técnica, com conexão direta ao SQL Server (SmartManager).

## Visão Geral

Replica o painel Excel de indicadores técnicos em uma aplicação web interativa com:

- **12 KPIs** com variação mensal (setas ▲/▼)
- **Filtros combinados**: Filial, Técnico, Mês, Segmento, Natureza
- **Parâmetros da query** configuráveis na interface (período, tolerâncias)
- **Gráficos interativos**: barras, roscas, evolução mensal, heatmaps
- **Tabela comparativa por técnico** (12 colunas)
- **Aba Mês a Mês** com grade heatmap

## Stack

| Camada    | Tecnologia                          |
|-----------|-------------------------------------|
| Backend   | Python 3.11 · FastAPI · pymssql     |
| Frontend  | Next.js 14 · React · Tailwind CSS · Recharts |
| Infra     | Docker Compose                      |
| Banco     | SQL Server (externo, via `.env`)    |

## Requisitos

- Docker e Docker Compose
- Acesso a um SQL Server com o banco **SmartManager**

## Início Rápido

### 1. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` com as credenciais do seu SQL Server:

```env
SQL_HOST=192.168.1.100
SQL_PORT=1433
SQL_USER=seu_usuario
SQL_PASSWORD=sua_senha
SQL_DATABASE=SmartManager
```

### 2. Subir os containers

```bash
docker compose up --build
```

### 3. Acessar o painel

Abra [http://localhost:3000](http://localhost:3000) no navegador.

## Como Usar

### Parâmetros da Query (barra superior)

Antes de consultar, configure:

| Parâmetro       | Padrão       | Descrição                                      |
|-----------------|--------------|-------------------------------------------------|
| Data Início     | 2026-05-01   | Início do período de análise                    |
| Data Fim        | 2026-10-31   | Fim do período de análise                       |
| Técnico         | (Todos)      | Filtrar por técnico específico na query SQL      |
| Gap (min)       | 30           | Tolerância para trajeto cliente → cliente        |
| Mín. Atend (min)| 2            | Atendimentos abaixo disso: tempo não considerado |
| Desloc. Máx (min)| 180         | Deslocamento acima disso: atípico                |

Clique em **Consultar** para executar a query no SQL Server.

### Filtros do Painel (após consulta)

Filtram os dados já carregados, sem nova query:

- **Filial** — ex.: Canoas, Ijuí, Indaiatuba
- **Técnico** — nome do técnico
- **Mês** — mês da visita (2026-05 a 2026-10)
- **Segmento** — Soluções de Impressão / Identificação e Automação
- **Natureza** — Campo / Interna / Remota

Todos combinam com "E". Selecionar "(Todos)" remove aquele filtro.

## Seções do Dashboard

### KPIs (cartões)

**Baseados em chamado (1 por OS):**
- Chamados Atendidos · Em Campo · Remotos · Internos

**Baseados em visita:**
- Horas de Deslocamento · Horas no Cliente · Deslocamento Médio · Tempo Médio por Parada

**Qualidade e retornos:**
- % Deslocamento Registrado · % Sem Registro de Saída · Visitas de Retorno · Deslocamentos Atípicos

### Gráficos

- **Top 5 Produtos** — barras empilhadas por segmento
- **Chamados por Segmento** — rosca (Impressão vs Automação)
- **Visitas por Tipo de OS** — com drill-down por produto (filtro próprio)
- **Evolução Mensal** — barras (horas) + linha (% registro)
- **Qualidade do Registro** — rosca com 4 situações
- **Comparativo por Tipo de OS e Segmento** — 4 gráficos de barra
- **Deslocamento por Filial** — 2 gráficos de barra
- **Horas por Técnico** — barras empilhadas (deslocamento vs cliente)
- **% Sem Registro por Técnico** — ranking

### Tabela por Técnico

12 colunas: Visitas, Horas Desloc., Horas Cliente, Desloc. Médio, Parada Média, Desloc./H Cliente, % Registrado, % Sem Registro, Retornos, Horas Retornos, Atípicos.

### Mês a Mês

3 grades heatmap (técnico × mês): Horas de Deslocamento, Horas no Cliente, % Registrado.

## Estrutura do Projeto

```
painel-area-tecnica/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py          # FastAPI — rotas e CORS
│       ├── config.py        # Configuração via env vars
│       ├── database.py      # Pool de conexão SQL Server
│       ├── query.py         # Query SQL parametrizada
│       └── models.py        # Schemas Pydantic
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── app/             # Pages Next.js
        ├── components/      # Componentes React (KPIs, gráficos, filtros)
        ├── hooks/           # useData — fetch + state
        └── lib/             # Cliente API
```

## Lógica de Cálculo

Os KPIs são computados no frontend a partir dos dados brutos retornados pelo backend:

| Indicador               | Regra                                                                 |
|--------------------------|-----------------------------------------------------------------------|
| Chamados Atendidos       | COUNT onde `Chamado Atendido = Sim` e `Linha Única da OS = 1`        |
| Em Campo/Remotos/Internos| Idem, filtrado por Natureza                                          |
| Horas de Deslocamento    | SUM(Tempo de Deslocamento) / 60                                      |
| Horas no Cliente         | SUM(Tempo no Cliente) / 60                                           |
| Deslocamento Médio       | AVG onde Situação = "Registrado" e Atípico = "Não"                   |
| Tempo Médio por Parada   | AVG(Tempo no Cliente) onde Exige Registro = "Sim"                    |
| % Registrado             | Registrados / Total com Exige Registro = "Sim"                       |
| % Sem Registro           | "Sem registro de saída" / Total com Exige Registro = "Sim"           |
| Setas ▲/▼                | Último mês vs penúltimo, mesma lógica do cartão                      |

## Notas

- **Visita × Chamado**: uma OS pode ter várias visitas. KPIs de chamado contam 1× por OS; KPIs de visita contam toda linha.
- **Mês da visita × Mês de encerramento**: chamados atendidos usam mês de encerramento; gráficos de evolução usam mês da visita.
- **Comparativo por técnico**: não aplica o filtro de técnico sobre si mesmo.
- **Evolução mensal**: ignora o filtro de mês (mostra todos os meses).

## Licença

Uso interno — Ricohpel.
