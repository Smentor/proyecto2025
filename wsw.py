import os
import requests
import json
from flask import Flask, request, jsonify

# Configurar la clave de API de OpenAI
os.environ["OPENAI_API_KEY"] = "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"

prompt1 = """
Eres un asistente que recibe un texto con información de instalación de internet y debe devolver
un JSON con las siguiente estructura y claves:

{
  "Datos_cliente": "FECHA_INSTALACION: jueves 26 de diciembre, HORA_INSTALACION: 8:30am a 11:00 am, NOMBRE_COMPLETO: MARCO ANTONIO FALCON AYBAR, DNI_RUC_CE: 29696646, CELULAR: 959787089, DIRECCION: urbanisación las terraaasas A-1 Paucarpata, PLAN_MEGAS: 1000, CORDENADA_MAPS: https://maps.app.goo.gl/bekAbdqYYDCkvE557, CORREO: marfay2007@hotmail.com, OBSERVACIONES: Con 4 tvs Total a pagar 104. Mensual Ryucra"
}


el resto de información dentro del campo "observaciones", en caso que exista. En ese orden.
Por favor, responde únicamente con el JSON. Nada de texto adicional, ni explicaciones.
Evita devolver campos con saltos de línea.
"""

def enviar_texto_a_chatgpt(texto, modelo="gpt-3.5-turbo", temperatura=0.7):
    """
    Envía un texto al modelo ChatGPT usando únicamente la librería requests.

    :param texto: (str) Mensaje que se envía al modelo.
    :param modelo: (str) Modelo a usar (ej: "gpt-3.5-turbo" o "gpt-4").
    :param temperatura: (float) Controla la creatividad de la respuesta (0.0 - 1.0).
    :return: (dict) Un diccionario de Python con el JSON parseado que devuelve el modelo.
                  Si no es posible parsear como JSON, se retorna un dict con un error.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    data = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": prompt1},
            {"role": "user", "content": texto}
        ],
        "temperature": temperatura
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()

        respuesta_json = response.json()
        contenido_respuesta = respuesta_json["choices"][0]["message"]["content"].strip()

        # Intentamos parsear el contenido como JSON
        try:
            parsed_json = json.loads(contenido_respuesta)
            return parsed_json
        except json.JSONDecodeError:
            # Si no se pudo parsear, devolvemos un dict con el error y la respuesta cruda
            return {
                "error": "No se pudo parsear el contenido como JSON válido",
                "raw_response": contenido_respuesta
            }

    except requests.exceptions.RequestException as e:
        return {
            "error": f"Ocurrió un error al conectarse con la API: {str(e)}"
        }
    except KeyError:
        return {
            "error": "No se pudo encontrar la clave adecuada en la respuesta de la API."
        }

# Crear la app Flask
app = Flask(__name__)

@app.route('/procesar', methods=['GET'])
def procesar_mensaje():
    # Obtener el parámetro GET 'mensaje_usuario'
    mensaje_usuario = request.args.get('mensaje_usuario')
    if not mensaje_usuario:
        return jsonify({"error": "El parámetro 'mensaje_usuario' es obligatorio."}), 400

    # Procesar el mensaje usando la función existente
    respuesta = enviar_texto_a_chatgpt(mensaje_usuario)
    return jsonify(respuesta)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
