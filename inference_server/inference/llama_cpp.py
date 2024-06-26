from threading import Lock
from typing import Iterator, Union, Optional
from llama_cpp import Completion, CompletionChunk, Llama

from inference.types import InferenceOptions, ModelLoadingOptions
from inference.prompts import PromptTemplate, get_tmpl

class LlamaCppModel:
    def __init__(
        self,
        path: str,
        options: ModelLoadingOptions = ModelLoadingOptions(),
    ) -> None:
        self.mutex = Lock()
        self.options = options
        self.model = Llama(
            model_path=path,
            n_ctx=options.n_ctx,
            n_batch=options.n_batch,
            n_gpu_layers=options.n_gpu_layers,
            n_threads=options.n_threads,
            verbose=False,
        )
        self.prompt_tmpl = get_tmpl(self.options.prompt_tmpl)
        print(f"Successfully loaded model: {path}")

    def __del__(self):
        del self.model
        print(f"Successfully unloaded model")

    def infer(
        self, options: InferenceOptions, prompt_tmpl: Optional[PromptTemplate] = None
    ) -> Union[Completion, Iterator[CompletionChunk]]:
        pt = self.prompt_tmpl if prompt_tmpl is None else prompt_tmpl
        with self.mutex:
            return self.model(
                prompt=pt.get_prompt(options.messages),
                max_tokens=options.max_tokens,
                temperature=options.temperature,
                top_p=options.top_p,
                top_k=options.top_k,
                stop=pt.stop,
            )
