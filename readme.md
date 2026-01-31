# 🌟 Mercado Don Onofre - E-commerce Gourmet

**Sistema de e-commerce completo integrado con AdamsPay**  
*Plataforma profesional para venta de productos gourmet*

https://don-onofre-adamspay.onrender.com/

---

## 📋 Resumen del Proyecto

Mercado Don Onofre es una plataforma de e-commerce especializada en productos gourmet, delicatessen y alimentos premium. El sistema incluye:

- 🛒 **Catálogo de productos** con filtros por categorías
- 💳 **Integración completa** con AdamsPay para procesamiento de pagos
- 📱 **Interfaz responsive** optimizada para todos los dispositivos
- 📊 **Historial de pedidos** con seguimiento en tiempo real
- 🔧 **Panel administrativo** Django para gestión de órdenes
- 🚀 **Despliegue automatizado** en Render

---

## 🏗️ Arquitectura del Sistema

### **Stack Tecnológico**
```
Frontend:
├── HTML5 + CSS3 (ES6+)
├── Font Awesome 6.4.0
├── Vanilla JavaScript
└── Diseño responsive con CSS Grid/Flexbox

Backend:
├── Django 6.0.1
├── Django REST Framework 3.16.1
├── PostgreSQL (Render)
└── Gunicorn + Whitenoise

Infraestructura:
├── Render.com (Hosting)
├── AdamsPay (Pasarela de pagos)
└── GitHub (Control de versiones)
```

---

## 📁 Estructura del Proyecto

```
don-onofre-adamspay/
├── dononofre/                    # Proyecto Django principal
│   ├── settings.py              # Configuración del proyecto
│   ├── urls.py                  # URLs principales
│   └── wsgi.py                  # Configuración WSGI
│
├── orders/                      # Aplicación Django de órdenes
│   ├── models.py               # Modelos de datos (Order)
│   ├── views.py               # Lógica de negocio
│   ├── serializers.py         # Serializadores API
│   ├── urls.py                # Rutas API
│   └── templates/             # Plantillas HTML
│       ├── index.html         # Página principal
│       └── payment_result.html # Resultado de pago
│
├── staticfiles/css/            # Estilos CSS
│   ├── styles.css             # Estilos principales
│   └── payment_result.css     # Estilos de resultado
│
├── requirements.txt            # Dependencias Python
├── render.yaml                # Configuración Render
├── manage.py                  # CLI Django
│
├── Scripts de automatización:
├── startup.sh                # Script de inicio (Render)
├── run.sh                   # Script de desarrollo local
├── setup_env.sh             # Configuración de entorno
├── build.sh                 # Build en Render
└── force_migrations.py      # Forzar migraciones
```

---

## 🔧 Características Principales

### **1. Sistema de Compras**
- ✅ Catálogo de productos con 8 categorías
- ✅ Filtros dinámicos por tipo (Gourmet, Orgánico, Bebidas, Panadería)
- ✅ Carrito de compras persistente
- ✅ Precios formateados en guaraníes (₲)

### **2. Integración de Pagos**
- ✅ **AdamsPay** como pasarela principal
- ✅ Webhooks para notificaciones en tiempo real
- ✅ URLs de retorno automático
- ✅ Modo simulación para desarrollo
- ✅ Manejo de estados (PENDING, PAID, FAILED)

### **3. Gestión de Órdenes**
- ✅ Historial completo de pedidos
- ✅ Actualización en tiempo real
- ✅ Filtros por estado
- ✅ Persistencia en localStorage + PostgreSQL
- ✅ Botones de acción contextuales

### **4. Interfaz de Usuario**
- ✅ Diseño responsive (mobile-first)
- ✅ Animaciones y transiciones suaves
- ✅ Iconografía Font Awesome
- ✅ Validación de formularios en tiempo real
- ✅ Mensajes de confirmación y error

---

## 🚀 Instalación y Configuración

### **Requisitos Previos**
```bash
Python 3.11+
PostgreSQL (opcional para desarrollo local)
Cuenta en Render.com
Cuenta en AdamsPay (para pagos reales)
```

### **1. Desarrollo Local**
```bash
# Clonar repositorio
git clone <repo-url>
cd don-onofre-adamspay

# Configurar entorno
chmod +x setup_env.sh
./setup_env.sh

# Iniciar servidor
./run.sh
```

### **2. Variables de Entorno**
Crear archivo `.env` en la raíz:
```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:pass@host/dbname

# AdamsPay
ADAMSPAY_API_KEY=your-adamspay-api-key
ADAMSPAY_APP_SECRET=your-app-secret
ADAMSPAY_BASE_URL=https://staging.adamspay.com
```

### **3. Migraciones**
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Forzar migraciones (si es necesario)
python force_migrations.py
```

---

## 🔌 Integración con AdamsPay

### **Flujo de Pagos**
1. **Creación de pedido** → POST `/api/orders/`
2. **Generación de deuda** → AdamsPay API
3. **Redirección** → URL de pago AdamsPay
4. **Callback** → POST `/api/adams/callback/`
5. **Redirect** → GET `/api/adams/redirect/`
6. **Resultado** → `/payment-result/`

---

## 📡 Endpoints API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Página principal |
| `POST` | `/api/orders/` | Crear nueva orden |
| `GET` | `/api/orders/<uuid>/` | Consultar estado |
| `POST` | `/api/adams/callback/` | Webhook AdamsPay |
| `GET` | `/api/adams/redirect/` | Redirect post-pago |
| `GET` | `/payment-result/` | Resultado de pago |
| `GET` | `/api/test-webhook/<uuid>/` | Probar webhook |

---

## 🎨 Personalización

### **1. Colores Principales**
```css
:root {
    --primary: #1A365D;       /* Azul marino */
    --secondary: #4c4a7c;     /* Púrpura intenso */
    --accent: #1babbe;        /* Turquesa */
    --success: #2e398b;       /* Azul éxito */
    --light: #F8F9FA;         /* Blanco gelo */
}
```

### **2. Modificar Productos**
Editar `orders/templates/index.html`:
- Actualizar productos en la sección `products-container`
- Modificar precios y descripciones
- Agregar nuevas categorías

### **3. Configurar Envíos**
Modificar política de envíos en:
- Línea 284 del `index.html`
- Sección "Información importante para tu compra"

---

## 🚢 Despliegue en Render

### **1. Configuración Automática**
```yaml
# render.yaml
services:
  - type: web
    name: don-onofre-adamspay
    env: python
    buildCommand: ./build.sh
    startCommand: ./startup.sh
```

### **2. Pasos Manuales**
1. Conectar repositorio GitHub a Render
2. Configurar variables de entorno en Render Dashboard
3. Desplegar manualmente o habilitar auto-deploy
4. Verificar migraciones en logs
5. Probar endpoints API

### **3. Variables en Render**
```bash
# Requeridas
DATABASE_URL
DJANGO_SECRET_KEY
ADAMSPAY_API_KEY
ADAMSPAY_APP_SECRET
```

---

## 🧪 Testing

### **1. API Local**
```bash
# Probar creación de orden
curl -X POST http://localhost:8001/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Jamón Ibérico", "amount": 153000}'
```

### **2. Webhook Simulado**
```bash
# Probar webhook manualmente
curl -X GET "http://localhost:8001/api/test-webhook/<order-uuid>/"
```

### **3. Scripts de Prueba**
```bash
# Ejecutar tests de integración
chmod +x test_api.sh
./test_api.sh
```

---

## 📊 Base de Datos

### **Modelo Order**
```python
class Order(models.Model):
    id = UUIDField(primary_key=True)
    product_name = CharField(max_length=100)
    amount = DecimalField(max_digits=10, decimal_places=2)
    status = CharField(choices=STATUS_CHOICES)  # PENDING, PAID, FAILED
    payment_link = URLField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
```

### **Migraciones**
```bash
# Ver estado de migraciones
python manage.py showmigrations

# Crear migración específica
python manage.py makemigrations orders

# Revertir migración
python manage.py migrate orders 0001
```

---

## 🛠️ Solución de Problemas

### **Problemas Comunes**

1. **Migraciones fallan en Render**
   ```bash
   # Ejecutar force_migrations.py
   python force_migrations.py
   ```

2. **AdamsPay no responde**
   - Verificar API key en variables de entorno
   - Confirmar que `ADAMSPAY_BASE_URL` sea correcto
   - Revisar logs de Render para errores de conexión

3. **CSS no carga**
   ```bash
   # Recopilar archivos estáticos
   python manage.py collectstatic --noinput
   ```

4. **Base de datos desconectada**
   - Verificar `DATABASE_URL` en Render
   - Revisar credenciales de PostgreSQL
   - Ejecutar migraciones manualmente

### **Logs en Render**
```bash
# Ver logs en tiempo real
render logs <service-name> --tail

# Filtrar por tipo
render logs <service-name> --type build
render logs <service-name> --type deploy
```

---

## 🔒 Seguridad

### **Buenas Prácticas Implementadas**
- ✅ Variables de entorno para datos sensibles
- ✅ CSRF protection en Django
- ✅ Validación de entrada en API
- ✅ HTTPS forzado en producción
- ✅ Sanitización de datos de usuario
- ✅ Logging de operaciones sensibles

### **Recomendaciones Adicionales**
1. **Rate limiting** en endpoints públicos
2. **Validación HMAC** para webhooks AdamsPay
3. **Backup automático** de base de datos
4. **Monitoreo** con servicios externos
5. **Auditoría** regular de logs

---

## 📈 Mejoras Futuras

### **Prioridad Alta**
- [ ] Sistema de inventario en tiempo real
- [ ] Notificaciones por email/SMS
- [ ] Cupones de descuento
- [ ] Integración con más pasarelas de pago

### **Prioridad Media**
- [ ] Sistema de reseñas y calificaciones
- [ ] Wishlist de productos
- [ ] Programa de fidelidad
- [ ] Dashboard de analytics

### **Prioridad Baja**
- [ ] App móvil nativa
- [ ] Integración con redes sociales
- [ ] Sistema de recomendaciones IA
- [ ] Multi-idioma (Portugués/Inglés)

---

## 👥 Contribución

### **Flujo de Trabajo**
1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m "Add: nueva funcionalidad"`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### **Convenciones**
- **Commits**: Usar prefijos (Add:, Fix:, Update:, Remove:)
- **Código**: Siguir PEP 8 para Python
- **Documentación**: Mantener README actualizado
- **Testing**: Agregar tests para nuevas funcionalidades

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

---

### **Documentación Adicional**
- [Documentación Django](https://docs.djangoproject.com/)
- [AdamsPay API Docs](https://adamspay.com/docs)
- [Render Docs](https://render.com/docs)

---

## ✨ Créditos

**Desarrollado por:** Luis Renan Pavanello 
**Arquitectura:** Django REST + AdamsPay  
**Despliegue:** Render Cloud Platform  

---

**Última actualización:** Enero 2025
**Versión:** 2.0.0  
**Estado:** ✅ Producción  

