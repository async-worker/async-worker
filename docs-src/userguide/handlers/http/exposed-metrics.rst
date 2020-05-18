Métricas expostas para aplicações HTTP
==========================================

Aqui estão descritas todas as métricas automaticamente expostas para qualquer aplicação asyncworker HTTP.


- ``http_request_duration``
    labels ("method", "path", "status")

    buckets (0.01, 0.05, 0.1, INFINITY)

    Histograma contento o tempo de duração de cada request.
