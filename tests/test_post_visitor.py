from unittest import TestCase
from unittest.mock import MagicMock, patch

from test_config import event
from post_visitor.app import (
    lambda_handler,
    process_visitor_photo,
    process_id_photo,
    create_visitor_and_history,
)


class TestPostVisitor(TestCase):
    def setUp(self):
        self.mock_s3_client = patch("boto3.client").start()
        self.event = event.event
        self.context = None

    @patch("vms_layer.helpers.db_helper.table")
    @patch("vms_layer.utils.s3_signed_url_generator.boto3.client")
    def test_process_visitor_photo(self, mock_db_helper, mock_s3_client):
        mock_db_helper.return_value.create_item.return_value = {}
        mock_s3_client.return_value.generate_presigned_url.return_value = (
            "https://test.com"
        )
        request_body = {
            "vistorPhotoBlob": "base64",
        }
        raw_visitor_id = "1234"
        result = process_visitor_photo(request_body, raw_visitor_id)
        self.assertEqual(result, "1234#photo_self")
