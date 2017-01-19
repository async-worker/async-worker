


class MockedAMQPConnection(mock.Mock):
    """
    Mocka conexão fornecedia pelo amqp.Connection e implementa basic_get,
    basic_put, basic_ack, basic_reject para testes sem utilizar rabbit
    """
    def _basic_get(self):
        pass

    def _basic_put(self):
        pass

    def _basic_ack(self):
        pass

    def _basic_reject(self):
        pass


fetcher_js_b2w_msg = {"content_length": 177843, "tp_browser": "FF",
                      "dt_visited": 1484327800.383136, "load_images": True,
                      "website_id": 1, "htmls": [], "fetcher_type": "javascript",
                      "nr_fetch_time": 0.4497511386871338,
                      "fetch_type": "javascript", "sr_interactive_actions": {
        "actions": "[{\"order\": 1, \"params\": [\"//span[@class=\\\"variation-label\\\"]\"], \"id\": 854, \"name\": \"iteratecombo\"}]"},
                      "redirected_link": None, "_meta": {},
                      "url": "http://www.americanas.com.br/produto/122690134",
                      "use_cookies": 1, "routing_key": "fetcher.js.b2w",
                      "platform_id": None, "_step": {"process": "fetcher_b2w",
                                                     "time": "2017-01-13T15:16:40.506024",
                                                     "address": "186.234.196.217",
                                                     "routing_key": "fetcher.js.b2w",
                                                     "exchange": "fetcher"},
                      "urls": [
                          "http://www.americanas.com.br/produto/122690134?Tamanho=TAM+31",
                          "http://www.americanas.com.br/produto/122690134?Tamanho=29",
                          "http://www.americanas.com.br/produto/122690134?Tamanho=33",
                          "http://www.americanas.com.br/produto/122690134?Tamanho=32",
                          "http://www.americanas.com.br/produto/122690134?Tamanho=35",
                          "http://www.americanas.com.br/produto/122690134?Tamanho=34",
                          "http://www.americanas.com.br/produto/122690134?Tamanho=36"],
                      "bl_interactive": True, "http_code": 200,
                      "load_finished_xpath": "", "_trail": {"debug": False,
                                                            "id_": "d575dc0f-c176-4cca-a456-9c65b4fc8099",
                                                            "live": False,
                                                            "steps": ["C9X3MXdC",
                                                                      "1XChUGsf",
                                                                      "xrreZqCP"],
                                                            "priority": 2}}