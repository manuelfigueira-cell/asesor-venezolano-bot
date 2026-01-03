# -*- coding: utf-8 -*-
"""
Archivo de acciones personalizadas corregido y optimizado
para el Asistente Emprendedor Venezolano.
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, ActiveLoop
from rasa_sdk.forms import FormValidationAction
import random
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# ACCIONES DE VALIDACIÓN DE FORMULARIOS
# =============================================================================

class ValidateFormRegistroCompleto(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_registro_completo"

    async def validate_tipo_empresa(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Valida el tipo de empresa."""
        valid_types = ["c.a.", "compañía anónima", "s.r.l.", "sociedad de responsabilidad limitada", 
                      "firma personal", "persona natural", "empresa de responsabilidad limitada"]
        
        if value.lower() in valid_types:
            return {"tipo_empresa": value}
        else:
            dispatcher.utter_message(response="utter_tipo_empresa_invalido")
            return {"tipo_empresa": None}

    async def validate_tipo_negocio(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Valida el tipo de negocio."""
        if value and len(value) > 2:
            return {"tipo_negocio": value}
        else:
            dispatcher.utter_message(text="Por favor, especifica qué tipo de negocio tienes o planeas tener.")
            return {"tipo_negocio": None}

    async def validate_capital_inicial(
        self,
        value: float,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Valida el capital inicial."""
        if value and value > 0:
            return {"capital_inicial": value}
        else:
            dispatcher.utter_message(text="Por favor, ingresa un monto válido para tu capital inicial en USD.")
            return {"capital_inicial": None}

class ValidateFormAnalisisViabilidad(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_analisis_viabilidad"

    async def validate_experiencia_negocio(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Valida la experiencia en el negocio."""
        if value and value.lower() in ["sí", "si", "sí tengo", "si tengo", "no", "no tengo"]:
            return {"experiencia_negocio": value}
        else:
            dispatcher.utter_message(text="Por favor, responde con 'sí' o 'no' si tienes experiencia en este tipo de negocio.")
            return {"experiencia_negocio": None}

# =============================================================================
# ACCIONES JURÍDICAS
# =============================================================================

class ActionRecomendarEstructuraLegal(Action):
    """Analiza y recomienda la estructura legal más adecuada."""
    
    def name(self) -> Text:
        return "action_recomendar_estructura_legal"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        tipo_empresa = tracker.get_slot("tipo_empresa")
        
        if not tipo_empresa:
            dispatcher.utter_message(response="utter_preguntar_tipo_empresa")
            return []

        tipo_empresa_lower = tipo_empresa.lower()
        
        if "c.a." in tipo_empresa_lower or "compañía anónima" in tipo_empresa_lower:
            message = self._get_message_ca()
        elif "s.r.l." in tipo_empresa_lower or "sociedad de responsabilidad limitada" in tipo_empresa_lower:
            message = self._get_message_srl()
        elif "firma personal" in tipo_empresa_lower or "persona natural" in tipo_empresa_lower:
            message = self._get_message_firma_personal()
        else:
            message = self._get_message_generico()

        dispatcher.utter_message(text=message)
        return []

    def _get_message_ca(self) -> Text:
        return """🏢 **COMPAÑÍA ANÓNIMA (C.A.)** - Ideal para proyectos con visión de crecimiento

✅ **VENTAJAS:**
• **Responsabilidad Limitada:** Tu patrimonio personal está protegido
• **Captación de Capital:** Puedes emitir acciones para inversionistas
• **Imagen Corporativa:** Transmite seriedad y confianza
• **Transferibilidad:** Las acciones se transfieren fácilmente

⚠️ **CONSIDERACIONES:**
• Constitución más compleja y costosa
• Requiere Junta Directiva y Asamblea de Accionistas
• Mayor regulación y control

💡 **Recomendación:** Perfecta si planeas buscar inversionistas o cotizar en bolsa."""

    def _get_message_srl(self) -> Text:
        return """🏪 **SOCIEDAD DE RESPONSABILIDAD LIMITADA (S.R.L.)** - La opción más popular para PYMES

✅ **VENTAJAS:**
• **Responsabilidad Limitada:** Protege tu patrimonio personal
• **Estructura Sencilla:** Menos complejidad administrativa
• **Flexibilidad:** Ideal para pocos socios (familiares o amigos)
• **Menores Costos:** Constitución y mantenimiento más económicos

⚠️ **CONSIDERACIONES:**
• Transferencia de participaciones más restrictiva
• Límite máximo de socios (generalmente 20)

💡 **Recomendación:** La mejor opción para la mayoría de emprendimientos en Venezuela."""

    def _get_message_firma_personal(self) -> Text:
        return """👤 **FIRMA PERSONAL** - Solo para riesgo muy bajo

✅ **VENTAJAS:**
• Mínimos trámites y costos iniciales
• Control total sobre las decisiones
• Rapidez para empezar operaciones

🚨 **DESVENTAJAS CRÍTICAS:**
• **RESPONSABILIDAD ILIMITADA:** Respondes con TODOS tus bienes personales
• Dificultad para acceder a financiamiento formal
• Limitaciones para crecer y asociarse
• Sin protección patrimonial

💡 **Recomendación:** Úsalo solo para probar ideas. Transición a S.R.L. tan pronto como sea viable."""

    def _get_message_generico(self) -> Text:
        return """🤔 **No reconozco esa estructura empresarial**

Las opciones más comunes en Venezuela son:

• **C.A.** (Compañía Anónima) - Para negocios que buscan inversionistas
• **S.R.L.** (Sociedad de Responsabilidad Limitada) - Ideal para PYMES
• **Firma Personal** - Solo para riesgo muy bajo

¿Podrías especificar cuál de estas te interesa?"""

class ActionCalcularCostosFormalizacion(Action):
    """Calcula costos estimados de formalización."""
    
    def name(self) -> Text:
        return "action_calcular_costos_formalizacion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Costos base en USD (valores estimativos 2024)
        costos_base = {
            "saren_registro": 180,
            "rif": 25,
            "honorarios_abogado": 400,
            "legalizacion_libros": 60,
            "publicacion_gaceta": 30
        }
        
        municipio = tracker.get_slot("municipio")
        costo_patente = self._calcular_patente_municipal(municipio)
        total_costos = sum(costos_base.values()) + costo_patente

        message = f"""
💰 **ESTIMACIÓN DE COSTOS DE FORMALIZACIÓN**

**GASTOS DE CONSTITUCIÓN:**
• Registro SAREN: ${costos_base['saren_registro']}
• Honorarios de Abogado: ${costos_base['honorarios_abogado']}
• Legalización Libros: ${costos_base['legalizacion_libros']}
• Publicación Gaceta: ${costos_base['publicacion_gaceta']}

**GASTOS FISCALES Y MUNICIPALES:**
• RIF SENIAT: ${costos_base['rif']}
• Patente Municipal ({municipio if municipio else 'estimado'}): ${costo_patente}

💎 **TOTAL ESTIMADO: ${total_costos} USD**

*Nota: Valores aproximados. Pueden variar según complejidad y honorarios profesionales.*
"""
        
        dispatcher.utter_message(text=message)
        return [SlotSet("costo_estimado_formalizacion", total_costos)]

    def _calcular_patente_municipal(self, municipio: Text) -> float:
        """Calcula costo de patente según municipio."""
        if not municipio:
            return 80.0
            
        municipio_lower = municipio.lower()
        if municipio_lower in ["chacao", "baruta", "sucre"]:
            return 150.0
        elif municipio_lower in ["maracaibo", "valencia"]:
            return 120.0
        else:
            return 80.0

# =============================================================================
# ACCIONES ECONÓMICAS
# =============================================================================

class ActionAnalizarViabilidad(Action):
    """Analiza viabilidad del negocio con enfoque venezolano."""
    
    def name(self) -> Text:
        return "action_analizar_viabilidad"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        capital = tracker.get_slot("capital_inicial") or 0
        experiencia = tracker.get_slot("experiencia_negocio")
        tipo_negocio = tracker.get_slot("tipo_negocio")

        # Análisis de riesgo
        riesgo_score, recomendaciones = self._analizar_riesgo(capital, experiencia, tipo_negocio)
        nivel_riesgo = self._determinar_nivel_riesgo(riesgo_score)

        message = f"""
📊 **ANÁLISIS DE VIABILIDAD PRELIMINAR**

**NIVEL DE RIESGO: {nivel_riesgo}**

**RECOMENDACIONES ESTRATÉGICAS:**
"""
        
        for rec in recomendaciones:
            message += f"• {rec}\n"

        message += "\n*Este es un análisis preliminar. Un estudio de mercado detallado es esencial.*"
        
        dispatcher.utter_message(text=message)
        return [SlotSet("nivel_riesgo", nivel_riesgo)]

    def _analizar_riesgo(self, capital: float, experiencia: Text, tipo_negocio: Text) -> tuple:
        """Analiza el riesgo y genera recomendaciones."""
        riesgo_score = 0
        recomendaciones = []

        # Análisis de capital
        if capital < 2000:
            riesgo_score += 3
            recomendaciones.append("💰 **Capital bajo:** Considera empezar con modelo 'lean' o buscar financiamiento complementario.")
        elif capital < 8000:
            riesgo_score += 1
            recomendaciones.append("💰 **Capital moderado:** Enfócate en control estricto de gastos y liquidez.")
        else:
            recomendaciones.append("💰 **Capital sólido:** Excelente base para ejecutar tu plan de negocio.")

        # Análisis de experiencia
        if experiencia and experiencia.lower() in ["no", "no tengo"]:
            riesgo_score += 2
            recomendaciones.append("🎓 **Sin experiencia:** Busca un mentor y capacítate en el sector.")
        elif experiencia and experiencia.lower() in ["sí", "si", "sí tengo", "si tengo"]:
            recomendaciones.append("🎓 **Con experiencia:** Tu conocimiento del sector es una ventaja competitiva.")

        # Análisis de tipo de negocio
        if tipo_negocio:
            if any(word in tipo_negocio.lower() for word in ["alimentos", "restaurante", "comida"]):
                riesgo_score += 1
                recomendaciones.append("🏭 **Sector regulado:** Cumple estrictamente con normas sanitarias.")

        return riesgo_score, recomendaciones

    def _determinar_nivel_riesgo(self, score: int) -> Text:
        """Determina el nivel de riesgo basado en el score."""
        if score >= 5:
            return "🔴 CRÍTICO - Reevalúa tu plan de negocio"
        elif score >= 3:
            return "🟠 ALTO - Sé extremadamente cuidadoso con tus finanzas"
        else:
            return "🟢 MODERADO - Buenas perspectivas con ejecución adecuada"

class ActionGenerarPlanFinanciero(Action):
    """Genera estructura de plan financiero adaptado a Venezuela."""
    
    def name(self) -> Text:
        return "action_generar_plan_financiero"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = """
📈 **ESTRUCTURA DE PLAN FINANCIERO - CONTEXTO VENEZOLANO**

**1. PROYECCIONES DE VENTAS (en USD):**
• Estimación mensual conservadora para el primer año
• Desglose por producto/servicio si aplica

**2. ESTRUCTURA DE COSTOS:**
• **Costos Fijos:** Alquiler, salarios, servicios, seguros
• **Costos Variables:** Materia prima, comisiones, logística

**3. ESTADO DE RESULTADOS PROYECTADO:**
• Ventas - Costos Variables = Margen de Contribución
• Margen - Costos Fijos = Utilidad Neta

**4. FLUJO DE CAJA (CRÍTICO EN VENEZUELA):**
• Proyección semanal o quincenal en USD
• Calcula tu Punto de Equilibrio
• Mantén colchón de 3-6 meses de gastos

**5. ANÁLISIS DE SENSIBILIDAD:**
• ¿Qué pasa si las ventas bajan 20%?
• ¿Y si los costos suben 30%?

💡 **Consejo clave:** Trabaja siempre en USD para planificación, convierte a bolívares para operaciones.
"""
        
        dispatcher.utter_message(text=message)
        return []

# =============================================================================
# ACCIONES OPERATIVAS
# =============================================================================

class ActionSugerirSistemaInventario(Action):
    """Sugiere sistema de gestión de inventario."""
    
    def name(self) -> Text:
        return "action_sugerir_sistema_inventario"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = """
📦 **SISTEMA DE GESTIÓN DE INVENTARIO RECOMENDADO**

**1. MÉTODO DE VALORACIÓN: FIFO (First-In, First-Out)**
• En contexto inflacionario, vendes productos más antiguos primero
• Refleja ganancias más reales
• Evita obsolescencia

**2. CLASIFICACIÓN ABC:**
• **Artículos A (20%):** 80% del valor - Control estricto diario
• **Artículos B (30%):** 15% del valor - Control semanal
• **Artículos C (50%):** 5% del valor - Control mensual simple

**3. HERRAMIENTAS RECOMENDADAS:**
• **Básico:** Excel/Google Sheets con plantillas
• **Intermedio:** Software de gestión de inventario
• **Avanzado:** Sistemas ERP integrados

🔑 **La clave es la disciplina en la actualización constante.**
"""
        
        dispatcher.utter_message(text=message)
        return []

# =============================================================================
# ACCIONES DE RESPUESTA RÁPIDA
# =============================================================================

class ActionProcesoLicenciasMunicipales(Action):
    """Describe proceso de licencias municipales."""
    
    def name(self) -> Text:
        return "action_proceso_licencias_municipales"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        municipio = tracker.get_slot("municipio")
        tipo_negocio = tracker.get_slot("tipo_negocio")

        message = f"""
🏛️ **PROCESO DE LICENCIAS MUNICIPALES**

**1. CONFORMIDAD DE USO (Urbanismo):**
• Verifica que el local sea apto para tu actividad
• **¡Obtén esto ANTES de firmar contrato de alquiler!**

**2. PATENTE MUNICIPAL (Hacienda):**
• Impuesto basado en ingresos brutos estimados
• Necesitas RIF y documentos de la propiedad

**3. CERTIFICADO DE BOMBEROS:**
• Inspección de seguridad obligatoria
• Requisitos: extintores, salidas de emergencia, instalación segura
"""

        if tipo_negocio and "alimento" in tipo_negocio.lower():
            message += """
**4. PERMISO SANITARIO (Específico para alimentos):**
• Ministerio de Salud de tu estado
• Curso de manipulación de alimentos obligatorio
"""

        message += f"\n📍 **Visita la página web de la Alcaldía de {municipio if municipio else 'tu municipio'} para requisitos específicos.**"
        
        dispatcher.utter_message(text=message)
        return []

class ActionRecomendarFinanciamiento(Action):
    """Recomienda fuentes de financiamiento."""
    
    def name(self) -> Text:
        return "action_recomendar_financiamiento"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = """
💳 **FUENTES DE FINANCIAMIENTO EN VENEZUELA**

**1. BANCA COMERCIAL:**
• **Microcréditos Productivos** ($1,000-10,000 USD)
• **Tasas:** Indexadas a UVC del BCV
• **Requisitos:** Empresa formalizada + historial

**2. FINANCIAMIENTO ALTERNATIVO:**
• **Inversores Ángeles:** Para startups innovadoras
• **Capital Riesgo:** Para alto crecimiento y escalabilidad

**3. BOOTSTRAPPING (Recomendado para empezar):**
• Ahorros personales + reinversión de utilidades
• Máximo control y 0% de interés
• Ideal para validar modelo de negocio

🎯 **Estrategia recomendada:** Comienza con bootstrapping, escala con microcréditos.
"""
        
        dispatcher.utter_message(text=message)
        return []

# =============================================================================
# ACCIONES DE RESPUESTA Y FALLBACK
# =============================================================================

class ActionProporcionarAsesoriaCompleta(Action):
    """Proporciona asesoría completa integrando toda la información."""
    
    def name(self) -> Text:
        return "action_proporcionar_asesoria_completa"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Recopilar información de slots
        tipo_empresa = tracker.get_slot("tipo_empresa") or "No definida"
        tipo_negocio = tracker.get_slot("tipo_negocio") or "No definido"
        capital = tracker.get_slot("capital_inicial") or 0
        municipio = tracker.get_slot("municipio") or "No definido"
        experiencia = tracker.get_slot("experiencia_negocio") or "No definida"
        nivel_riesgo = tracker.get_slot("nivel_riesgo") or "No evaluado"

        message = f"""
🎯 **PLAN DE ACCIÓN PERSONALIZADO**

**RESUMEN DE TU PROYECTO:**
• Estructura Legal: {tipo_empresa}
• Giro del Negocio: {tipo_negocio}
• Capital Inicial: ${capital} USD
• Municipio: {municipio}
• Experiencia: {experiencia}
• Nivel de Riesgo: {nivel_riesgo}

**PRÓXIMOS PASOS CRÍTICOS:**

1. **CONSTITUCIÓN LEGAL:**
   • Contacta abogado para {tipo_empresa} en SAREN
   • Legaliza libros contables (Diario, Mayor, Inventario)

2. **REGISTRO FISCAL:**
   • Solicita RIF en portal del SENIAT
   • Prepara espacio para cartelera fiscal

3. **PERMISOS MUNICIPALES:**
   • Gestiona Conformidad de Uso en {municipio}
   • Obtén Patente Municipal y Certificado de Bomberos

4. **PLANIFICACIÓN FINANCIERA:**
   • Construye tu plan financiero en USD
   • Prioriza control de flujo de caja semanal

5. **PROTECCIÓN DE ACTIVOS:**
   • Considera registro de marca en SAPI
   • Realiza búsqueda de anterioridades

🚀 **La formalidad es tu mejor herramienta para crecer con seguridad.**
"""
        
        dispatcher.utter_message(text=message)
        return [SlotSet("asesoria_completa_dada", True)]

class ActionDefaultFallback(Action):
    """Maneja fallbacks de manera inteligente."""
    
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        fallback_messages = [
            "No estoy seguro de haber entendido. ¿Podrías reformular tu pregunta?",
            "Esa consulta se me escapa. ¿Qué tal si hablamos de trámites legales, finanzas o gestión de negocio?",
            "No tengo una respuesta específica para eso. ¿Puedo ayudarte con registro de empresas, planificación financiera u obligaciones tributarias?",
            "Mi especialidad es el emprendimiento en Venezuela. ¿Tienes alguna pregunta sobre formalización, finanzas o gestión operativa?"
        ]
        
        dispatcher.utter_message(text=random.choice(fallback_messages))
        
        # Resetear cualquier formulario activo
        return [ActiveLoop(None)]