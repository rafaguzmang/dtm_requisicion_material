from odoo import fields, api, models
from datetime import datetime

from pkg_resources import require


class Requisicion(models.Model):
    _name = "dtm.requisicion"
    _description = "Modulo para la solicitud de materiales"
    _rec_name = "folio"
    _order = "id desc"
    #------------------------------Funciones Default ----------------------------
    def action_pasive(self):
        pass
    def action_autoNum(self):  # Genera número consecutivo de NPI y OT

        get_odt = self.env['dtm.requisicion'].search([], order='folio desc', limit=1)
        folio = get_odt.folio + 1
        return folio

    def firma_usuario(self):
        return self.env.user.partner_id.name

    def direccion_default(self):
        usuario = self.env.user.partner_id.email
        departamento = "diseno" if usuario in ["ingenieria@dtmindustry.com","ingenieria2@dtmindustry.com"] else "almacen" if usuario in ["almacen@dtmindustry.com"] else\
            "ventas" if usuario in ["ventas1@dtmindustry.com"] else "produccion" if usuario in ["manufactura@dtmindustry.com"] else "direccion" if usuario in ["hugo_chacon@dtmindustry.com","manufactura2@dtmindustry.com"] else\
            "Sistemas" if usuario in ["rafaguzmang@hotmail.com"] else "calidad" if usuario in ["calidad2@dtmindustry.com"] else ""

        return departamento
    #-------------------------------- Datos -------------------------------------
    folio = fields.Integer(string="Folio", default=action_autoNum, readonly=True)
    servicio = fields.Char(string="OT/OT Servicio")
    departamento = fields.Selection(string="Departamento",selection=[("diseno","Diseño"),("almacen","Almacén"),("ventas","Ventas"),
                                                                     ("produccion","Producción"),("direccion","Dirección"),("mantenimiento","Mantenimiento"),
                                                                     ("calidad","Calidad"),("sistemas","Sistemas")],default= direccion_default)
    solicitante_id = fields.Many2one('dtm.hr.empleados',string="Solicitó", require=True)
    date_in = fields.Date(string="Fecha de Solicitud", default=datetime.today(), readonly=True)

    tipo = fields.Selection(string="Tipo de Servicio", selection=[("proyecto", "Proyecto"), ("servicio", "Servicio"),
                                                                  ("consumible", "Consumible/Interno")], default="servicio")
    extraordinarias = fields.Text(string="Compras Extraordinarias")
    facturas = fields.Char(string="No. De Factura(s)")
    material_ids = fields.One2many("dtm.requisicion.material", "model_id", string="Lista")

    def action_comprar(self):
        for material in self.material_ids:
            vals = {
                'orden_trabajo':str(self.folio),
                'tipo_orden':'Requi',
                'codigo':material.codigo,
                'nombre':f"{material.nombre.nombre} {material.nombre.medida if material.nombre.medida else ''}",
                'cantidad':material.cantidad,
                'disenador':f"{self.solicitante_id.nombre} ({self.departamento})",
                'servicio':False,
                'nesteo':True
            }
            if not material.comprado:
                get_compras = self.env['dtm.compras.requerido'].search([("orden_trabajo","=",str(self.folio)),("codigo","=",material.nombre.id)])
                get_compras.write(vals) if get_compras else get_compras.create(vals)


class Materiales(models.Model):
    _name = "dtm.requisicion.material"
    _description = "Modelo para guardar la lista de material"

    model_id = fields.Many2one("dtm.requisicion")

    nombre = fields.Many2one("dtm.diseno.almacen",string="Material")
    codigo = fields.Integer(related='nombre.id')
    unidad = fields.Char(string="Unidad")
    cantidad = fields.Integer(string="Cantidad")
    comprado = fields.Boolean(string="Comprado",readonly = True)
