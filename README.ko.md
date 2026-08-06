# Obsidian Research Wiki: Reference

한국어 | [English](README.md)

`Obsidian Research Wiki: Reference`는 논문과 외부 자료를 Obsidian에서
근거 중심으로 정리하는 소스 공개형 Codex Skill입니다. 논문, 주장,
근거, 문헌 방법, 이론, 한계, 주제, 후속 질문을 연결하되 연구자의 실험
기록이나 연구 일지와는 분리합니다.

논문별 `Paper` 노트가 기본 읽기 기록입니다. 여러 논문에서 다시
사용하거나 별도로 검토할 가치가 있는 내용만 Claim, Method, Theory,
Evidence, Limitation 노트로 승격합니다. 논문의 모든 내용을 작은 노트로
무조건 분해하지 않습니다.

학술 논문 파일명은 `Paper — {짧은 제목}`, 보고서·웹페이지·표준·데이터셋
등은 `Source — {이름}`을 사용합니다. 같은 파일명이 이미 있으면 연도,
첫 저자 순서로 구분자를 추가합니다. 기존 Vault의 파일명과 링크는
자동으로 바꾸지 않습니다.

## 처음 선택하는 정리 깊이

첫 실행에서는 세 가지 프리셋 중 하나를 선택합니다.

| 프리셋 | 정리 범위 |
|---|---|
| `notes-only` | 검토한 논문별 Paper/Source 노트만 작성 |
| `searchable-library` | 논문 노트와 검색 가능한 전문 파생본을 함께 관리하는 기본 권장안 |
| `knowledge-network` | 검색 가능한 전문과 논문 노트에 더해 재사용 가치가 있는 지식 노트를 선택적으로 승격 |

선택한 프리셋은 `Reference Profile`에 저장됩니다. 전문 파생본의 저장
위치는 정리 깊이와 별도로 결정합니다. 개인용 비공개 Vault에서는
`vault-local` 캐시를 사용할 수 있지만, 공유·공개 Vault나 공개 동기화
환경에서는 `external` 저장을 권장합니다.

## 원본과 노트의 경계

이 Skill은 다음 네 층을 구분합니다.

1. Vault 밖의 PDF, 웹페이지, Zotero 항목이 정본입니다.
2. PDF에서 추출한 Markdown은 검색과 읽기를 위한 파생본입니다.
3. `Paper` 또는 `Source` 정리 노트에는 실제로 검토한 내용을 기록합니다.
4. 여러 자료에서 재사용할 가치가 있는 내용만 별도 지식 노트로 승격합니다.

PDF 파싱과 OCR은 수식이나 읽기 순서를 잘못 복원할 수 있습니다. 전문
파생본은 정본이나 지식 노트를 대신하지 않습니다. 추출 방식, 위치,
SHA-256 해시와 페이지 매핑은 `Source Text Manifest`에 기록합니다.

## 주요 기능

- 레퍼런스 중심 Obsidian Vault 설계와 안전한 초기 설정
- 정리 깊이 프리셋 추천과 `Reference Profile` 저장
- Zotero 또는 외부 정본 위치 보존
- 논문과 Claim, Evidence, Method, Theory, Limitation, Theme, Question 연결
- 기존 Vault를 먼저 읽기 전용으로 점검한 뒤 승인된 범위만 수정
- Poppler 또는 선택적 Docling을 이용한 로컬 PDF 전문 추출
- 전문 해시, 페이지 마커, 노트 링크, 출처 근거 검사

## 하지 않는 일

- PDF, Zotero 라이브러리, 원자료, 코드를 Vault에 자동 복사하지 않습니다.
- Obsidian 플러그인을 설치하거나 `.obsidian` 설정을 자동 변경하지 않습니다.
- 실험, 관찰, 실험실 기록 구조를 만들지 않습니다.
- 파일명만 보고 연구 내용을 추론하지 않습니다.
- 기존 Vault를 승인 없이 일괄 이동하거나 이름을 바꾸지 않습니다.

## 안전 원칙

설계 단계에서는 파일을 만들거나 수정하지 않습니다. 실제 적용에는 정확한
Vault 경로와 승인된 Blueprint가 필요합니다. 기존 노트는 별도 이동 승인이
없는 한 제자리에 두고, 새 노트에서 연결하는 방식을 기본으로 사용합니다.

## 설치

기술 식별자는 `obsidian-research-wiki-reference`입니다. 저장소를 Codex의
Skill 디렉터리에 설치합니다.

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

정상적으로 인식되면 첫 응답에서 `notes-only`, `searchable-library`,
`knowledge-network`를 먼저 제시합니다. 설치 확인, 업데이트, 안전한
비활성화, Windows 안내와 PDF 선택 의존성은
[설치 가이드](docs/INSTALLATION.md)에 정리되어 있습니다.

## 선택적 PDF 추출

노트만 정리할 때는 PDF 도구가 필요하지 않습니다. 간단한 PDF 텍스트
추출은 Poppler의 `pdftotext`를 사용합니다. 수식, 다단 편집, 복잡한 읽기
순서가 있는 과학 PDF에는 로컬 Docling을 선택할 수 있습니다.

Docling의 OCR과 수식 보강은 자동으로 켜지지 않습니다. 정본 PDF는 Vault
밖에 유지하며, 추출 결과는 페이지 마커와 해시를 기록한 파생본으로만
다룹니다. 설치와 실행 예시는 [설치 가이드](docs/INSTALLATION.md)를
참고하십시오.

## 포함된 구성

```text
README.md
README.ko.md
SKILL.md
CHANGELOG.md
CONTRIBUTING.md
LICENSE
NOTICE
SECURITY.md
docs/
evals/
scripts/
templates/
```

`templates/`와 검증 스크립트는 제품 안에 함께 들어 있으므로 다른
저장소에 의존하지 않고 설치하고 평가할 수 있습니다.

## 검증

공개 전 기본 스모크를 실행하려면 다음 명령을 사용합니다.

```bash
python scripts/smoke_release.py
```

실제 Vault를 넘기기 전에는 승인된 Paper/Source 개수를 명시해 검사합니다.

```bash
REFERENCE_SCHEMA_MODE=current python scripts/check_notes.py <승인된-vault> \
  --expect-sources <승인된-자료-수> \
  --expect-profile
```

전문 파생본이 있으면 manifest 파일과 파생본의 해시 및 페이지 마커도 별도로
검사합니다. 자동 검사를 통과했다는 사실만으로 수식, 그림 또는 과학적
주장이 검토 완료된 것은 아닙니다.

## 프로젝트 정책

- 변경 이력: [CHANGELOG.md](CHANGELOG.md)
- 보안 문제 신고: [SECURITY.md](SECURITY.md)
- 피드백과 기여: [CONTRIBUTING.md](CONTRIBUTING.md)

## 라이선스

현재 릴리스에는 SPDX 식별자 `PolyForm-Noncommercial-1.0.0`인
[PolyForm Noncommercial License 1.0.0](LICENSE)을 적용합니다.

개인 연구, 학습, 실험, 교육기관 및 공공 연구기관의 이용은 라이선스
조건에 따라 허용됩니다. 상업적 이용에는 Moonweave의 별도 라이선스가
필요합니다. 이 저장소는 소스 공개형이며 OSI 승인 오픈소스는 아닙니다.

라이선스 변경은 앞으로의 버전에만 적용됩니다. `8a43fd2` 커밋까지 공개된
버전에는 당시의 MIT 라이선스가 계속 적용됩니다.
