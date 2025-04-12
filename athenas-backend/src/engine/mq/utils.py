def get_servico():
    from common.services.models import ScheduledServices
    import inspect

    stack = inspect.stack()
    # Obtém a chamada anterior na pilha
    caller_frame = stack[2]
    # Obtém o nome do método que chamou este
    caller_method = caller_frame.function

    # Obtém a classe e seu caminho completo se o método pertence a uma classe
    caller_instance = caller_frame.frame.f_locals.get("self")
    if caller_instance:
        caller_class = type(caller_instance).__name__
        caller_module = caller_instance.__module__
        caller_class_path = f"{caller_module}.{caller_class}"
        query = ScheduledServices.objects.filter(
            classcode__path=caller_class_path, command=caller_method
        )
        return query.first() if query.exists() else None
    else:
        return None
