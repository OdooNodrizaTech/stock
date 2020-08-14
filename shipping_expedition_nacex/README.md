El módulo contiene el desarrollo que permite realizar toda la integración respecto a NACEX

## odoo.conf
- #nacex
- nacex_username=GRUPOARELUX
- nacex_password=xxxx

En el apartado de Inventario > Configuración > Carriers se añade el apartado "Nacex" desde donde se realizan las opciones de configuración correspondientes.


## Crones

### Shipping Expedition Update Nacex 
Frecuencia: cada 6 horas

Descripción: 

Revisa todas las expediciones con transportista 'nacex' y cuyo estado NO sea ('cancelado', 'entregado')
Respecto a los resultados anteriores se conecta al webservice de Nacex para consultar el estado de la expedición y actualizarlo así como notificar por Slack si hay algún error / incidencia
