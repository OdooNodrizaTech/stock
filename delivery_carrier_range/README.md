El módulo contiene el desarrollo que permite realizar algunas mejoras respecto a stock_picking.

## Parámetros de configuración
- arelux_stock_picking_delivery_carrier_default_carrier_id

Se añade el apartado del menú "Rangos precios" en Inventario > Configuración > Carriers, apartado que permite definir rangos de precios por transportistas.

Al crearse un albarán se calcula el "coste_estimado" de acuerdo a los rangos de precios definidos y al transportista del mismo según el peso del mismo.

Se modifican las siguientes vistas: delivery.view_picking_withcarrier_out_form
