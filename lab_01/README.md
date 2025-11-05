# Lab 01 – FastAPI + SQLAlchemy + Pydantic

REST API dla zarządzania produktami z walidacją nazw, cen, ilości i dynamiczną listą fraz zabronionych.
Dane inicjalizowane automatycznie przy pierwszym uruchomieniu aplikacji (seed w SQLite).

---
## Konfiguracja
Wymagania: Python ≥ 3.13, Poetry.

Struktura projektu:
```
lab_01/
├─ src/lab_01/
│ ├─ main.py
│ ├─ database.py
│ ├─ models.py
│ ├─ schemas.py
│ ├─ services.py
│ ├─ repositories.py
│ ├─ seeds.py
│ └─ routers/
│ ├─ products.py
│ └─ forbidden.py
├─ pyproject.toml
└─ lab01.db (tworzy się automatycznie przy pierwszym uruchomieniu)
```


---
## Uruchomienie
1. Zainstaluj zależności:
```
poetry install
```
2. Uruchom w trybie developerskim (autoreload):
```
poetry run lab01-dev
```
- przy pierwszym starcie utworzy się `lab01.db` i zainicjalizuje tabele przykłądowymi danymi


Aplikacja: http://127.0.0.1:8000  
Swagger: http://127.0.0.1:8000/docs

---
## Zasady walidacji
- Nazwa: 3–20 znaków, tylko litery i cyfry, unikalna, nie może zawierać żadnej frazy z listy zabronionych (porównanie case-insensitive, substring).
- Kategoria: jedna z: electronics, books, clothing.
- Cena (reguły wg kategorii):
  - electronics: 50.0 — 50000.0
  - books: 5.0 — 500.0
  - clothing: 10.0 — 5000.0
- Ilość: integer ≥ 0
- Historia: każda operacja create/update/delete rejestruje snapshot (JSON) + timestamp + typ operacji.

---
## Endpointy

### Produkty `/api/products`
- `POST /api/products/` — dodaj produkt  
  Body JSON: `{ "name": "...", "category": "books|electronics|clothing", "price": 12.3, "quantity": 5 }`  
  Walidacja: patrz sekcja "Zasady walidacji". Zwraca 201 lub 400/422.
- `GET /api/products/` — lista wszystkich produktów
- `GET /api/products/{id}` — pobierz produkt po id
- `PUT /api/products/{id}` — aktualizuj produkt (pola opcjonalne, te same reguły walidacji)
- `DELETE /api/products/{id}` — usuń produkt
- `GET /api/products/{id}/history` — historia zmian produktu (create/update/delete)

### Frazy zabronione `/api/forbidden`
- `GET /api/forbidden/` — lista fraz
- `POST /api/forbidden/` — dodaj frazę `{ "phrase": "..." }`
- `DELETE /api/forbidden/{id}` — usuń frazę po ID

---
## Dopuszczalne i zabronione operacje
- Dopuszczalne:
  - Tworzenie/edycja/usuwanie produktów spełniających reguły walidacji.
  - Dodawanie/usuwanie fraz zabronionych.
  - Pobieranie historii zmian.
- Zabronione (skutkuje 400/422):
  - Tworzenie/edycja produktu z nazwą zawierającą frazę zabronioną.
  - Tworzenie/edycja produktu z ceną poza zakresem dla danej kategorii.
  - Tworzenie/edycja produktu z niepoprawną nazwą (krótsza niż 3 znaki, niealfanumeryczna).
  - Ustawianie ilości na wartość < 0.

---
## Testy
Uruchom testy:
```
poetry run pytest -q
```
---
## Postman — kolekcja i import
Plik kolekcji: `lab01_api.postman_collection.json`

Import w Postmanie:
1. Otwórz Postman → File → Import.
2. Wybierz plik `lab01_api.postman_collection.json`.
3. Kliknij Import.
4. W lewej kolumnie wybierz zaimportowaną kolekcję.
5. Ustaw zmienną środowiskową `base_url` na `http://127.0.0.1:8000` (lub edytuj URL w requestach).
6. Wyślij requesty.

Przykładowe requesty zawarte w kolekcji:
- Get all products
- Create product
- Get product by ID
- Update product
- Delete product
- Get product history
- Get/Add/Delete forbidden phrases
