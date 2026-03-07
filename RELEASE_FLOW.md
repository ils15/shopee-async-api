# Guia de Desenvolvimento e Release — shopee-async-api

> Documento interno.

---

## Visão Geral do Fluxo

```
feature/fix branch
       │
       ▼  PR revisado
    develop  ──────────────────────────────────────────────────────► testes CI
       │
       ▼  PR revisado + CHANGELOG preenchido
    master   ──► CI bump de versão ──► build ──► PyPI ──► commit chore(release)
```

---

## Dia a Dia: Desenvolvendo uma Feature ou Fix

```bash
# 1. Partir sempre do develop atualizado
git checkout develop
git pull origin develop

# 2. Criar branch descritiva
git checkout -b feat/nome-da-feature
# ou: fix/descricao-do-bug, docs/ajuste-readme, refactor/nome

# 3. Desenvolver, rodar testes localmente
python -m pytest tests/ -q

# 4. Documentar em CHANGELOG.md na seção [Unreleased]
# (obrigatório antes de abrir PR para master)

# 5. Push e abrir PR -> develop
git push origin feat/nome-da-feature
# Abrir PR no GitHub: feat/nome-da-feature → develop
```

---

## Publicando uma Nova Versão (develop → master)

```bash
# Antes de abrir o PR develop → master, garantir:
# ✅ Todos os testes passando em develop
# ✅ CHANGELOG.md com [Unreleased] preenchido
# ✅ Mensagem do PR seguindo Conventional Commits (define o bump)

# Abrir PR no GitHub: develop → master
# Após aprovação: fazer merge
# O CI cuida do resto automaticamente
```

---

## Regra de Bump de Versão Semântica

O bump é detectado automaticamente pela mensagem do **título do PR** (ou commit de merge):

| Mensagem começa com | Bump | Exemplo |
|---|---|---|
| `feat!:` ou contém `breaking change` | **major** `X.0.0` | `1.0.0 → 2.0.0` |
| `feat:` ou `feat(...)` | **minor** `0.X.0` | `1.0.0 → 1.1.0` |
| `fix:`, `refactor:`, `perf:` | **patch** `0.0.X` | `1.0.0 → 1.0.1` |
| qualquer outro tipo | **patch** | — |
| `chore(release):` | nenhum (evita loop) | — |

---

## O que o Workflow Faz Automaticamente

Ao detectar push no `master`, o pipeline `publish.yml` executa:

1. **Testes** — `pytest tests/ -q` na matriz Python 3.9–3.12
2. **Bump de versão** — `scripts/bump_version.py` atualiza `pyproject.toml` e `__init__.py`
3. **Changelog** — `scripts/finalize_changelog.py` converte `[Unreleased]` → `[X.Y.Z] - AAAA-MM-DD`
4. **Validação** — `python -m build && twine check dist/*`
5. **Publicação** — `twine upload` no PyPI (se versão ainda não existir)
6. **Commit de release** — `chore(release): vX.Y.Z [skip ci]` commitado de volta no master

---

## Checklist Pré-Release

- [ ] Branch `develop` com testes passando (`pytest tests/ -q`)
- [ ] `CHANGELOG.md` com entradas em `## [Unreleased]`
- [ ] Título do PR no padrão Conventional Commits
- [ ] Secret `PYPI_API_TOKEN` configurado no GitHub (`Settings → Secrets → Actions`)
- [ ] PR `develop → master` aprovado

---

## Configuração do Secret no GitHub

```
GitHub → Settings → Secrets and variables → Actions → New repository secret

Nome:  PYPI_API_TOKEN
Valor: pypi-AgEIcHl...  (token gerado em pypi.org/manage/account/token/)
```

---

## Sincronizando develop com master após Release

Após o CI commitar `chore(release)` no master, manter o develop atualizado:

```bash
git checkout develop
git pull origin develop
git merge origin/master   # traz o chore(release) commit
git push origin develop
```

---

## Troubleshooting

| Problema | Causa Provável | Solução |
|---|---|---|
| Release não disparou | Push não foi no `master` | Verificar branch alvo do merge |
| Versão já existe no PyPI | Bump não ocorreu / versão duplicate | Verificar logs em Actions → Publish |
| `twine upload` falhou 403 | Token expirado ou inválido | Regenerar token no PyPI e atualizar secret |
| Testes falhando no CI | Regressão no código | Corrigir em branch, abrir novo PR |
| Loop de release | Commit sem `[skip ci]` | O `chore(release):` prefix evita o loop automaticamente |
| develop desatualizado | CI commitou no master | Rodar `git merge origin/master` no develop |

