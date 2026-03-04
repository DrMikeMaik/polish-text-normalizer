# polish-text-normalizer

Converts Polish text into its spoken form. Numbers, currencies, dates, times, abbreviations, Roman numerals, phone numbers, emails, URLs, and special characters — all expanded into natural Polish words with correct grammar (cases, genders, plural forms).

**Pure Python. Zero dependencies. Just regex and grammar rules.**

Built for TTS preprocessing, but useful anywhere you need Polish text in spoken form.

## Installation

```bash
pip install polish-text-normalizer
```

Or from source:

```bash
git clone https://github.com/clawdia-bot/polish-text-normalizer.git
cd polish-text-normalizer
pip install .
```

## Usage

```python
from polish_text_normalizer import normalize

normalize("Dr Nowak, ul. Długa 15, godz. 8-16.")
# → "doktor Nowak, ulica Długa piętnaście, godziny od osiem do szesnaście."

normalize("Cena: 5,99 zł za sztukę, tj. ok. $2.")
# → "Cena: pięć złotych dziewięćdziesiąt dziewięć groszy za sztukę, to jest około dwa dolary."

normalize("Jan III Sobieski rządził w XVII wieku.")
# → "Jan trzeci Sobieski rządził w siedemnastym wieku."

normalize("Spotkanie 14:00-15:30 w sali 5.")
# → "Spotkanie czternasta zero zero do piętnastu trzydzieści w sali pięć."
```

## Modules

The normalizer chains these steps in order (order matters — each step's output feeds the next):

| Module | What it does |
|--------|-------------|
| `emails_urls_pl` | `jan@x.pl` → `jan małpa x kropka pl` |
| `abbreviations_pl` | `dr` → `doktor`, `np.` → `na przykład` (80+ abbreviations) |
| `currency_pl` | `5,99 zł` → `pięć złotych dziewięćdziesiąt dziewięć groszy` (PLN/EUR/USD/GBP/CHF/CZK) |
| `roman_numerals_pl` | `XVII wiek` → `siedemnasty wiek` (context-aware: centuries, monarchs) |
| `dates_pl` | `27.02.2026` → `dwudziestego siódmego lutego dwa tysiące dwudziestego szóstego` |
| `time_pl` | `13:45` → `trzynasta czterdzieści pięć` (feminine ordinals, time ranges) |
| `phone_numbers_pl` | `512 345 678` → `pięć jeden dwa, trzy cztery pięć, sześć siedem osiem` |
| `ranges_pl` | `8-16` → `od osiem do szesnaście` (hour-context-aware) |
| `special_chars_pl` | `§ 5`, `20°C`, `→`, math operators, brackets, ©, ®, ™ |
| `num2words_pl` | `42` → `czterdzieści dwa` (cardinals, ordinals, decimals, percentages) |

## Individual modules

Each module is also importable on its own:

```python
from polish_text_normalizer.currency_pl import expand_currencies
from polish_text_normalizer.num2words_pl import number_to_words

expand_currencies("5,99 zł")
# → "pięć złotych dziewięćdziesiąt dziewięć groszy"

number_to_words(42)
# → "czterdzieści dwa"
```

## Tests

```bash
pip install pytest
python -m pytest tests/
```

310 tests covering all modules plus integration tests for pipeline ordering edge cases.

## License

MIT
