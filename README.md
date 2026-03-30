# `pypandoc-hwpx` MCP 서버

[`pypandoc-hwpx`](https://pypi.org/project/pypandoc-hwpx) 패키지를 활용하여 `.docx`, `.html`, `.md` 문서를 `.hwpx` 문서로 변환하는 도구를 제공하는 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 서버입니다.

﻿<video src="https://github.com/user-attachments/assets/ed60811a-49a9-4c8b-8e4e-447e04051927" controls width="600"></video>

## 요구 사항

- Python 3.12+
- [Pandoc](https://pandoc.org/)
- [uv](https://docs.astral.sh/uv/)
- [Docker Desktop](https://docs.docker.com/desktop/) 또는 동등한 컨테이너 도구

## 시작하기

### 설치

```bash
uv sync
```

### 서버 실행

<details>
<summary><h4>로컬 <code>stdio</code> 서버</h4></summary>

1. MCP 서버 설정을 복사합니다.

    ```bash
    # zsh/bash
    cp .vscode/mcp.local.stdio.json .vscode/mcp.json
    ```

    ```bash
    # PowerShell
    Copy-Item .vscode/mcp.local.stdio.json .vscode/mcp.json -Force
    ```

1. VS Code에서 MCP 서버를 실행합니다.

</details>

<details>
<summary><h4>로컬 Streamable HTTP 서버</h4></summary>

1. MCP 서버를 실행합니다.

    ```bash
    uv run python -m src.server --http --port 8000
    ```

   > **NOTE**: 포트 번호는 원하는 값으로 설정할 수 있습니다.

1. MCP 서버 설정을 복사합니다.

    ```bash
    # zsh/bash
    cp .vscode/mcp.local.http.json .vscode/mcp.json
    ```

    ```bash
    # PowerShell
    Copy-Item .vscode/mcp.local.http.json .vscode/mcp.json -Force
    ```

1. VS Code에서 MCP 서버를 실행합니다.

</details>

<details>
<summary><h4>컨테이너형 <code>stdio</code> 서버</h4></summary>

1. MCP 서버 설정을 복사합니다.

    ```bash
    # zsh/bash
    cp .vscode/mcp.container.stdio.json .vscode/mcp.json
    ```

    ```bash
    # PowerShell
    Copy-Item .vscode/mcp.container.stdio.json .vscode/mcp.json -Force
    ```

1. VS Code에서 MCP 서버를 실행합니다.

</details>

<details>
<summary><h4>컨테이너형 Streamable HTTP 서버</h4></summary>

1. MCP 서버를 실행합니다.

    ```bash
    # zsh/bash
    docker run -i --rm -p 8000:8000 \
        --mount "type=bind,src=$HOME,dst=/home/user" \
        ghcr.io/aliencube/mcp-pypandoc-hwpx:latest --http --port 8000
    ```

    ```bash
    # PowerShell
    docker run -i --rm -p 8000:8000 `
        --mount "type=bind,src=$HOME,dst=/home/user" `
        ghcr.io/aliencube/mcp-pypandoc-hwpx:latest --http --port 8000
    ```

   > **NOTE**: 포트 번호는 원하는 값으로 설정할 수 있습니다.

1. MCP 서버 설정을 복사합니다.

    ```bash
    # zsh/bash
    cp .vscode/mcp.container.http.json .vscode/mcp.json
    ```

    ```bash
    # PowerShell
    Copy-Item .vscode/mcp.container.http.json .vscode/mcp.json -Force
    ```

1. VS Code에서 MCP 서버를 실행합니다.

</details>

<details open>
<summary><h4>원격 Streamable HTTP 서버</h4></summary>

> **NOTE**: 원격 MCP 서버는 공개 URL로 접근할 수 있는 파일만 변환할 수 있습니다.

1. Azure에 로그인합니다.

    ```bash
    azd auth login
    ```

1. Azure에 배포합니다.

    ```bash
    azd up
    ```

   > **NOTE**: Azure 구독, 배포 지역, 환경 이름 등을 물어보면 입력하세요.

1. 배포가 끝나면 리모트 MCP 서버 URL 값을 가져옵니다.

    ```bash
    azd env get-value AZURE_RESOURCE_MCP_PYPANDOC_HWPX_FQDN
    ```

1. MCP 서버 설정을 복사합니다.

    ```bash
    # zsh/bash
    cp .vscode/mcp.remote.http.json .vscode/mcp.json
    ```

    ```bash
    # PowerShell
    Copy-Item .vscode/mcp.remote.http.json .vscode/mcp.json -Force
    ```

1. VS Code에서 MCP 서버를 실행합니다. 이 때 앞서 구한 리모트 서버의 주소를 입력하세요.

1. 더이상 사용하지 않으면 리소스를 삭제하세요.

    ```bash
    azd down --purge --force
    ```

</details>

## 알려진 이슈

`pypandoc-hwpx` 라이브러리의 [설명 및 제약사항](https://github.com/msjang/pypandoc-hwpx/blob/main/README.md#%EC%84%A4%EB%AA%85-%EB%B0%8F-%EC%A0%9C%EC%95%BD%EC%82%AC%ED%95%AD) 섹션을 참고하세요.

## MCP에 대해 더 자세히 알고 싶다면?

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [초보자를 위한 MCP](https://github.com/microsoft/mcp-for-beginners/)

## 문의

- `pypandoc-hwpx` MCP 서버 관련 문의 👉 [https://github.com/aliencube/mcp-pypandoc-hwpx/issues](https://github.com/aliencube/mcp-pypandoc-hwpx/issues)
- `pypandoc-hwpx` 라이브러리 관련 문의 👉 [https://github.com/msjang/pypandoc-hwpx/issues](https://github.com/msjang/pypandoc-hwpx/issues)
