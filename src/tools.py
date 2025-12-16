from collections.abc import Callable

from src.wiki_utils import get_full_wiki_page, make_wiki_query

# TODO: make base ToolsRegistrarAPI and inherit here
class ToolsRegistrar(object):
    """
    Following MCP separation style, this class works as a storage
    for tools and their calling
    """

    def __init__(self):
        self.tools_mapping: dict = dict()
        self.tools_description_mapping: dict = dict()
        self.tools_parameters_mapping: dict = dict()

    def register(
        self,
        func: Callable,
        description: str,
        params_description: dict,
    ):
        # TODO: fill those fields from docstring
        f_name = func.__name__
        self.tools_mapping[f_name] = func
        self.tools_description_mapping[f_name] = description
        self.tools_parameters_mapping[f_name] = params_description

    def get_tools_list(self):
        ret = []
        for f_name in self.tools_mapping:
            element = dict()
            element["type"] = "function"
            element_function = dict()
            element_function["name"] = f_name
            element_function["description"] = self.tools_description_mapping[f_name]
            element_function["parameters"] = self.tools_parameters_mapping[f_name]
            element["function"] = element_function
            ret.append(element)
        return ret

    def tool_call(self, tool_name: str, *args, **kwargs):
        return self.tools_mapping[tool_name](*args, **kwargs)


def get_tool_registrar():
    tool_registry = ToolsRegistrar()

    make_wiki_query_params_description = {
        "type": "object",
        "properties": {
            "q": {
                "type": "string",
                "description": "search query to Wikipedia. Should be string",
            }
        },
        "required": ["q"],
    }

    tool_registry.register(
        make_wiki_query,
        """функция, позволяющая выполнять 
    произвольный текстовый запрос к Википедии, и получать кусочки из топ-3
    результатов поиска по Википедии. Обрати внимание, что там может быть
    неполная информация.""",
        make_wiki_query_params_description,
    )

    get_full_wiki_page_params_description = {
        "type": "object",
        "properties": {
            "page_name": {
                "type": "string",
                "description": "name of the page to get from Wikipedia",
            }
        },
        "required": ["page_name"],
    }

    tool_registry.register(
        get_full_wiki_page,
        """функция, позволяющая 
    получить полный текст страницы Википедии с названием page_name. 
    Возвращает ошибку, если такой страницы нету""",
        get_full_wiki_page_params_description,
    )

    return tool_registry
