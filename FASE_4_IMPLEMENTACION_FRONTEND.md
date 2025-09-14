# 🚀 FASE 4 - GUÍA DE IMPLEMENTACIÓN FRONTEND
## Sistema de Chat Interno y Notificaciones Push

---

## 📋 ESTADO ACTUAL

### ✅ **BACKEND COMPLETADO (100%)**
- ✅ Sistema de Chat Interno completo
- ✅ Sistema de Notificaciones Push implementado
- ✅ Job Scheduler automático funcionando
- ✅ Base de datos estructurada y optimizada
- ✅ APIs RESTful documentadas y testeadas

### 🎯 **OBJETIVO MAÑANA**
Implementar la interfaz frontend para el sistema de chat y notificaciones, integrando con las APIs ya desarrolladas.

---

## 🗂️ ARQUITECTURA DEL FRONTEND

### **Estructura de Componentes Recomendada**
```
src/
├── components/
│   ├── chat/
│   │   ├── ChatContainer.jsx          # Contenedor principal del chat
│   │   ├── ConversationList.jsx       # Lista de conversaciones
│   │   ├── ChatWindow.jsx             # Ventana de chat activa
│   │   ├── MessageBubble.jsx          # Burbuja de mensaje individual
│   │   ├── MessageInput.jsx           # Input para escribir mensajes
│   │   └── UserSearch.jsx             # Búsqueda de usuarios
│   ├── notifications/
│   │   ├── NotificationCenter.jsx     # Centro de notificaciones
│   │   ├── NotificationItem.jsx       # Item individual de notificación
│   │   ├── NotificationBell.jsx       # Campana de notificaciones
│   │   └── NotificationSettings.jsx   # Configuración de notificaciones
│   └── common/
│       ├── FloatingChat.jsx           # Chat flotante/modal
│       └── StatusIndicator.jsx        # Indicador de estado en línea
├── services/
│   ├── chatService.js                 # Servicio para APIs de chat
│   ├── notificationService.js         # Servicio para APIs de notificaciones
│   └── websocketService.js            # WebSocket para tiempo real (futuro)
├── hooks/
│   ├── useChat.js                     # Hook personalizado para chat
│   ├── useNotifications.js            # Hook para notificaciones
│   └── useWebSocket.js                # Hook para WebSocket (futuro)
├── contexts/
│   ├── ChatContext.jsx                # Context para estado global del chat
│   └── NotificationContext.jsx        # Context para notificaciones
└── utils/
    ├── dateUtils.js                   # Utilidades de fecha
    └── chatUtils.js                   # Utilidades específicas del chat
```

---

## 🔌 ENDPOINTS DISPONIBLES

### **Chat Internal**
```javascript
// Obtener conversaciones del usuario
GET /api/chat/conversaciones
// Respuesta: { success: true, conversaciones: [...] }

// Obtener mensajes de una conversación
GET /api/chat/mensajes/{id_contacto}?limite=50
// Respuesta: { success: true, mensajes: [...] }

// Enviar nuevo mensaje
POST /api/chat/enviar
// Body: { id_destinatario, mensaje, tipo_mensaje, prioridad }
// Respuesta: { success: true, id_mensaje, fecha_envio }

// Marcar mensaje como leído
PUT /api/chat/marcar-leido/{id_mensaje}
// Respuesta: { success: true, message: "Mensaje marcado como leído" }

// Obtener usuarios disponibles para chat
GET /api/chat/usuarios-disponibles
// Respuesta: { success: true, usuarios: [...] }

// Buscar mensajes
GET /api/chat/buscar?q={texto}&contacto={id_contacto}
// Respuesta: { success: true, mensajes: [...] }

// Estadísticas de chat
GET /api/chat/estadisticas
// Respuesta: { success: true, estadisticas: {...} }
```

### **Notificaciones Push**
```javascript
// Obtener notificaciones del usuario
GET /api/notificaciones?incluir_leidas=false&limite=50
// Respuesta: { success: true, notificaciones: [...], total: 10 }

// Marcar notificación como leída
PUT /api/notificaciones/{id_notificacion}/leer
// Respuesta: { success: true, message: "Notificación marcada como leída" }

// Estadísticas de notificaciones
GET /api/notificaciones/estadisticas
// Respuesta: { success: true, estadisticas: {...} }
```

---

## 🛠️ SERVICIOS DE FRONTEND

### **1. ChatService.js**
```javascript
class ChatService {
  constructor() {
    this.baseURL = '/api/chat';
    this.token = localStorage.getItem('authToken');
  }

  async getConversations() {
    const response = await fetch(`${this.baseURL}/conversaciones`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return response.json();
  }

  async getMessages(contactId, limit = 50) {
    const response = await fetch(`${this.baseURL}/mensajes/${contactId}?limite=${limit}`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return response.json();
  }

  async sendMessage(messageData) {
    const response = await fetch(`${this.baseURL}/enviar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify(messageData)
    });
    return response.json();
  }

  async markAsRead(messageId) {
    const response = await fetch(`${this.baseURL}/marcar-leido/${messageId}`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return response.json();
  }

  async getAvailableUsers() {
    const response = await fetch(`${this.baseURL}/usuarios-disponibles`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return response.json();
  }

  async searchMessages(query, contactId = null) {
    const url = contactId 
      ? `${this.baseURL}/buscar?q=${query}&contacto=${contactId}`
      : `${this.baseURL}/buscar?q=${query}`;
    
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return response.json();
  }
}

export default new ChatService();
```

### **2. NotificationService.js**
```javascript
class NotificationService {
  constructor() {
    this.baseURL = '/api/notificaciones';
    this.token = localStorage.getItem('authToken');
  }

  async getNotifications(includeRead = false, limit = 50) {
    const response = await fetch(
      `${this.baseURL}?incluir_leidas=${includeRead}&limite=${limit}`,
      {
        headers: { 'Authorization': `Bearer ${this.token}` }
      }
    );
    return response.json();
  }

  async markAsRead(notificationId) {
    const response = await fetch(`${this.baseURL}/${notificationId}/leer`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return response.json();
  }

  async getStatistics() {
    const response = await fetch(`${this.baseURL}/estadisticas`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    return response.json();
  }

  // Notificaciones del navegador
  async requestPermission() {
    if ('Notification' in window) {
      return await Notification.requestPermission();
    }
    return 'denied';
  }

  showBrowserNotification(title, message, options = {}) {
    if (Notification.permission === 'granted') {
      return new Notification(title, {
        body: message,
        icon: '/logo.png',
        ...options
      });
    }
  }
}

export default new NotificationService();
```

---

## 🎨 COMPONENTES PRINCIPALES

### **1. ChatContainer.jsx**
```jsx
import React, { useState, useEffect } from 'react';
import ConversationList from './ConversationList';
import ChatWindow from './ChatWindow';
import chatService from '../../services/chatService';

const ChatContainer = () => {
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const result = await chatService.getConversations();
      if (result.success) {
        setConversations(result.conversaciones);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectConversation = async (contactId) => {
    setActiveConversation(contactId);
    try {
      const result = await chatService.getMessages(contactId);
      if (result.success) {
        setMessages(result.mensajes);
      }
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const sendMessage = async (messageData) => {
    try {
      const result = await chatService.sendMessage(messageData);
      if (result.success) {
        // Actualizar lista de mensajes
        await selectConversation(activeConversation);
        // Actualizar conversaciones
        await loadConversations();
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  if (loading) {
    return <div className="chat-loading">Cargando chat...</div>;
  }

  return (
    <div className="chat-container">
      <ConversationList 
        conversations={conversations}
        activeConversation={activeConversation}
        onSelectConversation={selectConversation}
      />
      <ChatWindow 
        messages={messages}
        activeConversation={activeConversation}
        onSendMessage={sendMessage}
      />
    </div>
  );
};

export default ChatContainer;
```

### **2. NotificationCenter.jsx**
```jsx
import React, { useState, useEffect } from 'react';
import NotificationItem from './NotificationItem';
import notificationService from '../../services/notificationService';

const NotificationCenter = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadNotifications();
    // Polling cada 30 segundos para nuevas notificaciones
    const interval = setInterval(loadNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    try {
      const result = await notificationService.getNotifications(false);
      if (result.success) {
        setNotifications(result.notificaciones);
        setUnreadCount(result.notificaciones.length);
      }
    } catch (error) {
      console.error('Error loading notifications:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      const result = await notificationService.markAsRead(notificationId);
      if (result.success) {
        await loadNotifications();
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  return (
    <div className="notification-center">
      <button 
        className="notification-bell"
        onClick={() => setIsOpen(!isOpen)}
      >
        🔔
        {unreadCount > 0 && (
          <span className="notification-badge">{unreadCount}</span>
        )}
      </button>
      
      {isOpen && (
        <div className="notification-dropdown">
          <div className="notification-header">
            <h3>Notificaciones</h3>
            <button onClick={() => setIsOpen(false)}>✕</button>
          </div>
          
          <div className="notification-list">
            {notifications.length === 0 ? (
              <div className="no-notifications">
                No hay notificaciones nuevas
              </div>
            ) : (
              notifications.map(notification => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onMarkAsRead={markAsRead}
                />
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationCenter;
```

---

## 📱 CARACTERÍSTICAS A IMPLEMENTAR

### **Funcionalidades Básicas (Prioridad Alta)**
1. ✅ **Lista de conversaciones** con usuarios disponibles
2. ✅ **Ventana de chat** con mensajes en tiempo real
3. ✅ **Envío de mensajes** con validación
4. ✅ **Notificaciones no leídas** con contador
5. ✅ **Centro de notificaciones** dropdown
6. ✅ **Búsqueda de mensajes** dentro de conversaciones

### **Funcionalidades Avanzadas (Prioridad Media)**
1. 🔄 **Estados de mensaje** (enviando, enviado, leído)
2. 🔄 **Indicadores de usuario en línea**
3. 🔄 **Notificaciones del navegador** (Web Push)
4. 🔄 **Chat flotante/modal** para acceso rápido
5. 🔄 **Archivos adjuntos** (imagen, documentos)

### **Funcionalidades Futuras (Prioridad Baja)**
1. ⏳ **WebSocket** para tiempo real
2. ⏳ **Reacciones a mensajes** (emojis)
3. ⏳ **Mensajes de voz**
4. ⏳ **Chat grupal**
5. ⏳ **Modo oscuro**

---

## 🎨 ESTILOS CSS RECOMENDADOS

### **Variables CSS**
```css
:root {
  /* Colores del chat */
  --chat-primary: #007bff;
  --chat-secondary: #6c757d;
  --chat-success: #28a745;
  --chat-danger: #dc3545;
  --chat-warning: #ffc107;
  
  /* Colores de fondo */
  --chat-bg: #ffffff;
  --chat-sidebar-bg: #f8f9fa;
  --chat-message-own: #007bff;
  --chat-message-other: #e9ecef;
  
  /* Espaciado */
  --chat-padding: 1rem;
  --chat-margin: 0.5rem;
  --chat-border-radius: 0.5rem;
  
  /* Sombras */
  --chat-shadow: 0 2px 10px rgba(0,0,0,0.1);
  --chat-shadow-hover: 0 4px 20px rgba(0,0,0,0.15);
}
```

### **Estructura Base**
```css
.chat-container {
  display: grid;
  grid-template-columns: 300px 1fr;
  height: 600px;
  border: 1px solid #dee2e6;
  border-radius: var(--chat-border-radius);
  overflow: hidden;
  box-shadow: var(--chat-shadow);
}

.conversation-list {
  background: var(--chat-sidebar-bg);
  border-right: 1px solid #dee2e6;
  overflow-y: auto;
}

.chat-window {
  display: flex;
  flex-direction: column;
  background: var(--chat-bg);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--chat-padding);
}

.message-bubble {
  max-width: 70%;
  margin: var(--chat-margin) 0;
  padding: 0.75rem 1rem;
  border-radius: var(--chat-border-radius);
  word-wrap: break-word;
}

.message-bubble.own {
  background: var(--chat-message-own);
  color: white;
  margin-left: auto;
  border-bottom-right-radius: 0.25rem;
}

.message-bubble.other {
  background: var(--chat-message-other);
  color: #333;
  border-bottom-left-radius: 0.25rem;
}

.notification-center {
  position: relative;
  display: inline-block;
}

.notification-bell {
  position: relative;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: var(--chat-danger);
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

---

## 🔄 FLUJO DE DATOS

### **1. Inicialización de la App**
```
App Start → Load Conversations → Load Notifications → Setup Polling
```

### **2. Envío de Mensaje**
```
User Input → Validate → Send to API → Update UI → Refresh Conversations
```

### **3. Recepción de Notificaciones**
```
Polling Check → New Notifications → Update UI → Show Browser Notification
```

### **4. Selección de Conversación**
```
Click Contact → Load Messages → Mark as Read → Update Counters
```

---

## 🧪 TESTING FRONTEND

### **Tests de Componentes**
```javascript
// ChatContainer.test.js
import { render, screen, waitFor } from '@testing-library/react';
import ChatContainer from '../ChatContainer';
import chatService from '../../services/chatService';

jest.mock('../../services/chatService');

test('loads and displays conversations', async () => {
  chatService.getConversations.mockResolvedValue({
    success: true,
    conversaciones: [
      { id_contacto: 1, nombre_contacto: 'Dr. Martínez' }
    ]
  });

  render(<ChatContainer />);
  
  await waitFor(() => {
    expect(screen.getByText('Dr. Martínez')).toBeInTheDocument();
  });
});
```

### **Tests de Servicios**
```javascript
// chatService.test.js
import chatService from '../chatService';

// Mock fetch
global.fetch = jest.fn();

test('sends message successfully', async () => {
  fetch.mockResolvedValueOnce({
    json: async () => ({
      success: true,
      id_mensaje: 123
    })
  });

  const result = await chatService.sendMessage({
    id_destinatario: 1,
    mensaje: 'Test message'
  });

  expect(result.success).toBe(true);
  expect(result.id_mensaje).toBe(123);
});
```

---

## 📦 DEPENDENCIAS RECOMENDADAS

### **React/Next.js**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "date-fns": "^2.30.0",
    "react-router-dom": "^6.8.0",
    "styled-components": "^6.1.0"
  },
  "devDependencies": {
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^5.16.5",
    "jest": "^29.0.0"
  }
}
```

### **Vue.js**
```json
{
  "dependencies": {
    "vue": "^3.3.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0",
    "date-fns": "^2.30.0"
  },
  "devDependencies": {
    "@vue/test-utils": "^2.4.0",
    "vitest": "^0.34.0"
  }
}
```

---

## 🚀 PLAN DE IMPLEMENTACIÓN MAÑANA

### **Fase 1: Setup Inicial (30 min)**
1. ✅ Crear estructura de carpetas
2. ✅ Instalar dependencias
3. ✅ Configurar servicios base

### **Fase 2: Chat Básico (2-3 horas)**
1. 🔄 Implementar ChatService
2. 🔄 Crear ConversationList
3. 🔄 Crear ChatWindow básica
4. 🔄 Implementar envío de mensajes

### **Fase 3: Notificaciones (1-2 horas)**
1. 🔄 Implementar NotificationService
2. 🔄 Crear NotificationCenter
3. 🔄 Implementar polling de notificaciones
4. 🔄 Integrar notificaciones del navegador

### **Fase 4: Integración y Testing (1 hora)**
1. 🔄 Integrar componentes en la app principal
2. 🔄 Testing básico de funcionalidades
3. 🔄 Ajustes de UI/UX
4. 🔄 Documentación final

### **Fase 5: Refinamiento (1 hora)**
1. 🔄 Optimizar rendimiento
2. 🔄 Mejorar estilos CSS
3. 🔄 Añadir animaciones básicas
4. 🔄 Testing final

---

## 🔧 COMANDOS RÁPIDOS

### **Desarrollo**
```bash
# Instalar dependencias del chat
npm install axios date-fns

# Ejecutar en modo desarrollo
npm run dev

# Ejecutar tests
npm test

# Build para producción
npm run build
```

### **Testing del Backend**
```bash
# Iniciar servidor Flask
python app.py

# Ejecutar tests de chat
python tests/test_chat_notificaciones_api.py

# Verificar endpoints manualmente
curl -X GET http://localhost:5000/api/chat/conversaciones \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📞 SOPORTE Y RECURSOS

### **Documentación del Backend**
- **Swagger UI**: http://localhost:5000/docs/
- **Health Check**: http://localhost:5000/health
- **Endpoints**: Documentados en `/static/swagger.json`

### **Archivos Clave del Backend**
- `src/api/Components/ChatComponent.py` - Componente de chat
- `src/api/Components/NotificacionesComponent.py` - Componente de notificaciones
- `src/api/Service/ChatService.py` - Servicio de chat
- `src/api/Service/NotificacionesService.py` - Servicio de notificaciones
- `src/utils/general/NotificationScheduler.py` - Job scheduler

### **Base de Datos**
- Tablas: `mensajes_chat`, `notificaciones_push`, `configuracion_notificaciones_push`
- Script de creación: `src/utils/database/03_notificaciones_chat.sql`

---

## 🎯 OBJETIVOS DEL DÍA

### **Mínimo Viable (Must Have)**
- ✅ Chat funcional con envío y recepción de mensajes
- ✅ Lista de conversaciones actualizada
- ✅ Centro de notificaciones básico
- ✅ Integración completa con APIs existentes

### **Funcionalidades Adicionales (Nice to Have)**
- 🔄 Notificaciones del navegador
- 🔄 Búsqueda de mensajes
- 🔄 Estados de lectura
- 🔄 Interfaz responsive

### **Entregables**
1. 📱 **Aplicación frontend** funcionando completamente
2. 📖 **Documentación** de componentes y servicios
3. 🧪 **Tests básicos** de funcionalidades críticas
4. 🎨 **UI/UX** pulida y profesional

---

**¡El backend está 100% listo! Mañana solo hay que implementar el frontend e integrar con las APIs ya funcionales. Todo el trabajo pesado del sistema de chat y notificaciones ya está completo. 🚀**