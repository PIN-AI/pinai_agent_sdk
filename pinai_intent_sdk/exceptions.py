class IntentMatchError(Exception):
    """基础异常类"""
    pass

class AgentNotFoundError(IntentMatchError):
    """Agent 不存在异常"""
    pass

class ValidationError(IntentMatchError):
    """数据验证异常"""
    pass 