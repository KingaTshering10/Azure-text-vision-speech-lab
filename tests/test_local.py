"""Offline regression checks; no real credentials, requests, or model downloads."""
import base64
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
from openai import AzureOpenAI

import ai_lab


def load_script(name, path):
    spec = importlib.util.spec_from_file_location(name, ai_lab.ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


receipt = load_script("receipt_cli", "01_vision/receipt_analyzer/receipt_analysis.py")
cli = load_script("chat_cli", "02_text/chat_cli.py")


class LocalChecks(unittest.TestCase):
    def make_client(self, handler):
        client = AzureOpenAI(
            api_key="offline-test-key", azure_endpoint="https://offline-test.invalid/",
            api_version="2024-10-21", max_retries=0,
            http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        )
        self.addCleanup(client.close)
        return client

    def test_image_mime_and_distinct_roles(self):
        messages = ai_lab.image_messages("Read this", ai_lab.ROOT / "01_vision/receipt.jpg", "Analyze images")
        self.assertEqual([m["role"] for m in messages], ["system", "user"])
        url = messages[1]["content"][1]["image_url"]["url"]
        self.assertTrue(url.startswith("data:image/jpeg;base64,"))
        self.assertEqual(base64.b64decode(url.split(",", 1)[1]),
                         (ai_lab.ROOT / "01_vision/receipt.jpg").read_bytes())
        png = ai_lab.image_messages("Read", ai_lab.ROOT / "01_vision/drinks.png")
        self.assertTrue(png[0]["content"][1]["image_url"]["url"].startswith("data:image/png;"))
        with self.assertRaises(FileNotFoundError):
            ai_lab.image_messages("Read", ai_lab.ROOT / "missing.jpg")

    def test_config_validation_and_hidden_key_repr(self):
        env = {"AZURE_OAI_ENDPOINT": "https://offline-test.invalid/", "AZURE_OAI_KEY": "offline-test-key",
               "AZURE_OAI_DEPLOYMENT": "custom-deployment"}
        with patch.dict(os.environ, env, clear=True), patch("dotenv.load_dotenv"):
            settings = ai_lab.AzureSettings.load("text")
            self.assertEqual(settings.deployment, "custom-deployment")
            self.assertNotIn("offline-test-key", repr(settings))
            with self.assertRaisesRegex(ValueError, "AZURE_ASR"):
                ai_lab.AzureSettings.load("asr")
        with patch.dict(os.environ, {}, clear=True), patch("dotenv.load_dotenv"):
            with self.assertRaisesRegex(ValueError, "AZURE_OAI"):
                ai_lab.AzureSettings.load()

    def test_chat_sdk_request_uses_deployment(self):
        def handler(request):
            self.assertIn("/deployments/custom-chat/chat/completions", request.url.path)
            body = json.loads(request.content)
            self.assertEqual(body["messages"], [{"role": "user", "content": "Hi"}])
            return httpx.Response(200, json={"id": "offline", "object": "chat.completion", "created": 0,
                "model": "offline", "choices": [{"index": 0, "finish_reason": "stop",
                "message": {"role": "assistant", "content": "Hello"}}]})
        client = self.make_client(handler)
        with patch.object(ai_lab, "azure_client", return_value=(client, "custom-chat")):
            self.assertEqual(ai_lab.chat([{"role": "user", "content": "Hi"}]), "Hello")

    def test_asr_routes_and_file_closure(self):
        paths = []
        def handler(request):
            paths.append(request.url.path)
            self.assertIn("multipart/form-data", request.headers["content-type"])
            return httpx.Response(200, json={"text": "Offline sample"})
        client = self.make_client(handler)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "test.wav"
            source.write_bytes(b"offline audio placeholder")
            with patch.object(ai_lab, "azure_client", return_value=(client, "custom-asr")):
                self.assertEqual(ai_lab.transcribe_audio(source), "Offline sample")
                self.assertEqual(ai_lab.transcribe_audio(source, translate=True), "Offline sample")
        self.assertTrue(paths[0].endswith("/audio/transcriptions"))
        self.assertTrue(paths[1].endswith("/audio/translations"))

    def test_tts_streams_to_new_output(self):
        def handler(request):
            body = json.loads(request.content)
            self.assertEqual(body["model"], "custom-tts")
            self.assertEqual(body["response_format"], "mp3")
            return httpx.Response(200, content=b"offline audio bytes", headers={"content-type": "audio/mpeg"})
        client = self.make_client(handler)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nested/output.mp3"
            with patch.object(ai_lab, "azure_client", return_value=(client, "custom-tts")):
                ai_lab.synthesize_speech("Hello", target)
                self.assertEqual(target.read_bytes(), b"offline audio bytes")
                with self.assertRaises(ValueError):
                    ai_lab.synthesize_speech("", target)

    def test_cli_retains_assistant_role(self):
        calls = []
        def fake_chat(messages):
            calls.append(messages)
            return "Answer"
        with patch("builtins.input", side_effect=["First", "Second", "quit"]), \
             patch.object(cli, "chat", side_effect=fake_chat), patch("sys.stdout", new_callable=io.StringIO):
            cli.main()
        self.assertEqual([m["role"] for m in calls[1]], ["system", "user", "assistant", "user"])

    def test_receipt_parser_and_item_rows(self):
        from langchain_core.runnables import RunnableLambda
        fixture = json.loads((ai_lab.ROOT / "01_vision/receipt_analyzer/receipt_result.json").read_text())
        parsed = receipt.get_response("Offline receipt text", RunnableLambda(lambda _: json.dumps(fixture)))
        rows = receipt.make_csv_rows(parsed)
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(row["Item Total"] for row in rows), 750)
        self.assertEqual(rows[0]["Total"], 817.5)
        self.assertEqual(rows[0]["Receipt Number"], "RCPT-2026-1047")
        self.assertEqual(len(receipt.make_csv_rows({})), 1)
        for invalid in [[], {"Items": "not a list"}, {"Items": ["not an object"]}]:
            with self.assertRaises(ValueError):
                receipt.make_csv_rows(invalid)


if __name__ == "__main__":
    unittest.main()
