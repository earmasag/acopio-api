from io import BytesIO
import uuid
import qrcode
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

router = APIRouter()

@router.get("/pdf", summary="Generar PDF con etiquetas QR")
def generate_qrs_pdf(pages: int = Query(1, ge=1, le=100)):
    """
    Genera un documento PDF con 8 códigos QR por página.
    Cada código QR contiene un UUID único que luego será registrado 
    en el sistema cuando el voluntario lo escanee.
    """
    buffer = BytesIO()
    # A4 size in points: 595.27 x 841.89
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    cols = 2
    rows = 4
    col_width = width / cols
    row_height = height / rows
    qr_size = 200  # QR más grande (era 130)
    font_size = 7  # UUID más pequeño (era 10)
    
    for _ in range(pages):
        for row in range(rows):
            for col in range(cols):
                # Coordenadas de la celda (esquina inferior izquierda)
                x_cell = col * col_width
                y_cell = height - ((row + 1) * row_height)
                
                # Generar UUID
                qr_id = str(uuid.uuid4())
                
                # Generar imagen QR
                qr = qrcode.make(qr_id)
                qr_buffer = BytesIO()
                qr.save(qr_buffer, format="PNG")
                qr_buffer.seek(0)
                qr_image = ImageReader(qr_buffer)
                
                # Centrar QR en la celda
                x_qr = x_cell + (col_width - qr_size) / 2
                y_qr = y_cell + (row_height - qr_size) / 2 + 10
                
                # Dibujar QR
                c.drawImage(qr_image, x_qr, y_qr, width=qr_size, height=qr_size)
                
                # Dibujar UUID debajo del QR con fuente pequeña
                c.setFont("Helvetica", font_size)
                c.drawCentredString(x_cell + col_width / 2, y_qr - 12, qr_id)
        
        c.showPage()
    
    c.save()
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=acopio_etiquetas.pdf"}
    )

@router.get("/center/{token_hash}", summary="Generar QR individual")
def generate_center_qr(token_hash: str):
    """
    Genera una imagen PNG con el código QR para un token de centro de acopio específico.
    Ideal para mostrar en pantalla o imprimir individualmente.
    """
    qr = qrcode.make(token_hash)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="image/png"
    )
