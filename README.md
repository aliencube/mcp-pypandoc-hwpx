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

1. VS Code에서 MCP 서버를 실행합니다.

</details>

<details>
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

1. VS Code에서 MCP 서버를 실행합니다.

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

1. VS Code에서 MCP 서버를 실행합니다.

</details>

<details>
<summary><h4>컨테이너형 Streamable HTTP 서버</h4></summary>

1. 컨테이너 이미지를 빌드합니다.

    ```bash
    docker build -f Dockerfile -t mcp-pypandoc-hwpx:latest .
    ```

1. MCP 서버를 실행합니다.

    ```bash
    # zsh/bash
    docker run -i --rm -p 8000:8000 \
        --mount "type=bind,src=$HOME,dst=/home/user" \
        mcp-pypandoc-hwpx:latest --http --port 8000
    ```

    ```bash
    # PowerShell
    docker run -i --rm -p 8000:8000 `
        --mount "type=bind,src=$HOME,dst=/home/user" `
        mcp-pypandoc-hwpx:latest --http --port 8000
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
<summary><h4>리모트 Streamable HTTP 서버</h4></summary>

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

## 알려진 이슈

`pypandoc-hwpx` 라이브러리의 [설명 및 제약사항](https://github.com/msjang/pypandoc-hwpx/blob/main/README.md#%EC%84%A4%EB%AA%85-%EB%B0%8F-%EC%A0%9C%EC%95%BD%EC%82%AC%ED%95%AD) 섹션을 참고하세요.

## 문의

- `pypandoc-hwpx` MCP 서버 관련 문의 👉 [https://github.com/aliencube/mcp-pypandoc-hwpx/issues](https://github.com/aliencube/mcp-pypandoc-hwpx/issues)
- `pypandoc-hwpx` 라이브러리 관련 문의 👉 [https://github.com/msjang/pypandoc-hwpx/issues](https://github.com/msjang/pypandoc-hwpx/issues)

## MCP에 대해 더 자세히 알고 싶다면?

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [초보자를 위한 MCP](https://github.com/microsoft/mcp-for-beginners/)
