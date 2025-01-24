import streamlit as st
import os
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO

# Inicializa o estado da sessão para armazenar perguntas e alternativas
if "generating_test" not in st.session_state:
    st.session_state["generating_test"] = False
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

letter_alternatives = ["A", "B", "C", "D", "E"]


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
            textLines.append(f"    {letter_alternatives[idx]}) {alt['text']} {status}")
            textLines.append(f"  - {alt['explanation']}")
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
    st.title("Criação de :blue[Provas] 📄🖊️")
    st.write("\n\n\n\n\n\n\n\n\n")
    if not st.session_state["generating_test"]:
        if st.button("Construir Prova", key="generate_test_button"):
            st.session_state["generating_test"] = True
            st.rerun()
            st.write("\n\n\n\n\n\n\n\n\n")
    else:
        if st.session_state["quest_num_alts"] != 0:
            # Campos de entrada para a pergunta e alternativas
            with st.form(key="question_form"):
                st.write("### Adicionar Questão:")
                enunciate = st.text_area(
                    "Digite o enunciado da questão:",
                    placeholder="Digite sua pergunta aqui",
                )
                alternativas = []
                col1, col2 = st.columns([10, 8])
                with col1:
                    st.write("↓ Marque ✅ 1 ou + alternativas corretas")
                for i in range(st.session_state["quest_num_alts"]):
                    col1, col2, col3 = st.columns([1, 1, 20])
                    with col1:
                        st.write(f"\n")
                        st.write(f"\n")
                        is_true = st.checkbox(
                            "",
                            key=f"new_is_true_{i}",
                            value=False,
                        )
                    with col2:
                        st.write(f"\n")
                        st.write(f"\n")
                        st.write(f"\n")

                        st.write(f"{letter_alternatives[i]})")
                    with col3:
                        alternative_text = st.text_area(
                            "",
                            placeholder="Digite uma alternativa aqui",
                            key=f"new_alt_{i}",
                            height=80,
                        )
                        alternativas.append(
                            {
                                "text": alternative_text,
                                "is_true": is_true,
                                "explanation": "",
                            }
                        )
                    st.write("---")
                st.write("\n")

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
            with st.expander("### Questões Salvas", expanded=True):
                st.write("### Questões:")
                if st.session_state.questions:
                    for idx, question in enumerate(st.session_state.questions):
                        st.write(f"#### Questão {idx + 1}.")
                        st.write(f"{question['enunciate']}")
                        for alt_idx, alt in enumerate(question["alternatives"]):
                            status = "✅" if alt["is_true"] else ""
                            st.write(
                                f"{status} {letter_alternatives[alt_idx]}) {alt['text']}"
                            )
                            st.write(f"Explicação: {alt['explanation']}")
                            st.write(f"\n")
                        col1, col2 = st.columns([1, 7])
                        with col1:
                            st.button(
                                "Editar",
                                key=f"edit_quest_button_{idx}",
                                on_click=lambda idx=idx: start_editing_question(idx),
                            )
                        with col2:
                            st.button(
                                "Excluir",
                                key=f"delete_quest_button_{idx}",
                                on_click=lambda idx=idx: st.session_state.questions.pop(
                                    idx
                                ),
                            )
                        st.write("---")  # Adiciona um delimitador entre perguntas
                else:
                    st.write("Nenhuma pergunta adicionada ainda.")

        if st.session_state["editing_quest"] == True:
            with st.form(key="edit_question_form"):
                st.write("### Editar Questão:")
                question = st.session_state.questions[
                    st.session_state["edit_quest_index"]
                ]
                enunciate = st.text_area(
                    "Edite o enunciado da questão:", value=question["enunciate"]
                )
                alternatives = []
                for idx, alt in enumerate(question["alternatives"]):
                    col1, col2, col3 = st.columns([1, 20, 1])
                    with col1:
                        st.write(f"\n")
                        st.write(f"\n")
                        st.write(f"\n")
                        st.write(f"{letter_alternatives[idx]})")
                    with col2:
                        alternative_text = st.text_area(
                            "",
                            value=f"{alt['text']}",
                            key=f"edit_alt_{idx}",
                        )
                        question["alternatives"][idx]["text"] = alternative_text
                    with col3:
                        st.write(f"\n")
                        st.write(f"\n")
                        is_true = st.checkbox(
                            "",
                            key=f"edit_is_true_{idx}",
                            value=alt["is_true"],
                        )
                    explanation_text = st.text_area(
                        f"Explicação",
                        value=alt["explanation"],
                        key=f"edit_exp_{idx}",
                    )
                    st.write("\n")
                    alternatives.append(
                        {
                            "text": alternative_text,
                            "is_true": is_true,
                            "explanation": explanation_text,
                        }
                    )
                col1, col2 = st.columns([1, 7])
                with col1:
                    if st.form_submit_button("Salvar"):
                        st.session_state.questions[
                            st.session_state["edit_quest_index"]
                        ] = {
                            "enunciate": enunciate,
                            "alternatives": alternatives,
                        }
                        st.success("Questão editada com sucesso")
                        st.session_state["editing_quest"] = False
                        st.rerun()
                with col2:
                    if st.form_submit_button("Cancelar"):
                        st.warning("Edição cancelada")
                        st.session_state["editing_quest"] = False
                        st.rerun()

        if st.button("Gerar Prova", key="genereta_bottom_button"):
            if st.session_state.questions:
                pdf_buffer = generate_pdf(st.session_state.questions)
                st.success("Prova gerada com sucesso! Baixe o arquivo abaixo:")
                st.download_button(
                    label="Download PDF",
                    data=pdf_buffer,
                    file_name="prova.pdf",
                    mime="application/pdf",
                )
                st.session_state["generating_test"] = False
            else:
                st.warning("Nenhuma pergunta disponível para gerar a prova.")


if __name__ == "__main__":
    main()
