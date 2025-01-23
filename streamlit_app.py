import streamlit as st
import os
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO

# Inicializa o estado da sessão para armazenar perguntas e alternativas
if "questions" not in st.session_state:
    st.session_state["questions"] = []
if "current_alternatives" not in st.session_state:
    st.session_state["current_alternatives"] = []
if "edit_quest_index" not in st.session_state:
    st.session_state["edit_quest_index"] = None
if "edit_alt_index" not in st.session_state:
    st.session_state["edit_alt_index"] = None
if "editing_alt" not in st.session_state:
    st.session_state["editing_alt"] = False
if "editing_quest" not in st.session_state:
    st.session_state["editing_quest"] = False
if "adding_question" not in st.session_state:
    st.session_state["adding_question"] = False
if "quest_num_alts" not in st.session_state:
    st.session_state["quest_num_alts"] = 0


def add_question(enunciate, alternatives):
    """Adiciona uma pergunta com suas alternativas à lista de perguntas salvas."""
    pergunta = {
        "enunciate": enunciate,
        "alternatives": alternatives,
    }
    st.session_state.questions.append(pergunta)


def start_editing_question(index):
    st.session_state["edit_quest_index"] = index
    st.session_state["editing_quest"] = True


def start_editing_alternative(index):
    st.session_state["edit_alt_index"] = index
    st.session_state["editing_alt"] = True


def stop_editing_alt():
    st.session_state["editing_alt"] = False


def stop_editing_quest():
    st.session_state["editing_quest"] = False


def generate_pdf(questions):
    buffer = BytesIO()
    fileName = "prova.pdf"
    documentTitle = "Prova"
    title = "Prova"
    subTitle = "Responda as questões abaixo:"
    textLines = []
    for idx, question in enumerate(questions):
        textLines.append(f"{idx + 1}. {question['enunciate']}")
        for alt in question["alternatives"]:
            status = "(Correta)" if alt["is_true"] else "(Incorreta)"
            textLines.append(f"    - {alt['text']} {status}")
        textLines.append("---")

    pdf = canvas.Canvas(buffer)
    pdf.setTitle(documentTitle)

    pdf.setFont("Courier", 12)
    pdf.drawCentredString(300, 800, title)

    pdf.setFillColorRGB(0, 0, 255)
    pdf.setFont("Courier-Bold", 24)
    pdf.drawCentredString(300, 750, subTitle)

    pdf.line(30, 710, 550, 710)

    text = pdf.beginText(40, 680)
    text.setFont("Courier", 12)
    text.setFillColor(colors.red)

    for line in textLines:
        text.textLine(line)

    pdf.drawText(text)

    pdf.save()

    buffer.seek(0)
    return buffer


def main():
    st.title("Gerador de Provas")

    if st.session_state["quest_num_alts"] != 0:
        # Campos de entrada para a pergunta e alternativas
        with st.form(key="question_form"):
            st.write("### Adicionar Questão:")
            enunciate = st.text_area(
                "Digite o enunciado da questão:", placeholder="Digite sua pergunta aqui"
            )
            alternativas = []
            for i in range(st.session_state["quest_num_alts"]):
                alternatives_text = st.text_area(
                    "Adicione uma alternativa:",
                    placeholder="Digite uma alternativa aqui",
                    key=f"new_alt_{i}",
                )

                is_true = st.checkbox(
                    "Alternativa correta?",
                    key=f"new_is_true_{i}",
                    value=False,
                )
                alternativas.append({"text": alternatives_text, "is_true": is_true})

            col1, col2 = st.columns([3, 1])
            with col1:
                if st.form_submit_button("Adicionar Questão"):
                    if enunciate and all(alt["text"] for alt in alternativas):
                        st.session_state.questions.append(
                            {"enunciate": enunciate, "alternatives": alternativas}
                        )
                        st.session_state.current_alternatives = (
                            []
                        )  # Limpa as alternativas após adicionar a pergunta
                        st.session_state["quest_num_alts"] = 0
                        st.rerun()
                        st.success("Questão adicionada com sucesso!")
                    else:
                        st.error(
                            "Por favor, forneça tanto o enunciado da questão quanto pelo menos uma alternativa."
                        )
            with col2:
                if st.form_submit_button("Descartar Questão"):
                    st.session_state["quest_num_alts"] = 0
                    st.rerun()
                    st.warning("Questão descartada.")

    else:
        if st.button("Criar Questão", key="create_question_button"):
            st.session_state["adding_question"] = True
            st.rerun()
    if st.session_state["adding_question"] == True:
        num_alt = st.number_input(
            "Quantas alternativas a questão terá?", min_value=2, value=2
        )
        if st.button("Confirmar", key="confirm_button"):
            st.session_state["quest_num_alts"] = num_alt
            st.session_state["adding_question"] = False
            st.rerun()

    if not st.session_state["editing_quest"]:
        # Exibe questões salvas abaixo do formulário
        st.write("### Questões Salvas:")
        if st.session_state.questions:
            for idx, question in enumerate(st.session_state.questions):
                st.write(f"{idx + 1}. {question['enunciate']}")
                for alt in question["alternatives"]:
                    status = "(Correta)" if alt["is_true"] else "(Incorreta)"
                    st.write(f"    - {alt['text']} {status}")
                st.button(
                    "Editar",
                    key=f"edit_quest_button_{idx}",
                    on_click=lambda idx=idx: start_editing_question(idx),
                )
                st.write("---")  # Adiciona um delimitador entre perguntas
        else:
            st.write("Nenhuma pergunta adicionada ainda.")

    if st.session_state["editing_quest"] == True:
        st.write("### Editar Questão:")
        question = st.session_state.questions[st.session_state["edit_quest_index"]]
        enunciate = st.text_area(
            "Edite o enunciado da questão:", value=question["enunciate"]
        )
        for idx, alt in enumerate(question["alternatives"]):
            alt_text = st.text_area(
                f"Edite a alternativa {idx + 1}:", value=alt["text"]
            )
            is_true = st.checkbox("Alternativa correta?", value=alt["is_true"], key=idx)
            question["alternatives"][idx] = {"text": alt_text, "is_true": is_true}
        col1, col2 = st.columns([1, 8])
        with col1:
            if st.button("Salvar", key="save_button", on_click=stop_editing_quest):
                st.success("Questão editada com sucesso")
                st.session_state["editing_quest"] = False
        with col2:
            if st.button("Cancelar", key="cancel_button"):
                st.warning("Edição cancelada")
                st.session_state["editing_quest"] = False
                st.rerun()

    if st.button("Gerar Prova", key="genereta_bottom_button"):
        st.success("Prova gerada com sucesso!")
        if st.session_state.questions:
            pdf_buffer = generate_pdf(st.session_state.questions)
            st.success("Prova gerada com sucesso! Arquivo salvo como 'prova.pdf'.")
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name="prova.pdf",
                mime="application/pdf",
            )
        else:
            st.warning("Nenhuma pergunta disponível para gerar a prova.")


if __name__ == "__main__":
    main()
