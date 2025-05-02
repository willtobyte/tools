import asyncio
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Set

import langcodes
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
import argparse

class Translation(BaseModel):
    translation: str = Field(..., description="Exact translation of the provided string.")

STRING_PATTERN = re.compile(r'_\(\s*["\'](.*?)["\']\s*\)')
semaphore = asyncio.Semaphore(4)

async def main():
    parser = argparse.ArgumentParser(description="Generate locales from Lua files.")
    parser.add_argument("-d", "--directory", required=True, help="Directory to scan for Lua files.")
    parser.add_argument("-l", "--language", required=True, help="Target language code (ISO 639-1).")
    args = parser.parse_args()

    directory = Path(args.directory)
    language = args.language
    language_name = langcodes.Language.make(language).language_name()

    model = ChatOpenAI(model="gpt-4", temperature=0)
    parser_output = PydanticOutputParser(pydantic_object=Translation)

    lua_files = list(directory.rglob("*.lua"))
    all_strings: Set[str] = set()

    for lua_file in lua_files:
        try:
            content = lua_file.read_text(encoding="utf-8")
            all_strings.update(STRING_PATTERN.findall(content))
        except Exception as e:
            print(f"Error reading {lua_file}: {e}")
            continue

    print(f"Translating {len(all_strings)} strings to {language_name} ({language})...")

    async def translate(text: str) -> str:
        prompt = PromptTemplate(
            template="""Translate the following text to {language}.

Text: "{text}"

Respond strictly in the following JSON format:
{format_instructions}""",
            input_variables=["language", "text"],
            partial_variables={"format_instructions": parser_output.get_format_instructions()},
        )
        input_prompt = prompt.format_prompt(language=language_name, text=text)
        async with semaphore:
            try:
                response = await model.ainvoke(input_prompt)
                result = parser_output.parse(response.content)
                return result.translation
            except Exception as e:
                print(f"Error translating '{text}': {e}")
                return text

    tasks = [translate(s) for s in all_strings]
    translations = await asyncio.gather(*tasks)
    result: Dict[str, str] = dict(zip(all_strings, translations))

    output_file = Path("translations.json")
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Translations saved to: {output_file.resolve()}")

if __name__ == "__main__":
    asyncio.run(main())
