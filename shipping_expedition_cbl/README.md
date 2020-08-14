El módulo contiene el desarrollo que permite realizar toda la integración respecto a CBL

## odoo.conf
- aws_access_key_id=xxxx
- aws_secret_key_id=xxxxx
- aws_region_name=eu-west-1

## Parámetros de configuración
- cbl_sender_customer
- cbl_s3_bucket
- cbl_s3_folder
- cbl_expedition_info_template_id

## Crones

### Shipping Expedition Update Cbl 
Frecuencia: cada 6 horas

Descripción: 

Revisa todas las expediciones con transportista 'cbl' con fecha de creación < hoy y cuyo estado NO sea ('cancelado', 'entregado')
Respecto a los resultados anteriores se conecta a la web ("API") de CBL para consultar el estado de la expedición y actualizarlo así como notificar por Slack si hay algún error / incidencia
