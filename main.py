
__version__ = (1, 0, 0)

import contextlib
import logging
import re

import requests
from telethon.tl.types import Message

from .. import loader, utils  # noqa

logger = logging.getLogger(__name__)


@loader.tds
class ChatGPT(loader.Module):
    """ChatGPT AI API interaction"""

    strings = {
        "name": "ChatGPT",
        "no_args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>No arguments"
            " provided</b>"
        ),
        "question": (
            "<emoji document_id=5974038293120027938>👤</emoji> <b>Question:</b>"
            " {question}\n"
        ),
        "answer": (
            "{answer}"
        ),
        "loading": "<code>Loading...</code>",
        "no_api_key": (
            "<b>🚫 No API key provided</b>\n<i><emoji"
            " document_id=5199682846729449178>ℹ️</emoji> Get it from official OpenAI"
            " website and add it to config</i>"
        ),
    }

    strings_ru = {
        "no_args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Не указаны"
            " аргументы</b>"
        ),
        "question": (
            "<emoji document_id=5974038293120027938>👤</emoji> <b>Вопрос:</b>"
            " {question}\n"
        ),
        "answer": (
            "{answer}"
        ),
        "loading": "<code>Загрузка...</code>",
        "no_api_key": (
            "<b>🚫 Не указан API ключ</b>\n<i><emoji"
            " document_id=5199682846729449178>ℹ️</emoji> Получите его на официальном"
            " сайте OpenAI и добавьте в конфиг</i>"
        ),
    }

    strings_es = {
        "no_args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>No se han"
            " proporcionado argumentos</b>"
        ),
        "question": (
            "<emoji document_id=5974038293120027938>👤</emoji> <b>Pregunta:</b>"
            " {question}\n"
        ),
        "answer": (
            "{answer}"
        ),
        "loading": "<code>Cargando...</code>",
        "no_api_key": (
            "<b>🚫 No se ha proporcionado una clave API</b>\n<i><emoji"
            " document_id=5199682846729449178>ℹ️</emoji> Obtenga una en el sitio web"
            " oficial de OpenAI y agréguela a la configuración</i>"
        ),
    }

    strings_fr = {
        "no_args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Aucun argument"
            " fourni</b>"
        ),
        "question": (
            "<emoji document_id=5974038293120027938>👤</emoji> <b>Question:</b>"
            " {question}\n"
        ),
        "answer": (
            "{answer}"
        ),
        "loading": "<code>Chargement...</code>",
        "no_api_key": (
            "<b>🚫 Aucune clé API fournie</b>\n<i><emoji"
            " document_id=5199682846729449178>ℹ️</emoji> Obtenez-en un sur le site"
            " officiel d'OpenAI et ajoutez-le à la configuration</i>"
        ),
    }

    strings_de = {
        "no_args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Keine Argumente"
            " angegeben</b>"
        ),
        "question": (
            "<emoji document_id=5974038293120027938>👤</emoji> <b>Frage:</b>"
            " {question}\n"
        ),
        "answer": (
            "{answer}"
        ),
        "loading": "<code>Laden...</code>",
        "no_api_key": (
            "<b>🚫 Kein API-Schlüssel angegeben</b>\n<i><emoji"
            " document_id=5199682846729449178>ℹ️</emoji> Holen Sie sich einen auf der"
            " offiziellen OpenAI-Website und fügen Sie ihn der Konfiguration hinzu</i>"
        ),
    }

    strings_tr = {
        "no_args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Argümanlar"
            " verilmedi</b>"
        ),
        "question": (
            "<emoji document_id=5974038293120027938>👤</emoji> <b>Soru:</b> {question}\n"
        ),
        "answer": (
            "{answer}"
        ),
        "loading": "<code>Yükleniyor...</code>",
        "no_api_key": (
            "<b>🚫 API anahtarı verilmedi</b>\n<i><emoji"
            " document_id=5199682846729449178>ℹ️</emoji> OpenAI'nın resmi websitesinden"
            " alın ve yapılandırmaya ekleyin</i>"
        ),
    }

    strings_uz = {
        "no_args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Argumentlar"
            " ko'rsatilmadi</b>"
        ),
        "question": (
            "<emoji document_id=5974038293120027938>👤</emoji> <b>Savol:</b>"
            " {question}\n"
        ),
        "answer": (
            "{answer}"
        ),
        "loading": "<code>Yuklanmoqda...</code>",
        "no_api_key": (
            "<b>🚫 API kalit ko'rsatilmadi</b>\n<i><emoji"
            " document_id=5199682846729449178>ℹ️</emoji> Ofitsial OpenAI veb-saytidan"
            " oling</i>"
        ),
    }

    strings_it = {
        "no_args": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Nessun argomento"
            " fornito</b>"
        ),
        "question": (
            ""
            ""
        ),
        "answer": (
            "{answer}"
        ),
        "loading": "<code>Caricamento...</code>",
        "no_api_key": (
            "<b>🚫 Nessuna chiave API fornita</b>\n<i><emoji"
            " document_id=5199682846729449178>ℹ️</emoji> Ottienila dal sito ufficiale"
            " di OpenAI e aggiungila al tuo file di configurazione</i>"
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                "",
                "API key from OpenAI",
                validator=loader.validators.Hidden(loader.validators.String()),
            ),
        )

    async def _make_request(
        self,
        method: str,
        url: str,
        headers: dict,
        data: dict,
    ) -> dict:
        resp = await utils.run_sync(
            requests.request,
            method,
            url,
            headers=headers,
            json=data,
        )
        return resp.json()

    def _process_code_tags(self, text: str) -> str:
        return re.sub(
            r"`(.*?)`",
            r"<code>\1</code>",
            re.sub(r"```(.*?)```", r"<code>\1</code>", text, flags=re.DOTALL),
            flags=re.DOTALL,
        )



    async def _get_chat_completion(self, prompt: str) -> str:
        htf = ('Перепеши текст : ')
        promt = (htf+prompt)
        resp = await self._make_request(
            method="POST",
            url="https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f'Bearer {self.config["api_key"]}',
            },
            data={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": promt}],
            },
        )
        if resp.get("error", None):
            return f"🚫 {resp['error']['message']}"
        return resp["choices"][0]["message"]["content"]

    @loader.command(
        ru_doc="<текст> - Правильно написать текст",
        it_doc="<testo> - Scrive correttamente il testo",
        fr_doc="<text> - Écrire correctement le texte",
        de_doc="<text> – Text richtig schreiben",
        es_doc="<texto> - Escribe correctamente el texto",
        tr_doc="<text> - Metni doğru şekilde yaz",
        uz_doc="<matn> - matnni to'g'ri yozish",
    )
    async def correct(self, message: Message):
        """<text> - Correctly write text"""
        if self.config["api_key"] == "":
            return await utils.answer(message, self.strings("no_api_key"))

        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings("no_args"))

        await utils.answer(
            message,
            "\n".join(
                [
                    self.strings("answer").format(answer=self.strings("loading")),
                ]
            ),
        )
        answer = await self._get_chat_completion(args)
        await utils.answer(
            message,
            "\n".join(
                [
                    self.strings("answer").format(
                        answer=self._process_code_tags(answer)
                    ),
                ]
            ),
        )