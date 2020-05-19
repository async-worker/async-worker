Métricas expostas para aplicações HTTP
==========================================

Aqui estão descritas todas as métricas automaticamente expostas para qualquer aplicação asyncworker HTTP.


- ``http_request_duration_seconds``
    - labels
        - ``method``: Método usado no request
        - ``path``: Path do request
        - ``status``: Status code retornado, mesmo quando já uma exception.

    - ``buckets`` :py:class:`settings.METRICS_DEFAULT_HISTOGRAM_BUCKETS_IN_MS <asyncworker.conf.Settings>`

    Histograma que mede o tempo (em segundos) de cada request e distribui essas ocorrências nos buckets configurados.
