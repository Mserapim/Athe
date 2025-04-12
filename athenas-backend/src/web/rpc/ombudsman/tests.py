# -*- coding:utf-8 -*-

import json, re
from io import BytesIO
from django.test import TestCase, Client
from rh.models import Pessoa as Person
from auth.ws.models import UserPermission


def clear_text(string):
    if isinstance(string, str):
        return re.sub(r"\W", "", string)
    return string


class OmbudsmanServerTestCase(TestCase):

    def _endpoint(self, part):
        return "/".join([self.api_uri, part, ""])

    def _test_status_200(self, response):
        self.assertEqual(response.status_code, 200, response.status_code)

    def _test_is_response_json(self, response):
        self.json_loaded = json.loads(response.content)
        self.assertIsInstance(self.json_loaded, dict)

    def _test_is_success(self):
        self.assertTrue(self.json_loaded["success"], self.json_loaded)

    def _test_response_requirements(self, response):
        self._test_status_200(response)
        self._test_is_response_json(response)
        self._test_is_success()

    def setUp(self):
        user_perm = UserPermission.objects.get(
            application__title="Ombudsman Client", user__username="web"
        )

        credentials = ":".join([user_perm.application.app_key, user_perm.user_token])
        headers = {"HTTP_AUTHORIZATION": credentials}

        self.api_uri = "/athenas/OmbudsmanServer"
        self.client = Client(**headers)

    def test_get_form_choices(self):
        endpoint = self._endpoint("form_choices")

        response = self.client.get(endpoint)
        self._test_response_requirements(response)

        self.assertIn("choices", self.json_loaded)
        choices = self.json_loaded["choices"]

        for key in [
            "PERSON_TYPE",
            "SUBJECT",
            "SCHOOL",
            "GENRE",
            "YESNO",
            "ADDRESS_TYPE",
            "PUBLIC_PLACE_TYPE",
            "PHONE_TYPE",
            "CITY",
            "RACE",
            "MARITAL_STATUS",
        ]:
            self.assertIn(key, choices)
            self.assertIsInstance(choices[key], list, "Failed choice %s" % key)

    def _base_manifestation_params(self):
        return {
            "subject": "Denúncia",
            "text": """
            Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quod sint corrupti rem aperiam voluptatem
            impedit ad aut repellendus doloremque, quia atque eligendi non perferendis debitis quos magni nulla suscipit maiores!
            Mollitia dolore earum, a corporis consequatur cum delectus totam facilis laborum voluptatem
            temporibus eligendi. Cum modi consequuntur quo quas ipsam, veritatis aperiam. Id expedita, soluta provident nam itaque
            sapiente impedit accusamus non perferendis molestias veniam, qui natus ex reiciendis neque sequi fuga odit mollitia.
            """,
        }

    def _anonymous_manifestation_params(self):
        params = self._base_manifestation_params()
        params.update(person_kind=0, person="ouvidoria-anonimo")
        return params

    def test_create_anonymous_manifestation(self):

        endpoint = self._endpoint("anonymous_manifestation")
        params = self._anonymous_manifestation_params()
        response = self.client.post(endpoint, params)

        self._test_response_requirements(response)

        self.assertEqual(self.json_loaded["message"], "Manifestação criada.")
        self.assertIn("protocol", self.json_loaded)
        self.assertTrue(self.json_loaded["protocol"])

    def test_create_anonymous_manifestation_with_file_upload(self):

        endpoint = self._endpoint("anonymous_manifestation")
        params = self._anonymous_manifestation_params()

        params.update(file=BytesIO(b"binarydata"))

        response = self.client.post(endpoint, params)

        self._test_response_requirements(response)

        self.assertEqual(self.json_loaded["message"], "Manifestação criada.")
        self.assertIn("protocol", self.json_loaded)
        protocol_code = self.json_loaded["protocol"]
        self.assertTrue(protocol_code)

        search_endpoint = "/".join(["search", protocol_code])
        response = self.client.get(self._endpoint(search_endpoint))
        protocol = json.loads(response.content).get("protocol")
        self.assertGreater(len(protocol["attachs"]), 0)

    def _person_base_manifestation_params(self):
        params = self._base_manifestation_params()
        params.update(
            {
                "address_type": 1,
                "public_place_type": 9,
                "public_place": "Quadra 212 Norte",
                "zipcode": "77132-789",
                "extra": "Conj 2",
                "neighborhood": "Centro",
                "number": "5",
                "city": 12178,
                "phone_type": 1,
                "phone_number": "63 98448-2854",
                "name": "Fulano da Silva",
                "email": "fulano@email.com",
            }
        )
        return params

    def _citizen_manifestation_params(self):
        params = self._person_base_manifestation_params()
        params.update(
            {
                "cpf": "261.881.314-64",
                "genre": "M",
                "marital_status": 7,
                "race": 5,
                "school": 8,
                "live_in_referenced_city": 1,
            }
        )
        return params

    def test_create_citizen_manifestation(self):

        endpoint = self._endpoint("citizen_manifestation")
        params = self._citizen_manifestation_params()
        response = self.client.post(endpoint, params)

        self._test_response_requirements(response)

        self.assertEqual(self.json_loaded["message"], "Manifestação criada.")
        self.assertIn("protocol", self.json_loaded)

        protocol_number = self.json_loaded["protocol"]

        person = Person.objects.get(prot_interessado__codigo=protocol_number)
        self.assertTrue(person)
        self.assertEqual(person.email, params["email"])

        address = person.address.first()
        self.assertEqual(address.cep, clear_text(params["zipcode"]))

        phone = person.phone.first()
        self.assertEqual(phone.numero, clear_text(params["phone_number"]))

    def test_create_legal_person_manifestation(self):

        endpoint = self._endpoint("legal_person_manifestation")
        params = self._person_base_manifestation_params()
        params.update(cnpj="23.716.874/0001-45")
        response = self.client.post(endpoint, params)

        self._test_response_requirements(response)

        self.assertEqual(self.json_loaded["message"], "Manifestação criada.")
        self.assertIn("protocol", self.json_loaded)

        protocol_number = self.json_loaded["protocol"]

        person = Person.objects.get(prot_interessado__codigo=protocol_number)
        self.assertTrue(person)
        self.assertEqual(person.email, params["email"])

        address = person.address.first()
        self.assertEqual(address.cep, clear_text(params["zipcode"]))

        phone = person.phone.first()
        self.assertEqual(phone.numero, clear_text(params["phone_number"]))

    def test_search_protocol(self):
        endpoint = self._endpoint("anonymous_manifestation")
        params = self._anonymous_manifestation_params()
        response = self.client.post(endpoint, params)

        protocol_code = json.loads(response.content).get("protocol")
        endpoint_part = "/".join(["search", protocol_code])
        endpoint = self._endpoint(endpoint_part)

        response = self.client.get(endpoint)

        self._test_response_requirements(response)
        self.assertIn("protocol", self.json_loaded)
        protocol = self.json_loaded["protocol"]

        self.assertGreater(len(protocol["moves"]), 0)

        move = protocol["moves"][0]
        self.assertIn("to", move)
        self.assertIn("sent_date", move)
        self.assertIn("feedback", move)
        self.assertIn("attachs", move)
        self.assertIsInstance(move["attachs"], list)

        self.assertIsInstance(protocol["lawsuits"], list)
        self.assertIsInstance(protocol["attachs"], list)

    def _test_response_data_x_params(self, params, response_data):
        for k, v in list(response_data.items()):
            self.assertIn(k, params)
            value = params[k]
            if (
                isinstance(value, str)
                and "@" not in value
                and ("-" in value or "." in value or "/" in value)
            ):
                value = clear_text(value)
            self.assertEqual(v, value)

    def test_load_personal_data(self):
        endpoint = self._endpoint("load_personal_data")

        params = self._citizen_manifestation_params()
        self.client.post(self._endpoint("citizen_manifestation"), params)

        response = self.client.get("%s?cpf=%s" % (endpoint, clear_text(params["cpf"])))
        self._test_response_requirements(response)
        self._test_response_data_x_params(params, self.json_loaded["data"])

        params = self._person_base_manifestation_params()
        params.update(cnpj="23.716.874/0001-45")
        self.client.post(self._endpoint("legal_person_manifestation"), params)

        response = self.client.get(
            "%s?cnpj=%s" % (endpoint, clear_text(params["cnpj"]))
        )
        self._test_response_requirements(response)
        self._test_response_data_x_params(params, self.json_loaded["data"])
