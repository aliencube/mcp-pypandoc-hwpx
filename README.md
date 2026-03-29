# `pypandoc-hwpx` MCP 서버

[`pypandoc-hwpx`](https://pypi.org/project/pypandoc-hwpx) 패키지를 활용하여 `.docx`, `.html`, `.md` 문서를 `.hwpx` 문서로 변환하는 도구를 제공하는 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 서버입니다.

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

1. MCP 서버를 실행합니다.

</details>

<details open>
<summary><h4>로컬 Streamable HTTP 서버</h4></summary>

1. MCP 서버를 실행합니다.

    ```bash
    uv run src/server.py --http --port 8000
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

1. MCP 서버를 실행합니다.

</details>

<details>
<summary><h4>컨테이너형 <code>stdio</code> 서버</h4></summary>

1. 컨테이너 이미지를 빌드합니다.

    ```bash
    docker build -f Dockerfile -t mcp-pypandoc-hwpx:latest .
    ```

1. MCP 서버 설정을 복사합니다.

    ```bash
    # zsh/bash
    cp .vscode/mcp.container.stdio.json .vscode/mcp.json
    ```

    ```bash
    # PowerShell
    Copy-Item .vscode/mcp.container.stdio.json .vscode/mcp.json -Force
    ```

1. MCP 서버를 실행합니다.

</details>

<details open>
<summary><h4>컨테이너형 Streamable HTTP 서버</h4></summary>

1. 컨테이너 이미지를 빌드합니다.

    ```bash
    docker build -f Dockerfile -t mcp-pypandoc-hwpx:latest .
    ```

1. MCP 서버를 실행합니다.

    ```bash
    docker run -i --rm -p 8000:8000 --mount "type=bind,src=$HOME,dst=/home/user" mcp-pypandoc-hwpx:latest --http --port 8000
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

1. MCP 서버를 실행합니다.

</details>

<details>
<summary><h4>리모트 Streamable HTTP 서버</h4></summary>

1. Azure에 로그인합니다.

    ```bash
    azd auth login
    ```

1. Azure에 배포합니다.

    ```bash
    azd up
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

1. MCP 서버를 실행합니다.

</details>

## 제공 도구

| 도구           | 설명                                                  |
|----------------|-------------------------------------------------------|
| `docx_to_hwpx` | 워드(`.docx`) 파일을 아래아 한글(`.hwpx`) 파일로 변환 |
| `html_to_hwpx` | HTML 파일을 아래아 한글(`.hwpx`) 파일로 변환          |
| `md_to_hwpx`   | 마크다운 파일을 아래아 한글(`.hwpx`) 파일로 변환      |

### 도구 매개변수

세 도구 모두 동일한 매개변수를 사용합니다:

| 매개변수         | 타입   | 필수 여부 | 설명                                                                               |
|------------------|--------|-----------|------------------------------------------------------------------------------------|
| `input_path`     | string | 예        | 원본 파일 경로                                                                     |
| `output_path`    | string | 예        | `.hwpx` 출력 파일이 저장될 경로                                                    |
| `reference_hwpx` | string | 아니오    | 스타일 참조용 `.hwpx` 파일 경로 (지정하지 않으면 내장된 `blank.hwpx`를 사용합니다) |
