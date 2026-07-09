import os
import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
DEFAULT_API_KEY = os.getenv("API_ACCESS_KEY", "")


st.set_page_config(
    page_title="OmniDoc AI",
    page_icon="📄",
    layout="wide"
)


st.markdown(
    """
    <style>
        .main-title {
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 0px;
        }

        .subtitle {
            font-size: 22px;
            color: #B8BCC8;
            margin-top: 0px;
            margin-bottom: 24px;
        }

        .info-card {
            background-color: #1E1E2F;
            padding: 22px;
            border-radius: 14px;
            border: 1px solid #33364A;
            margin-bottom: 18px;
        }

        .result-card {
            background-color: #1A1B26;
            padding: 24px;
            border-radius: 16px;
            border: 1px solid #303348;
            margin-top: 20px;
        }

        .small-text {
            color: #A9ADC1;
            font-size: 15px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


with st.sidebar:
    st.header("⚙️ Configurações")

    api_url = st.text_input(
        "URL da API",
        value=API_URL
    )

    api_key = st.text_input(
        "API Key",
        value=DEFAULT_API_KEY,
        type="password"
    )

    st.divider()

    st.markdown("### Como rodar localmente")

    st.code("uvicorn app.main:app --reload", language="bash")

    st.markdown(
        """
        <p class="small-text">
        A API precisa estar ativa na porta 8000 para que a interface consiga enviar os documentos.
        </p>
        """,
        unsafe_allow_html=True
    )


st.markdown('<p class="main-title">📄 OmniDoc AI</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Transforme documentos em resumos, riscos e ações sugeridas com apoio de IA.</p>',
    unsafe_allow_html=True
)


col_intro_1, col_intro_2, col_intro_3 = st.columns(3)

with col_intro_1:
    st.markdown(
        """
        <div class="info-card">
            <h3>📤 Envie documentos</h3>
            <p class="small-text">
            Faça upload de arquivos TXT, PDF ou DOCX diretamente pela interface.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_intro_2:
    st.markdown(
        """
        <div class="info-card">
            <h3>🧠 Análise inteligente</h3>
            <p class="small-text">
            A API extrai o texto e gera uma análise estruturada com apoio de IA.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_intro_3:
    st.markdown(
        """
        <div class="info-card">
            <h3>✅ Resultado objetivo</h3>
            <p class="small-text">
            Receba resumo, pontos principais, riscos e ações sugeridas.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


with st.expander("💡 Como funciona o OmniDoc AI?"):
    st.write(
        """
        O OmniDoc AI é uma aplicação criada para demonstrar, de forma prática, 
        como uma API backend em Python pode ser integrada a uma interface visual 
        e a serviços de Inteligência Artificial.

        O fluxo é simples:

        1. O usuário envia um ou mais documentos;
        2. A API recebe os arquivos e extrai o texto;
        3. O conteúdo é analisado;
        4. O sistema retorna um resultado organizado e fácil de entender.

        Esse projeto foi desenvolvido com foco em portfólio, aplicando FastAPI, 
        processamento assíncrono, autenticação com API Key, testes automatizados, 
        Docker e interface com Streamlit.
        """
    )


st.markdown("## 📎 Enviar documentos")

uploaded_files = st.file_uploader(
    "Selecione até 5 documentos",
    type=["txt", "pdf", "docx"],
    accept_multiple_files=True,
    help="Formatos aceitos: TXT, PDF e DOCX."
)


if uploaded_files:
    st.success(f"{len(uploaded_files)} arquivo(s) selecionado(s).")

    with st.container():
        for file in uploaded_files:
            file_size_kb = round(len(file.getvalue()) / 1024, 2)
            st.write(f"📄 **{file.name}** — {file_size_kb} KB")


if len(uploaded_files or []) > 5:
    st.error("Envie no máximo 5 documentos por vez.")


st.divider()


col_button, col_hint = st.columns([1, 3])

with col_button:
    analyze_button = st.button("🚀 Analisar documentos", type="primary")

with col_hint:
    st.caption("A análise pode levar alguns segundos, dependendo do tamanho dos arquivos.")


if analyze_button:
    if not uploaded_files:
        st.warning("Selecione pelo menos um documento antes de analisar.")

    elif len(uploaded_files) > 5:
        st.error("O limite é de 5 documentos por análise.")

    elif not api_key:
        st.error("Informe a API Key na barra lateral.")

    else:
        with st.spinner("Lendo documentos e gerando análise..."):
            files = []

            for index, uploaded_file in enumerate(uploaded_files, start=1):
                files.append(
                    (
                        f"file_{index}",
                        (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type or "application/octet-stream"
                        )
                    )
                )

            headers = {
                "X-API-Key": api_key
            }

            try:
                response = requests.post(
                    f"{api_url}/analyze-batch",
                    headers=headers,
                    files=files,
                    timeout=120
                )

                if response.status_code == 200:
                    data = response.json()

                    st.success("Análise concluída com sucesso!")

                    metric_1, metric_2 = st.columns(2)

                    with metric_1:
                        st.metric(
                            "Documentos analisados",
                            data["total_documents"]
                        )

                    with metric_2:
                        st.metric(
                            "Tempo de processamento",
                            f'{data["processing_time_seconds"]}s'
                        )

                    st.markdown("## 📊 Resultado da análise")

                    for document in data["documents"]:
                        st.markdown(
                            f"""
                            <div class="result-card">
                                <h2>📄 {document['filename']}</h2>
                                <p class="small-text">
                                    {document['characters']} caracteres analisados.
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.markdown("### 📝 Resumo")
                        st.write(document["summary"])

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown("### 🔎 Pontos principais")

                            if document["key_points"]:
                                for item in document["key_points"]:
                                    st.write(f"• {item}")
                            else:
                                st.write("Nenhum ponto principal identificado.")

                        with col2:
                            st.markdown("### ⚠️ Riscos")

                            if document["risks"]:
                                for item in document["risks"]:
                                    st.write(f"• {item}")
                            else:
                                st.write("Nenhum risco identificado.")

                        with col3:
                            st.markdown("### ✅ Ações sugeridas")

                            if document["suggested_actions"]:
                                for item in document["suggested_actions"]:
                                    st.write(f"• {item}")
                            else:
                                st.write("Nenhuma ação sugerida.")

                        st.divider()

                elif response.status_code == 401:
                    st.error("API Key inválida ou ausente. Confira a chave na barra lateral.")

                else:
                    st.error(f"Erro na API: {response.status_code}")
                    st.write(response.text)

            except requests.exceptions.ConnectionError:
                st.error(
                    "Não foi possível conectar à API. "
                    "Confirme se o FastAPI está rodando em http://127.0.0.1:8000."
                )

            except requests.exceptions.Timeout:
                st.error("A análise demorou demais e atingiu o tempo limite.")

            except Exception as error:
                st.error("Ocorreu um erro inesperado.")
                st.write(str(error))


st.divider()

st.markdown(
    """
    <p class="small-text">
    Projeto desenvolvido para portfólio, com foco em Python, FastAPI, IA, Docker, testes automatizados e interface visual.
    </p>
    """,
    unsafe_allow_html=True
)