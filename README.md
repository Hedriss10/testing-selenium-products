<h1 align="center">Python + Selenium + FastAPI Challenge</h1>

**Descrição**:

O objetivo deste projeto é raspar dados de produtos do site `testing-selenium`. Os produtos são randômicos e não seguem um padrão de quantidade, sendo filtrados apenas por categoria — que é padronizada.  
Este projeto foi desenvolvido como parte de um teste técnico para demonstrar conceitos de desenvolvimento com `Selenium` e `FastAPI`.

---

### Como rodar esse projeto?

#### .venv

Ao clocar o projeto, é necessario criar uma `venv` que é o ambiente virual do `Python`, segue o comando, lembrando que o `namespace` fica da sua preferência:

```sh
python3 -m venv .venv
```


#### **Environments**

Ao clonar o projeto, é necessário criar um arquivo `.env` no diretório principal. Abaixo estão as variáveis de ambiente utilizadas no projeto:

```sh
# URL do site de teste
URL = "https://selenium-html-test.replit.app/"

# Configurações do driver
HEADLES = "--headless"
NO_SANDBOX = "--no-sandbox"
DISABLE_DEV_SHM_USAGE = "--disable-dev-shm-usage"
HUB_SELENIUM = "http://selenium-chrome:4444/wd/hub"

# Threads
WORK_THREAD = 4

# Logs
SELENIUM_TESTING = "testing-selenium"
````

---

#### **Script rápido**

Foi disponibilizado o script `quick-check.sh` para execução completa do projeto, incluindo:

* Build com Docker,
* Extração de dados,
* Execução dos testes e lint do projeto.

```bash
./quick-check.sh
```

---

#### **Notação**:

O filtro `| jq length` foi removido para permitir a visualização da lista de dicionários com os resultados dos produtos raspados:

```sh
curl -s 'http://localhost:8000/scrape?category=Apparel'
```

---

### Tests

Os testes unitários foram implementados com cobertura superior a **70%**, garantindo a confiabilidade do `scraper`.

```textplain
| Arquivo                      | Statements | Missing | Excluded | Coverage |
| ---------------------------- | ---------- | ------- | -------- | -------- |
| `src/__init__.py`            | 0          | 0       | 0        | 100%     |
| `src/automation/__init__.py` | 0          | 0       | 0        | 100%     |
| `src/automation/app.py`      | 25         | 3       | 0        | 88%      |
| `src/builder/__init__.py`    | 0          | 0       | 0        | 100%     |
| `src/builder/pool.py`        | 29         | 13      | 0        | 55%      |
| `src/builder/scraper.py`     | 111        | 20      | 0        | 82%      |
| `src/execute/__init__.py`    | 0          | 0       | 0        | 100%     |
| `src/execute/service.py`     | 31         | 15      | 0        | 52%      |
| `src/models/__init__.py`     | 0          | 0       | 0        | 100%     |
| `src/models/product.py`      | 9          | 0       | 0        | 100%     |
| **Total**                    | **205**    | **51**  | **0**    | **75%**  |
```
