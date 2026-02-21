class AppError(Exception):
    """도메인/서비스 공통 에러"""
    pass

class NotFoundError(AppError):
    pass

class ValidationError(AppError):
    pass

class ConflictError(AppError):
    pass