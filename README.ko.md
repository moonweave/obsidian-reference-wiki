# Obsidian Research Wiki: Reference

한국어 | [English](README.md)

> 출처와의 연결을 유지하면서 논문을 추적 가능한 지식으로 정리합니다.

`Obsidian Research Wiki: Reference`는 Obsidian에 근거 중심 문헌 체계를
구축하는 독립형 Codex Skill입니다. 검토한 논문 노트, 검색 가능한 전문
파생본, 재사용 가능한 지식 노트를 서로 구분합니다. 따라서 짧은 요약이
정본 PDF, 웹페이지 또는 Zotero 항목을 대신하지 않습니다.

새 Vault와 기존 Vault에서 모두 사용할 수 있으며, 파일을 만들기 전에 전체
적용 설계안(Blueprint)을 제안합니다. 사용자가 명시적으로 승인하지 않는 한
기존 노트, `.obsidian` 설정, 플러그인, PDF와 Zotero 라이브러리를 변경하지
않습니다.

## 빠른 시작

노트만 정리할 때 필요한 것은 Git과 Codex뿐입니다.

macOS 또는 Linux:

```bash
mkdir -p "$HOME/.codex/skills"
git clone https://github.com/moonweave/obsidian-reference-wiki.git \
  "$HOME/.codex/skills/obsidian-research-wiki-reference"
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME/.codex/skills" | Out-Null
git clone https://github.com/moonweave/obsidian-reference-wiki.git `
  "$HOME/.codex/skills/obsidian-research-wiki-reference"
```

설치한 뒤 새 Codex 세션을 시작하고 다음과 같이 호출합니다.

```text
$obsidian-research-wiki-reference 문헌 Vault를 설계해줘. 아직 파일은 만들지 마.
```

> [!NOTE]
> 첫 응답은 설계 대화입니다. 정확한 Vault 경로, 적용 설계안, 시험 적용할 자료,
> 변경 금지 목록을 승인하기 전에는 Vault 파일을 만들지 않습니다.

설치 확인, 업데이트, 안전한 비활성화, Windows 안내와 선택적 PDF 의존성은
[설치 가이드](docs/INSTALLATION.md)에서 확인할 수 있습니다.

## 만들어지는 구조

첫 시험 적용에서는 Reference Index에서 실제 논문이나 자료까지 따라갈 수
있는 경로를 만듭니다. 별도 지식 노트는 한 논문을 넘어 재사용할 가치가
있을 때만 생성합니다.

```text
Reference Index
├── Reference Profile
├── Paper — 짧은 제목
│   ├── 검토한 방법·결과·한계와 원문 근거
│   └── Source Text Manifest — 짧은 제목  (선택)
├── Claim — 재사용할 주장                   (선택)
├── Method — 재사용할 문헌 방법             (선택)
└── Theory — 출처에 근거한 이론             (선택)
```

논문별 Paper 노트가 기본 읽기 기록입니다. Claim, Method, Theory,
Evidence, Limitation, Theme, Question 노트는 모든 문단을 잘게 나누는 용도가
아니라 여러 자료에서 재사용할 내용을 선택적으로 승격하는 용도입니다.

학술 논문은 `Paper — {짧은 제목}`, 보고서·웹페이지·표준·데이터셋 등은
`Source — {이름}`을 사용합니다. 기존 파일명과 링크는 보존합니다. 같은
파일명이 있으면 연도, 첫 저자 순서로 구분자를 추가합니다.

## 처음 선택하는 정리 깊이

첫 온보딩에서 문헌을 어디까지 정리할지 선택합니다. 대부분의 사용자에게는
`searchable-library`를 권장합니다.

| 프리셋 | 포함 범위 | 적합한 용도 |
| --- | --- | --- |
| `notes-only` | Paper/Source 노트 | 집중 읽기 |
| `searchable-library` | 노트 + 검색 가능한 전문 | 일반 문헌함 |
| `knowledge-network` | 위 구성 + 승격 지식 | 논문 간 종합 |

세 프리셋은 누적되는 깊이지만, 전문 저장 위치는 별도의 안전 결정입니다.
개인용 비공개 Vault는 재생성 가능한 `vault-local` 캐시를 사용할 수 있습니다.
공유·공개·공개 동기화 Vault 또는 노출 범위가 불확실한 Vault는 `external`
저장을 사용합니다. 승인한 선택은 `Reference Profile`에 기록됩니다.

## 네 가지 표현 층

1. **정본 자료** — 일반적으로 Vault 밖에 있는 PDF, 웹페이지 또는 Zotero
   항목이며 판단의 기준입니다.
2. **전문 파생본** — 검색과 재열람을 위한 선택적 텍스트·OCR Markdown이며,
   파싱 및 OCR 오류가 있을 수 있습니다.
3. **Paper 또는 Source 정리 노트** — 한 자료에서 실제로 검토한 방법,
   측정, 모델 가정, 결과, 한계와 검토 흔적입니다.
4. **승격한 지식 노트** — 여러 자료에서 재사용하는 Claim, Method, Theory,
   Evidence, Limitation, Theme 또는 Question입니다.

전문 파생본은 정본이 아닙니다. 중요한 수식, 기호, 표, 그림, 캡션과 다단
편집의 읽기 순서는 정본과 직접 비교해야 합니다.

## 선택적 로컬 PDF 추출

사용자가 명시적으로 승인한 PDF에 한해 정본은 외부에 유지하고, 페이지
마커가 있는 전문 파생본과 `Source Text Manifest`를 생성할 수 있습니다.

- 텍스트 층이 정상적인 PDF에는 `pdftotext` 호환 경로를 사용합니다.
- 복잡한 과학 논문 레이아웃에는 Docling을 사용할 수 있으며 OCR과 수식
  보강은 명시적으로 선택해야 합니다.
- 새 매니페스트에는 정본·파생본 해시, 추출기 정보와 옵션, 페이지 수와
  정렬된 페이지 마커가 기록됩니다.
- 기존 결과를 암묵적으로 덮어쓰거나 추출 엔진을 몰래 전환하지 않습니다.

명령과 의존성 설정은 [설치 가이드](docs/INSTALLATION.md), 전체 추출·검토
규칙은 [노트 품질 계약](docs/NOTE_QUALITY.md)에 정리되어 있습니다.

## 안전 경계

- 설계 단계는 읽기 전용입니다.
- 실제 적용에는 정확한 Vault 경로와 승인한 Blueprint가 필요합니다.
- 기존 노트는 기본적으로 제자리에 두고 새 노트에서 연결합니다.
- Obsidian 플러그인을 설치하거나 `.obsidian` 설정을 변경하지 않습니다.
- PDF, Zotero 라이브러리, 연구 원자료 또는 코드를 복사하지 않습니다.
- 실험, 관찰 또는 실험실 기록 구조를 만들지 않습니다.
- 파일명만 보고 논문 내용을 추론하지 않습니다.

## 품질 검사

Vault 작업을 마치기 전에는 적용 설계안에서 승인한 정확한 자료 수를 지정해
읽기 전용 노트 검사를 실행합니다.

```bash
REFERENCE_SCHEMA_MODE=current python scripts/check_notes.py <승인된-vault> \
  --expect-sources <승인된-자료-수> \
  --expect-profile
```

전문 파생본이 있으면 해시와 페이지 맵을 별도로 확인합니다.

```bash
python scripts/check_source_text.py <manifest.md> --vault-root <승인된-vault>
```

저장소 유지관리자는 독립 설치 스모크 검사를 실행할 수 있습니다.

```bash
python scripts/smoke_release.py
```

이 검사는 구조와 출처 추적 오류를 찾지만, 원문 읽기나 과학적 주장 검토를
대신하지 않습니다.

## 문서

- [작동 계약](SKILL.md)
- [레퍼런스 아키텍처](docs/CONTRACT.md)
- [온보딩 인터뷰](docs/ONBOARDING.md)
- [설치와 PDF 추출](docs/INSTALLATION.md)
- [노트 품질 계약](docs/NOTE_QUALITY.md)
- [워크플로 사용성 평가 절차](docs/USABILITY_TEST.md)
- [변경 이력](CHANGELOG.md)
- [보안 정책](SECURITY.md)
- [피드백과 기여](CONTRIBUTING.md)

템플릿, 평가 사례와 검증 스크립트가 모두 이 저장소에 포함되므로 다른
저장소 없이 독립적으로 설치하고 평가할 수 있습니다.

## 라이선스

현재 릴리스에는 [PolyForm Noncommercial License 1.0.0](LICENSE)을
적용합니다. 개인 연구, 학습, 실험, 교육기관 및 공공 연구기관의 이용은
라이선스 조건에 따라 허용됩니다. 상업적 이용에는 Moonweave의 별도
라이선스가 필요합니다. 이 저장소는 소스 공개형이며 OSI 승인 오픈소스는
아닙니다.

라이선스 변경은 앞으로의 버전에만 적용됩니다. `8a43fd2` 커밋까지 공개된
버전에는 당시의 MIT 라이선스가 계속 적용됩니다.
