# Runner setup for nduworker/nduwork (agent instructions)

You are on Niu's workstation, the machine that already runs the self-hosted
runner for `nduworker/careerlifty` and has Ollama with `qwen3.8:27b`. Your job
is to get the daily **pick-of-the-day** workflow running here and confirm that
www.nduwork.com serves a real pick. Do the steps in order and stop to report if
any check fails.

## Guardrails
- Leave the careerlifty runner and its directory alone. This is a **second**,
  separate runner.
- Never print, log or commit the registration token.
- Don't edit `.github/workflows/pick-of-the-day.yml` or `scripts/pick.py`. If
  something is broken there, report it.
- The repo is public. Step 5 (fork-PR approval) is required, not optional.

## 0. Preconditions
```bash
gh api user --jq .login                                # must be: nduworker
gh api repos/nduworker/nduwork --jq .permissions.admin  # must be: true
ollama list | grep -q 'qwen3.8:27b' && echo model ok
curl -s http://localhost:11434/v1/chat/completions \
  -d '{"model":"qwen3.8:27b","messages":[{"role":"user","content":"say ok"}],"stream":false}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["choices"][0]["message"]["content"][:80])'
command -v python3
```
If `gh` is logged in as a different account, run `gh auth login` and choose
**nduworker**, or ask Niu to. If the model is missing, run `ollama pull qwen3.8:27b`.

## 1. Download the runner
```bash
mkdir -p ~/actions-runner-nduwork && cd ~/actions-runner-nduwork
V=$(gh api repos/actions/runner/releases/latest --jq .tag_name | sed 's/^v//')
F=actions-runner-osx-arm64-$V.tar.gz
curl -fsSLO https://github.com/actions/runner/releases/download/v$V/$F
# Verify the checksum published in the release notes
gh api repos/actions/runner/releases/latest --jq .body | grep -i 'osx-arm64' | grep -oE '[0-9a-f]{64}' | head -1 > expected.sha
[ "$(shasum -a 256 $F | cut -d' ' -f1)" = "$(cat expected.sha)" ] && echo checksum ok || { echo CHECKSUM MISMATCH; exit 1; }
tar xzf $F && rm $F expected.sha
```

## 2. Register the runner
```bash
cd ~/actions-runner-nduwork
TOKEN=$(gh api -X POST repos/nduworker/nduwork/actions/runners/registration-token --jq .token)
./config.sh --unattended --url https://github.com/nduworker/nduwork --token "$TOKEN" \
  --name "$(hostname -s)-nduwork" --labels nduwork --work _work
unset TOKEN
```
The default labels `self-hosted, macOS, ARM64` are added automatically, so
together with `nduwork` they match the workflow's `runs-on`.

## 3. Run it as a service
```bash
cd ~/actions-runner-nduwork
./svc.sh install && ./svc.sh start && ./svc.sh status
```
The service uses the PATH saved in `.path` at config time. Check that `python3`
and `git` resolve with it: `cat .path`. If they don't, fix `.path`, then run
`./svc.sh stop && ./svc.sh start`.

Confirm the runner shows as online:
```bash
gh api repos/nduworker/nduwork/actions/runners --jq '.runners[] | {name, status, labels: [.labels[].name]}'
```

## 4. Repo variable
```bash
gh variable set OLLAMA_MODEL -b 'qwen3.8:27b' -R nduworker/nduwork
```

## 5. Lock down fork PRs (required: public repo + self-hosted runner)
```bash
gh api -X PUT repos/nduworker/nduwork/actions/permissions/fork-pr-contributor-approval \
  -f approval_policy=all_external_contributors
gh api repos/nduworker/nduwork/actions/permissions/fork-pr-contributor-approval
```

## 6. Run the job and verify
Run 35933266304 may still be queued, and it will start once the runner is online.
If it expired, start a new run:
```bash
gh run list -R nduworker/nduwork -w pick-of-the-day.yml -L 3
gh workflow run pick-of-the-day.yml -R nduworker/nduwork --ref main   # only if nothing is queued or running
gh run watch -R nduworker/nduwork $(gh run list -R nduworker/nduwork -w pick-of-the-day.yml -L 1 --json databaseId --jq '.[0].databaseId')
```
Success looks like this:
- The run is green, and `main` has a new commit `chore(pick): <owner/repo>` from github-actions[bot].
- `gh api repos/nduworker/nduwork/contents/pick.json --jq .content | base64 -d` shows `"model": "qwen3.8:27b"` and a 2–3 sentence first-person `summary`.

If the job fails at the LLM step, check that Ollama is running for the service
user and that a request to `localhost:11434` works from inside the service
environment. Don't change the model.

## 7. HTTPS and live site
First, enable Pages. As of 2026-09-23 23:40 UTC the repo showed `has_pages: false`, which is why the browser warns that the connection isn't private.
```bash
gh api repos/nduworker/nduwork --jq .has_pages   # if false:
gh api -X POST repos/nduworker/nduwork/pages -f 'source[branch]=main' -f 'source[path]=/'
gh api -X PUT repos/nduworker/nduwork/pages -f cname=www.nduwork.com
```
Then poll until the certificate is issued (10–60 min):
```bash
gh api repos/nduworker/nduwork/pages --jq '{status, cname, https_enforced, cert: .https_certificate.state}'
```
- When `cert` is `approved`, run `gh api -X PUT repos/nduworker/nduwork/pages -F https_enforced=true`.
- `curl -sI https://www.nduwork.com | grep -i server` should show `GitHub.com`, and the page should show today's pick.
  If this Mac still resolves to Squarespace, run `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`.

## Report back
Report the runner name and status, the run URL and its result, the picked repo
and model from `pick.json`, the fork-PR policy value, and the Pages cert state
with `https_enforced`.
