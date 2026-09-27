"""Chapter 28: tracing an agent with OpenTelemetry, the standard most observability
tools read (Jaeger, Grafana Tempo, Honeycomb, Datadog, Langfuse and others).

The agent code doesn't change. We wrap the two things it calls, the model client and
run_tool, so every run produces a trace:
    invoke_agent                     one per question
      chat claude-sonnet-5           one per model call: tokens, stop reason
      execute_tool get_current_date  one per tool call: name, error flag
Attribute names follow OpenTelemetry's GenAI semantic conventions (gen_ai.*), so tools
that understand them can show token use and cost per step.

Run:  python ch28_otel.py     (prints spans; spans.jsonl gets one JSON line per span)"""
import json
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (SimpleSpanProcessor, SpanExporter,
                                            SpanExportResult)
import ch04_agent

class JsonLinesExporter(SpanExporter):
    """Writes each finished span as one JSON line. In production you'd use the OTLP
    exporter instead, pointed at your collector: the code above it stays the same."""
    def __init__(self, path="spans.jsonl"):
        self.path = path

    def export(self, spans):
        with open(self.path, "a") as f:
            for s in spans:
                f.write(json.dumps({"name": s.name,
                                    "trace_id": f"{s.context.trace_id:032x}",
                                    "span_id": f"{s.context.span_id:016x}",
                                    "parent_id": (f"{s.parent.span_id:016x}"
                                                  if s.parent else None),
                                    "ms": round((s.end_time - s.start_time) / 1e6, 1),
                                    "attributes": dict(s.attributes)}) + "\n")
        return SpanExportResult.SUCCESS

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(JsonLinesExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("building-agentic-ai")

class TracedClient:
    """Looks like the Anthropic client to run_agent; adds a span around each call."""
    def __init__(self, client):
        self.client = client

    @property
    def messages(self):
        outer = self
        class Messages:
            def create(self, **kw):
                with tracer.start_as_current_span(f"chat {kw['model']}") as span:
                    span.set_attribute("gen_ai.operation.name", "chat")
                    span.set_attribute("gen_ai.request.model", kw["model"])
                    r = outer.client.messages.create(**kw)
                    span.set_attribute("gen_ai.usage.input_tokens",
                                       r.usage.input_tokens)
                    span.set_attribute("gen_ai.usage.output_tokens",
                                       r.usage.output_tokens)
                    span.set_attribute("gen_ai.response.finish_reasons",
                                       [r.stop_reason])
                    return r
        return Messages()

def traced_tool(run_tool):
    def wrapper(name, args):
        with tracer.start_as_current_span(f"execute_tool {name}") as span:
            span.set_attribute("gen_ai.operation.name", "execute_tool")
            span.set_attribute("gen_ai.tool.name", name)
            # arguments are NOT recorded: they may hold personal data
            out = run_tool(name, args)
            span.set_attribute("error", str(out).startswith("ERROR"))
            return out
    return wrapper

def run_traced(question, tools, run_tool, **kw):
    ch04_agent._client = TracedClient(ch04_agent.get_client())
    try:
        with tracer.start_as_current_span("invoke_agent") as span:
            span.set_attribute("gen_ai.operation.name", "invoke_agent")
            answer, messages, stats = ch04_agent.run_agent(
                question, tools, traced_tool(run_tool), verbose=False, **kw)
            span.set_attribute("agent.steps", stats["steps"])
            span.set_attribute("agent.stop_reason", str(stats["stop_reason"]))
            return answer, messages, stats
    finally:
        ch04_agent._client = ch04_agent._client.client      # unwrap again

if __name__ == "__main__":
    from ch03_tools import TOOLS, run_tool
    print(run_traced("How many days until July 4 next year?", TOOLS, run_tool)[0])
    for line in open("spans.jsonl").read().splitlines()[-5:]:
        span = json.loads(line)
        print(f"{span['name']:<32} {span['ms']:>8} ms  {span['attributes']}")
