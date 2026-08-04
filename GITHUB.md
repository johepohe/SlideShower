# GitHub – minnesanteckning

## Logga in

Kontrollera först om GitHub CLI redan är inloggad:

```bash
gh auth status
```

Om du inte är inloggad:

```bash
gh auth login --hostname github.com --git-protocol https --web
```

Svara `Y`, öppna länken som visas och ange engångskoden. Ett Chrome-meddelande
om `Crash Reports` kan ignoreras om GitHub-sidan ändå öppnas.

Om systemets nyckelring inte kan spara inloggningen kan detta användas som
reservlösning:

```bash
gh auth login --hostname github.com --git-protocol https --web --insecure-storage
```

Det sparar GitHub-token okrypterad lokalt, så använd helst det vanliga
kommandot när det fungerar. Lägg aldrig tokens eller engångskoder i Git.

## Publicera ändringar

Kör i projektmappen:

```bash
git status
git add .
git commit -m "Kort beskrivning av ändringen"
git push
```

Kontrollera efteråt:

```bash
git status
```

När allt är synkroniserat står det att `main` följer `origin/main` och att
arbetskatalogen är ren.

## Hämta ändringar från GitHub

Om repot har ändrats från en annan dator:

```bash
git pull
```

Projektets publika repo finns på:

<https://github.com/johepohe/SlideShower>
