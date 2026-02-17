import streamlit as st
import fitz
from io import BytesIO

st.set_page_config(page_title="Murlidhar PDF Tool", layout="wide")
st.title("🔥 Murlidhar Academy PDF Marketing Tool")

uploaded_file = st.file_uploader("Upload PDF (A4 Recommended)", type=["pdf"])

# ---------------- CONFIG ----------------
DEFAULT_FONT_SIZE = 9
DEFAULT_HEADER_MARGIN = 0.02
DEFAULT_FOOTER_MARGIN = 0.00

def inch_to_point(inch):
    return inch * 72

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

def parse_page_range(range_text, total_pages):
    pages = set()
    parts = range_text.split(",")
    for part in parts:
        if "-" in part:
            start, end = part.split("-")
            for i in range(int(start)-1, int(end)):
                pages.add(i)
        else:
            pages.add(int(part)-1)
    return [p for p in pages if 0 <= p < total_pages]

# ---------------- PAGE SELECTION ----------------
st.subheader("📄 Page Selection")

page_option = st.selectbox(
    "Apply Changes To",
    ["All Pages", "First Page Only", "Custom Page Range"]
)

custom_range = ""
if page_option == "Custom Page Range":
    custom_range = st.text_input("Enter Page Numbers (Example: 1-3,5)")

# ---------------- HEADER ----------------
st.subheader("📝 Header Settings")

header_text = st.text_input(
    "Header Text",
    value="CLICK HERE FOR MORE UPDATES AND STUDY MATERIALS | JOIN MURLIDHAR ACADEMY WHATSAPP GROUP"
)

header_alignment = st.selectbox("Header Alignment", ["left", "center", "right"], index=1)
header_font_size = st.number_input("Header Font Size", 6, 50, DEFAULT_FONT_SIZE)
header_color = st.color_picker("Header Color", "#008000")
header_margin = st.number_input("Header Top Margin (inch)", 0.0, 2.0, DEFAULT_HEADER_MARGIN)

upper_half_link = st.text_input(
    "Upper Half Page Link",
    value="https://api.whatsapp.com/send?phone=917878186867&text=JOIN%20ME%20IN%20MURLIDHAR%20ACADEMY%20WHATSAPP%20GROUP"
)

# ---------------- FOOTER ----------------
st.subheader("📝 Footer Settings")

footer_text = st.text_input(
    "Footer Text",
    value="CLICK HERE FOR MORE UPDATES AND STUDY MATERIALS | JOIN MURLIDHAR ACADEMY TELEGRAM CHANNEL"
)

footer_alignment = st.selectbox("Footer Alignment", ["left", "center", "right"], index=1)
footer_font_size = st.number_input("Footer Font Size", 6, 50, DEFAULT_FONT_SIZE)
footer_color = st.color_picker("Footer Color", "#0000FF")
footer_margin = st.number_input("Footer Bottom Margin (inch)", 0.0, 2.0, DEFAULT_FOOTER_MARGIN)

bottom_half_link = st.text_input(
    "Bottom Half Page Link",
    value="https://t.me/MurlidharAcademy"
)

# ---------------- OPTIONAL FULL PAGE LINK ----------------
st.subheader("🔗 Optional Full Page Link")
full_page_link = st.text_input("Full Page Link (Leave Blank If Not Needed)")

# ---------------- PROCESS ----------------
if st.button("🚀 Generate Modified PDF") and uploaded_file:

    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    total_pages = len(doc)

    if page_option == "All Pages":
        pages_to_edit = range(total_pages)
    elif page_option == "First Page Only":
        pages_to_edit = [0]
    else:
        pages_to_edit = parse_page_range(custom_range, total_pages)

    header_rgb = hex_to_rgb(header_color)
    footer_rgb = hex_to_rgb(footer_color)

    for i in pages_to_edit:
        page = doc[i]
        width = page.rect.width
        height = page.rect.height

        # -------- LINKS --------
        if full_page_link.strip():
            page.insert_link({
                "kind": fitz.LINK_URI,
                "from": fitz.Rect(0, 0, width, height),
                "uri": full_page_link
            })

        if upper_half_link.strip():
            page.insert_link({
                "kind": fitz.LINK_URI,
                "from": fitz.Rect(0, 0, width, height/2),
                "uri": upper_half_link
            })

        if bottom_half_link.strip():
            page.insert_link({
                "kind": fitz.LINK_URI,
                "from": fitz.Rect(0, height/2, width, height),
                "uri": bottom_half_link
            })

        # -------- HEADER --------
        if header_text.strip():
            y = inch_to_point(header_margin)
            header_rect = fitz.Rect(0, y, width, y + 20)

            align_value = 1 if header_alignment == "center" else 2 if header_alignment == "right" else 0

            page.insert_textbox(
                header_rect,
                header_text,
                fontsize=header_font_size,
                color=header_rgb,
                align=align_value
            )

        # -------- FOOTER (VISIBLE FIXED) --------
        if footer_text.strip():

            bottom_margin_points = inch_to_point(footer_margin)

            y_top = height - bottom_margin_points - 20
            y_bottom = height - bottom_margin_points

            footer_rect = fitz.Rect(
                0,
                y_top,
                width,
                y_bottom
            )

            align_value = 1 if footer_alignment == "center" else 2 if footer_alignment == "right" else 0

            page.insert_textbox(
                footer_rect,
                footer_text,
                fontsize=footer_font_size,
                color=footer_rgb,
                align=align_value
            )

    output = BytesIO()
    doc.save(output)
    doc.close()

    st.success("✅ PDF Modified Successfully!")

    st.download_button(
        "📥 Download Modified PDF",
        data=output.getvalue(),
        file_name=uploaded_file.name,
        mime="application/pdf"
    )
