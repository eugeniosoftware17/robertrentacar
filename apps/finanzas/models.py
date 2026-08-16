from decimal import Decimal

from django.db import models

from apps.vehiculos.models import Vehiculo


class Empleado(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido', max_length=100)
    puesto = models.CharField('Puesto', max_length=80, blank=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    email = models.EmailField('Correo', blank=True)
    salario_base = models.DecimalField(
        'Salario base (RD$)',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Referencial. Los pagos reales se registran en Nómina.',
    )
    fecha_ingreso = models.DateField('Fecha de ingreso', blank=True, null=True)
    activo = models.BooleanField('Activo', default=True)
    notas = models.TextField('Notas', blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['apellido', 'nombre']
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'


class PagoNomina(models.Model):
    class Concepto(models.TextChoices):
        SALARIO = 'salario', 'Salario'
        BONO = 'bono', 'Bono'
        COMISION = 'comision', 'Comisión'
        OTRO = 'otro', 'Otro'

    class Metodo(models.TextChoices):
        EFECTIVO = 'efectivo', 'Efectivo'
        TRANSFERENCIA = 'transferencia', 'Transferencia'
        CHEQUE = 'cheque', 'Cheque'

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name='pagos_nomina',
        verbose_name='Empleado',
    )
    concepto = models.CharField('Concepto', max_length=20, choices=Concepto.choices, default=Concepto.SALARIO)
    monto = models.DecimalField('Monto (RD$)', max_digits=10, decimal_places=2)
    fecha_pago = models.DateField('Fecha de pago')
    metodo = models.CharField('Método', max_length=20, choices=Metodo.choices, default=Metodo.EFECTIVO)
    notas = models.TextField('Notas', blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_pago', '-creado_en']
        verbose_name = 'Pago de nómina'
        verbose_name_plural = 'Pagos de nómina'

    def __str__(self):
        return f'{self.empleado} — RD$ {self.monto} ({self.fecha_pago})'


class Gasto(models.Model):
    class Categoria(models.TextChoices):
        COMBUSTIBLE = 'combustible', 'Combustible'
        SEGURO = 'seguro', 'Seguro'
        PUBLICIDAD = 'publicidad', 'Publicidad'
        OFICINA = 'oficina', 'Oficina / administrativo'
        IMPUESTOS = 'impuestos', 'Impuestos'
        OTRO = 'otro', 'Otro'

    concepto = models.CharField('Concepto', max_length=120)
    categoria = models.CharField('Categoría', max_length=20, choices=Categoria.choices, default=Categoria.OTRO)
    monto = models.DecimalField('Monto (RD$)', max_digits=10, decimal_places=2)
    fecha = models.DateField('Fecha')
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.SET_NULL,
        related_name='gastos',
        verbose_name='Vehículo (opcional)',
        blank=True,
        null=True,
        help_text='Si el gasto es específico de un vehículo, selecciónalo para incluirlo en su rentabilidad.',
    )
    notas = models.TextField('Notas', blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha', '-creado_en']
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'

    def __str__(self):
        return f'{self.concepto} — RD$ {self.monto} ({self.fecha})'
