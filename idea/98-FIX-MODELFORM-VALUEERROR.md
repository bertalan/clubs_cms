# 98 - Fix ModelForm ValueError sulle pagine autenticate

## Panoramica

Questo documento descrive la correzione del bug critico `ValueError: ModelForm
has no model class specified` che impediva l'accesso a tutte le pagine
autenticate del progetto ClubCMS (profilo, privacy, notifiche, mutuo soccorso).

Commit: `55e2090` — `fix: resolve ModelForm ValueError on authenticated pages`

---

## 1. Il Problema

### Sintomo

```
ValueError at /it/account/profile/
ModelForm has no model class specified.

File "/app/apps/members/forms.py", line 164, in __init__
    super().__init__(*args, **kwargs)
```

Tutte le pagine sotto `/account/` che richiedono autenticazione restituivano
errore 500.

### Pagine coinvolte

| URL | View | Form |
|-----|------|------|
| `/account/profile/` | `ProfileView` | `ProfileForm` |
| `/account/privacy/` | `PrivacySettingsView` | `PrivacySettingsForm` |
| `/account/notifications/` | `NotificationPrefsView` | `NotificationPreferencesForm` |
| `/account/aid/` | `AidAvailabilityView` | `AidAvailabilityForm` |

---

## 2. Analisi della causa

### Pattern originale (errato)

```python
class ProfileForm(forms.ModelForm):
    class Meta:
        model = None  # set dynamically
        fields = [...]

    def __init__(self, *args, **kwargs):
        if self.Meta.model is None:
            self.Meta.model = _get_user_model()
        super().__init__(*args, **kwargs)
```

### Perche' non funziona

Django usa una **metaclasse** (`ModelFormMetaclass`) che risolve `Meta.model`
al momento della **definizione della classe**, non al momento dell'istanziazione.

Sequenza di esecuzione Django:

1. **Class definition time** — La metaclasse legge `Meta.model = None` e crea
   `_meta.model = None`. Nessun campo del modello viene generato (`fields = {}`)
2. **`__init__()` time** — `self.Meta.model = _get_user_model()` modifica
   l'attributo di classe `Meta`, ma `self._meta.model` (l'oggetto interno
   `ModelFormOptions`) resta `None`
3. **`super().__init__()`** — Django legge `self._meta.model`, trova `None`,
   lancia `ValueError`

Il pattern `model = None` con assegnamento lazy in `__init__` e'
**fondamentalmente incompatibile** con il funzionamento delle ModelForm di Django.

### Primo tentativo (insufficiente)

Invertire l'ordine (`_get_user_model()` prima di `super().__init__()`) non
risolve il problema perche' `self.Meta.model = ...` aggiorna solo l'attributo
della classe `Meta` interna, non l'oggetto `_meta` gia' creato dalla metaclasse.

---

## 3. La Soluzione

### Pattern corretto

```python
from django.contrib.auth import get_user_model

class ProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()  # risolto a class definition time
        fields = [...]
```

`get_user_model()` e' il pattern standard Django per riferire il modello utente.
Viene chiamato al momento della definizione della classe, quando il registry
delle app e' gia' pronto (i form vengono importati dalle view, che vengono
caricate durante il setup degli URL, dopo `django.setup()`).

### Modifiche a `apps/members/forms.py`

| Azione | Dettaglio |
|--------|----------|
| Rimosso | `_get_user_model()` helper function |
| Aggiunto | `from django.contrib.auth import get_user_model` |
| Sostituito | `model = None` → `model = get_user_model()` in 5 form |
| Rimosso | Logic `if self.Meta.model is None` da tutti gli `__init__()` |
| Mantenuto | `__init__()` in form che assegnano label personalizzate |

### Form corretti

1. **`RegistrationForm`** (fallback non-allauth) — rimosso `__init__` per model
2. **`ProfileForm`** — rimosso intero `__init__` (serviva solo per model)
3. **`PrivacySettingsForm`** — rimossa logica model, mantenute label
4. **`NotificationPreferencesForm`** — rimossa logica model, mantenute label
5. **`AidAvailabilityForm`** — rimossa logica model, mantenute label

### Bonus: fix `directory.html`

| Prima | Dopo |
|-------|------|
| `{% url 'account:public_profile' ... %}` | `{% url 'public_profile' ... %}` |

L'URL `public_profile` e' registrato nella root URL conf (`clubcms/urls.py:41`),
non nel namespace `account`. Il template directory causava `NoReverseMatch`.

---

## 4. Verifica

### Test suite

```
181 passed in 24.28s
```

(Rispetto alla sessione precedente: 177 passed + 4 skipped → ora 181 passed,
i test Stripe non vengono piu' skippati in Docker)

### Test end-to-end autenticato (Django test client in Docker)

```
Profile (/it/account/profile/):         200
Privacy (/it/account/privacy/):         200
Notifications (/it/account/notifications/): 200
Aid (/it/account/aid/):                 200
Card (/it/account/card/):              200
Directory (/it/account/directory/):     200
Membership Plans (/it/account/become-member/): 200
Profile (no auth):                      302 → redirect OK
```

### Verifica form fields (ProfileForm)

```python
Form class: ProfileForm
Form model: ClubUser
Form fields: ['first_name', 'last_name', 'display_name', 'phone', 'mobile',
              'birth_date', 'birth_place', 'bio', 'address', 'city',
              'province', 'postal_code', 'country']
```

---

## 5. File modificati

| File | Tipo modifica |
|------|--------------|
| `apps/members/forms.py` | `model = None` → `get_user_model()`, rimossi `__init__` superflui |
| `templates/account/directory.html` | Fix namespace URL `public_profile` |

---

## 6. Lezione appresa

> **Non usare mai `Meta.model = None` in una Django ModelForm.**
>
> La metaclasse `ModelFormMetaclass` risolve il model e genera i campi del form
> durante la definizione della classe. Qualsiasi assegnamento successivo a
> `self.Meta.model` o `self._meta.model` nell'`__init__` e' troppo tardi:
> i campi del form non verranno generati e Django lancera' `ValueError`.
>
> Usare sempre `get_user_model()` o un import diretto nel `Meta.model`.
