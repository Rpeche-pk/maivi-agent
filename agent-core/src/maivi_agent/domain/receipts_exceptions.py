"""Excepciones personalizadas para el repositorio de recibos."""


class ReceiptRepositoryException(Exception):
    """Excepción base para errores del repositorio de recibos."""
    
    def __init__(self, message: str = "Error en el repositorio de recibos"):
        self.message = message
        super().__init__(self.message)


class ReceiptNotFoundError(ReceiptRepositoryException):
    """Se lanza cuando no se encuentra un recibo específico."""
    
    def __init__(self, receipt_id: str):
        self.receipt_id = receipt_id
        super().__init__(f"Recibo con ID '{receipt_id}' no encontrado")


class ReceiptSaveError(ReceiptRepositoryException):
    """Se lanza cuando falla el guardado de un recibo."""
    
    def __init__(self, message: str = "Error al guardar el recibo", original_error: Exception = None):
        self.original_error = original_error
        error_detail = f": {str(original_error)}" if original_error else ""
        super().__init__(f"{message}{error_detail}")


class ReceiptUpdateError(ReceiptRepositoryException):
    """Se lanza cuando falla la actualización de un recibo."""
    
    def __init__(self, receipt_id: str, message: str = "Error al actualizar el recibo", original_error: Exception = None):
        self.receipt_id = receipt_id
        self.original_error = original_error
        error_detail = f": {str(original_error)}" if original_error else ""
        super().__init__(f"{message} '{receipt_id}'{error_detail}")


class ReceiptQueryError(ReceiptRepositoryException):
    """Se lanza cuando falla una consulta al repositorio."""
    
    def __init__(self, query_type: str, message: str = "Error al consultar recibos", original_error: Exception = None):
        self.query_type = query_type
        self.original_error = original_error
        error_detail = f": {str(original_error)}" if original_error else ""
        super().__init__(f"{message} ({query_type}){error_detail}")


class DatabaseConnectionError(ReceiptRepositoryException):
    """Se lanza cuando falla la conexión con la base de datos."""
    
    def __init__(self, message: str = "Error de conexión con la base de datos", original_error: Exception = None):
        self.original_error = original_error
        error_detail = f": {str(original_error)}" if original_error else ""
        super().__init__(f"{message}{error_detail}")


class InvalidReceiptDataError(ReceiptRepositoryException):
    """Se lanza cuando los datos del recibo son inválidos."""
    
    def __init__(self, message: str = "Datos de recibo inválidos", field: str = None):
        self.field = field
        field_detail = f" en el campo '{field}'" if field else ""
        super().__init__(f"{message}{field_detail}")


class DuplicateReceiptError(ReceiptRepositoryException):
    """Se lanza cuando se intenta guardar un recibo duplicado."""
    
    def __init__(self, identifier: str):
        self.identifier = identifier
        super().__init__(f"Ya existe un recibo con el identificador '{identifier}'")
