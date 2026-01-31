import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.trace import get_current_span
from opentelemetry.trace.span import INVALID_SPAN_CONTEXT

class TraceIdFormatter(logging.Formatter):
    def format(self, record):
        span = get_current_span()
        trace_id = None
        if span is not None and span.get_span_context() is not None:
            ctx = span.get_span_context()
            if ctx.trace_id != INVALID_SPAN_CONTEXT.trace_id:
                trace_id = format(ctx.trace_id, '032x')
        record.trace_id = trace_id or "-"
        return super().format(record)

def setup_logger(service_name: str):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = TraceIdFormatter('%(asctime)s %(levelname)s %(name)s %(message)s trace_id=%(trace_id)s')
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    return logger

def setup_otel(app, service_name: str):
    resource = Resource(attributes={
        SERVICE_NAME: service_name
    })

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://tempo:4318"
        )
    )

    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()

    setup_logger(service_name)